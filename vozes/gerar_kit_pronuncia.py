"""Geração do Kit de Escuta de Pronúncia (Tarefa 6 - Diretriz do Fabrício).
Testa palavras de risco nas duas vozes (Ana v3 e Gabriel v2) em frases-veículo curtas.
Gera original e candidata, aplica cadeia de estúdio offline, afere Scribe e copia para ~/Downloads/frila-escuta-pronuncia/.
"""
import json
import os
import pathlib
import shutil
import subprocess
import sys
import wave

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from motor.audio_util import SR, db, gravar_json, hash_arquivo, ler, medir_loudness
from vozes.eleven import API, chave, chamar, multipart
from vozes.estudio import cadeia_estudio

DESTINO_DOWNLOADS = pathlib.Path.home() / "Downloads/frila-escuta-pronuncia"
CACHE_DIR = ROOT / "motor/cache/kit-pronuncia"

# Parâmetros oficiais aprovados para cada voz
VOZES_CONFIG = {
    "ana": {
        "nome": "Ana Dias",
        "voice_id": "MZxV5lN3cv7hi1376O0m",
        "modelo": "eleven_v3",
        "formato": "pcm_48000",
        "seed": 1,
        "settings": {"stability": 0.5},
        "contexto": {}
    },
    "gabriel": {
        "nome": "Gabriel pt-BR publicidade",
        "voice_id": "WPgqgCVa3mD38JuyODU6",
        "modelo": "eleven_multilingual_v2",
        "formato": "pcm_48000",
        "seed": 1,
        "settings": {
            "stability": 0.45,
            "similarity_boost": 0.75,
            "style": 0.22,
            "speed": 0.98,
            "use_speaker_boost": True
        },
        "contexto": {}
    }
}

