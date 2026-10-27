"""Regressões offline: preservação de fala e isolamento dos derivados."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import numpy as np

RAIZ = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(RAIZ / 'motor'), str(RAIZ / 'vozes')]
import audio2


class Preparacao(unittest.TestCase):
    def test_importar_regua_nao_grava_nem_exige_voz(self):
        r = subprocess.run([sys.executable, '-c', 'import motor.tempos2'], cwd=RAIZ, capture_output=True)
        self.assertEqual(r.returncode, 0, r.stderr.decode())

    def test_bruto_com_consoante_fraca_preservado_sem_fade(self):
        from motor.tempos2 import preparar
        x = np.r_[np.full(2000, 0.00002), np.full(4000, 0.1), np.full(2000, -0.00002)].astype('float32')
        self.assertTrue(np.array_equal(preparar(x)[0], x), 'Consoante/cauda não podem ser alteradas')

    def test_preparacao_invalida_bloqueia_e_padding_preserva(self):
        import motor.tempos2 as t
        self.assertTrue(callable(getattr(t, 'preparar', None)), 'Falta preparação auditável')
        for x in (np.array([]), np.zeros(8000), np.array([np.nan])):
            with self.assertRaises(ValueError):
                t.preparar(x)
        x = np.sin(np.arange(24000) * .1).astype('float32') * .1
        y, m = t.preparar(x, limites=(0, len(x)), confirmado=True)
        self.assertTrue(np.array_equal(y[m['padding_ini']:m['padding_ini'] + len(x)], x))
        self.assertEqual(m['padding_ini'], 3840)
        self.assertEqual(m['padding_fim'], 7680)

    def test_corte_so_com_aprovacao_e_sem_energia_removida(self):
        from tempos2 import preparar
        x = np.zeros(50000, dtype='float32'); x[20000:24800] = .1
        with self.assertRaises(ValueError):
            preparar(x, limites=(20000, 24800), confirmado=True, cortar=True)
        y, m = preparar(x, limites=(20000, 24800), confirmado=True, cortar=True, aprovado=True)
        self.assertEqual(m['corte_ini'], 16160)
        self.assertEqual(m['corte_fim'], 17520)
        self.assertTrue(np.array_equal(y[3840:8640], x[20000:24800]))
        x[100] = .002  # Energia de −54 dBFS fora da região declarada impede o corte.
        with self.assertRaises(ValueError):
            preparar(x, limites=(20000, 24800), confirmado=True, cortar=True, aprovado=True)


class Manifesto(unittest.TestCase):
    def test_selecao_frase_contagem_e_tomadas_imutaveis(self):
        import manifesto as m
        roteiro = {'cenas': [{'id': 'teste', 'pt': {'fala': 'Uma. Duas.', 'legenda': '1. 2.'}}]}
        itens = m.frases_do_roteiro(roteiro, ['teste-2'])
        self.assertEqual([f['id'] for f in itens], ['teste-2'])
        roteiro['cenas'][0]['pt']['legenda'] = 'Só uma.'
        with self.assertRaises(ValueError):
            m.frases_do_roteiro(roteiro)
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'bruto.wav'; p.write_bytes(b'tomada antiga')
            a = m.guardar_tomada(p, Path(d) / 'tomadas', {'fala': 'Uma.'})
            p.write_bytes(b'tomada nova')
            b = m.guardar_tomada(p, Path(d) / 'tomadas', {'fala': 'Uma.'})
            self.assertNotEqual(a, b)
            self.assertEqual(a.read_bytes(), b'tomada antiga')


class Automacao(unittest.TestCase):
    def test_antecipacao_cauda_grave_e_pausa_curta(self):
        self.assertTrue(callable(getattr(audio2, 'envoltoria', None)), 'Falta envelope por intervalo')
        cfg = json.loads((RAIZ / 'motor/mixagem.json').read_text())
        n = 4 * audio2.SR
        g = audio2.envoltoria(n, [(1., 1.5), (1.9, 2.4)], cfg['musica']['duck'], cfg['protecao'])
        # Patamar completo antes do primeiro fonema; pausa de 400 ms não reabre.
        self.assertLessEqual(g[round(.95 * audio2.SR)], 10 ** (-14 / 20) + 1e-6)
        self.assertLessEqual(g[round(1.7 * audio2.SR)], 10 ** (-14 / 20) + 1e-6)
        self.assertAlmostEqual(g[0], 1)

    def test_evento_aleatorio_independe_da_ordem(self):
        self.assertTrue(callable(getattr(audio2, 'sintetizar_evento', None)), 'Falta seed individual')
        e = {'id': 'grave-a', 'tipo': 'grave', 't': .7145}
        a, _ = audio2.sintetizar_evento(e)
        audio2.sintetizar_evento({'id': 'outro', 'tipo': 'clique', 't': .1})
        b, _ = audio2.sintetizar_evento(e)
        self.assertTrue(np.array_equal(a, b))



class Sessao(unittest.TestCase):
    def test_regua_por_blocos_insere_tomadas_uma_vez_sem_usar_legendas_como_audio(self):
        from audio_util import ler, salvar, hash_arquivo
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            x = (.1 * np.sin(2*np.pi*350*np.arange(9600)/48000)).astype('float32')
            salvar(d/'tomada.wav', x)
            salvar(d/'trilha.wav', np.tile(x,20))
            blocos = [{'id':f'bloco-{b}','cena':f'v0{i+1}','k':1,
                       'ini':.2+i*.6,'fim':.4+i*.6,'arquivo':str(d/'tomada.wav'),
                       'sha256':hash_arquivo(d/'tomada.wav'),'fala':'Uma. Duas.'}
                      for i,b in enumerate('ABCD')]
            t = {'total':4.,'bar':4.,'musica':[{'src':0.,'v':0.}], 'cenas':[],
                 'audio_blocos':blocos,
                 'falas':[{'id':f'legenda-{i}','cena':'v01','k':i+1,'ini':.2,'fim':.3}
                          for i in range(8)]}
            cfg=json.loads((RAIZ/'motor/mixagem.json').read_text())
            cfg['musica'].pop('montagem', None)  # Este ensaio usa trilha sintética de quatro segundos.
            cfg['voz']['frases']={b['id']:{'ganho_db':0} for b in blocos}
            m=audio2.montar(t,[],cfg,d/'sessao',trilha=d/'trilha.wav')
            self.assertEqual([f['id'] for f in m['frases']],[b['id'] for b in blocos])
            esperado=np.zeros(4*48000,dtype='float32')
            for b in blocos:
                a=round(b['ini']*48000); esperado[a:a+len(x)]=x
            self.assertTrue(np.array_equal(ler(d/'sessao/stems/voz.wav',1)[:,0],esperado))
            t['audio_blocos'][0]['sha256']='hash-divergente'
            with self.assertRaisesRegex(ValueError,'Hash'):
                audio2.montar(t,[],cfg,d/'adulterado',trilha=d/'trilha.wav')

    def test_stems_null_cache_e_qa_detecta_mascaramento(self):
        self.assertTrue(callable(getattr(audio2, 'montar', None)), 'Falta montagem com stems')
        import conferir_audio as qa
        from audio_util import ler, salvar, hash_arquivo
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            x = .14 * np.sin(2 * np.pi * 350 * np.arange(48000) / 48000)
            salvar(d / 'frase.wav', x)
            salvar(d / 'trilha.wav', np.tile(x, 4))
            t = {'total': 4., 'bar': 4., 'musica': [{'src': 0., 'v': 0.}],
                 'cenas': [], 'falas': [{'id': 'teste-1', 'cena': 'teste', 'k': 1,
                 'ini': 1., 'fim': 2., 'arquivo': str(d / 'frase.wav'), 'fala': 'Teste.',
                 'limites_confirmados': True, 'fala_ini_amostra': 0, 'fala_fim_amostra': 48000}]}
            cfg = json.loads((RAIZ / 'motor/mixagem.json').read_text())
            cfg['efeitos']['habilitado'] = True  # Regressão específica do bus de efeitos legado.
            # O ensaio aumenta o ducking em 1 dB para provar reúso do cache;
            # começa abaixo do teto, independentemente da receita de produção.
            cfg['musica']['duck']['profundidade_db'] = 14
            eventos = [{'id': 'g', 'tipo': 'grave', 't': .7145}, {'id': 'colisao', 'tipo': 'grave', 't': 1.}]
            m = audio2.montar(t, eventos, cfg, d / 'sessao', trilha=d / 'trilha.wav')
            stems = d / 'sessao/stems'
            soma = ler(stems / 'voz.wav', 2) + ler(stems / 'musica-duck.wav', 2) + ler(stems / 'efeitos-duck.wav', 2)
            self.assertLess(np.max(np.abs(soma - ler(d / 'sessao/premix.wav', 2))), 1e-6)
            r = qa.conferir_sessao(d / 'sessao', cfg)
            self.assertTrue(r['tecnico_ok'], r)
            self.assertTrue(any(e['silenciado'] for e in m['eventos']))
            base = hash_arquivo(stems / 'musica-base.wav')
            cfg['musica']['duck']['profundidade_db'] += 1
            from unittest.mock import patch
            with patch.object(audio2, 'sintetizar_evento', side_effect=AssertionError('ressíntese desnecessária')):
                audio2.montar(t, eventos, cfg, d / 'sessao', trilha=d / 'trilha.wav')
            self.assertEqual(base, hash_arquivo(stems / 'musica-base.wav'))
            # Mesmo premix não libera stems de fundo adulterados: QA mede os derivados.
            salvar(stems / 'efeitos-duck.wav', ler(stems / 'voz.wav', 2))
            ruim = qa.conferir_sessao(d / 'sessao', cfg)
            self.assertFalse(ruim['tecnico_ok'])

class Master(unittest.TestCase):
    def test_duas_passagens_aac_final_e_atraso(self):
        self.assertTrue(callable(getattr(audio2, 'masterizar', None)), 'Falta master com medição AAC')
        import conferir_audio as qa
        from audio_util import ler, salvar
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            cfg = json.loads((RAIZ / 'motor/mixagem.json').read_text())
            rng = np.random.default_rng(15)
            x = rng.normal(0, .03, 12 * 48000).astype('float32')
            x[:4800] *= np.linspace(0, 1, 4800); x[-4800:] *= np.linspace(1, 0, 4800)
            salvar(d / 'premix.wav', np.repeat(x[:, None], 2, axis=1))
            r = audio2.masterizar(d, cfg)
            self.assertTrue(r['aac']['ok'], r)
            self.assertEqual(len(ler(d / 'master.wav', 2)), len(x))
            self.assertLessEqual(abs(r['aac']['atraso_ms']), 10)
            self.assertIn(r['passagem2']['normalization_type'], ('linear', 'dynamic'))
            # Um deslocamento de 25 ms é detectado pelo mesmo medidor do QA final.
            ref = ler(d / 'master.wav', 2)
            atrasado = np.pad(ref, ((1200, 0), (0, 0)))[:len(ref)]
            self.assertEqual(qa.atraso_amostras(ref, atrasado), 1200)

class Janelas(unittest.TestCase):
    def test_varredura_usa_100ms_inteiros_inclusive_no_fim(self):
        from conferir_audio import medir_frase
        cfg = json.loads((RAIZ / 'motor/mixagem.json').read_text())
        x = np.full((48000, 2), .1, dtype='float32')
        r = medir_frase(x, x * .01, x * 0, 0, len(x), cfg)
        self.assertTrue(all(abs(j['fim'] - j['ini'] - .1) < 1e-6 for j in r['janelas']))
        self.assertAlmostEqual(r['janelas'][-1]['fim'], 1.)


class Coexistencia(unittest.TestCase):
    def test_impacto_curto_nao_dilui_margem_com_silencio(self):
        from conferir_audio import medir_frase
        cfg = json.loads((RAIZ / 'motor/mixagem.json').read_text())
        v = np.full((48000, 2), .1, dtype='float32')
        e = np.zeros_like(v); e[24000:24480] = .08
        r = medir_frase(v, e * 0, e, 0, len(v), cfg)
        self.assertLess(r['voz_efeitos_coexistencia_min_db'], 3)
        self.assertFalse(r['ok'])


class Limites(unittest.TestCase):
    def test_limites_nao_confirmados_protegem_arquivo_inteiro(self):
        from tempos2 import preparar
        x = np.full(48000, .01, dtype='float32')
        y, m = preparar(x, limites=(2000, 10000), confirmado=False)
        self.assertEqual(m['fala_ini_amostra'], 0)
        self.assertEqual(m['fala_fim_amostra'], len(x))
        self.assertTrue(np.array_equal(x, y))


class ServicoOffline(unittest.TestCase):
    def test_selecao_tomadas_e_timestamps_com_resposta_gravada(self):
        import eleven
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as d:
            d = Path(d); roteiro = d / 'roteiro.json'
            roteiro.write_text(json.dumps({'cenas': [{'id': 'teste', 'pt': {'fala': 'Uma. Duas.', 'legenda': '1. 2.'}}]}))
            saida = d / 'frases'; saida.mkdir()
            eleven.pcm_para_wav(b'\x01\x00' * 24000, saida / 'teste-2.wav')
            resposta = {'text': 'Duas.', 'words': [{'type': 'word', 'text': 'Duas.', 'start': .1, 'end': .8}]}
            with patch.multiple(eleven, AQUI=d, ROTEIRO=roteiro, SAIDA=saida):
                with patch.object(eleven, 'chamar', return_value=b'\x02\x00' * 24000):
                    eleven.gerar(['teste-2'])
                self.assertFalse((saida / 'teste-1.wav').exists())
                tomadas = list((d / 'tomadas/pt/teste-2').glob('*.wav'))
                self.assertEqual(len(tomadas), 2)
                with patch.object(eleven, 'chamar', return_value=json.dumps(resposta).encode()):
                    eleven.conferir(['teste-2'])
                with patch.object(eleven, 'chamar', side_effect=AssertionError('Cache deveria evitar requisição')):
                    eleven.conferir(['teste-2'])
                rel = json.loads((d / 'conferencia.json').read_text())
                self.assertEqual(rel['teste-2']['palavras'][0]['start'], .1)
                self.assertTrue(rel['teste-2']['ok'])


if __name__ == '__main__':
    unittest.main()
