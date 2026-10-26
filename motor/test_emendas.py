"""Sinais controlados e relatórios de verdade, sem serviços externos."""
import json
from pathlib import Path
import tempfile
import unittest

import numpy as np

try:
    from motor import analisar_emendas as em
except ImportError:
    em = None
from motor.audio_util import salvar, hash_arquivo


class Emendas(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(em, 'Falta o analisador')

    def test_manifesto_nunca_omite_emenda_e_detecta_frase_partida(self):
        x = np.zeros((4 * 48000, 2), dtype='float32')
        palavras = [{'text': 'Uma', 'start': .5, 'end': .8}, {'text': 'frase.', 'start': 2.4, 'end': 2.8}]
        manifesto = {'emendas': [{'tempo': 2}], 'frases': [
            {'id': 'f', 'ini': .5, 'fim': 1.9, 'tomada': 'a'},
            {'id': 'f', 'ini': 2.1, 'fim': 2.8, 'tomada': 'b'}]}
        r = em.analisar(x, palavras, manifesto)
        self.assertEqual(len(r), 1)
        self.assertTrue(r[0]['frase_dividida_comprovada'])
        self.assertFalse(r[0]['aprovado'])

    def test_pausa_natural_nao_comprova_corte_e_ausencia_de_scribe_bloqueia(self):
        x = np.zeros((4 * 48000, 2), dtype='float32')
        w = [{'text': 'Fim.', 'start': 1, 'end': 1.6}, {'text': 'Nova.', 'start': 2.4, 'end': 3}]
        m = {'emendas': [{'tempo': 2}], 'frases': [{'id': 'a', 'ini': 1, 'fim': 1.6, 'tomada': 'a'},
             {'id': 'b', 'ini': 2.4, 'fim': 3, 'tomada': 'b'}]}
        r = em.analisar(x, w, m)[0]
        self.assertTrue(r['aprovado'], r['motivos'])
        self.assertFalse(r['frase_dividida_comprovada'])
        self.assertFalse(em.analisar(x, [], m)[0]['aprovado'])

    def test_palavra_no_corte_reprova(self):
        x = np.zeros((4 * 48000, 2), dtype='float32')
        r = em.analisar(x, [{'text': 'cortada', 'start': 1.8, 'end': 2.2}], {'emendas': [{'tempo': 2}]})[0]
        self.assertTrue(any('palavra' in m for m in r['motivos']))
        self.assertFalse(r['aprovado'])

    def test_palavra_atravessada_nao_vira_pausa_entre_palavras_vizinhas(self):
        w = [{'text': 'Uma', 'start': 1, 'end': 1.2}, {'text': 'cortada', 'start': 1.8, 'end': 2.2},
             {'text': 'aqui.', 'start': 2.8, 'end': 3}]
        r = em.analisar(np.zeros((4 * 48000, 2)), w, {'emendas': [{'tempo': 2}]})[0]
        self.assertIsNone(r['medidas']['pausa_scribe_s'])

    def test_detecta_queda_dentro_de_palavra_sem_manifesto(self):
        t = np.arange(4 * 48000) / 48000
        x = .1 * np.sin(2 * np.pi * 400 * t)
        x[round(1.98 * 48000):round(2.04 * 48000)] = 0
        r = em.analisar(np.column_stack([x, x]), [{'text': 'partida', 'start': 1.5, 'end': 2.5}])
        self.assertTrue(any(abs(c['tempo'] - 2.01) < .05 and not c['aprovado'] for c in r))

    def test_fundo_mais_de_3db_e_clique_bloqueiam(self):
        rng = np.random.default_rng(8)
        side = rng.normal(0, .001, 4 * 48000); side[2 * 48000:] *= 2
        x = np.column_stack([side, -side]); x[2 * 48000] += .5
        w = [{'text': 'Fim.', 'start': .5, 'end': 1.6}, {'text': 'Nova.', 'start': 2.4, 'end': 3}]
        r = em.analisar(x, w, {'emendas': [{'tempo': 2}]})[0]
        self.assertGreater(r['medidas']['fundo_delta_db'], 3)
        self.assertTrue(any('clique' in m for m in r['motivos']))
        self.assertFalse(r['aprovado'])

    def test_cache_offset_hash_e_trecho_exato(self):
        with tempfile.TemporaryDirectory() as d:
            d = Path(d); salvar(d / 'a.wav', np.zeros(4 * 48000))
            salvar(d / 'trecho.wav', np.zeros(48000))
            cache = {'sha256': hash_arquivo(d / 'a.wav'), 'frases': [{'ini_amostra': 48000,
                'trecho': str(d / 'trecho.wav'), 'sha256_trecho': hash_arquivo(d / 'trecho.wav'),
                'palavras': [{'text': 'Teste.', 'start': .1, 'end': .9}]}]}
            p = d / 'cache.json'; p.write_text(json.dumps(cache))
            w = em.ler_scribe(p, d / 'a.wav')
            self.assertAlmostEqual(w[0]['start'], 1.1)
            cache['sha256'] = 'errado'; p.write_text(json.dumps(cache))
            with self.assertRaisesRegex(ValueError, 'hash'):
                em.ler_scribe(p, d / 'a.wav')


    def test_scribe_duracao_zero_preserva_pista_sem_inventar_intervalo(self):
        w = {'text': '1', 'start': 1., 'end': 1.}
        self.assertEqual(em.validar_palavras([w], 2)[0]['end'], 1.)

    def test_frase_continua_cruza_troca_de_tomada_e_bloco_sem_corte_reprova(self):
        x = np.zeros((4 * 48000, 2))
        m = {'emendas': [{'tempo': 2, 'entre_blocos': True,
                          'tomada_antes': 'a', 'tomada_depois': 'b'}],
             'frases': [{'id': 'f', 'ini': 1, 'fim': 3, 'tomada': 'a'}]}
        r = em.analisar(x, [], m)[0]
        self.assertTrue(r['frase_dividida_comprovada'])
        self.assertTrue(any('corte de cena' in s for s in r['motivos']))

    def test_corte_declarado_dentro_da_frase_bloqueia_mesmo_com_mesma_tomada(self):
        m = {'emendas': [{'tempo': 2}],
             'frases': [{'id': 'f', 'ini': 1, 'fim': 3, 'tomada': 'a'}]}
        r = em.analisar(np.zeros((4 * 48000, 2)), [], m)[0]
        self.assertTrue(r['frase_dividida_comprovada'])

    def test_wav_extraido_e_offset_correspondem_as_amostras(self):
        with tempfile.TemporaryDirectory() as d:
            from motor.audio_util import ler
            d = Path(d); x = np.zeros((5 * 48000, 2), dtype='float32'); x[120000] = .5
            salvar(d / 'mix.wav', x)
            m = {'sha256': hash_arquivo(d / 'mix.wav'), 'emendas': [{'tempo': 2.5}]}
            (d / 'm.json').write_text(json.dumps(m))
            r = em.executar(d / 'mix.wav', d / 'out', manifesto=d / 'm.json')
            c = r['emendas'][0]; y = ler(c['trecho'], 2)
            self.assertEqual(c['trecho_ini'], .5)
            self.assertEqual(c['trecho_fim'], 4.5)
            np.testing.assert_array_equal(y, x[24000:216000])

    def test_pausas_uniformes_sao_listadas_sem_manifesto(self):
        w = [{'text': 'Uma.', 'start': .2, 'end': .8}, {'text': 'Outra.', 'start': 1.05, 'end': 1.5},
             {'text': 'Fim.', 'start': 1.75, 'end': 2.2}]
        r = em.analisar(np.zeros((3 * 48000, 2)), w)
        self.assertEqual(len(r), 2)
        self.assertTrue(all('pausa_curta_uniforme_scribe' in c['sinais'] for c in r))
        self.assertTrue(all(not c['aprovado'] for c in r))

    def test_hash_trecho_adulterado_bloqueia(self):
        with tempfile.TemporaryDirectory() as d:
            d = Path(d); salvar(d / 'a.wav', np.zeros(48000))
            p = d / 's.json'; p.write_text(json.dumps({'sha256': hash_arquivo(d / 'a.wav'),
                'frases': [{'ini_amostra': 0, 'trecho': 'a.wav', 'sha256_trecho': 'errado', 'palavras': []}]}))
            with self.assertRaisesRegex(ValueError, 'hash de trecho'):
                em.ler_scribe(p, d / 'a.wav')


class RegraA8(unittest.TestCase):
    def setUp(self):
        self.assertTrue(callable(getattr(em, 'verificar_a8', None)), 'Falta A8 determinístico')

    def test_meio_segundo_inclusive_bloqueia_e_abaixo_nao(self):
        for gap, falha in [(.499, False), (.5, True), (.501, True)]:
            w = [{'text': 'Uma', 'start': .1, 'end': .3},
                 {'text': 'frase.', 'start': .3 + gap, 'end': 1.2}]
            r = em.verificar_a8([{'id': 'f', 'fala': 'Uma frase.'}], w)
            self.assertEqual(r['bloqueado'], falha)
            self.assertEqual(r['alinhamento_completo'], True)

    def test_pausa_entre_frases_permitida_mesmo_sem_ponto_no_scribe(self):
        w = [{'text': 'Uma', 'start': .1, 'end': .3}, {'text': 'Outra', 'start': 1., 'end': 1.2}]
        r = em.verificar_a8([{'id': 'f', 'fala': 'Uma. Outra.'}], w)
        self.assertFalse(r['bloqueado'])
        self.assertEqual(r['pausas'][0]['tipo'], 'entre_frases')

    def test_dois_pontos_do_roteiro_nao_vira_fronteira_por_pontuacao_asr(self):
        w = [{'text': 'Avaliam.', 'start': .1, 'end': .3}, {'text': 'Chamaria?', 'start': 1., 'end': 1.2}]
        r = em.verificar_a8([{'id': 'f', 'fala': 'Avaliam: chamaria?'}], w)
        self.assertTrue(r['bloqueado'])
        self.assertEqual({f['regra'] for f in r['falhas']}, {'A8_dois_pontos', 'A8_pausa_interna'})

    def test_numeros_e_aliases_alinham_sem_perder_timestamps(self):
        w = [{'text': '19h', 'start': .1, 'end': .4}, {'text': 'Frila.', 'start': 1., 'end': 1.2}]
        r = em.verificar_a8([{'id': 'f', 'fala': 'Dezenove horas, Frila.'}], w)
        self.assertTrue(r['alinhamento_completo'])
        self.assertEqual(r['falhas'][0]['palavra_antes']['end'], .4)

    def test_sem_timestamps_ou_com_divergencia_fica_inconclusivo(self):
        for w in [[], [{'text': 'diferente', 'start': .1, 'end': .4}]]:
            r = em.verificar_a8([{'id': 'f', 'fala': 'Uma frase.'}], w)
            self.assertEqual(r['estado'], 'inconclusivo')
            self.assertFalse(r['alinhamento_completo'])

    def test_a8_bloqueia_e_exporta_sem_emendas_fisicas(self):
        with tempfile.TemporaryDirectory() as d:
            d = Path(d); salvar(d / 'a.wav', np.zeros(2 * 48000))
            digest = hash_arquivo(d / 'a.wav')
            m = {'sha256': digest, 'emendas': []}; (d / 'm.json').write_text(json.dumps(m))
            s = {'sha256': digest, 'words': [{'text': 'Uma', 'start': .1, 'end': .3},
                                            {'text': 'frase.', 'start': 1., 'end': 1.2}]}
            (d / 's.json').write_text(json.dumps(s))
            (d / 'f.json').write_text(json.dumps({'fala': 'Uma frase.'}))
            r = em.executar(d / 'a.wav', d / 'out', d / 's.json', d / 'm.json', falas=d / 'f.json')
            self.assertTrue(r['bloqueado'])
            self.assertFalse(r['aprovado'])
            self.assertTrue(Path(r['a8']['falhas'][0]['trecho']).exists())

    def test_quatro_referencias_reais_da_v5(self):
        casos = [('pública: quantas', 'pública:', 53.71083333333333, 'quantas', 54.33083333333333),
                 ('avaliam: chamaria?', 'avaliam:', 61.84020833333334, 'chamaria?', 62.34020833333334),
                 ('piloto: oito', 'piloto:', 77.29183333333333, 'oito', 78.21183333333333),
                 ('semanas, cinquenta', 'semanas,', 79.11183333333334, '50', 79.97183333333334)]
        falas, w = [], []
        for i, (texto, a, fim, b, ini) in enumerate(casos):
            falas.append({'id': str(i), 'fala': texto})
            w.extend([{'text': a, 'start': fim - .2, 'end': fim},
                      {'text': b, 'start': ini, 'end': ini + .2}])
        r = em.verificar_a8(falas, w)
        pausas = [f for f in r['falhas'] if f['regra'] == 'A8_pausa_interna']
        self.assertEqual(len(pausas), 4)
        for f, esperado in zip(pausas, [54.020833, 62.090208, 77.751833, 79.541833]):
            self.assertAlmostEqual(f['tempo'], esperado, places=5)

    def test_suspeita_cega_informa_sem_aprovar_ou_bloquear(self):
        with tempfile.TemporaryDirectory() as d:
            d = Path(d); salvar(d / 'a.wav', np.zeros(2 * 48000))
            s = {'sha256': hash_arquivo(d / 'a.wav'), 'words': [
                {'text': 'Uma.', 'start': .1, 'end': .3}, {'text': 'Outra.', 'start': 1., 'end': 1.2}]}
            (d / 's.json').write_text(json.dumps(s)); (d / 'f.json').write_text(json.dumps({'fala': 'Uma. Outra.'}))
            r = em.executar(d / 'a.wav', d / 'out', d / 's.json', falas=d / 'f.json')
            self.assertTrue(r['emendas'])
            self.assertFalse(r['bloqueado'])
            self.assertFalse(r['aprovado'])
            self.assertFalse(r['apto_para_escuta'], 'Sem manifesto não declarar completude')



if __name__ == '__main__':
    unittest.main()
