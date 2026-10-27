"""Produção dos 4 blocos da Tarefa 6 (Ana v3 / Gabriel v2 / Ana v3 / Ana v3).
Orçamento rigoroso, UMA chamada por bloco, verificação A8 e Scribe.
"""
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

ROTEIRO_PATH = ROOT / "roteiro.json"
ROTEIRO = json.loads(ROTEIRO_PATH.read_text())

# Configuração das vozes aprovadas pelo Fabrício em 26/10/2026
VOZ_ANA = "MZxV5lN3cv7hi1376O0m"
VOZ_GABRIEL = "WPgqgCVa3mD38JuyODU6"

BLOCOS_CONFIG = {
    "A": {
        "voz": VOZ_ANA,
        "modelo": "eleven_v3",
        "settings": {"stability": 0.5},
        "seed": 1,
        "contexto": {},  # v3 não suporta previous_text/next_text
        "texto_direcao": (
            "Hoje, dezenove horas. Faltou gente no turno. "
            "Segundo a Abrasel, nove em cada dez empresários de bares e restaurantes acham difícil contratar. "
            "[thoughtful] Uma plataforma declara um milhão e meio de cadastrados. Cadastro não é turno. "
            "Nos bares e restaurantes, a rotatividade passou de setenta por cento em um ano."
        ),
        "uuid_existente": "0b4c957960dc4ea8bfa77e1100c8a579"
    },
    "B": {
        "voz": VOZ_GABRIEL,
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
        "texto_direcao": (
            "O Frila conecta quem precisa de gente a profissionais perto. "
            "Você publica a vaga. O Frila avisa quem está perto, até quinze quilômetros. "
            "Antes de escolher, você vê o histórico. No local, o profissional faz check-in. "
            "Depois do turno, os dois lados avaliam, chamaria de novo?"
        ),
    },
    "C": {
        "voz": VOZ_ANA,
        "modelo": "eleven_v3",
        "settings": {"stability": 0.5},
        "seed": 1,
        "contexto": {},
        "texto_direcao": (
            "Dos vinte e dois apps que estudamos, nenhum mostra comparecimento medido. "
            "Meta do piloto, oito semanas, cinquenta vagas por semana e nove em cada dez profissionais presentes. "
            "Começamos por um núcleo de quinze quilômetros. Depois, bares e restaurantes. Depois, o Distrito Federal."
        ),
    },
    "D": {
        "voz": VOZ_ANA,
        "modelo": "eleven_v3",
        "settings": {"stability": 0.5},
        "seed": 1,
        "contexto": {},
        "texto_direcao": (
            "[thoughtful] Menos tempo procurando gente. [happy] Mais tempo no seu negócio. "
            "[thoughtful] Deixa que o Frila cuida. Frila. Turno combinado, regra clara."
        ),
    },
}

