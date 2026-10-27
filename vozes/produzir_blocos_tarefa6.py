"""Produção dos 4 blocos da Tarefa 6 (Ana v3 / Gabriel v2 / Ana v3 / Ana v3).
Orçamento rigoroso, UMA chamada por bloco, verificação A8 e Scribe.

Controles de segurança (PR #27):
- Dry-run por padrão (código 0, sem rede, sem chave);
- Só chama API com --executar E --teto-caracteres <N>;
- Recusa com código 2 se houver termos com status != 'aprovada' em vozes/pronuncia.json;
- Textos dos blocos derivados dinamicamente de roteiro.json via aplicar_pronuncia().
"""
import argparse
import copy
import hashlib
import json
import os
import pathlib
import re
import sys
import uuid
import wave

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from motor.audio_util import SR, db, gravar_json, hash_arquivo, ler, salvar
from motor.analisar_emendas import verificar_a8, validar_palavras, ler_scribe
from vozes.eleven import API, chave, chamar, multipart
from vozes.manifesto import normal, frases_do_roteiro
from vozes.estudio import cadeia_estudio
from vozes.pronuncia import aplicar_pronuncia, carregar_pronuncia
from vozes.deriva_timbre import analisar_timbre_arquivo
from vozes.metrica_chiado import analisar_chiado_tomada

ROTEIRO_PATH = ROOT / "roteiro.json"

# IDs das vozes aprovadas pelo Fabrício em 26/10/2026
VOZ_ANA = "MZxV5lN3cv7hi1376O0m"
VOZ_GABRIEL = "WPgqgCVa3mD38JuyODU6"

CONFIG_MODELOS = {
    "A": {
        "voz": VOZ_ANA,
        "voz_tipo": "ana",
        "modelo": "eleven_v3",
        "settings": {"stability": 0.5},
        "seed": 1,
        "contexto": {},
        "uuid_existente": "5dcbc2883164470aa2d0cb7fbe2b4a44"
    },
    "B": {
        "voz": VOZ_GABRIEL,
        "voz_tipo": "gabriel",
        "modelo": "eleven_multilingual_v2",
        "settings": {
            "stability": 0.45,
            "similarity_boost": 0.75,
            "style": 0.22,
            "speed": 0.98,
            "use_speaker_boost": True,
        },
        "seed": 1,
        "contexto": {
            "previous_text": "Nos bares e restaurantes, a rotatividade passou de setenta por cento em um ano.",
            "next_text": "Dos vinte e dois apps que estudamos, nenhum mostra comparecimento medido.",
        },
        "uuid_existente": "8f28d33d7aa44331ab4b8fccc47cdced"
    },
    "C": {
        "voz": VOZ_ANA,
        "voz_tipo": "ana",
        "modelo": "eleven_v3",
        "settings": {"stability": 0.5},
        "seed": 1,
        "contexto": {},
        "uuid_existente": "fcd0c415fbbd41318b4a4951f89fa4d5"
    },
    "D": {
        "voz": VOZ_ANA,
        "voz_tipo": "ana",
        "modelo": "eleven_v3",
        "settings": {"stability": 0.5},
        "seed": 1,
        "contexto": {},
        "uuid_existente": "e4116cbda2d946b1b5055f61f7d222ca"
    },
}


