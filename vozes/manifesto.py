"""IDs compartilhados de fala/legenda e tomadas imutáveis, sem acesso à API."""
import hashlib
import json
from pathlib import Path
import re
import shutil


def frases(texto):
    return [f for f in re.split(r'(?<=[.?!])\s+', texto.strip()) if f]


def frases_do_roteiro(roteiro, filtro=(), idioma='pt'):
    itens = []
    for c in roteiro['cenas']:
        falas, legendas = frases(c[idioma]['fala']), frases(c[idioma]['legenda'])
        if len(falas) != len(legendas) or not falas:
            raise ValueError(f"Fala/legenda com contagem divergente ou vazia: {c['id']}")
        for k, (fala, legenda) in enumerate(zip(falas, legendas), 1):
            fid = f"{c['id']}-{k}"
            if not filtro or any(v in (fid, c['id'], c['id'].split('-')[0]) for v in filtro):
                itens.append({'id': fid, 'cena': c['id'], 'k': k, 'fala': fala, 'legenda': legenda})
    if filtro and not itens:
        raise ValueError('Filtro sem frases correspondentes')
    return itens


def guardar_tomada(arquivo, raiz, metadados):
    arquivo = Path(arquivo)
    digest = hashlib.sha256(arquivo.read_bytes()).hexdigest()
    destino = Path(raiz) / arquivo.stem / f'{digest}.wav'
    destino.parent.mkdir(parents=True, exist_ok=True)
    if not destino.exists():
        shutil.copyfile(arquivo, destino)
    meta = destino.with_suffix('.json')
    if not meta.exists():
        meta.write_text(json.dumps({**metadados, 'sha256': digest}, ensure_ascii=False, indent=2) + '\n')
    return destino
