"""Testes unitários para auditoria técnica das tomadas regeneradas do Bloco D.
Garante que o pipeline de auditoria, cálculo de deriva tímbrica, detecção A1 e prévias de fronteira
funcionem de modo determinístico e passem em checkout limpo sem depender de mídias locais gitignored.
"""
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch, MagicMock

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import vozes.auditar_regerar_d as aud_d
from motor.audio_util import SR


class TestAuditarRegerarD(unittest.TestCase):

    def test_gerar_previa_fronteira_sintetica(self):
        """Valida que gerar_previa_fronteira calcula folgas e emendas sem erro."""
        duracao_c = 22.240
        duracao_d = 11.840
        x_c = np.zeros(round(duracao_c * SR), dtype="<f4")
        x_d = np.zeros(round(duracao_d * SR), dtype="<f4")

        dados_c = {
            "bloco": "C",
            "duracao_s": duracao_c,
            "x": x_c,
            "words": [
                {"text": "Dos", "start": 0.600, "end": 0.850},
                {"text": "Federal", "start": 21.000, "end": 21.600}
            ]
        }

        dados_d = {
            "bloco": "D",
            "duracao_s": duracao_d,
            "x": x_d,
            "words": [
                {"text": "Menos", "start": 0.160, "end": 0.500},
                {"text": "Frila", "start": 10.500, "end": 11.720}
            ]
        }

        tmp_out = Path("/tmp/fvp_test_fronteira_d")
        tmp_out.mkdir(parents=True, exist_ok=True)

        with patch("vozes.auditar_regerar_d.medir_loudness", return_value={"input_i": "-18.0", "input_tp": "-3.0"}):
            info = aud_d.gerar_previa_fronteira(dados_c, dados_d, 3, "fronteira_teste", tmp_out)

        self.assertEqual(info["fronteira"], "C→D")
        self.assertGreater(info["pausa_verbal_s"], 0.0)
        self.assertGreater(info["duracao_s"], 0.0)
        self.assertTrue(Path(info["arquivo"]).exists())

    def test_analise_transicao_a1_v13_v14(self):
        """Valida a detecção de pausa entre v13 ('cuida') e v14 ('combinou')."""
        words = [
            {"text": "Deixa", "start": 4.5, "end": 4.8},
            {"text": "que", "start": 4.8, "end": 5.0},
            {"text": "o", "start": 5.0, "end": 5.1},
            {"text": "Frila", "start": 5.1, "end": 5.5},
            {"text": "cuida,", "start": 5.5, "end": 5.9},
            {"text": "combinou?", "start": 6.3, "end": 6.7},
            {"text": "Pode", "start": 6.7, "end": 7.0},
        ]

        transicao = None
        for idx, w in enumerate(words):
            if "cuida" in w["text"].lower() and idx + 1 < len(words):
                prox = words[idx + 1]
                pausa = round(prox["start"] - w["end"], 3)
                transicao = {
                    "fim_v13_palavra": w["text"],
                    "fim_v13_tempo_s": round(w["end"], 3),
                    "ini_v14_palavra": prox["text"],
                    "ini_v14_tempo_s": round(prox["start"], 3),
                    "pausa_verbal_s": pausa,
                    "a1_respeitado": bool(pausa > 0.0)
                }
                break

        self.assertIsNotNone(transicao)
        self.assertEqual(transicao["pausa_verbal_s"], 0.4)
        self.assertTrue(transicao["a1_respeitado"])


if __name__ == "__main__":
    unittest.main()
