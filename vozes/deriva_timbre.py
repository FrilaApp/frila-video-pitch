"""Medição objetiva de timbre e deriva entre blocos de locução (Tarefas 6+).
Calcula F0 médio/mediano, centroide espectral e envelope espectral por bandas de frequência
para monitorar consistência vocal entre blocos de uma mesma narradora (Ana v3 em A, C e D)
e aferir contraste nítido com narrador distinto (Gabriel em B).
"""
import json
import pathlib
import numpy as np

from motor.audio_util import SR, db, ler


def analisar_timbre_arquivo(caminho_wav):
    """Extrai características físicas de timbre na fala ativa."""
    x = ler(caminho_wav, canais=1)[:, 0]
    frame_len = int(0.040 * SR)  # 40 ms
    hop = int(0.010 * SR)        # 10 ms
    
    if len(x) < frame_len:
        return {"erro": "audio_muito_curto"}

    n_frames = (len(x) - frame_len) // hop
    rms_total = np.sqrt(np.mean(x**2))
    limiar_ativo = 0.05 * rms_total
    
    f0_list = []
    centroides = []
    espectros_quadro = []
    
    for i in range(n_frames):
        quadro = x[i * hop : i * hop + frame_len]
        rms_q = np.sqrt(np.mean(quadro**2))
        if rms_q < limiar_ativo:
            continue
            
        w = np.hanning(len(quadro)) * quadro
        spec = np.abs(np.fft.rfft(w))
        freqs = np.fft.rfftfreq(len(w), 1 / SR)
        sum_spec = np.sum(spec)
        
        if sum_spec > 1e-12:
            c = np.sum(freqs * spec) / sum_spec
            centroides.append(c)
            espectros_quadro.append(spec)
            
        # Pitch tracking por autocorrelação
        corr = np.correlate(w, w, mode='full')
        corr = corr[len(corr)//2:]
        min_lag = int(SR / 400)  # teto 400 Hz
        max_lag = int(SR / 70)   # piso 70 Hz
        if max_lag < len(corr):
            lag = min_lag + np.argmax(corr[min_lag:max_lag])
            if corr[lag] > 0.3 * corr[0]:
                f0_list.append(SR / lag)

    f0_mediano = float(np.median(f0_list)) if f0_list else 0.0
    f0_std = float(np.std(f0_list)) if len(f0_list) > 1 else 0.0
    centroide_medio = float(np.mean(centroides)) if centroides else 0.0
    centroide_std = float(np.std(centroides)) if len(centroides) > 1 else 0.0

    # Energia por bandas críticas na fala ativa
    bandas = {
        "grave_80_300": 0.0,
        "formantes_300_3000": 0.0,
        "presenca_3000_6000": 0.0,
        "brilho_6000_12000": 0.0,
        "ar_12000_20000": 0.0
    }
    
    if espectros_quadro:
        spec_medio = np.mean(espectros_quadro, axis=0)
        freqs = np.fft.rfftfreq(frame_len, 1 / SR)
        energia_total = np.sum(spec_medio**2) + 1e-12
        
        m_grave = (freqs >= 80) & (freqs < 300)
        m_formantes = (freqs >= 300) & (freqs < 3000)
        m_presenca = (freqs >= 3000) & (freqs < 6000)
        m_brilho = (freqs >= 6000) & (freqs < 12000)
        m_ar = (freqs >= 12000) & (freqs < 20000)
        
        bandas["grave_80_300"] = round(float(np.sum(spec_medio[m_grave]**2) / energia_total * 100), 2)
        bandas["formantes_300_3000"] = round(float(np.sum(spec_medio[m_formantes]**2) / energia_total * 100), 2)
        bandas["presenca_3000_6000"] = round(float(np.sum(spec_medio[m_presenca]**2) / energia_total * 100), 2)
        bandas["brilho_6000_12000"] = round(float(np.sum(spec_medio[m_brilho]**2) / energia_total * 100), 2)
        bandas["ar_12000_20000"] = round(float(np.sum(spec_medio[m_ar]**2) / energia_total * 100), 2)

    return {
        "f0_mediano_hz": round(f0_mediano, 1),
        "f0_std_hz": round(f0_std, 1),
        "centroide_medio_hz": round(centroide_medio, 1),
        "centroide_std_hz": round(centroide_std, 1),
        "energia_por_banda_pct": bandas
    }


def comparar_timbre_blocos(dados_blocos):
    """Calcula a variação relativa de F0 e centroide espectral entre blocos da mesma voz."""
    # Exemplo dados_blocos: {"A": {...}, "C": {...}, "D": {...}}
    relatorio = {}
    chaves = list(dados_blocos.keys())
    for i in range(len(chaves)):
        for j in range(i + 1, len(chaves)):
            b1 = chaves[i]
            b2 = chaves[j]
            d1 = dados_blocos[b1]
            d2 = dados_blocos[b2]
            
            diff_f0 = round(abs(d1["f0_mediano_hz"] - d2["f0_mediano_hz"]), 1)
            diff_cent = round(abs(d1["centroide_medio_hz"] - d2["centroide_medio_hz"]), 1)
            
            # Razão de F0 em semitons
            if d1["f0_mediano_hz"] > 0 and d2["f0_mediano_hz"] > 0:
                semitons = round(abs(12 * np.log2(d1["f0_mediano_hz"] / d2["f0_mediano_hz"])), 2)
            else:
                semitons = 0.0
                
            relatorio[f"{b1}_vs_{b2}"] = {
                "diff_f0_hz": diff_f0,
                "diff_f0_semitons": semitons,
                "diff_centroide_hz": diff_cent
            }
    return relatorio
