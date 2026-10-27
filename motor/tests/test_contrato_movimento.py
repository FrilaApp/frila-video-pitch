import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import render


class ContratoMovimentoTest(unittest.TestCase):
    def test_janelas_c_e_d_refletem_movimento_observado(self):
        regua = {'total': 24.1167, 'cenas': [{'ini': 0}, {'ini': 5.76}, {'ini': 14.23}]}
        contratos = {bloco: render.contrato_bloco(bloco, regua)['movimento'] for bloco in ('C', 'D')}
        c = [(j['de'], j['ate']) for j in contratos['C']]
        d = [(j['de'], j['ate']) for j in contratos['D']]
        self.assertEqual(c[:2], [(0.48, 1.1), (2.95, 3.1)])
        self.assertAlmostEqual(c[-2][0], 17.98)
        self.assertAlmostEqual(c[-1][0], 20.98)
        self.assertNotIn((3.8, 5.4), d)
        self.assertNotIn((5.6, 7.0), d)


if __name__ == '__main__':
    unittest.main()
