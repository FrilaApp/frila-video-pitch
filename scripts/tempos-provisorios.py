#!/usr/bin/env python3
"""PROVISÓRIO: ensaio visual T6/T7 SEM voz. Não substitui T5 nem serve à mixagem.

Uso: .venv/bin/python scripts/tempos-provisorios.py [--palavras-s 2.3]
Lê somente o rascunho da v5; grava motor/tempos-pt.json (ignorado pelo git).
Não importa tempos2.py, não lê credenciais e não chama serviço algum.
"""
import argparse
import json
import math
import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--palavras-s', type=float, default=2.3)
    args = parser.parse_args()
    if not math.isfinite(args.palavras_s) or args.palavras_s <= 0:
        parser.error('--palavras-s deve ser positivo')
    roteiro = json.loads((RAIZ / 'roteiro.json').read_text())['cenas']
    cenas, falas, t = [], [], 0.0
    for c in roteiro:
        separar = lambda texto: re.split(r'(?<=[.?!])\s+', texto.strip())
        voz, leg = separar(c['pt']['fala']), separar(c['pt']['legenda'])
        if len(voz) != len(leg):
            raise ValueError(f"{c['id']}: fala e legenda com contagens diferentes")
        ini = t + (0.65 if c is roteiro[0] else 0.3)
        lista = []
        for k, (fala, legenda) in enumerate(zip(voz, leg), 1):
            fim = ini + len(fala.split()) / args.palavras_s
            lista.append(dict(cena=c['id'], k=k, ini=round(ini, 4), fim=round(fim, 4), legenda=legenda))
            ini = fim + 0.25
        dur = max(c['janela_s'], lista[-1]['fim'] - t + 0.55)
        cenas.append(dict(id=c['id'], ini=round(t, 4), dur=round(dur, 4), legenda_queimada=c['legenda_queimada']))
        for i, f in enumerate(lista):
            f['leg_ini'] = round(f['ini'] - 0.05, 4)
            f['leg_fim'] = round(lista[i+1]['ini'] - 0.05 if i+1 < len(lista) else min(f['fim'] + 0.4, t + dur - 0.12), 4)
        falas.extend(lista)
        t += dur
    saida = dict(_provisorio=True, _nota=f'ENSAIO VISUAL SEM VOZ: {args.palavras_s} palavras/s; não é a régua T5; música ausente.',
                 lang='pt', P=0.491835, bar=1.96734, total=round(t, 4), cenas=cenas, falas=falas, musica=[])
    destino = RAIZ / 'motor/tempos-pt.json'
    destino.write_text(json.dumps(saida, ensure_ascii=False, indent=2) + '\n')
    print(f'PROVISÓRIO: {len(cenas)} cenas, {len(falas)} frases, {t:.3f} s → {destino}')


if __name__ == '__main__':
    main()
