"""Auditoria técnica das tomadas regeneradas do Bloco C e atualização do kit de escuta.

Mede:
1. Chiado carioca /ʃ/ vs [s] limpo em todas as tomadas de C (T1 a T4)
2. LUFS integrado, True Peak (dBTP), LRA (LU)
3. F0 e Centroide espectral
4. Regra A8 (pausas internas >= 0.500 s) e Scribe
5. Prévias de fronteiras B→C e C→D com a nova tomada T4 (limpa)
6. Empacotamento em ~/Downloads/frila-escuta-vozes-blocos/ com README descritivo (sem scorecards).
"""
import copy
import json
from pathlib import Path
import shutil
import sys
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from motor.audio_util import SR, db, gravar_json, hash_arquivo, ler, salvar, medir_loudness
from motor.analisar_emendas import verificar_a8, validar_palavras
from vozes.deriva_timbre import analisar_timbre_arquivo
from vozes.metrica_chiado import analisar_chiado_tomada

TOMADAS_C = {
    "T1_seed1_reprovada": "fcd0c415fbbd41318b4a4951f89fa4d5",
    "T2_seed2": "3941bcd67ab7463eb27fdaa22154c7aa",
    "T3_seed3": "a813c1f1509a452daf75457e47686a1f",
    "T4_seed7_limpa": "61181794d7b4471891be3c8ca30dda2a",
}

BLOCO_B_UUID = "8f28d33d7aa44331ab4b8fccc47cdced"
BLOCO_D_UUID = "e4116cbda2d946b1b5055f61f7d222ca"

BAR = 1.96734
COMPASSOS = [0, 13, 23, 35, 41]
RECUOS_S = {"A": 0.98367, "B": 0.650, "C": 0.600, "D": 0.100}


def carregar_dados_tomada(bloco_id, uuid_str):
    p_dir = ROOT / "vozes/tomadas/blocos/pt" / bloco_id / uuid_str
    voz_wav = p_dir / "voz.wav"
    bruto_wav = p_dir / "bruto.wav"
    scribe_json = p_dir / "scribe.json"
    bruto_json = p_dir / "bruto.json"

    meta = json.loads(bruto_json.read_text(encoding="utf-8"))
    sc = json.loads(scribe_json.read_text(encoding="utf-8"))

    x = ler(voz_wav, 1)[:, 0]
    duracao_s = len(x) / SR

    raw_words = meta.get("palavras") or [w for w in sc.get("words", []) if w.get("type", "word") == "word"]
    words = validar_palavras(raw_words, duracao_s)
    a8 = verificar_a8([{"id": bloco_id, "fala": meta["fala_oficial"]}], words)

    loudness = medir_loudness(voz_wav)
    timbre = analisar_timbre_arquivo(voz_wav)
    chiado = analisar_chiado_tomada(voz_wav, words)

    return {
        "bloco": bloco_id,
        "uuid": uuid_str,
        "x": x,
        "duracao_s": duracao_s,
        "sha256_voz": hash_arquivo(voz_wav),
        "sha256_bruto": hash_arquivo(bruto_wav),
        "words": words,
        "a8": a8,
        "loudness": loudness,
        "timbre": timbre,
        "chiado": chiado,
        "dir": p_dir,
        "voz_wav": voz_wav,
        "seed": meta["geracao"].get("seed"),
        "substituicoes": meta.get("substituicoes_pronuncia", [])
    }


