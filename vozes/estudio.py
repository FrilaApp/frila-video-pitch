"""Experimento autorizado: orçamento persistente e variantes, sem alterar tomadas."""
import json
import re
from pathlib import Path
import subprocess
import urllib.error
import urllib.request

import numpy as np
from motor.audio_util import SR, db, gravar_json, hash_arquivo, ler, medir_loudness


def validar_direcao(texto, fonte):
    sem_tags=re.sub(r'\[[^\]]+\]\s*','',texto)
    if ':' in fonte or sem_tags.strip()!=fonte.strip():
        raise ValueError('Direção não pode mudar texto/pontuação nem inserir dois-pontos')
    return sem_tags.strip()


def reservar_tts(ledger, nome, voz, formato, payload):
    ledger=Path(ledger); ledger.parent.mkdir(parents=True,exist_ok=True)
    lock=ledger.with_suffix('.lock')
    with lock.open('x'):
        try:
            itens=json.loads(ledger.read_text()) if ledger.exists() else []
            if any(x['nome']==nome for x in itens):
                raise ValueError('Solicitação já solicitada; não repetir automaticamente')
            tamanho=len(payload['text'])
            if sum(x['caracteres_texto'] for x in itens)+tamanho>3000:
                raise ValueError('Teto de3000 caracteres excedido antes da API')
            item={'nome':nome,'voz':voz,'formato':formato,'modelo':payload['model_id'] if 'model_id' in payload else None,
                  'payload':payload,'text':payload['text'],'caracteres_texto':tamanho,'estado':'reservado'}
            itens.append(item); gravar_json(ledger,itens)
        finally:
            lock.unlink()
    return item


def pedir_tts(base,nome,voz,formato,payload):
    from vozes.eleven import chave
    base=Path(base); ledger=base/'tts-ledger.json'
    itens=json.loads(ledger.read_text()) if ledger.exists() else []
    anterior=next((x for x in itens if x['nome']==nome),None)
    if anterior:
        if anterior.get('payload')!=payload:
            raise ValueError('Nome reutilizado com outra receita')
        return anterior
    item=reservar_tts(ledger,nome,voz,formato,payload)
    key=chave()
    req=urllib.request.Request('https://api.elevenlabs.io/v1/text-to-speech/'+voz+'?output_format='+formato,
                              data=json.dumps(payload).encode(),headers={'xi-api-key':key,'Content-Type':'application/json'})
    try:
        with urllib.request.urlopen(req,timeout=100) as r:
            data=r.read(); item.update(http=r.status,content_type=r.headers.get('content-type'),request_id=r.headers.get('request-id'))
        dest=base/'originais'/f'{nome}.bin'; dest.parent.mkdir(exist_ok=True); dest.write_bytes(data)
        item.update(arquivo=str(dest.resolve()),sha256=hash_arquivo(dest),bytes=len(data),estado='gerado')
    except urllib.error.HTTPError as e:
        item.update(http=e.code,erro=e.read().decode().replace(key,'[oculto]')[:1800],estado='negado_ou_invalido')
    itens=json.loads(ledger.read_text()); itens=[item if x['nome']==nome else x for x in itens]; gravar_json(ledger,itens)
    return item


def decodificar_tts(item,destino):
    entrada=[]
    if item['formato'].startswith('pcm_'):
        entrada=['-f','s16le','-ar',item['formato'].split('_')[1],'-ac','1']
    subprocess.run(['ffmpeg','-v','error','-y',*entrada,'-i',item['arquivo'],'-ar',str(SR),'-ac','1','-c:a','pcm_f32le',str(destino)],check=True)


def filtro_banda(x,sr=SR,lo=300,hi=6000):
    """Análise RMS por FFT; não é filtro aplicado à voz ou à música ouvida."""
    x=np.asarray(x); spec=np.fft.rfft(x,axis=0); freq=np.fft.rfftfreq(len(x),1/sr)
    spec[(freq<lo)|(freq>hi)]=0
    return np.fft.irfft(spec,n=len(x),axis=0).astype('float32')


def banda_db(x,sr=SR):
    return db(filtro_banda(x,sr))


def cadeia_estudio(fonte,destino):
    x=ler(fonte,1)[:,0]
    spec=abs(np.fft.rfft(x))**2; freq=np.fft.rfftfreq(len(x),1/SR)
    fracao=float(spec[(freq>=10000)&(freq<=20000)].sum()/(spec.sum()+1e-20))
    ar=fracao>10**(-45/10)
    filtros=['highpass=f=80:p=2','deesser=i=0.08:m=0.15:f=0.6',
             'equalizer=f=3800:t=q:w=0.8:g=1.5']
    if ar: filtros.append('highshelf=f=11000:g=1:t=q:w=0.707')
    filtros.append('acompressor=threshold=0.125:ratio=1.6:attack=15:release=120:knee=2.828:makeup=1')
    subprocess.run(['ffmpeg','-v','error','-y','-i',str(fonte),'-af',','.join(filtros),'-ar',str(SR),'-c:a','pcm_f32le',str(destino)],check=True)
    if len(ler(destino,1))!=len(x): raise ValueError('Cadeia mudou a duração')
    return {'filtros':filtros,'fracao_energia_acima10k':fracao,'shelf_ar_aplicado':ar,'reverb':False}


def igualar_volume(fonte,destino,alvo=-20):
    m=medir_loudness(fonte); ganho=alvo-float(m['input_i'])
    # Somente ganho estático; manter teto sem clipping e documentar se alvo não couber.
    ganho=min(ganho,-1.5-float(m['input_tp']))
    subprocess.run(['ffmpeg','-v','error','-y','-i',str(fonte),'-af',f'volume={ganho}dB',
                    '-ar',str(SR),'-c:a','pcm_f32le',str(destino)],check=True)
    return ganho