def pcm48_para_wav(pcm, destino):
    with wave.open(str(destino), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(48000)
        w.writeframes(pcm)


def compor_texto_bloco(cenas):
    """Compõe o texto do bloco a partir das cenas de roteiro.json, aplicando tags de direção."""
    partes = []
    for c in cenas:
        cid = c["id"]
        fala = c["pt"]["fala"].strip()
        if cid == "v03-dor2":
            partes.append(f"[thoughtful] {fala}")
        elif cid == "v13-fecho":
            partes.append("[thoughtful] Menos tempo procurando gente. [happy] Mais tempo no seu negócio. [thoughtful] Deixa que o Frila cuida.")
        else:
            partes.append(fala)
    return " ".join(partes)


def planejar_blocos(roteiro=None, pronuncia_dict=None, blocos_filtro=None, seed=None, forcar_nova_tomada=False):
    """Lê roteiro.json e pronuncia.json para planejar os blocos filtrados e identificar pendências de aprovação."""
    if roteiro is None:
        roteiro = json.loads(ROTEIRO_PATH.read_text(encoding="utf-8"))
    if pronuncia_dict is None:
        pronuncia_dict = carregar_pronuncia()
    if blocos_filtro is None:
        blocos_filtro = ["A", "B", "C", "D"]
    blocos_filtro = [b.strip().upper() for b in blocos_filtro if b.strip()]

    blocos_planejados = {}
    pendencias_bloqueantes = []

    for bloco_id in ["A", "B", "C", "D"]:
        if bloco_id not in blocos_filtro:
            continue
        cfg = copy.deepcopy(CONFIG_MODELOS[bloco_id])
        if seed is not None:
            cfg["seed"] = seed
            cfg["uuid_existente"] = None
        if forcar_nova_tomada:
            cfg["uuid_existente"] = None
        cenas_bloco = [c for c in roteiro["cenas"] if c.get("bloco") == bloco_id]
        fala_oficial = " ".join(c["pt"]["fala"].strip() for c in cenas_bloco)
        texto_direcao_base = compor_texto_bloco(cenas_bloco)
        frases_oficiais = frases_do_roteiro({"cenas": cenas_bloco})

        # Verificar se termos de risco ocorrem nesta fala e qual seu status em pronuncia.json
        for chave_item, dados in pronuncia_dict.items():
            termo = dados.get("termo") or dados.get("palavra") or chave_item
            padrao = r'(?<![\w-])' + re.escape(termo) + r'(?![\w-])'
            if re.search(padrao, fala_oficial, re.IGNORECASE):
                status = dados.get("status", "candidata")
                regra_voz = dados.get("voz", "ambas")
                pertence_a_esta_voz = (regra_voz == "ambas" or regra_voz == cfg["voz_tipo"])
                if pertence_a_esta_voz and status != "aprovada":
                    pendencias_bloqueantes.append({
                        "bloco": bloco_id,
                        "termo": termo,
                        "status": status,
                        "forma": dados.get("forma"),
                        "voz": cfg["voz_tipo"]
                    })

        # Aplicar pronúncias aprovadas sobre o texto de envio
        texto_envio, substituicoes = aplicar_pronuncia(
            texto_direcao_base,
            voz=cfg["voz_tipo"],
            apenas_aprovadas=True,
            dicionario=pronuncia_dict
        )

        blocos_planejados[bloco_id] = {
            "bloco": bloco_id,
            "cenas": [c["id"] for c in cenas_bloco],
            "voz_id": cfg["voz"],
            "voz_tipo": cfg["voz_tipo"],
            "modelo": cfg["modelo"],
            "fala_oficial": fala_oficial,
            "texto_envio": texto_envio,
            "chars_envio": len(texto_envio),
            "substituicoes": substituicoes,
            "frases_oficiais": frases_oficiais,
            "cfg": cfg
        }

    return blocos_planejados, pendencias_bloqueantes


def sintetizar_e_validar_bloco(bloco_info, continuar_apos_falha=False):
    bloco_id = bloco_info["bloco"]
    cfg = bloco_info["cfg"]
    texto_envio = bloco_info["texto_envio"]
    frases_oficiais = bloco_info["frases_oficiais"]

    # Validar A8 preliminar (dois-pontos)
    if ":" in texto_envio:
        raise ValueError(f"Bloco {bloco_id}: violação A8 detectada (dois-pontos no texto de envio)!")

    print(f"\n==========================================")
    print(f"  Sintetizando Bloco {bloco_id} (Voz: {cfg['voz'][:8]}..., Modelo: {cfg['modelo']})")
    print(f"==========================================")
    print(f"Texto a enviar ({len(texto_envio)} chars): {texto_envio}")

    existente_uuid = cfg.get("uuid_existente")
    tomada_dir = None
    if existente_uuid:
        candidato_dir = ROOT / "vozes/tomadas/blocos/pt" / bloco_id / existente_uuid
        if (candidato_dir / "bruto.wav").exists() and (candidato_dir / "scribe.json").exists():
            print(f"Reutilizando tomada existente em {candidato_dir}...")
            tomada_dir = candidato_dir
            bruto_wav = tomada_dir / "bruto.wav"
            scribe_file = tomada_dir / "scribe.json"
            scribe_resp = json.loads(scribe_file.read_text())
            duracao_s = len(ler(bruto_wav, 1)) / SR

    if tomada_dir is None:
        payload = {
            "text": texto_envio,
            "model_id": cfg["modelo"],
            "language_code": "pt",
            "seed": cfg["seed"],
            **cfg["contexto"],
            "voice_settings": cfg["settings"]
        }

        endpoint = f"/v1/text-to-speech/{cfg['voz']}?output_format=pcm_48000"
        pcm = chamar(endpoint, payload)
        if not pcm or len(pcm) % 2:
            raise ValueError(f"Bloco {bloco_id}: PCM retornado vazio ou corrompido!")

        tomada_uuid = uuid.uuid4().hex
        tomada_dir = ROOT / "vozes/tomadas/blocos/pt" / bloco_id / tomada_uuid
        tomada_dir.mkdir(parents=True, exist_ok=True)

        bruto_wav = tomada_dir / "bruto.wav"
        pcm48_para_wav(pcm, bruto_wav)
        duracao_s = len(pcm) / (48000 * 2)
        print(f"✅ Bruto salvo: {bruto_wav} (Duração: {duracao_s:.3f} s)")

        print(f"Transcrevendo com Scribe para validação de integridade e A8...")
        scribe_resp = json.loads(chamar('/v1/speech-to-text', multipart=multipart(
            {'model_id': 'scribe_v2', 'language_code': 'por', 'timestamps_granularity': 'word'}, bruto_wav)))

        scribe_file = tomada_dir / "scribe.json"
        scribe_file.write_text(json.dumps(scribe_resp, ensure_ascii=False, indent=2) + "\n")

    palavras = [w for w in scribe_resp.get('words', []) if w.get('type') == 'word']
    if not palavras:
        raise ValueError(f"Bloco {bloco_id}: Scribe não retornou palavras válidas!")

    texto_scribe = scribe_resp.get('text', '')
    texto_sem_tags = re.sub(r'\[[^\]]+\]\s*', '', texto_envio).strip()
    match_texto = normal(texto_sem_tags) == normal(texto_scribe)
    print(f"Conferência de texto Scribe: {'✅ IDÊNTICO' if match_texto else '⚠️ DIVERGÊNCIA'}")
    if not match_texto:
        print(f"  Esperado: {normal(texto_sem_tags)}")
        print(f"  Scribe:   {normal(texto_scribe)}")
        raise ValueError(f"Bloco {bloco_id}: texto falado diverge do roteiro oficial no Scribe!")

    a8_result = verificar_a8(frases_oficiais, palavras)
    print(f"Regra A8 (pausas internas <= 0,5s): Estado = {a8_result['estado']}")
    if a8_result['falhas']:
        for f in a8_result['falhas']:
            print(f"  🚨 Falha A8: {f['duracao']:.3f} s em t={f['tempo']:.3f} s ({f['tipo']})")
        if not continuar_apos_falha:
            raise ValueError(f"Bloco {bloco_id}: regra A8 violada com {len(a8_result['falhas'])} pausa(s) interna(s) >= 0.500 s!")

    voz_tratada_wav = tomada_dir / "voz.wav"
    recibo_cadeia = cadeia_estudio(bruto_wav, voz_tratada_wav)
    print(f"✅ Cadeia de estúdio aplicada: {voz_tratada_wav} (Ar: {recibo_cadeia['shelf_ar_aplicado']})")

    timbre = analisar_timbre_arquivo(voz_tratada_wav)
    print(f"Métricas tímbricas: F0={timbre.get('f0_mediano_hz')} Hz | Centroide={timbre.get('centroide_medio_hz')} Hz")

    chiado = analisar_chiado_tomada(voz_tratada_wav, palavras)
    print(f"Métrica de chiado: taxa={chiado['taxa_chiado_pct']}% ({chiado['palavras_com_chiado']}/{chiado['total_palavras_analisadas']}) | veredito={chiado['veredito_triagem']} | razão L/C={chiado['razao_mediana_limpo_chiado']}")

    meta = {
        "bloco": bloco_id,
        "fala_oficial": bloco_info["fala_oficial"],
        "texto_enviado": texto_envio,
        "cenas": bloco_info["cenas"],
        "geracao": {
            "voice_id": cfg["voz"],
            "modelo": cfg["modelo"],
            "settings": cfg["settings"],
            "seed": cfg["seed"],
            "contexto": cfg["contexto"],
            "formato": "pcm_48000"
        },
        "cadeia_estudio": recibo_cadeia,
        "timbre": timbre,
        "chiado": chiado,
        "substituicoes_pronuncia": bloco_info["substituicoes"],
        "sha256_bruto": hash_arquivo(bruto_wav),
        "sha256_voz": hash_arquivo(voz_tratada_wav),
        "duracao": duracao_s,
        "palavras": palavras,
        "a8": a8_result,
        "aprovada": False,
        "aprovacao_ouvido": None
    }

    meta_path = tomada_dir / "bruto.json"
    gravar_json(meta_path, meta)

    return {
        "bloco": bloco_id,
        "dir": str(tomada_dir),
        "bruto": str(bruto_wav),
        "voz": str(voz_tratada_wav),
        "duracao": duracao_s,
        "chars": len(texto_envio),
        "timbre": timbre,
        "chiado": chiado,
        "a8": a8_result
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description="Produção dos blocos de locução da Tarefa 6.")
    parser.add_argument("--executar", action="store_true", help="Dispara a geração real contra a API ElevenLabs.")
    parser.add_argument("--teto-caracteres", type=int, default=None, help="Teto obrigatório de caracteres para execução.")
    parser.add_argument("--blocos", default="A,B,C,D", help="Lista de blocos separados por vírgula (ex: A,C,D).")
    parser.add_argument("--seed", type=int, default=None, help="Semente de geração específica para os blocos selecionados.")
    parser.add_argument("--forcar-nova-tomada", action="store_true", help="Gera nova tomada ignorando uuid_existente.")
    parser.add_argument("--continuar-apos-falha", action="store_true", help="Permite prosseguir mesmo se houver falha A8.")
    args = parser.parse_args(argv)

    roteiro = json.loads(ROTEIRO_PATH.read_text(encoding="utf-8"))
    pronuncia_dict = carregar_pronuncia()
    blocos_filtro = [b.strip().upper() for b in args.blocos.split(",") if b.strip()]
    blocos_planejados, pendencias = planejar_blocos(
        roteiro,
        pronuncia_dict,
        blocos_filtro=blocos_filtro,
        seed=args.seed,
        forcar_nova_tomada=args.forcar_nova_tomada
    )

    total_chars_previstos = sum(b["chars_envio"] for b in blocos_planejados.values())

    print("==================================================================")
    print("  Planejamento de Produção de Locução por Bloco (Tarefa 6)")
    print("==================================================================")
    for b_id, b_info in blocos_planejados.items():
        print(f"Bloco {b_id} [{b_info['modelo']}] (Voz: {b_info['voz_tipo']}) | {b_info['chars_envio']} caracteres")
        if b_info["substituicoes"]:
            subs_str = ", ".join(f"{s['original']} -> {s['substituicao']}" for s in b_info["substituicoes"])
            print(f"  Pronúncias aplicadas: {subs_str}")
        print(f"  Texto envio: \"{b_info['texto_envio']}\"")

    print(f"\nTotal previsto para os blocos ({', '.join(blocos_planejados.keys())}): {total_chars_previstos} caracteres.")

    if pendencias:
        print("\n⚠️ AVISO DE TERMOS COM STATUS PENDENTE/NÃO APROVADO:")
        for p in pendencias:
            print(f"  - Bloco {p['bloco']}: termo '{p['termo']}' tem status '{p['status']}' (forma candidata: '{p['forma']}')")

    # MODO 1: DRY-RUN (padrão)
    if not args.executar:
        print("\n[DRY-RUN] Modo informativo por padrão. Nenhuma chamada de rede foi realizada.")
        print("Para sintetizar de fato, use: --executar --teto-caracteres <N>")
        return 0

    # MODO 2: EXECUTAR (validações estritas)
    if args.teto_caracteres is None:
        print("\n🚨 ERRO: A flag --executar exige a definição obrigatória de --teto-caracteres <N>!", file=sys.stderr)
        sys.exit(1)

    if total_chars_previstos > args.teto_caracteres:
        print(f"\n🚨 ERRO: Caracteres previstos ({total_chars_previstos}) excedem o teto fornecido ({args.teto_caracteres})!", file=sys.stderr)
        sys.exit(1)

    if pendencias:
        print("\n🚨 EXECUÇÃO BLOQUEADA (Código 2):", file=sys.stderr)
        print("Existem termos em vozes/pronuncia.json com status diferente de 'aprovada' presentes na fala dos blocos selecionados.", file=sys.stderr)
        print("A produção oficial só pode prosseguir após a aprovação soberana de ouvido do Fabrício.", file=sys.stderr)
        sys.exit(2)

    # Leitura e verificação de saldo da API só no modo --executar
    saldo_antes_data = json.loads(chamar("/v1/user/subscription"))
    caracteres_antes = saldo_antes_data["character_count"]
    limite = saldo_antes_data["character_limit"]
    print(f"\nSaldo ElevenLabs antes: {caracteres_antes} de {limite} caracteres usados.")

    resultados = {}
    for bloco_id in blocos_planejados.keys():
        res = sintetizar_e_validar_bloco(blocos_planejados[bloco_id], continuar_apos_falha=args.continuar_apos_falha)
        resultados[bloco_id] = res

    saldo_depois_data = json.loads(chamar("/v1/user/subscription"))
    caracteres_depois = saldo_depois_data["character_count"]
    delta_tts = caracteres_depois - caracteres_antes

    print(f"\n==========================================")
    print(f"  Todas as 4 tomadas geradas com sucesso!")
    print(f"  Saldo final: {caracteres_depois} de {limite} caracteres usados.")
    print(f"  Consumo adicional nesta rodada: {delta_tts} caracteres.")
    print(f"==========================================")

    out_file = ROOT / "motor/cache/tomadas_tarefa6_resumo.json"
    gravar_json(out_file, {
        "saldo_antes": caracteres_antes,
        "saldo_depois": caracteres_depois,
        "delta": delta_tts,
        "blocos": resultados
    })

    return 0


if __name__ == "__main__":
    sys.exit(main())