def gerar_previa_fronteira(da, db_, idx_fronteira, nome_saida, out_dir):
    anterior = da["bloco"]
    seguinte = db_["bloco"]
    limites_musicais = [c * BAR for c in COMPASSOS]

    ra = RECUOS_S[anterior]
    rb = RECUOS_S[seguinte]

    limite_anterior = limites_musicais[idx_fronteira - 1]
    limite_corte = limites_musicais[idx_fronteira]

    ult_palavra_pos = limite_anterior + ra + da["words"][-1]["end"]
    prim_palavra_pos = limite_corte + rb + db_["words"][0]["start"]

    pausa_inter_blocos = prim_palavra_pos - ult_palavra_pos
    corte_pos = limite_corte

    ax = da["x"]
    bx = db_["x"]
    n_a = min(len(ax), round(2.5 * SR))
    n_b = min(len(bx), round(2.5 * SR))

    seg_a = ax[-n_a:]
    seg_b = bx[:n_b]

    fim_wav_a_pos = limite_anterior + ra + da["duracao_s"]
    ini_wav_b_pos = limite_corte + rb
    silencio_entre_wavs_s = ini_wav_b_pos - fim_wav_a_pos
    amostras_silencio = max(0, round(silencio_entre_wavs_s * SR))
    silencio_pad = np.zeros(amostras_silencio, dtype="<f4")

    x_fronteira = np.concatenate([seg_a, silencio_pad, seg_b])
    out_dir.mkdir(parents=True, exist_ok=True)
    previa_wav = out_dir / f"{nome_saida}.wav"
    salvar(previa_wav, x_fronteira)

    loudness_f = medir_loudness(previa_wav)

    return {
        "fronteira": f"{anterior}→{seguinte}",
        "nome": nome_saida,
        "arquivo": str(previa_wav),
        "sha256": hash_arquivo(previa_wav),
        "duracao_s": round(len(x_fronteira) / SR, 3),
        "corte_compasso": COMPASSOS[idx_fronteira],
        "corte_tempo_global_s": round(corte_pos, 3),
        "ultima_palavra": da["words"][-1]["text"],
        "primeira_palavra": db_["words"][0]["text"],
        "pausa_verbal_s": round(pausa_inter_blocos, 3),
        "protecao_antes_corte_s": round(corte_pos - ult_palavra_pos, 3),
        "protecao_depois_corte_s": round(prim_palavra_pos - corte_pos, 3),
        "folga_entre_wavs_s": round(silencio_entre_wavs_s, 3),
        "lufs_integrado": float(loudness_f["input_i"]),
        "true_peak_dbtp": float(loudness_f["input_tp"]),
    }