ITENS_PRONUNCIA = [
    {
        "id": "frila",
        "palavra": "Frila",
        "categoria": "P1 Marca / Termo",
        "pontos": [
            "Tônica na primeira sílaba ('Frí-la') vs oxítona ('Fri-lá').",
            "Não soar como leitura inglesa ('fraila') nem 'freela' abafado.",
            "Clareza e naturalidade do 'ri' no português brasileiro."
        ],
        "variantes": [
            {"tipo": "original", "forma": "Frila", "texto": "O Frila conecta."},
            {"tipo": "candidata", "forma": "Fríla", "texto": "O Fríla conecta."}
        ]
    },
    {
        "id": "checkin",
        "palavra": "check-in",
        "categoria": "P1 Estrangeirismo",
        "pontos": [
            "Pronúncia nativa brasileira ('tchéquin') vs anglicismo truncado.",
            "Final nasalizado suave ('-in'/'-im') vs oclusiva surda dura.",
            "Integração rítmica natural na locução rápida."
        ],
        "variantes": [
            {"tipo": "original", "forma": "check-in", "texto": "Faz o check-in."},
            {"tipo": "candidata", "forma": "tchéquin", "texto": "Faz o tchéquin."}
        ]
    },
    {
        "id": "abrasel",
        "palavra": "Abrasel",
        "categoria": "P1 Sigla / Setor",
        "pontos": [
            "'S' intervocálico sonoro (/z/) vs chiado ou /s/ surdo.",
            "Terminação '-el' vocalizada em /w/ brasileiro ('-éu') vs lateral europeia (-eL).",
            "Peso institucional e autoridade na dicção factual."
        ],
        "variantes": [
            {"tipo": "original", "forma": "Abrasel", "texto": "Segundo a Abrasel."},
            {"tipo": "candidata", "forma": "Abrazéu", "texto": "Segundo a Abrazéu."}
        ]
    },
    {
        "id": "meta_piloto",
        "palavra": "meta / piloto",
        "categoria": "P1 Editorial / Termo",
        "pontos": [
            "Vogal 'e' aberta (/ˈmɛ.tɐ/) vs fechada (/ˈme.tɐ/) ou emenda como 'método'.",
            "Paroxítona firme em 'piloto' sem cair em 'pilotó'.",
            "Ritmo métrico limpo entre substantivo e complemento."
        ],
        "variantes": [
            {"tipo": "original", "forma": "Meta do piloto", "texto": "Meta do piloto."},
            {"tipo": "candidata", "forma": "Méta do piloto", "texto": "Méta do piloto."}
        ]
    },
    {
        "id": "dezenove",
        "palavra": "dezenove",
        "categoria": "P1 Números",
        "pontos": [
            "Tônica aberta no penúltimo 'o' (/de.zeˈnɔ.vi/) sem abafamento.",
            "Transição limpa para a palavra 'horas'.",
            "Precisão temporal e clareza da urgência."
        ],
        "variantes": [
            {"tipo": "original", "forma": "dezenove", "texto": "Dezenove horas."},
            {"tipo": "candidata", "forma": "dezenóve", "texto": "Dezenóve horas."}
        ]
    },
    {
        "id": "cinquenta",
        "palavra": "cinquenta",
        "categoria": "P1 Números",
        "pontos": [
            "Clareza do ditongo nasal com semivogal 'u' (/sĩˈkwẽ.tɐ/).",
            "Ausência de corte em 'cin-quen' ou oclusão /k/ excessivamente dura.",
            "Articulação inteligível da meta numérica."
        ],
        "variantes": [
            {"tipo": "original", "forma": "cinquenta", "texto": "Cinquenta vagas."},
            {"tipo": "candidata", "forma": "cinkuenta", "texto": "Cinkuenta vagas."}
        ]
    },
    {
        "id": "dez",
        "palavra": "dez",
        "categoria": "P1 Números",
        "pontos": [
            "Abertura da vogal /dɛs/ sem fechar em monotongo /dez/ abafado.",
            "Final de frase com apoio firme sem perda de volume.",
            "Soar natural em contexto de métrica estatística."
        ],
        "variantes": [
            {"tipo": "original", "forma": "dez", "texto": "Nove em cada dez."},
            {"tipo": "candidata", "forma": "déis", "texto": "Nove em cada déis."}
        ]
    },
    {
        "id": "federal",
        "palavra": "Federal",
        "categoria": "P2 Terminações",
        "pontos": [
            "'L' final vocalizado em /w/ ('-au') padrão brasileiro vs lateral consonantal.",
            "'S' de coda em 'Distrito' limpo (/s/) sem chiado regional (/ʃ/).",
            "Gravidade e fechamento geográfico institucional."
        ],
        "variantes": [
            {"tipo": "original", "forma": "Federal", "texto": "Distrito Federal."},
            {"tipo": "candidata", "forma": "Federau", "texto": "Distrito Federau."}
        ]
    },
    {
        "id": "cuida",
        "palavra": "cuida",
        "categoria": "P2 Terminações / Fecho",
        "pontos": [
            "Ditongo decrescente /ˈkuj.dɐ/ sem separação em hiato 'cu-í-da'.",
            "Calor e acolhimento emocional no fecho da promessa.",
            "Apoio vocal suave e sem decaimento brusco."
        ],
        "variantes": [
            {"tipo": "original", "forma": "cuida", "texto": "O Frila cuida."},
            {"tipo": "candidata", "forma": "cúida", "texto": "O Frila cúida."}
        ]
    },
    {
        "id": "comparecimento",
        "palavra": "comparecimento",
        "categoria": "P2 Palavra Longa",
        "pontos": [
            "Tônica na sílaba 'men' sem deslocamento para o início ou final.",
            "Articulação inteligível das 6 sílabas sem atropelo rítmico.",
            "Ênfase na palavra de prova e métrica."
        ],
        "variantes": [
            {"tipo": "original", "forma": "comparecimento", "texto": "Comparecimento medido."},
            {"tipo": "candidata", "forma": "com-pa-re-ci-men-to", "texto": "Com-pa-re-ci-men-to medido."}
        ]
    },
    {
        "id": "rotatividade",
        "palavra": "rotatividade",
        "categoria": "P2 Palavra Longa",
        "pontos": [
            "Ataque no 'r' inicial vibrante sem aspiração excessiva.",
            "Terminação '-dade' limpa no português neutro sem virar '-dadi' arrastado.",
            "Gravidade e clareza do problema de mercado."
        ],
        "variantes": [
            {"tipo": "original", "forma": "rotatividade", "texto": "Alta rotatividade."}
        ]
    },
    {
        "id": "negocio",
        "palavra": "negócio",
        "categoria": "P2 Terminações",
        "pontos": [
            "Ditongo final '-cio' fluido sem fragmentação em três sílabas separadas.",
            "Abertura correta da vogal tônica 'ó'.",
            "Tom próximo e convidativo ao empresário."
        ],
        "variantes": [
            {"tipo": "original", "forma": "negócio", "texto": "No seu negócio."}
        ]
    },
    {
        "id": "historico",
        "palavra": "histórico",
        "categoria": "P2 's' de coda",
        "pontos": [
            "'S' de coda na sílaba 'his' estritamente neutro (/s/) sem sibilância chiada (/ʃ/).",
            "Tônica limpa na proparoxítona.",
            "Dicção fluida de produto."
        ],
        "variantes": [
            {"tipo": "original", "forma": "histórico", "texto": "Vê o histórico."}
        ]
    },
    {
        "id": "restaurantes",
        "palavra": "restaurantes",
        "categoria": "P2 's' de coda",
        "pontos": [
            "'S' de coda medial em 'res-' e plural final em '-tes' limpos (/s/).",
            "Ausência de sotaque carioca ou regionalizado no chiado.",
            "Sonoridade editorial comercial."
        ],
        "variantes": [
            {"tipo": "original", "forma": "restaurantes", "texto": "Bares e restaurantes."}
        ]
    }
]

