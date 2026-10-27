"""Testes unitários da métrica de chiado de coda /ʃ/ vs /s/ limpo.
Valida que a métrica separa objetivamente o Bloco A (aprovado de ouvido) do Bloco C atual (reprovado por chiado).
"""
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
from vozes.metrica_chiado import identificar_palavras_coda_s, analisar_chiado_tomada

TOMADAS = {
    "A": ROOT / "vozes/tomadas/blocos/pt/A/5dcbc2883164470aa2d0cb7fbe2b4a44",
    "C": ROOT / "vozes/tomadas/blocos/pt/C/fcd0c415fbbd41318b4a4951f89fa4d5",
}


class TestMetricaChiado(unittest.TestCase):

    def test_identificar_palavras_coda(self):
        palavras = [
            {"text": "Hoje,", "type": "word"},
            {"text": "horas.", "type": "word"},
            {"text": "restaurantes", "type": "word"},
            {"text": "Distrito", "type": "word"},
            {"text": "turno", "type": "word"},
        ]
        filtradas = identificar_palavras_coda_s(palavras)
        textos = [p["text"] for p in filtradas]
        self.assertIn("horas.", textos)
        self.assertIn("restaurantes", textos)
        self.assertIn("Distrito", textos)
        self.assertNotIn("Hoje,", textos)
        self.assertNotIn("turno", textos)

    def test_separacao_bloco_a_vs_bloco_c(self):
        """Valida que o Bloco A (aprovado) é classificado como limpo e o Bloco C (reprovado) como chiado_carioca."""
        p_a = TOMADAS["A"]
        sc_a = json.loads((p_a / "scribe.json").read_text(encoding="utf-8"))
        res_a = analisar_chiado_tomada(p_a / "voz.wav", sc_a.get("words", []))

        p_c = TOMADAS["C"]
        sc_c = json.loads((p_c / "scribe.json").read_text(encoding="utf-8"))
        res_c = analisar_chiado_tomada(p_c / "voz.wav", sc_c.get("words", []))

        # Bloco A deve ser limpo (< 25% de palavras chiadas)
        self.assertEqual(res_a["veredito_triagem"], "limpo")
        self.assertLessEqual(res_a["taxa_chiado_pct"], 25.0)

        # Bloco C deve ser reprovado por chiado (> 35% de palavras chiadas)
        self.assertEqual(res_c["veredito_triagem"], "chiado_carioca")
        self.assertGreaterEqual(res_c["taxa_chiado_pct"], 35.0)

        # A separação deve ser nítida: taxa de chiado de C bem maior que a de A
        self.assertGreater(res_c["taxa_chiado_pct"], res_a["taxa_chiado_pct"] * 2)


if __name__ == "__main__":
    unittest.main()