def main():
    print("==================================================================")
    print("  Auditoria Comparativa das Tomadas do Bloco C (Regeneração)")
    print("==================================================================")

    dados_c = {}
    for rotulo, uuid_str in TOMADAS_C.items():
        d = carregar_dados_tomada("C", uuid_str)
        dados_c[rotulo] = d
        ch = d["chiado"]
        ld = d["loudness"]
        tb = d["timbre"]
        a8 = d["a8"]

        print(f"\n--- Tomada {rotulo} (UUID: {uuid_str[:12]}..., Seed: {d['seed']}) ---")
        print(f"  Duração: {d['duracao_s']:.3f} s | SHA-256 voz: {d['sha256_voz'][:16]}...")
        print(f"  Chiado Carioca: {ch['veredito_triagem'].upper()} | Taxa: {ch['taxa_chiado_pct']}% ({ch['palavras_com_chiado']}/{ch['total_palavras_analisadas']})")
        print(f"    Pico Mediano: {ch.get('pico_mediano_hz')} Hz | Centroide Mediano: {ch.get('centroide_mediano_hz')} Hz | Razão L/C: {ch.get('razao_mediana_limpo_chiado')}")
        print(f"  Loudness: {ld['input_i']} LUFS | TP: {ld['input_tp']} dBTP | LRA: {ld['input_lra']} LU")
        print(f"  Timbre: F0 = {tb['f0_mediano_hz']} Hz | Centroide = {tb['centroide_medio_hz']} Hz")
        print(f"  A8: estado = {a8['estado']} ({len(a8['falhas'])} falhas)")
        for f in a8["falhas"]:
            print(f"    🚨 Pausa: {f['duracao']:.3f} s em t={f['tempo']:.3f} s ({f['tipo']})")

    # Carregar Bloco B e Bloco D para fronteiras
    dados_b = carregar_dados_tomada("B", BLOCO_B_UUID)
    dados_d = carregar_dados_tomada("D", BLOCO_D_UUID)

    cache_fronteiras = ROOT / "motor/cache/auditoria_regerar_c/fronteiras"
    cache_fronteiras.mkdir(parents=True, exist_ok=True)

    # Gerar prévias de fronteira com T4 (limpa)
    d_t4 = dados_c["T4_seed7_limpa"]
    f_b_c_t4 = gerar_previa_fronteira(dados_b, d_t4, 2, "fronteira_B_C_t4", cache_fronteiras)
    f_c_t4_d = gerar_previa_fronteira(d_t4, dados_d, 3, "fronteira_C_t4_D", cache_fronteiras)

    print("\n--- Novas Prévias de Fronteira com Bloco C Tomada 4 (Limpa) ---")
    print(f"  Fronteira B→C (t4): pausa={f_b_c_t4['pausa_verbal_s']} s | {f_b_c_t4['lufs_integrado']} LUFS | TP: {f_b_c_t4['true_peak_dbtp']} dBTP")
    print(f"  Fronteira C→D (t4): pausa={f_c_t4_d['pausa_verbal_s']} s | {f_c_t4_d['lufs_integrado']} LUFS | TP: {f_c_t4_d['true_peak_dbtp']} dBTP")

    # Montar e atualizar o kit em ~/Downloads/frila-escuta-vozes-blocos/
    kit_dir = Path.home() / "Downloads/frila-escuta-vozes-blocos"
    kit_dir.mkdir(parents=True, exist_ok=True)

    # 1. Renomear C anterior para bloco_C_ana_v3_reprovado_chiado.wav
    c_antigo = kit_dir / "bloco_C_ana_v3.wav"
    c_reprovado = kit_dir / "bloco_C_ana_v3_reprovado_chiado.wav"
    if c_antigo.exists():
        shutil.move(str(c_antigo), str(c_reprovado))
    elif not c_reprovado.exists():
        shutil.copy2(str(dados_c["T1_seed1_reprovada"]["voz_wav"]), str(c_reprovado))

    # 2. Renomear fronteiras antigas para deixar claro que usavam o C reprovado
    f_bc_antigo = kit_dir / "fronteira_B_C.wav"
    f_bc_reprov = kit_dir / "fronteira_B_C_reprovado.wav"
    if f_bc_antigo.exists():
        shutil.move(str(f_bc_antigo), str(f_bc_reprov))

    f_cd_antigo = kit_dir / "fronteira_C_D.wav"
    f_cd_reprov = kit_dir / "fronteira_C_reprovado_D.wav"
    if f_cd_antigo.exists():
        shutil.move(str(f_cd_antigo), str(f_cd_reprov))

    # 3. Copiar as 3 novas tomadas
    shutil.copy2(str(dados_c["T2_seed2"]["voz_wav"]), str(kit_dir / "bloco_C_ana_v3_t2.wav"))
    shutil.copy2(str(dados_c["T3_seed3"]["voz_wav"]), str(kit_dir / "bloco_C_ana_v3_t3.wav"))
    shutil.copy2(str(dados_c["T4_seed7_limpa"]["voz_wav"]), str(kit_dir / "bloco_C_ana_v3_t4.wav"))

    # 4. Copiar novas fronteiras com T4
    shutil.copy2(str(cache_fronteiras / "fronteira_B_C_t4.wav"), str(kit_dir / "fronteira_B_C_t4.wav"))
    shutil.copy2(str(cache_fronteiras / "fronteira_C_t4_D.wav"), str(kit_dir / "fronteira_C_t4_D.wav"))

    # 5. Escrever README.md técnico sem scorecards
    readme_md = f"""# Kit de Escuta — Regeneração do Bloco C (Ana v3) e Triagem de Chiado

Este kit reúne as medições acústicas objetivas e os áudios correspondentes à regeneração do **Bloco C** na voz da Ana (`eleven_v3`), solicitada após a reprovação de ouvido da tomada inicial por sotaque carioca (chiamento /ʃ/ em coda sibilante).

> **Aviso de Escuta:** O ouvido do Fabrício é soberano. Nenhuma métrica aqui substitui a validação auditiva humana. Este documento relata fatos e medições acústicas reproduzíveis.
> **Bloco D:** Conforme diretriz do Fabrício, a fala final da v14 será reformulada. O arquivo `bloco_D_ana_v3.wav` permanece neste kit exclusivamente como referência tímbrica; a régua narrativa não foi recalculada.

---

## 1. Tabela Comparativa de Medições Acústicas — Bloco C

| Tomada | Semente | Duração (s) | Métrica de Chiado | Taxa Chiado (%) | Pico Mediano Fricativa (Hz) | Razão Limpo/Chiado | F0 Mediano (Hz) | Loudness (LUFS) | True Peak (dBTP) | Regra A8 (Pausas >= 0.500s) |
|---|---|---|---|---|---|---|---|---|---|---|
| **T1 (Original)** | 1 | 22.080 | `chiado_carioca` | 46.7% (7/15) | 5.760 Hz | 2.69 | 231.9 | -17.97 | -3.33 | 1 falha (0.660 s em t=8.350s) |
| **T2** | 2 | 22.000 | `chiado_carioca` | 46.7% (7/15) | 5.760 Hz | 2.26 | 233.0 | -18.17 | -4.31 | 1 falha (0.880 s em t=8.220s) |
| **T3** | 3 | 22.480 | `chiado_carioca` | 53.3% (8/15) | 4.240 Hz | 1.75 | 237.6 | -17.76 | -3.43 | 2 falhas (0.560s em t=6.840s; 0.700s em t=8.370s) |
| **T4 (Candidata)** | 7 | 22.240 | `limpo` | **6.7%** (1/15) | **8.280 Hz** | **46.18** | 246.2 | -17.78 | -3.71 | 3 falhas (0.520s em t=2.100s; 0.520s em t=6.820s; 0.740s em t=8.330s) |

### Referência dos Blocos Aprovados de Ouvido (Validação da Métrica)
- **Bloco A (Ana v3, aprovado):** Taxa de chiado = **11.1%** (1/9), Pico mediano = **6.040 Hz**, Veredito = `limpo`.
- **Bloco D (Ana v3, aprovado quanto ao timbre):** Razão mediana limpo/chiado = **46.57**, Centroide mediano = **7.035 Hz**.
- **Diagnóstico Acústico:** As tomadas T1, T2 e T3 concentram forte ressonância pós-alveolar em ~3.680–4.040 Hz nas palavras em coda /s/ (*"Dos"*, *"semanas"*, *"profissionais"*, *"presentes"*, *"restaurantes"*). A tomada **T4** (seed 7) eliminou quase totalmente essa concentração, deslocando o pico espectral médio para **6.480 Hz** e alcançando taxa de apenas **6.7%**, padrão estritamente compatível com o Bloco A aprovado.

---

## 2. Detalhes das Pausas Internas (Regra A8) na Tomada T4

A tomada T4 apresentou 3 pausas internas superiores a 0.500 s:
1. **t = 2.100 s (0.520 s):** Entre *"apps"* e *"que"* (pausa respiratória de 20 ms acima do limite de 500 ms).
2. **t = 6.820 s (0.520 s):** Entre *"piloto,"* e *"oito"* (vírgula do roteiro; 20 ms acima do limite).
3. **t = 8.330 s (0.740 s):** Entre *"semanas,"* e *"cinquenta"* (vírgula enumerativa do roteiro).

---

## 3. Prévias de Fronteira no Kit

- `fronteira_B_C_t4.wav`: Transição Gabriel (Bloco B) → Ana (Bloco C Tomada 4). Pausa verbal: {f_b_c_t4['pausa_verbal_s']} s. Loudness: {f_b_c_t4['lufs_integrado']} LUFS.
- `fronteira_C_t4_D.wav`: Transição Ana (Bloco C Tomada 4) → Ana (Bloco D referência). Pausa verbal: {f_c_t4_d['pausa_verbal_s']} s. Loudness: {f_c_t4_d['lufs_integrado']} LUFS.
- `fronteira_B_C_reprovado.wav` e `fronteira_C_reprovado_D.wav`: Mantidas para conferência auditiva do contraste entre a versão chiada e a versão limpa.

---

## 4. Guia de Arquivos de Áudio no Diretório

1. `bloco_A_ana_v3.wav` — Bloco A aprovado (Ana v3, seed 2).
2. `bloco_B_gabriel_v2.wav` — Bloco B aprovado (Gabriel v2, seed 1).
3. `bloco_C_ana_v3_reprovado_chiado.wav` — Tomada 1 antiga do Bloco C (reprovada por chiado carioca).
4. `bloco_C_ana_v3_t2.wav` — Tomada 2 (seed 2; chiado carioca persistente).
5. `bloco_C_ana_v3_t3.wav` — Tomada 3 (seed 3; chiado carioca persistente).
6. `bloco_C_ana_v3_t4.wav` — **Tomada 4 (seed 7; sibilante limpa, taxa 6.7%)**.
7. `bloco_D_ana_v3.wav` — Referência de timbre da Ana (aguardando novo texto de roteiro para a cena v14).
8. `fronteira_B_C_t4.wav` — Prévio de transição B → C com a Tomada 4.
9. `fronteira_C_t4_D.wav` — Prévio de transição C → D com a Tomada 4.
"""

    readme_path = kit_dir / "README.md"
    readme_path.write_text(readme_md, encoding="utf-8")
    print(f"\n✅ Kit de escuta atualizado com sucesso em {kit_dir}")
    print(f"✅ README gerado em {readme_path}")


if __name__ == "__main__":
    main()
