"""Métrica acústica objetiva para detecção de chiado carioca (/ʃ/ vs /s/ limpo).
PRONUNCIA-FALA §4 e diretriz de escuta do Fabrício (27/10/2026).

Fonética acústica:
- [s] limpo (alveolar): cavidade frontal curta, ressonância concentrada em 5.500–10.000 Hz,
  com centroide elevado (tipicamente > 6.500 Hz) e pico de energia acima de 5.500 Hz.
- [ʃ] chiado (pós-alveolar/palatoalveolar carioca): cavidade frontal longa com projeção labial,
  polo de ressonância principal deslocado para 2.500–4.500 Hz, centroide rebaixado
  e razão de energia (5.5–10k / 2.5–4.5k) rebaixada (< 1.5).

A métrica realiza triagem espectral das fricativas de coda (/s/ em final de palavra e antes
de consoante) isoladas a partir dos timestamps de palavras do Scribe.

Calibração e limiares:
Os limiares de triagem (taxa <= 25.0% para 'limpo' e taxa >= 35.0% para 'chiado_carioca')
foram calibrados preliminarmente sobre 3 blocos da Ana (Bloco A aprovado com 11,1% e Bloco C
reprovado com 46,7%). Servem exclusivamente como ferramenta de triagem prévia de segurança;
o ouvido do Fabrício decide soberanamente a aprovação estética e fonética de cada tomada.
"""
import json
from pathlib import Path
import numpy as np

from motor.audio_util import SR, ler


def identificar_palavras_coda_s(palavras_scribe):
    """Filtra palavras que contêm s de coda (final de palavra ou preconsonantal)."""
    coda_words = []
    for w in palavras_scribe:
        txt = w["text"].lower().strip(".,;:?!\"")
        # Terminações em s ou encontro preconsonantal típico
        if txt.endswith("s") or any(sub in txt for sub in ["st", "sp", "sc", "sd", "sm", "sn"]):
            coda_words.append(w)
    return coda_words


def extrair_fricativa_palavra(audio, w_start, w_end):
    """Localiza a fatia desvozeada de alta frequência correspondente à fricativa de coda na palavra."""
    i_start = int(w_start * SR)
    i_end = int(w_end * SR)
    trecho = audio[i_start:i_end]
    if len(trecho) < int(0.030 * SR):
        return None

    # Varredura em quadros de 25 ms com passo de 5 ms
    n_w = int(0.025 * SR)
    step = int(0.005 * SR)

    quadros_fricativa = []
    for k in range(0, len(trecho) - n_w, step):
        q = trecho[k : k + n_w]
        spec = np.abs(np.fft.rfft(np.hanning(len(q)) * q))
        freqs = np.fft.rfftfreq(len(q), 1 / SR)

        e_grave = np.sum(spec[freqs < 1000] ** 2) + 1e-12
        e_agudo = np.sum(spec[freqs >= 2500] ** 2) + 1e-12
        rms = np.sqrt(np.mean(q ** 2))

        # Critério acústico de fricativa não-vozeada: forte predomínio de agudos sobre graves
        if e_agudo / e_grave > 1.2 and rms > 0.008:
            quadros_fricativa.append((k, q, spec, freqs))

    if not quadros_fricativa:
        # Fallback: últimos 60 ms da palavra
        q = trecho[-int(0.060 * SR) :]
        if len(q) < 128:
            return None
        spec = np.abs(np.fft.rfft(np.hanning(len(q)) * q))
        freqs = np.fft.rfftfreq(len(q), 1 / SR)
        quadros_fricativa = [(0, q, spec, freqs)]

    # Espectro médio das fatias de fricativa
    spec_fric = np.mean([item[2] for item in quadros_fricativa], axis=0)
    freqs = quadros_fricativa[0][3]

    # Bandas de energia
    m_chiado = (freqs >= 2500) & (freqs <= 4500)
    m_limpo = (freqs >= 5500) & (freqs <= 10000)

    e_chiado = float(np.sum(spec_fric[m_chiado] ** 2))
    e_limpo = float(np.sum(spec_fric[m_limpo] ** 2))
    razao = float(e_limpo / (e_chiado + 1e-12))

    # Centroide da região fricativa (>= 2000 Hz)
    m_calc = freqs >= 2000
    sum_calc = np.sum(spec_fric[m_calc])
    if sum_calc > 1e-12:
        centroide = float(np.sum(freqs[m_calc] * spec_fric[m_calc]) / sum_calc)
    else:
        centroide = 0.0

    # Frequência de pico na região fricativa
    idx_pico = int(np.argmax(spec_fric[m_calc]))
    pico_freq = float(freqs[m_calc][idx_pico])

    # Classificação da ocorrência: pico em 2.5–4.5 kHz ou razão desbalanceada
    eh_chiado = (pico_freq < 4800.0) or (razao < 1.30)

    return {
        "centroide_hz": round(centroide, 1),
        "pico_hz": round(pico_freq, 1),
        "e_chiado_2k5_4k5": e_chiado,
        "e_limpo_5k5_10k": e_limpo,
        "razao_limpo_chiado": round(razao, 2),
        "classificacao": "chiado" if eh_chiado else "limpo",
    }


