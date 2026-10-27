"""Testes unitários da métrica de chiado de coda /ʃ/ vs /s/ limpo.

Inclui:
1. Identificação de palavras com coda sibilante /s/;
2. Teste DETERMINÍSTICO com áudio SINTÉTICO (independe de arquivos de mídia versionados);
3. Teste complementar com tomadas reais de voz (com skipTest em checkout limpo).
"""
import json
from pathlib import Path
import tempfile
import unittest
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
from motor.audio_util import SR, salvar
from vozes.metrica_chiado import identificar_palavras_coda_s, analisar_chiado_tomada

TOMADAS = {
    "A": ROOT / "vozes/tomadas/blocos/pt/A/5dcbc2883164470aa2d0cb7fbe2b4a44",
    "C": ROOT / "vozes/tomadas/blocos/pt/C/fcd0c415fbbd41318b4a4951f89fa4d5",
}


def sintetizar_audio_teste(tipo="limpo", duracao_s=1.0):
    """Gera um sinal de áudio com duas palavras sintéticas para teste determinístico da métrica."""
    n_amostras = int(duracao_s * SR)
    audio = np.zeros(n_amostras, dtype=np.float32)
    t = np.arange(n_amostras) / SR

    # Duas palavras:
    # Palavra 1: 0.100s a 0.400s (fricativa nos últimos 50ms: 0.350 a 0.400s)
    # Palavra 2: 0.500s a 0.800s (fricativa nos últimos 50ms: 0.750 a 0.800s)
    palavras = [
        {"text": "horas", "start": 0.100, "end": 0.400, "type": "word"},
        {"text": "restaurantes", "start": 0.500, "end": 0.800, "type": "word"}
    ]

    for p in palavras:
        ini = int(p["start"] * SR)
        fim = int(p["end"] * SR)
        fric_ini = int((p["end"] - 0.050) * SR)

        # Corpo da vogal: formantes vocálicas graves (200 Hz e 600 Hz)
        audio[ini:fric_ini] = 0.3 * np.sin(2 * np.pi * 200 * t[ini:fric_ini]) + 0.2 * np.sin(2 * np.pi * 600 * t[ini:fric_ini])

        # Fricativa de coda /s/:
        if tipo == "limpo":
            # Alta frequência (> 6.000 Hz, pico em 7.000 Hz)
            audio[fric_ini:fim] = 0.25 * np.sin(2 * np.pi * 7000 * t[fric_ini:fim]) + 0.15 * np.sin(2 * np.pi * 8500 * t[fric_ini:fim])
        else:
            # Chiado carioca pós-alveolar: pico concentrado em 3.500 Hz (faixa 2.500–4.500 Hz)
            audio[fric_ini:fim] = 0.35 * np.sin(2 * np.pi * 3500 * t[fric_ini:fim])

    return audio, palavras


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

    def test_separacao_sintetica_deterministica_limpo_vs_chiado(self):
        """Testa determinística e offline a separação exata entre sinal limpo e sinal chiado carioca."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)

            # 1. Sinal sintético limpo ([s] com alta frequência > 6 kHz)
            audio_limpo, palavras_limpo = sintetizar_audio_teste(tipo="limpo")
            wav_limpo = tmp_path / "limpo.wav"
            salvar(wav_limpo, audio_limpo)

            res_limpo = analisar_chiado_tomada(wav_limpo, palavras_limpo)
            self.assertEqual(res_limpo["total_palavras_analisadas"], 2)
            self.assertEqual(res_limpo["palavras_com_chiado"], 0)
            self.assertEqual(res_limpo["taxa_chiado_pct"], 0.0)
            self.assertEqual(res_limpo["veredito_triagem"], "limpo")
            self.assertGreaterEqual(res_limpo["pico_mediano_hz"], 6000.0)

            # 2. Sinal sintético chiado (/ʃ/ com pico em 3.5 kHz)
            audio_chiado, palavras_chiado = sintetizar_audio_teste(tipo="chiado")
            wav_chiado = tmp_path / "chiado.wav"
            salvar(wav_chiado, audio_chiado)

            res_chiado = analisar_chiado_tomada(wav_chiado, palavras_chiado)
            self.assertEqual(res_chiado["total_palavras_analisadas"], 2)
            self.assertEqual(res_chiado["palavras_com_chiado"], 2)
            self.assertEqual(res_chiado["taxa_chiado_pct"], 100.0)
            self.assertEqual(res_chiado["veredito_triagem"], "chiado_carioca")
            self.assertLessEqual(res_chiado["pico_mediano_hz"], 4500.0)

    def test_separacao_bloco_a_vs_bloco_c(self):
        """Valida nos áudios reais locais (quando presentes) que o Bloco A é limpo e o Bloco C é chiado."""
        p_a = TOMADAS["A"]
        p_c = TOMADAS["C"]

        wav_a = p_a / "voz.wav"
        sc_a_path = p_a / "scribe.json"
        wav_c = p_c / "voz.wav"
        sc_c_path = p_c / "scribe.json"

        # Em checkout limpo, esses arquivos não existem (não são versionados conforme AGENTS.md)
        if not (wav_a.exists() and sc_a_path.exists() and wav_c.exists() and sc_c_path.exists()):
            self.skipTest("Tomadas reais de voz não encontradas no checkout (não versionadas conforme AGENTS.md).")

        sc_a = json.loads(sc_a_path.read_text(encoding="utf-8"))
        res_a = analisar_chiado_tomada(wav_a, sc_a.get("words", []))

        sc_c = json.loads(sc_c_path.read_text(encoding="utf-8"))
        res_c = analisar_chiado_tomada(wav_c, sc_c.get("words", []))

        # Bloco A deve ser limpo (<= 25% de palavras chiadas)
        self.assertEqual(res_a["veredito_triagem"], "limpo")
        self.assertLessEqual(res_a["taxa_chiado_pct"], 25.0)

        # Bloco C deve ser reprovado por chiado (>= 35% de palavras chiadas)
        self.assertEqual(res_c["veredito_triagem"], "chiado_carioca")
        self.assertGreaterEqual(res_c["taxa_chiado_pct"], 35.0)
        self.assertGreater(res_c["taxa_chiado_pct"], res_a["taxa_chiado_pct"] * 2)


if __name__ == "__main__":
    unittest.main()