def pcm48_para_wav(pcm, destino):
    with wave.open(str(destino), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(48000)
        w.writeframes(pcm)

def gerar_kit():
    DESTINO_DOWNLOADS.mkdir(parents=True, exist_ok=True)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    saldo_antes = json.loads(chamar("/v1/user/subscription"))
    chars_antes = saldo_antes['character_count']
    limite = saldo_antes['character_limit']
    print(f"=== INÍCIO DO KIT DE PRONÚNCIA ===")
    print(f"Saldo ElevenLabs antes: {chars_antes} de {limite} caracteres usados.")

    relatorio_geral = []
    chars_totais_enviados = 0

    for item in ITENS_PRONUNCIA:
        print(f"\n--- Testando [{item['categoria']}] {item['palavra']} ---")
        for var in item['variantes']:
            for chave_voz in ["ana", "gabriel"]:
                v_cfg = VOZES_CONFIG[chave_voz]
                nome_base = f"{chave_voz}_{item['id']}_{var['tipo']}"
                dir_cache = CACHE_DIR / nome_base
                dir_cache.mkdir(parents=True, exist_ok=True)
                
                bruto_wav = dir_cache / "bruto.wav"
                voz_wav = dir_cache / "voz.wav"
                scribe_json_path = dir_cache / "scribe.json"
                
                texto_envio = var['texto']
                chars_totais_enviados += len(texto_envio)
                
                print(f"[{nome_base}] Sintetizando ({len(texto_envio)} chars): '{texto_envio}' com {v_cfg['nome']}...")
                payload = {
                    "text": texto_envio,
                    "model_id": v_cfg["modelo"],
                    "language_code": "pt",
                    "seed": v_cfg["seed"],
                    "voice_settings": v_cfg["settings"]
                }
                endpoint = f"/v1/text-to-speech/{v_cfg['voice_id']}?output_format=pcm_48000"
                pcm = chamar(endpoint, payload)
                if not pcm or len(pcm) % 2:
                    raise ValueError(f"Falha ao sintetizar {nome_base}: PCM inválido")
                    
                pcm48_para_wav(pcm, bruto_wav)
                duracao_s = len(pcm) / (48000 * 2)
                
                # Aplica cadeia de estúdio não destrutiva
                cadeia_estudio(bruto_wav, voz_wav)
                
                # Transcrição via Scribe para registrar o que a máquina ouve
                scribe_resp = json.loads(chamar('/v1/speech-to-text', multipart=multipart(
                    {'model_id': 'scribe_v2', 'language_code': 'por', 'timestamps_granularity': 'word'}, voz_wav)))
                scribe_json_path.write_text(json.dumps(scribe_resp, ensure_ascii=False, indent=2))
                scribe_ouviu = scribe_resp.get("text", "").strip()
                
                # Medição objetiva de loudness
                loud = medir_loudness(voz_wav)
                lufs = round(float(loud['input_i']), 2)
                tp = round(float(loud['input_tp']), 2)
                
                # Copiar para Downloads com identificação clara
                destino_final = DESTINO_DOWNLOADS / f"{nome_base}.wav"
                shutil.copyfile(voz_wav, destino_final)
                
                registro = {
                    "arquivo": f"{nome_base}.wav",
                    "caminho": str(destino_final),
                    "voz": chave_voz,
                    "nome_voz": v_cfg['nome'],
                    "modelo": v_cfg['modelo'],
                    "item_id": item['id'],
                    "palavra": item['palavra'],
                    "categoria": item['categoria'],
                    "tipo": var['tipo'],
                    "forma": var['forma'],
                    "texto_enviado": texto_envio,
                    "duracao_s": round(duracao_s, 3),
                    "lufs": lufs,
                    "true_peak": tp,
                    "scribe_ouviu": scribe_ouviu,
                    "pontos": item['pontos'],
                    "sha256": hash_arquivo(destino_final)
                }
                relatorio_geral.append(registro)
                print(f"  -> Concluído: {destino_final.name} | Scribe ouviu: '{scribe_ouviu}' | {lufs} LUFS, {tp} dBTP")

    saldo_depois = json.loads(chamar("/v1/user/subscription"))
    chars_depois = saldo_depois['character_count']
    delta_real = chars_depois - chars_antes
    print(f"\n=== KIT DE PRONÚNCIA FINALIZADO ===")
    print(f"Saldo ElevenLabs depois: {chars_depois} de {limite} caracteres usados.")
    print(f"Consumo medido da rodada: {delta_real} caracteres (texto enviado: {chars_totais_enviados} caracteres).")

    # Gravar relatório JSON no cache
    gravar_json(CACHE_DIR / "relatorio_pronuncia.json", {
        "saldo_antes": chars_antes,
        "saldo_depois": chars_depois,
        "delta_consumo": delta_real,
        "total_ativos": len(relatorio_geral),
        "ativos": relatorio_geral
    })

    # Gerar README.md no diretório de Downloads em formato livre, sem scorecards
    gerar_readme_downloads(relatorio_geral, delta_real, chars_antes, chars_depois)

def gerar_readme_downloads(ativos, delta_consumo, chars_antes, chars_depois):
    readme_path = DESTINO_DOWNLOADS / "README.md"
    
    linhas = []
    linhas.append("# Kit de Escuta de Pronúncia — Frila Vídeo Pitch")
    linhas.append("")
    linhas.append("**Decisão do Fabrício (26/10/2026):** escuta prévia e escolha da forma que soa mais familiar e neutra no português do Brasil, antes da geração final dos blocos.")
    linhas.append("")
    linhas.append("## Informações Técnicas e Contabilidade")
    linhas.append(f"- **Diretório dos ativos:** `{DESTINO_DOWNLOADS}`")
    linhas.append(f"- **Total de amostras geradas:** {len(ativos)} arquivos WAV PCM 48 kHz (cadeia de estúdio aplicada)")
    linhas.append(f"- **Vozes testadas:** Ana Dias (`eleven_v3`, seed 1) e Gabriel pt-BR publicidade (`eleven_multilingual_v2`, seed 1)")
    linhas.append(f"- **Consumo ElevenLabs:** {delta_consumo} caracteres (saldo: {chars_antes} → {chars_depois} de 40.000)")
    linhas.append("- **Avaliação de ouvido:** livre, sem scorecards ou notas numéricas. Selecione qual forma fica para cada palavra.")
    linhas.append("")
    linhas.append("---")
    linhas.append("")

    # Agrupar por palavra
    por_palavra = {}
    for a in ativos:
        por_palavra.setdefault(a['palavra'], []).append(a)

    for palavra, grupo in por_palavra.items():
        primeiro = grupo[0]
        linhas.append(f"### {palavra} ({primeiro['categoria']})")
        linhas.append("**O que ouvir:**")
        for p in primeiro['pontos']:
            linhas.append(f"- {p}")
        linhas.append("")
        linhas.append("| Arquivo | Voz | Variante | Texto Enviado | Scribe Ouviu (Pista) | LUFS / TP | Duração |")
        linhas.append("|---|---|---|---|---|---|---|")
        for item in grupo:
            linhas.append(f"| `{item['arquivo']}` | {item['nome_voz']} | **{item['tipo'].upper()}** (`{item['forma']}`) | \"{item['texto_enviado']}\" | \"{item['scribe_ouviu']}\" | {item['lufs']} LUFS / {item['true_peak']} dBTP | {item['duracao_s']} s |")
        linhas.append("")
        linhas.append("---")
        linhas.append("")

    readme_path.write_text("\n".join(linhas), encoding="utf-8")
    print(f"README.md gravado em: {readme_path}")

if __name__ == "__main__":
    gerar_kit()