def analisar_chiado_tomada(caminho_wav, palavras_scribe):
    """Analisa a presença de chiado carioca /ʃ/ nas palavras com coda /s/ de uma tomada."""
    audio = ler(caminho_wav, canais=1)[:, 0]
    palavras_coda = identificar_palavras_coda_s(palavras_scribe)

    detalhes_palavras = []
    for w in palavras_coda:
        res = extrair_fricativa_palavra(audio, w["start"], w["end"])
        if res:
            detalhes_palavras.append({
                "palavra": w["text"],
                "start": round(w["start"], 3),
                "end": round(w["end"], 3),
                **res
            })

    if not detalhes_palavras:
        return {
            "total_palavras_analisadas": 0,
            "palavras_com_chiado": 0,
            "taxa_chiado_pct": 0.0,
            "centroide_mediano_hz": 0.0,
            "pico_mediano_hz": 0.0,
            "razao_mediana_limpo_chiado": 0.0,
            "veredito_triagem": "inconclusivo",
            "detalhes": []
        }

    n_total = len(detalhes_palavras)
    n_chiado = sum(1 for d in detalhes_palavras if d["classificacao"] == "chiado")
    taxa_chiado = round((n_chiado / n_total) * 100, 1)

    centroides = [d["centroide_hz"] for d in detalhes_palavras]
    picos = [d["pico_hz"] for d in detalhes_palavras]
    razoes = [d["razao_limpo_chiado"] for d in detalhes_palavras]

    med_cent = round(float(np.median(centroides)), 1)
    med_pico = round(float(np.median(picos)), 1)
    med_razao = round(float(np.median(razoes)), 2)

    # Triagem objetiva da tomada:
    # - Taxa de chiado <= 25%: limpo (como Bloco A, com 11.1%)
    # - Taxa de chiado >= 35%: chiado_carioca (como Bloco C reprovado, com 46.7%)
    # - Intermediário: moderado_a_ouvir
    if taxa_chiado <= 25.0:
        veredito = "limpo"
    elif taxa_chiado >= 35.0:
        veredito = "chiado_carioca"
    else:
        veredito = "moderado_a_ouvir"

    return {
        "total_palavras_analisadas": n_total,
        "palavras_com_chiado": n_chiado,
        "taxa_chiado_pct": taxa_chiado,
        "centroide_mediano_hz": med_cent,
        "pico_mediano_hz": med_pico,
        "razao_mediana_limpo_chiado": med_razao,
        "veredito_triagem": veredito,
        "detalhes": detalhes_palavras
    }
