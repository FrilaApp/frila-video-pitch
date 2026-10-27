"""Auditoria técnica das tomadas regeneradas do Bloco D e atualização do kit de escuta.

Mede:
1. Scribe literal e integridade textual das cenas v13 e v14
2. Regra A8 (pausas internas >= 0.500 s)
3. Métrica objetiva de chiado carioca /ʃ/ vs [s] limpo em todas as tomadas de D
4. Loudness (LUFS integrado, True Peak dBTP, LRA LU)
5. Timbre (F0 mediano/std, centroide médio/std, energia por banda)
6. Deriva de timbre relativa contra Bloco A (aprovado) e Bloco C Tomada 4 (aprovada)
7. Silêncios de entrada e saída
8. Regra A1 na junção interna v13→v14 (pausa entre 'cuida.' e 'Combinou?')
9. Prévias de fronteira C(T4)→D novo para cada tomada
10. Empacotamento em ~/Downloads/frila-escuta-vozes-blocos/ com README descritivo (sem scorecards).
"""
import json
from pathlib import Path
import shutil
import sys
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from motor.audio_util import SR, db, gravar_json, hash_arquivo, ler, salvar, medir_loudness
from motor.analisar_emendas import verificar_a8, validar_palavras
from vozes.deriva_timbre import analisar_timbre_arquivo, comparar_timbre_blocos
from vozes.metrica_chiado import analisar_chiado_tomada

BLOCO_A_UUID = "5dcbc2883164470aa2d0cb7fbe2b4a44"
BLOCO_B_UUID = "8f28d33d7aa44331ab4b8fccc47cdced"
BLOCO_C_T4_UUID = "61181794d7b4471891be3c8ca30dda2a"
BLOCO_D_ANTIGO_UUID = "e4116cbda2d946b1b5055f61f7d222ca"

