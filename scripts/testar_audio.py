#!/usr/bin/env python3
"""Aceite T4 offline com FFmpeg; só grava em motor/cache/teste-audio/.

Uso: .venv/bin/python scripts/testar_audio.py [--saida CAMINHO]
Não lê chave, não chama ElevenLabs, não usa a voz nem a régua do vídeo.
"""
import argparse
import json
from pathlib import Path
import subprocess
import sys

import numpy as np

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / 'motor'))
from audio2 import montar, masterizar
from audio_util import SR, gravar_json, hash_arquivo, ler, salvar
from conferir_audio import conferir_sessao
from tempos2 import preparar


def gerar(destino, fonte, filtros=None, codec='pcm_s16le'):
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'lavfi', '-i', fonte,
                    *(['-af', filtros] if filtros else []), '-c:a', codec, str(destino)], check=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--saida', type=Path, default=RAIZ / 'motor/cache/teste-audio')
    args = ap.parse_args(); saida = args.saida.resolve(); saida.mkdir(parents=True, exist_ok=True)
    cfg = json.loads((RAIZ / 'motor/mixagem.json').read_text())
    # Override documentado: o detector de coexistência encontrou 12,20 dB no baseline.
    cfg['eventos']['clique-meio'] = {'ajuste_sobre_referencia_legada_db': -10}
    trilha = saida / 'trilha-sintetica.wav'
    gerar(trilha, 'anoisesrc=color=pink:amplitude=0.15:duration=16:sample_rate=48000:seed=19')
    falas = []
    for k, (inicio, freq) in enumerate([(1., 293), (3.5, 347), (7., 419)], 1):
        bruto = saida / f'sinal-{k}.wav'
        gerar(bruto, f'sine=frequency={freq}:duration=1.8:sample_rate=24000',
              'volume=1.13137,afade=t=in:st=0:d=0.008,afade=t=out:st=1.7:d=0.1,adelay=120,apad=pad_dur=0.28')
        original = ler(bruto, 1)[:, 0]
        x, meta = preparar(original, limites=(round(.12 * SR), round(1.92 * SR)), confirmado=True)
        p = saida / f'preparado-{k}.wav'; salvar(p, x)
        # Garantir que o reamostrado, antes de ganho de mix, está intacto.
        assert np.array_equal(x, original)
        meta.update(bruto=str(bruto), sha256=hash_arquivo(bruto), fala='Sinal sintético; não representa uma palavra.')
        gravar_json(p.with_suffix('.json'), meta)
        falas.append({'id': f'teste-{k}', 'cena': 'teste', 'k': k, 'ini': inicio,
                      'fim': inicio + len(x) / SR, 'arquivo': str(p), **meta})
    t = {'lang': 'pt', 'bar': 4., 'total': 12., 'cenas': [{'id': 'teste', 'ini': 0., 'dur': 12.}],
         'musica': [{'src': 0., 'v': 0.}, {'src': 4., 'v': 4.}, {'src': 8., 'v': 8.}], 'falas': falas}
    eventos = [{'id': 'grave-antes', 'tipo': 'grave', 't': 1.12 - .2855},
               {'id': 'grave-borda', 'tipo': 'grave', 't': 3.62},
               {'id': 'clique-meio', 'tipo': 'clique', 't': 7.85}]
    gravar_json(saida / 'tempos-teste.json', t); gravar_json(saida / 'eventos-teste.json', eventos)
    sessao = saida / 'sessao'
    montar(t, eventos, cfg, sessao, trilha)
    qa = conferir_sessao(sessao, cfg)
    if not qa['tecnico_ok']:
        raise SystemExit('QA bloqueou: ' + '; '.join(qa['falhas']))
    master = masterizar(sessao, cfg)
    qa = conferir_sessao(sessao, cfg, final=sessao / 'verificacao.m4a', trechos=True)
    assert qa['tecnico_ok'], qa['falhas']
    resumo = {'tipo': 'medição sintética, sem voz v5 ou aprovação auditiva',
              'sessao': str(sessao), 'amostras_por_stem': round(t['total'] * SR),
              'null_maximo': qa['null_maximo'], 'aac': master['aac'],
              'modo_loudnorm': master['passagem2']['normalization_type'],
              'master_atraso_amostras': master['master_atraso_amostras'],
              'frases': [{'id': f['id'], **{k: f['medidas'][k] for k in
                          ('voz_musica_db', 'voz_efeitos_coexistencia_min_db', 'voz_fundo_local_min_db', 'bordas')}}
                         for f in qa['frases']],
              'colisoes': qa['colisoes'], 'estado': qa['estado']}
    gravar_json(saida / 'resultado.json', resumo)
    print(json.dumps(resumo, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
