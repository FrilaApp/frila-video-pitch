"""Testes unitários da ferramenta de medição objetiva de timbre e deriva."""
import pathlib
import tempfile
import unittest
import numpy as np

from motor.audio_util import SR, salvar
from vozes.deriva_timbre import analisar_timbre_arquivo, comparar_timbre_blocos


class TestDerivaTimbre(unittest.TestCase):

    def test_analisar_timbre_seno(self):
        """Testa que um tom puro de 200 Hz tem F0 mediano próximo de 200 Hz e centroide próximo de 200 Hz."""
        with tempfile.TemporaryDirectory() as tmpdir:
            wav_path = pathlib.Path(tmpdir) / "seno200.wav"
            t = np.arange(SR * 2) / SR
            x = 0.5 * np.sin(2 * np.pi * 200 * t)
            salvar(wav_path, x, codec="pcm_s16le")

            res = analisar_timbre_arquivo(wav_path)
            self.assertIn("f0_mediano_hz", res)
            self.assertIn("centroide_medio_hz", res)
            # F0 deve estar entre 195 e 205 Hz
            self.assertAlmostEqual(res["f0_mediano_hz"], 200.0, delta=5.0)
            # Centroide espectral deve estar perto de 200 Hz
            self.assertAlmostEqual(res["centroide_medio_hz"], 200.0, delta=20.0)
            self.assertGreater(res["energia_por_banda_pct"]["grave_80_300"], 90.0)

    def test_comparar_timbre_blocos(self):
        """Testa o cálculo de diferenças de F0 e semitons."""
        dados = {
            "A": {"f0_mediano_hz": 220.0, "centroide_medio_hz": 3000.0},
            "C": {"f0_mediano_hz": 233.08, "centroide_medio_hz": 3100.0}, # ~1 semitom acima de 220 Hz
        }
        comp = comparar_timbre_blocos(dados)
        self.assertIn("A_vs_C", comp)
        self.assertAlmostEqual(comp["A_vs_C"]["diff_f0_semitons"], 1.0, delta=0.1)
        self.assertEqual(comp["A_vs_C"]["diff_f0_hz"], 13.1)
        self.assertEqual(comp["A_vs_C"]["diff_centroide_hz"], 100.0)


if __name__ == "__main__":
    unittest.main()