def pcm48_para_wav(pcm, destino):
    with wave.open(str(destino), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(48000)
        w.writeframes(pcm)

def extrair_f0_e_centroide(arquivo_wav):
    """Calcula métricas objetivas de timbre: F0 médio e centroide espectral na fala ativa."""
    x = ler(arquivo_wav, 1)[:, 0]
    frame_len = int(0.040 * SR)  # 40 ms
    hop = int(0.010 * SR)        # 10 ms
    n_frames = (len(x) - frame_len) // hop
    
    f0_list = []
    centroides = []
    
    rms_total = np.sqrt(np.mean(x**2))
    limiar_ativo = 0.05 * rms_total
    
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
            
        corr = np.correlate(w, w, mode='full')
        corr = corr[len(corr)//2:]
        min_lag = int(SR / 400)
        max_lag = int(SR / 70)
        if max_lag < len(corr):
            lag = min_lag + np.argmax(corr[min_lag:max_lag])
            if corr[lag] > 0.3 * corr[0]:
                f0_list.append(SR / lag)
                
    f0_med = float(np.median(f0_list)) if f0_list else 0.0
    c_med = float(np.mean(centroides)) if centroides else 0.0
    return {"f0_mediano_hz": round(f0_med, 1), "centroide_medio_hz": round(c_med, 1)}

def sintetizar_e_validar_bloco(bloco_id):
    cfg = BLOCOS_CONFIG[bloco_id]
    cenas_bloco = [c for c in ROTEIRO['cenas'] if c.get('bloco') == bloco_id]
    fala_roteiro = " ".join(c['pt']['fala'].strip() for c in cenas_bloco)
    frases_oficiais = frases_do_roteiro({'cenas': cenas_bloco})
    
    # Validar que texto de direção sem tags casa com o roteiro exatamente
    texto_sem_tags = re.sub(r'\[[^\]]+\]\s*', '', cfg['texto_direcao']).strip()
    if normal(texto_sem_tags) != normal(fala_roteiro):
        raise ValueError(f"Bloco {bloco_id}: texto com tags diverge do roteiro oficial!")
    if ":" in fala_roteiro or ":" in cfg['texto_direcao']:
        raise ValueError(f"Bloco {bloco_id}: violação A8 detectada (dois-pontos)!")
        
    print(f"\n==========================================")
    print(f"  Processando Bloco {bloco_id} (Voz: {cfg['voz'][:8]}..., Modelo: {cfg['modelo']})")
    print(f"==========================================")
    
    # Se já existir tomada gravada com sucesso (ex: Bloco A já gerado)
    existente_uuid = cfg.get("uuid_existente")
    if existente_uuid:
        tomada_dir = ROOT / "vozes/tomadas/blocos/pt" / bloco_id / existente_uuid
        bruto_wav = tomada_dir / "bruto.wav"
        scribe_file = tomada_dir / "scribe.json"
        if bruto_wav.exists() and scribe_file.exists():
            print(f"Reutilizando tomada já sintetizada em {tomada_dir}...")
            pcm = bruto_wav.read_bytes()
            duracao_s = len(ler(bruto_wav, 1)) / SR
            scribe_resp = json.loads(scribe_file.read_text())
        else:
            existente_uuid = None
            
    if not existente_uuid:
        print(f"Texto a enviar ({len(cfg['texto_direcao'])} chars): {cfg['texto_direcao']}")
        payload = {
            "text": cfg['texto_direcao'],
            "model_id": cfg['modelo'],
            "language_code": "pt",
            "seed": cfg['seed'],
            **cfg['contexto']
        }
        payload["voice_settings"] = cfg['settings']
            
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
        raise ValueError(f"Bloco {bloco_id} FALHOU na Regra A8! Interrompendo conforme instrução.")
        
    voz_tratada_wav = tomada_dir / "voz.wav"
    recibo_cadeia = cadeia_estudio(bruto_wav, voz_tratada_wav)
    print(f"✅ Cadeia de estúdio aplicada: {voz_tratada_wav} (Ar: {recibo_cadeia['shelf_ar_aplicado']})")
    
    timbre = extrair_f0_e_centroide(voz_tratada_wav)
    print(f"Métricas tímbricas: F0={timbre['f0_mediano_hz']} Hz | Centroide={timbre['centroide_medio_hz']} Hz")
    
    meta = {
        "bloco": bloco_id,
        "fala": fala_roteiro,
        "texto_enviado": cfg['texto_direcao'],
        "cenas": [c['id'] for c in cenas_bloco],
        "geracao": {
            "voice_id": cfg['voz'],
            "modelo": cfg['modelo'],
            "settings": cfg['settings'],
            "seed": cfg['seed'],
            "contexto": cfg['contexto'],
            "formato": "pcm_48000"
        },
        "cadeia_estudio": recibo_cadeia,
        "timbre": timbre,
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
        "chars": len(cfg['texto_direcao']),
        "timbre": timbre,
        "palavras": palavras,
        "a8": a8_result
    }

if __name__ == "__main__":
    saldo_antes = chamar("/v1/user/subscription")
    saldo_antes_data = json.loads(saldo_antes)
    caracteres_antes = saldo_antes_data['character_count']
    limite = saldo_antes_data['character_limit']
    print(f"Saldo inicial: {caracteres_antes} de {limite} caracteres usados.")
    
    resultados = {}
    for bloco_id in ["A", "B", "C", "D"]:
        res = sintetizar_e_validar_bloco(bloco_id)
        resultados[bloco_id] = res
        
    saldo_depois = chamar("/v1/user/subscription")
    saldo_depois_data = json.loads(saldo_depois)
    caracteres_depois = saldo_depois_data['character_count']
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
        "blocos": {b: {k: v for k, v in r.items() if k != 'palavras'} for b, r in resultados.items()}
    })