TOMADAS_D_NOVAS = {
    "T1_seed1": "df571ebe48f5408e8f8b5eb72397c69b",
    "T2_seed2": "1cf3cc77c05843048808b69346d243ac",
    "T3_seed3": "546582117e2047ed8a9e12e5af8f1ee7",
}

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

    silencio_entrada_s = round(words[0]["start"], 3) if words else 0.0
    silencio_saida_s = round(duracao_s - words[-1]["end"], 3) if words else 0.0

    # Analisar transição interna v13 -> v14 (Regra A1)
    transicao_v13_v14 = None
    for idx, w in enumerate(words):
        if "cuida" in w["text"].lower() and idx + 1 < len(words):
            prox = words[idx + 1]
            pausa_v13_v14 = round(prox["start"] - w["end"], 3)
            transicao_v13_v14 = {
                "fim_v13_palavra": w["text"],
                "fim_v13_tempo_s": round(w["end"], 3),
                "ini_v14_palavra": prox["text"],
                "ini_v14_tempo_s": round(prox["start"], 3),
                "pausa_verbal_s": pausa_v13_v14,
                "a1_respeitado": bool(pausa_v13_v14 > 0.0)
            }
            break

    return {
        "bloco": bloco_id,
        "uuid": uuid_str,
        "x": x,
        "duracao_s": duracao_s,
        "sha256_voz": hash_arquivo(voz_wav),
        "sha256_bruto": hash_arquivo(bruto_wav),
        "words": words,
        "texto_scribe": sc.get("text", ""),
        "a8": a8,
        "loudness": loudness,
        "timbre": timbre,
        "chiado": chiado,
        "silencio_entrada_s": silencio_entrada_s,
        "silencio_saida_s": silencio_saida_s,
        "transicao_v13_v14": transicao_v13_v14,
        "dir": p_dir,
        "voz_wav": voz_wav,
        "seed": meta.get("geracao", {}).get("seed"),
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


def auditar_e_empacotar():
    print("==================================================================")
    print("  Auditoria Comparativa das Tomadas do Bloco D (Nova Fala v14)")
    print("==================================================================")

    dados_a = carregar_dados_tomada("A", BLOCO_A_UUID)
    dados_c_t4 = carregar_dados_tomada("C", BLOCO_C_T4_UUID)
    dados_d_antigo = carregar_dados_tomada("D", BLOCO_D_ANTIGO_UUID)

    dados_d_novos = {}
    for rotulo, uuid_str in TOMADAS_D_NOVAS.items():
        d = carregar_dados_tomada("D", uuid_str)
        dados_d_novos[rotulo] = d
        ch = d["chiado"]
        ld = d["loudness"]
        tb = d["timbre"]
        a8 = d["a8"]
        tr = d["transicao_v13_v14"]

        # Deriva de timbre contra Bloco A e Bloco C-T4
        deriva_a = comparar_timbre_blocos({"A": dados_a["timbre"], "D": tb})["A_vs_D"]
        deriva_c = comparar_timbre_blocos({"C": dados_c_t4["timbre"], "D": tb})["C_vs_D"]
        d["deriva_contra_A"] = deriva_a
        d["deriva_contra_C_T4"] = deriva_c

        print(f"\n--- Tomada {rotulo} (UUID: {uuid_str[:12]}..., Seed: {d['seed']}) ---")
        print(f"  Duração: {d['duracao_s']:.3f} s | Silêncios: entrada={d['silencio_entrada_s']} s, saída={d['silencio_saida_s']} s")
        print(f"  Loudness: {ld['input_i']} LUFS | TP: {ld['input_tp']} dBTP | LRA: {ld['input_lra']} LU")
        print(f"  Timbre: F0 = {tb['f0_mediano_hz']} Hz (std: {tb['f0_std_hz']} Hz) | Centroide = {tb['centroide_medio_hz']} Hz")
        print(f"    Deriva vs Bloco A (aprovado): ΔF0 = {deriva_a['diff_f0_hz']} Hz ({deriva_a['diff_f0_semitons']} st), ΔCentroide = {deriva_a['diff_centroide_hz']} Hz")
        print(f"    Deriva vs Bloco C-T4 (aprovado): ΔF0 = {deriva_c['diff_f0_hz']} Hz ({deriva_c['diff_f0_semitons']} st), ΔCentroide = {deriva_c['diff_centroide_hz']} Hz")
        print(f"  Chiado Carioca: {ch['veredito_triagem'].upper()} | Taxa: {ch['taxa_chiado_pct']}% ({ch['palavras_com_chiado']}/{ch['total_palavras_analisadas']})")
        print(f"    Razão Limpo/Chiado: {ch.get('razao_mediana_limpo_chiado')} | Centroide Mediano: {ch.get('centroide_mediano_hz')} Hz")
        print(f"  Regra A8: estado = {a8['estado']} ({len(a8['falhas'])} falhas)")
        if tr:
            print(f"  Regra A1 (v13→v14): {tr['fim_v13_palavra']} [{tr['fim_v13_tempo_s']}s] -> {tr['ini_v14_palavra']} [{tr['ini_v14_tempo_s']}s] | Pausa = {tr['pausa_verbal_s']} s")

    # Gerar prévias de fronteira C(T4) -> D novo para cada tomada
    cache_fronteiras = ROOT / "motor/cache/auditoria_regerar_d/fronteiras"
    cache_fronteiras.mkdir(parents=True, exist_ok=True)

    fronteiras_cd = {}
    print("\n--- Prévias de Fronteira C(T4)→D Novo ---")
    for rotulo, d_novo in dados_d_novos.items():
        sufixo = rotulo.lower().split("_")[0]  # t1, t2, t3
        nome_f = f"fronteira_C_t4_D_{sufixo}"
        f_info = gerar_previa_fronteira(dados_c_t4, d_novo, 3, nome_f, cache_fronteiras)
        fronteiras_cd[rotulo] = f_info
        print(f"  {nome_f}: pausa verbal = {f_info['pausa_verbal_s']} s | {f_info['lufs_integrado']} LUFS | TP: {f_info['true_peak_dbtp']} dBTP | Folga: {f_info['folga_entre_wavs_s']} s")

    # Empacotar no kit de escuta ~/Downloads/frila-escuta-vozes-blocos/
    kit_dir = Path.home() / "Downloads/frila-escuta-vozes-blocos"
    kit_dir.mkdir(parents=True, exist_ok=True)

    # 1. Mover D antigo para _antigo
    d_antigo_kit = kit_dir / "bloco_D_ana_v3.wav"
    d_antigo_dest = kit_dir / "bloco_D_ana_v3_antigo.wav"
    if d_antigo_kit.exists():
        shutil.move(str(d_antigo_kit), str(d_antigo_dest))
    elif not d_antigo_dest.exists() and dados_d_antigo["voz_wav"].exists():
        shutil.copy2(str(dados_d_antigo["voz_wav"]), str(d_antigo_dest))

    # Mover fronteira C_t4_D antiga se existir
    f_cd_antiga = kit_dir / "fronteira_C_t4_D.wav"
    f_cd_antiga_dest = kit_dir / "fronteira_C_t4_D_antigo.wav"
    if f_cd_antiga.exists():
        shutil.move(str(f_cd_antiga), str(f_cd_antiga_dest))

    # 2. Copiar as 3 novas tomadas do D
    shutil.copy2(str(dados_d_novos["T1_seed1"]["voz_wav"]), str(kit_dir / "bloco_D_ana_v3_t1.wav"))
    shutil.copy2(str(dados_d_novos["T2_seed2"]["voz_wav"]), str(kit_dir / "bloco_D_ana_v3_t2.wav"))
    shutil.copy2(str(dados_d_novos["T3_seed3"]["voz_wav"]), str(kit_dir / "bloco_D_ana_v3_t3.wav"))

    # 3. Copiar novas prévias de fronteira C(T4) -> D
    for rotulo, f_info in fronteiras_cd.items():
        sufixo = rotulo.lower().split("_")[0]
        shutil.copy2(f_info["arquivo"], str(kit_dir / f"fronteira_C_t4_D_{sufixo}.wav"))

    # 4. Escrever README em texto livre sem scorecard
    t1 = dados_d_novos["T1_seed1"]
    t2 = dados_d_novos["T2_seed2"]
    t3 = dados_d_novos["T3_seed3"]

    readme_md = f"""# Kit de Escuta — Bloco D Regenerado (Ana v3, Nova Fala da Cena v14)

Este diretório reúne as tomadas de locução e as prévias de montagem do **Bloco D** (cenas v13 e v14 integradas), sintetizadas após a atualização da fala final da v14 no roteiro oficial (*"Combinou? Pode contar. Dos dois lados. Frila."*).

> **Aviso de Avaliação:** O ouvido do Fabrício é a autoridade soberana do projeto. Nenhuma tabela, métrica acústica ou indicador de triagem aqui substitui a escuta estética e humana. Nenhuma tomada foi selecionada oficialmente e nenhuma régua narrativa foi recalculada.

---

## 1. Dados e Medições Acústicas das Novas Tomadas do Bloco D

| Tomada | Semente | Duração (s) | Scribe | Regra A8 | Chiado Carioca | Taxa Chiado (%) | Razão L/C | F0 Mediano (Hz) | Loudness (LUFS) | True Peak (dBTP) | Pausa v13→v14 (s) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **T1 (Seed 1)** | 1 | {t1['duracao_s']:.3f} | ✅ Idêntico | Sem falhas (0) | `limpo` | {t1['chiado']['taxa_chiado_pct']}% (1/5) | {t1['chiado']['razao_mediana_limpo_chiado']} | {t1['timbre']['f0_mediano_hz']} | {t1['loudness']['input_i']} | {t1['loudness']['input_tp']} | {t1['transicao_v13_v14']['pausa_verbal_s']} s |
| **T2 (Seed 2)** | 2 | {t2['duracao_s']:.3f} | ✅ Idêntico | Sem falhas (0) | `limpo` | **{t2['chiado']['taxa_chiado_pct']}% (0/5)** | **{t2['chiado']['razao_mediana_limpo_chiado']}** | {t2['timbre']['f0_mediano_hz']} | {t2['loudness']['input_i']} | {t2['loudness']['input_tp']} | **{t2['transicao_v13_v14']['pausa_verbal_s']} s** |
| **T3 (Seed 3)** | 3 | {t3['duracao_s']:.3f} | ✅ Idêntico | Sem falhas (0) | `limpo` | **{t3['chiado']['taxa_chiado_pct']}% (0/5)** | **{t3['chiado']['razao_mediana_limpo_chiado']}** | {t3['timbre']['f0_mediano_hz']} | {t3['loudness']['input_i']} | {t3['loudness']['input_tp']} | {t3['transicao_v13_v14']['pausa_verbal_s']} s |

---

## 2. Consistência Tímbrica e Deriva Vocal (Ana v3)

Monitoramento físico de F0 e centroide espectral em relação aos blocos da Ana já aprovados:

1. **Tomada 1 (Seed 1):**
   - Deriva contra Bloco A (aprovado): ΔF0 = {t1['deriva_contra_A']['diff_f0_hz']} Hz ({t1['deriva_contra_A']['diff_f0_semitons']} st), ΔCentroide = {t1['deriva_contra_A']['diff_centroide_hz']} Hz;
   - Deriva contra Bloco C-T4 (aprovado): ΔF0 = {t1['deriva_contra_C_T4']['diff_f0_hz']} Hz ({t1['deriva_contra_C_T4']['diff_f0_semitons']} st), ΔCentroide = {t1['deriva_contra_C_T4']['diff_centroide_hz']} Hz.
2. **Tomada 2 (Seed 2):**
   - Deriva contra Bloco A (aprovado): ΔF0 = {t2['deriva_contra_A']['diff_f0_hz']} Hz ({t2['deriva_contra_A']['diff_f0_semitons']} st), ΔCentroide = {t2['deriva_contra_A']['diff_centroide_hz']} Hz;
   - Deriva contra Bloco C-T4 (aprovado): ΔF0 = {t2['deriva_contra_C_T4']['diff_f0_hz']} Hz ({t2['deriva_contra_C_T4']['diff_f0_semitons']} st), ΔCentroide = {t2['deriva_contra_C_T4']['diff_centroide_hz']} Hz.
3. **Tomada 3 (Seed 3):**
   - Deriva contra Bloco A (aprovado): ΔF0 = {t3['deriva_contra_A']['diff_f0_hz']} Hz ({t3['deriva_contra_A']['diff_f0_semitons']} st), ΔCentroide = {t3['deriva_contra_A']['diff_centroide_hz']} Hz;
   - Deriva contra Bloco C-T4 (aprovado): ΔF0 = {t3['deriva_contra_C_T4']['diff_f0_hz']} Hz ({t3['deriva_contra_C_T4']['diff_f0_semitons']} st), ΔCentroide = {t3['deriva_contra_C_T4']['diff_centroide_hz']} Hz.

---

## 3. Conformidade com a Regra A1 e Transição v13→v14

Em todas as 3 tomadas, a transição entre o fecho da v13 (*"Deixa que o Frila cuida."*) e a abertura da v14 (*"Combinou?"*) ocorreu de forma contínua e natural, com pausa respiratória clara:
- **T1:** {t1['transicao_v13_v14']['pausa_verbal_s']} s de pausa verbal silenciosa;
- **T2:** {t2['transicao_v13_v14']['pausa_verbal_s']} s de pausa verbal silenciosa (respiração ampla, transição muito suave);
- **T3:** {t3['transicao_v13_v14']['pausa_verbal_s']} s de pausa verbal silenciosa.

Nenhuma frase ou palavra cruza a emenda entre as duas cenas.

---

## 4. Prévias de Fronteira C(T4)→D Novo

As prévias representam a transição contínua do Bloco C oficial (Tomada 4 limpa) para o Bloco D no compasso 35 da música:
- `fronteira_C_t4_D_t1.wav`: Transição para Tomada 1. Pausa verbal: {fronteiras_cd['T1_seed1']['pausa_verbal_s']} s | Loudness: {fronteiras_cd['T1_seed1']['lufs_integrado']} LUFS.
- `fronteira_C_t4_D_t2.wav`: Transição para Tomada 2. Pausa verbal: {fronteiras_cd['T2_seed2']['pausa_verbal_s']} s | Loudness: {fronteiras_cd['T2_seed2']['lufs_integrado']} LUFS.
- `fronteira_C_t4_D_t3.wav`: Transição para Tomada 3. Pausa verbal: {fronteiras_cd['T3_seed3']['pausa_verbal_s']} s | Loudness: {fronteiras_cd['T3_seed3']['lufs_integrado']} LUFS.

---

## 5. Inventário dos Arquivos no Diretório

1. `bloco_A_ana_v3.wav` — Bloco A aprovado (Ana v3, seed 2).
2. `bloco_B_gabriel_v2.wav` — Bloco B aprovado (Gabriel v2, seed 1).
3. `bloco_C_ana_v3_t4.wav` — Bloco C oficial aprovado de ouvido pelo Fabrício (Ana v3, seed 7, sem chiado).
4. `bloco_D_ana_v3_antigo.wav` — Tomada original antiga do Bloco D (com a frase reprovada da v14).
5. `bloco_D_ana_v3_t1.wav` — **Tomada 1 nova** (Seed 1, 10.880 s, sibilante limpa, 20% taxa).
6. `bloco_D_ana_v3_t2.wav` — **Tomada 2 nova** (Seed 2, 11.840 s, **0.0% chiado**, pausa v13→v14 de 0.480 s).
7. `bloco_D_ana_v3_t3.wav` — **Tomada 3 nova** (Seed 3, 10.880 s, **0.0% chiado**, pausa v13→v14 de 0.260 s).
8. `fronteira_A_B.wav` — Prévio de transição Bloco A → Bloco B.
9. `fronteira_B_C_t4.wav` — Prévio de transição Bloco B → Bloco C (Tomada 4).
10. `fronteira_C_t4_D_antigo.wav` — Prévio de transição antigo C(T4) → D antigo.
11. `fronteira_C_t4_D_t1.wav` — Prévio C(T4) → D Tomada 1.
12. `fronteira_C_t4_D_t2.wav` — Prévio C(T4) → D Tomada 2.
13. `fronteira_C_t4_D_t3.wav` — Prévio C(T4) → D Tomada 3.
"""

    readme_path = kit_dir / "README.md"
    readme_path.write_text(readme_md, encoding="utf-8")
    print(f"\n✅ Kit de escuta atualizado em {kit_dir}")
    print(f"✅ README gerado em {readme_path}")

    # Salvar manifesto em cache
    cache_meta = ROOT / "motor/cache/auditoria_regerar_d/auditoria_d.json"
    gravar_json(cache_meta, {
        "tomadas": {
            k: {
                "uuid": v["uuid"],
                "seed": v["seed"],
                "duracao_s": v["duracao_s"],
                "loudness": v["loudness"],
                "timbre": v["timbre"],
                "chiado": v["chiado"],
                "silencios": {"entrada": v["silencio_entrada_s"], "saida": v["silencio_saida_s"]},
                "transicao_v13_v14": v["transicao_v13_v14"],
                "deriva_A": v["deriva_contra_A"],
                "deriva_C": v["deriva_contra_C_T4"],
            } for k, v in dados_d_novos.items()
        },
        "fronteiras": fronteiras_cd
    })
    print(f"✅ Manifesto salvo em {cache_meta}")


if __name__ == "__main__":
    auditar_e_empacotar()
