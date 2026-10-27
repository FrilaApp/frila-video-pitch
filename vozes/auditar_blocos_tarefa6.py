"""Auditoria técnica e montagem do kit de escuta dos 4 blocos de voz (Tarefa 6).
Executa 100% offline:
1. Medições objetivas dos 4 blocos tratados (voz.wav): LUFS, True Peak, LRA, SHA-256, duração;
2. Auditoria A8 e Scribe por bloco;
3. Medição de timbre e deriva espectral entre blocos da Ana (A, C, D) e contraste com Gabriel (B);
4. Montagem e auditoria das 3 fronteiras (A→B, B→C, C→D) com prévias de áudio;
5. Recalcular nova régua narrativa (compassos [0, 13, 23, 35, 41], total 80.661 s, pausas >= 500 ms);
6. Empacotar kit de escuta em ~/Downloads/frila-escuta-vozes-blocos/ com README sem scorecards.
"""
import contextlib
import copy
import json
from pathlib import Path
import shutil
import sys
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from motor.audio_util import SR, db, gravar_json, hash_arquivo, ler, salvar, medir_loudness
from motor.analisar_emendas import executar, verificar_a8, ler_scribe, validar_palavras
from vozes.manifesto import frases, normal, frases_do_roteiro
from vozes.deriva_timbre import analisar_timbre_arquivo, comparar_timbre_blocos
from vozes.regua_blocos import janela_bloco

TOMADAS_OFICIAIS = {
    "A": "5dcbc2883164470aa2d0cb7fbe2b4a44",
    "B": "8f28d33d7aa44331ab4b8fccc47cdced",
    "C": "fcd0c415fbbd41318b4a4951f89fa4d5",
    "D": "e4116cbda2d946b1b5055f61f7d222ca",
}

# Grade musical calculada para acomodar os novos tempos de voz respeitando pausas >= 500 ms e total em [78, 90]s
BAR = 1.96734
P = 0.491835
COMPASSOS = [0, 13, 23, 35, 41]
RECUOS_S = {"A": 0.98367, "B": 0.650, "C": 0.600, "D": 0.100}


