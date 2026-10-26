"""Regressões offline; rede é sempre mockada."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from vozes import eleven


class Blocos(unittest.TestCase):
    def roteiro(self):
        return {'audio_blocos_aprovados': True,
                'blocos': [{'id': 'A', 'cenas': ['um']}, {'id': 'B', 'cenas': ['dois']}],
                'cenas': [{'id': 'um', 'pt': {'fala': 'Uma frase. Outra frase.'}},
                          {'id': 'dois', 'pt': {'fala': 'Vizinha.'}}]}

    def test_pendente_bloqueia_antes_da_rede(self):
        self.assertTrue(callable(getattr(eleven, 'gerar_bloco', None)))
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'roteiro.json'; p.write_text('{"cenas": []}')
            with patch.object(eleven, 'ROTEIRO', p), patch.object(eleven, 'chamar', side_effect=AssertionError('rede')):
                with self.assertRaisesRegex(ValueError, 'aprovad'):
                    eleven.gerar_bloco('A')

    def test_uma_tomada_continua_contexto_timestamps_e_imutabilidade(self):
        self.assertTrue(callable(getattr(eleven, 'gerar_bloco', None)))
        scribe = {'text': 'Uma frase. Outra frase.', 'words': [
            {'type': 'word', 'text': 'Uma', 'start': .1, 'end': .3},
            {'type': 'word', 'text': 'frase.', 'start': .32, 'end': .5},
            {'type': 'word', 'text': 'Outra', 'start': .77, 'end': .85},
            {'type': 'word', 'text': 'frase.', 'start': .86, 'end': .95}]}
        with tempfile.TemporaryDirectory() as d:
            d = Path(d); p = d / 'roteiro.json'; p.write_text(json.dumps(self.roteiro()))
            calls = []
            def servico(caminho, corpo=None, multipart=None):
                calls.append((caminho, corpo))
                return json.dumps(scribe).encode() if multipart else b'\x01\x00' * 24000
            with patch.multiple(eleven, AQUI=d, ROTEIRO=p), patch.object(eleven, 'chamar', side_effect=servico):
                a = eleven.gerar_bloco('A'); antes = {p: p.read_bytes() for p in a.parent.iterdir()}
                b = eleven.gerar_bloco('A')
            self.assertNotEqual(a, b)
            self.assertTrue(all(p.read_bytes() == x for p, x in antes.items()))
            self.assertEqual(len(calls), 4)
            self.assertEqual(calls[0][1]['text'], 'Uma frase. Outra frase.')
            self.assertEqual(calls[0][1]['next_text'], 'Vizinha.')
            m = json.loads(a.with_suffix('.json').read_text())
            self.assertEqual(m['palavras'], scribe['words'])
            self.assertAlmostEqual(m['pausas'][1]['duracao'], .27)
            self.assertFalse(m['aprovada'])
            self.assertEqual(a.read_bytes()[44:], b'\x01\x00' * 24000)

    def test_scribe_falha_preserva_bruto_e_bloqueia(self):
        self.assertTrue(callable(getattr(eleven, 'gerar_bloco', None)))
        with tempfile.TemporaryDirectory() as d:
            d = Path(d); p = d / 'roteiro.json'; p.write_text(json.dumps(self.roteiro()))
            with patch.multiple(eleven, AQUI=d, ROTEIRO=p), patch.object(
                    eleven, 'chamar', side_effect=[b'\x01\x00' * 24000, RuntimeError('indisponível')]):
                with self.assertRaises(RuntimeError):
                    eleven.gerar_bloco('A')
            self.assertEqual(len(list(d.glob('tomadas/blocos/pt/A/*/bruto.wav'))), 1)

    def test_ordem_ou_cena_repetida_bloqueia_antes_da_rede(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'r.json'
            for modo in ['ordem', 'repetida']:
                r = self.roteiro()
                if modo == 'ordem':
                    r['blocos'].reverse()
                else:
                    r['blocos'][1]['cenas'] = ['um']
                p.write_text(json.dumps(r))
                with patch.object(eleven, 'ROTEIRO', p), patch.object(eleven, 'chamar', side_effect=AssertionError('rede')):
                    with self.assertRaises(ValueError):
                        eleven.gerar_bloco('A')


if __name__ == '__main__':
    unittest.main()