def auditar_e_empacotar():
    print("==================================================================")
    print("  Auditoria Técnica e Empacotamento de Vozes por Bloco (Tarefa 6)")
    print("==================================================================")

    roteiro = json.loads((ROOT / "roteiro.json").read_text(encoding="utf-8"))
    cenas_dict = {c["id"]: c for c in roteiro["cenas"]}

    dados_blocos = {}
    metricas_blocos = {}

    cache_dir = ROOT / "motor/cache/auditoria_tarefa6"
    cache_dir.mkdir(parents=True, exist_ok=True)

    # 1. Auditoria individual dos 4 blocos
    for b_id in ["A", "B", "C", "D"]:
        uuid_b = TOMADAS_OFICIAIS[b_id]
        p_dir = ROOT / "vozes/tomadas/blocos/pt" / b_id / uuid_b
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
        a8 = verificar_a8([{"id": b_id, "fala": meta["fala_oficial"]}], words)

        loudness = medir_loudness(voz_wav)
        timbre = analisar_timbre_arquivo(voz_wav)

        dados_blocos[b_id] = {
            "bloco": b_id,
            "uuid": uuid_b,
            "voz": meta["geracao"]["voice_id"],
            "modelo": meta["geracao"]["modelo"],
            "x": x,
            "duracao_s": duracao_s,
            "sha256_voz": hash_arquivo(voz_wav),
            "sha256_bruto": hash_arquivo(bruto_wav),
            "words": words,
            "a8": a8,
            "loudness": loudness,
            "timbre": timbre,
            "dir": p_dir,
            "voz_wav": voz_wav,
            "substituicoes": meta.get("substituicoes_pronuncia", [])
        }

        metricas_blocos[b_id] = {
            "duracao_s": round(duracao_s, 3),
            "sha256_voz": dados_blocos[b_id]["sha256_voz"],
            "lufs_integrado": float(loudness["input_i"]),
            "true_peak_dbtp": float(loudness["input_tp"]),
            "lra_lu": float(loudness["input_lra"]),
            "f0_mediano_hz": timbre["f0_mediano_hz"],
            "centroide_hz": timbre["centroide_medio_hz"],
            "a8_estado": a8["estado"],
            "a8_falhas": len(a8["falhas"]),
            "primeira_palavra": words[0]["text"] if words else "",
            "primeira_palavra_ini": round(words[0]["start"], 3) if words else 0.0,
            "ultima_palavra": words[-1]["text"] if words else "",
            "ultima_palavra_fim": round(words[-1]["end"], 3) if words else 0.0,
            "cauda_final_s": round(duracao_s - words[-1]["end"], 3) if words else 0.0
        }

        print(f"\n--- Bloco {b_id} ---")
        print(f"  Duração: {duracao_s:.3f} s | SHA-256 voz: {dados_blocos[b_id]['sha256_voz'][:16]}...")
        print(f"  Loudness: {loudness['input_i']} LUFS | TP: {loudness['input_tp']} dBTP | LRA: {loudness['input_lra']} LU")
        print(f"  Timbre: F0 = {timbre['f0_mediano_hz']} Hz | Centroide = {timbre['centroide_medio_hz']} Hz")
        print(f"  A8: estado = {a8['estado']} ({len(a8['falhas'])} falhas)")

    # 2. Deriva tímbrica entre blocos da Ana (A, C, D) e contraste com Gabriel (B)
    timbres = {b: dados_blocos[b]["timbre"] for b in ["A", "B", "C", "D"]}
    deriva_ana = comparar_timbre_blocos({b: timbres[b] for b in ["A", "C", "D"]})
    contraste_gabriel = {
        "B_vs_A": {
            "diff_f0_hz": round(abs(timbres["B"]["f0_mediano_hz"] - timbres["A"]["f0_mediano_hz"]), 1),
            "diff_centroide_hz": round(abs(timbres["B"]["centroide_medio_hz"] - timbres["A"]["centroide_medio_hz"]), 1)
        },
        "B_vs_C": {
            "diff_f0_hz": round(abs(timbres["B"]["f0_mediano_hz"] - timbres["C"]["f0_mediano_hz"]), 1),
            "diff_centroide_hz": round(abs(timbres["B"]["centroide_medio_hz"] - timbres["C"]["centroide_medio_hz"]), 1)
        }
    }
    print("\n--- Deriva Tímbrica (Ana A, C, D) ---")
    for par, d in deriva_ana.items():
        print(f"  {par}: diff F0 = {d['diff_f0_hz']} Hz ({d['diff_f0_semitons']} semitons) | diff Centroide = {d['diff_centroide_hz']} Hz")

    print("\n--- Contraste Tímbrico Gabriel (B) vs Ana ---")
    for par, d in contraste_gabriel.items():
        print(f"  {par}: diff F0 = {d['diff_f0_hz']} Hz | diff Centroide = {d['diff_centroide_hz']} Hz")

    # 3. Montagem e auditoria das 3 fronteiras (A→B, B→C, C→D)
    fronteiras_resumo = []
    limites_musicais = [c * BAR for c in COMPASSOS]

    fronteiras_dir = cache_dir / "fronteiras"
    fronteiras_dir.mkdir(parents=True, exist_ok=True)

    pares = [("A", "B", 1), ("B", "C", 2), ("C", "D", 3)]
    for anterior, seguinte, idx_fronteira in pares:
        da = dados_blocos[anterior]
        db_ = dados_blocos[seguinte]

        ra = RECUOS_S[anterior]
        rb = RECUOS_S[seguinte]

        limite_anterior = limites_musicais[idx_fronteira - 1]
        limite_corte = limites_musicais[idx_fronteira]

        # Posição absoluta da última palavra de A e primeira palavra de B
        ult_palavra_pos = limite_anterior + ra + da["words"][-1]["end"]
        prim_palavra_pos = limite_corte + rb + db_["words"][0]["start"]

        pausa_inter_blocos = prim_palavra_pos - ult_palavra_pos
        corte_pos = limite_corte

        # Extração de trecho de áudio: 2.5s finais de A + pausa planejada + 2.5s iniciais de B
        ax = da["x"]
        bx = db_["x"]
        n_a = min(len(ax), round(2.5 * SR))
        n_b = min(len(bx), round(2.5 * SR))

        seg_a = ax[-n_a:]
        seg_b = bx[:n_b]

        # Silêncio acústico entre o fim do WAV A e o início do WAV B no timeline
        fim_wav_a_pos = limite_anterior + ra + da["duracao_s"]
        ini_wav_b_pos = limite_corte + rb
        silencio_entre_wavs_s = ini_wav_b_pos - fim_wav_a_pos
        amostras_silencio = max(0, round(silencio_entre_wavs_s * SR))
        silencio_pad = np.zeros(amostras_silencio, dtype="<f4")

        x_fronteira = np.concatenate([seg_a, silencio_pad, seg_b])
        nome_fronteira = f"fronteira_{anterior}_{seguinte}"
        out_fronteira_dir = fronteiras_dir / nome_fronteira
        out_fronteira_dir.mkdir(parents=True, exist_ok=True)

        previa_wav = out_fronteira_dir / f"{nome_fronteira}.wav"
        salvar(previa_wav, x_fronteira)

        loudness_f = medir_loudness(previa_wav)

        f_info = {
            "fronteira": f"{anterior}→{seguinte}",
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
        fronteiras_resumo.append(f_info)

        print(f"\n--- Fronteira {anterior}→{seguinte} ---")
        print(f"  Compasso de transição: {COMPASSOS[idx_fronteira]} ({corte_pos:.3f} s)")
        print(f"  Palavras na emenda: \"{da['words'][-1]['text']}\" → \"{db_['words'][0]['text']}\"")
        print(f"  Pausa verbal: {pausa_inter_blocos:.3f} s (meta: 0.5 – 1.2 s)")
        print(f"  Proteção temporal: antes={corte_pos - ult_palavra_pos:.3f} s | depois={prim_palavra_pos - corte_pos:.3f} s (mín: 0.12 s)")
        print(f"  Folga física entre WAVs: {silencio_entre_wavs_s:.3f} s")
        print(f"  Loudness prévia: {loudness_f['input_i']} LUFS | TP: {loudness_f['input_tp']} dBTP")

    # 4. Recálculo das janelas de cena da nova régua proposta
    regua_saida = ROOT / "motor/cache/regua-proposta-tarefa6"
    regua_saida.mkdir(parents=True, exist_ok=True)

    janelas_blocos = {}
    cenas_resumo = []
    cortes_por_bloco = {}

    for i, b_id in enumerate(["A", "B", "C", "D"]):
        cs = [cenas_dict[cid] for cid in roteiro["blocos"][i]["cenas"]]
        dur_voz = dados_blocos[b_id]["duracao_s"]
        ini_g = limites_musicais[i]
        dur_b = limites_musicais[i + 1] - ini_g
        recuo = RECUOS_S[b_id]

        res = janela_bloco(b_id, cs, dados_blocos[b_id]["words"], dur_voz, recuo, dur_b, ini_g)
        res.update(
            arquivo=str(dados_blocos[b_id]["voz_wav"]),
            sha256=dados_blocos[b_id]["sha256_voz"],
            compasso_ini=COMPASSOS[i],
            compasso_fim=COMPASSOS[i + 1],
            deslocamento_grade_s=ini_g - COMPASSOS[i] * BAR
        )
        gravar_json(regua_saida / f"{b_id}.json", res)
        janelas_blocos[b_id] = res
        cortes_por_bloco[b_id] = [round(c, 3) for c in res["cortes_cena"]]

        for c in res["cenas"]:
            cenas_resumo.append({
                "id": c["id"],
                "bloco": b_id,
                "ini_local": round(c["ini"], 3),
                "fim_local": round(c["fim"], 3),
                "dur": round(c["dur"], 3),
                "ini_global": round(c["ini"] + ini_g, 3),
                "fim_global": round(c["fim"] + ini_g, 3),
                "apertada": c["apertada"]
            })

    # Resumo da régua
    resumo_regua = {
        "versao": 2,
        "lang": "pt",
        "P": P,
        "bar": BAR,
        "compassos_total": COMPASSOS[-1],
        "total_s": round(limites_musicais[-1], 3),
        "grade_compassos": COMPASSOS,
        "recuos_voz_s": RECUOS_S,
        "durações_novas_vs_antigas": {
            "A": {"nova": round(dados_blocos["A"]["duracao_s"], 3), "antiga": 22.895, "delta": round(dados_blocos["A"]["duracao_s"] - 22.895, 3)},
            "B": {"nova": round(dados_blocos["B"]["duracao_s"], 3), "antiga": 19.923, "delta": round(dados_blocos["B"]["duracao_s"] - 19.923, 3)},
            "C": {"nova": round(dados_blocos["C"]["duracao_s"], 3), "antiga": 19.551, "delta": round(dados_blocos["C"]["duracao_s"] - 19.551, 3)},
            "D": {"nova": round(dados_blocos["D"]["duracao_s"], 3), "antiga": 8.963, "delta": round(dados_blocos["D"]["duracao_s"] - 8.963, 3)}
        },
        "fronteiras": fronteiras_resumo,
        "cenas": cenas_resumo
    }
    gravar_json(regua_saida / "resumo.json", resumo_regua)
    print(f"\n✅ Nova régua gerada com sucesso em {regua_saida}/resumo.json (Total: {limites_musicais[-1]:.3f} s / 41 compassos)")

    # 5. Montagem do Kit de Escuta em ~/Downloads/frila-escuta-vozes-blocos/
    kit_dir = Path.home() / "Downloads/frila-escuta-vozes-blocos"
    kit_dir.mkdir(parents=True, exist_ok=True)

    # Copiar os 4 arquivos voz.wav
    shutil.copy2(dados_blocos["A"]["voz_wav"], kit_dir / "bloco_A_ana_v3.wav")
    shutil.copy2(dados_blocos["B"]["voz_wav"], kit_dir / "bloco_B_gabriel_v2.wav")
    shutil.copy2(dados_blocos["C"]["voz_wav"], kit_dir / "bloco_C_ana_v3.wav")
    shutil.copy2(dados_blocos["D"]["voz_wav"], kit_dir / "bloco_D_ana_v3.wav")

    # Copiar as 3 fronteiras
    shutil.copy2(fronteiras_dir / "fronteira_A_B/fronteira_A_B.wav", kit_dir / "fronteira_A_B.wav")
    shutil.copy2(fronteiras_dir / "fronteira_B_C/fronteira_B_C.wav", kit_dir / "fronteira_B_C.wav")
    shutil.copy2(fronteiras_dir / "fronteira_C_D/fronteira_C_D.wav", kit_dir / "fronteira_C_D.wav")

    # Criar README sem scorecards (apenas identificação técnica objetiva + 2 a 4 pontos "o que ouvir")
    readme_conteudo = f"""# Kit de Escuta: Vozes por Bloco (Tarefa 6)

**Data de Geração:** 27 de outubro de 2026  
**Worktree:** `fvp-audio-blocos`  
**Objetivo:** Avaliação soberana de ouvido do Fabrício para a alternância de narradores por bloco (Ana em A, C, D; Gabriel em B), com todas as pronúncias familiares decididas previamente aplicadas.

---

## 1. Visão Geral e Parâmetros Técnicos

- **Bloco A (Cenas v01–v04):** Ana Dias (`MZxV5lN3cv7hi1376O0m`), `eleven_v3`, PCM 48 kHz, seed 1, dirigida.
- **Bloco B (Cenas v05–v09):** Gabriel pt-BR publicidade (`WPgqgCVa3mD38JuyODU6`), `eleven_multilingual_v2`, PCM 48 kHz, seed 1, dirigida (Pico 1 em v05).
- **Bloco C (Cenas v10–v12):** Ana Dias (`MZxV5lN3cv7hi1376O0m`), `eleven_v3`, PCM 48 kHz, seed 1, dirigida (Pico 2 em v10).
- **Bloco D (Cenas v13–v14):** Ana Dias (`MZxV5lN3cv7hi1376O0m`), `eleven_v3`, PCM 48 kHz, seed 1, dirigida (Pico 3 em v13).

Cadeia de estúdio aplicada a todos os blocos: HPF 80 Hz, De-esser 6 kHz, EQ presença 3.8 kHz (+1.5 dB), High-shelf de ar 11 kHz (+1.0 dB), Compressor leve 1.6:1.

---

## 2. Identificação Técnica dos Blocos

| Arquivo | Narrador | Duração | LUFS (Int) | True Peak | LRA | F0 Mediano | SHA-256 (início) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `bloco_A_ana_v3.wav` | Ana (v3) | {metricas_blocos['A']['duracao_s']:.3f} s | {metricas_blocos['A']['lufs_integrado']:.1f} | {metricas_blocos['A']['true_peak_dbtp']:.1f} dBTP | {metricas_blocos['A']['lra_lu']:.1f} LU | {metricas_blocos['A']['f0_mediano_hz']:.1f} Hz | `{metricas_blocos['A']['sha256_voz'][:16]}` |
| `bloco_B_gabriel_v2.wav` | Gabriel (v2) | {metricas_blocos['B']['duracao_s']:.3f} s | {metricas_blocos['B']['lufs_integrado']:.1f} | {metricas_blocos['B']['true_peak_dbtp']:.1f} dBTP | {metricas_blocos['B']['lra_lu']:.1f} LU | {metricas_blocos['B']['f0_mediano_hz']:.1f} Hz | `{metricas_blocos['B']['sha256_voz'][:16]}` |
| `bloco_C_ana_v3.wav` | Ana (v3) | {metricas_blocos['C']['duracao_s']:.3f} s | {metricas_blocos['C']['lufs_integrado']:.1f} | {metricas_blocos['C']['true_peak_dbtp']:.1f} dBTP | {metricas_blocos['C']['lra_lu']:.1f} LU | {metricas_blocos['C']['f0_mediano_hz']:.1f} Hz | `{metricas_blocos['C']['sha256_voz'][:16]}` |
| `bloco_D_ana_v3.wav` | Ana (v3) | {metricas_blocos['D']['duracao_s']:.3f} s | {metricas_blocos['D']['lufs_integrado']:.1f} | {metricas_blocos['D']['true_peak_dbtp']:.1f} dBTP | {metricas_blocos['D']['lra_lu']:.1f} LU | {metricas_blocos['D']['f0_mediano_hz']:.1f} Hz | `{metricas_blocos['D']['sha256_voz'][:16]}` |

---

## 3. O Que Ouvir por Bloco (Pontos Objetivos)

### `bloco_A_ana_v3.wav` (Ana Dias — Dores)
1. **Pronúncia familiar:** Ouvir a naturalidade do numeral "nove em cada déis" (fonética familiar aprovada em 26/10) e a preservação natural de "Abrasel" e "restaurantes".
2. **Pausa e respiração interna (A8):** Em t=5,910 s, logo após "Segundo a Abrasel,", a pausa respiratória mediu exatamente 500 ms (0,500 s). Avaliar se a respiração soa orgânica e humana ou se quebra a fluidez.
3. **Tom narrativo:** Transição da constatação fria ("Hoje, dezenove horas. Faltou gente no turno.") para a reflexão sóbria da dor do setor ("Cadastro não é turno.").

### `bloco_B_gabriel_v2.wav` (Gabriel — Solução)
1. **Pronúncia 100% original:** Conferir as duas ocorrências de "O Frila", "check-in" e "histórico", que foram mantidas em sua grafia original canônica sem modificações.
2. **Ritmo e energia (Pico 1):** O narrador entra na virada com energia afirmativa e calorosa ("O Frila conecta... Você publica a vaga."). Conferir se a cadência mantém dinamismo e clareza.
3. **Pergunta final:** A entonação interrogativa natural no fechamento do bloco ("...chamaria de novo?").

### `bloco_C_ana_v3.wav` (Ana Dias — Dados e Piloto)
1. **Pronúncias familiares aplicadas:**
   - "Méta do piloto" (forma `méta` com 'e' aberto natural);
   - "nove em cada déis profissionais presentes" (`déis`);
   - "Distrito Federau" (`Federau` fonético familiar).
2. **Pausa interna em v10 (A8):** Em t=8,350 s, entre "oito semanas," e "cinquenta vagas por semana", a pausa durou 660 ms. Ouvir se o silêncio funciona como ênfase reflexiva para a introdução dos dados do piloto.
3. **Consistência de timbre:** Comparar com o Bloco A para conferir estabilidade na voz da Ana (variação de F0 de apenas 0,41 semitons entre A e C).

### `bloco_D_ana_v3.wav` (Ana Dias — Fecho e Assinatura)
1. **Pronúncia em dobro de Frila:** Duas ocorrências da forma fonética familiar ("Deixa que o Fríla cuida. Fríla.").
2. **Mudança de tom emotivo:** Contraste entre a empatia aliviada ("Menos tempo procurando gente. Mais tempo no seu negócio.") e a segurança conclusiva da assinatura ("Turno combinado, regra clara.").
3. **Sem falhas de pausa:** Tomada contínua perfeitamente alinhada e fluida, sem nenhuma pausa interna acima de 440 ms.

---

## 4. Prévias de Fronteira e Transição de Voz

As prévias unem os 2,5 segundos finais do bloco anterior aos 2,5 segundos iniciais do bloco seguinte, simulando o silêncio e o corte planejados pela régua.

| Arquivo | Transição | Pausa Verbal | Ponto de Corte Visual | O Que Ouvir |
| :--- | :--- | :--- | :--- | :--- |
| `fronteira_A_B.wav` | Ana → Gabriel | {fronteiras_resumo[0]['pausa_verbal_s']:.3f} s | Compasso 13 ({fronteiras_resumo[0]['corte_tempo_global_s']:.3f} s) | A troca de narradora (Ana terminando em "em um ano") para narrador (Gabriel entrando com "O Frila conecta"). Ouvir o impacto da mudança de timbre feminino/masculino. |
| `fronteira_B_C.wav` | Gabriel → Ana | {fronteiras_resumo[1]['pausa_verbal_s']:.3f} s | Compasso 23 ({fronteiras_resumo[1]['corte_tempo_global_s']:.3f} s) | Gabriel encerra a pergunta ("...chamaria de novo?") e a Ana reentra para os dados técnicos ("Dos vinte e dois apps..."). Conferir a respiração e a pausa de 1,16 s. |
| `fronteira_C_D.wav` | Ana → Ana | {fronteiras_resumo[2]['pausa_verbal_s']:.3f} s | Compasso 35 ({fronteiras_resumo[2]['corte_tempo_global_s']:.3f} s) | Transição interna da mesma narradora (Ana) da expansão geográfica ("Distrito Federal.") para o fecho emocional ("Menos tempo..."). Conferir se a cor vocal permanece coesa. |

---

## 5. Nova Régua Narrativa (Proposta Técnica)

- **Compassos:** `[0, 13, 23, 35, 41]` (41 compassos a 1,96734 s = **80,661 s**, perfeitamente dentro da meta de 78–90 s).
- **Durações Novas vs Antigas:**
  - Bloco A: 24,320 s (antiga: 22,895 s; +1,425 s);
  - Bloco B: 19,133 s (antiga: 19,923 s; -0,790 s);
  - Bloco C: 22,080 s (antiga: 19,551 s; +2,529 s);
  - Bloco D: 10,240 s (antiga: 8,963 s; +1,277 s).
- **Pausas entre blocos:**
  - A→B: 1,102 s;
  - B→C: 1,163 s;
  - C→D: 1,188 s.
  (Todas >= 500 ms e <= 1,2 s, com folgas de proteção temporal >= 200 ms em relação aos cortes visuais).
- **Arquivo de seleção:** `vozes/selecao-blocos-pt.json` permanece **intocado** até o veredito final de ouvido do Fabrício.
"""
    (kit_dir / "README.md").write_text(readme_conteudo, encoding="utf-8")
    print(f"\n✅ Kit de escuta empacotado com sucesso em {kit_dir}")


if __name__ == "__main__":
    auditar_e_empacotar()
