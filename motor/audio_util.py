"""I/O, hashes e medições locais de áudio; não acessa serviços ou credenciais."""
import hashlib
import json
from pathlib import Path
import subprocess

import numpy as np

SR = 48000


def hash_json(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def hash_arquivo(p):
    h = hashlib.sha256()
    with Path(p).open('rb') as f:
        for bloco in iter(lambda: f.read(1024 * 1024), b''):
            h.update(bloco)
    return h.hexdigest()


def gravar_json(p, obj):
    p = Path(p)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=2, allow_nan=False) + '\n')


def ler(p, canais=1):
    filtros = []
    if canais == 2:
        probe = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'a:0',
                                '-show_entries', 'stream=channels', '-of', 'json', str(p)],
                               capture_output=True, text=True, check=True)
        if json.loads(probe.stdout)['streams'][0]['channels'] == 1:
            filtros = ['-af', 'pan=stereo|c0=c0|c1=c0']
    r = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(p), *filtros, '-f', 'f32le',
                        '-ac', str(canais), '-ar', str(SR), '-'], capture_output=True, check=True)
    x = np.frombuffer(r.stdout, dtype='<f4').reshape(-1, canais).copy()
    if not x.size or not np.isfinite(x).all():
        raise ValueError(f'Áudio vazio ou não finito: {p}')
    return x


def salvar(p, x, codec='pcm_f32le'):
    p = Path(p)
    p.parent.mkdir(parents=True, exist_ok=True)
    x = np.asarray(x, dtype='<f4')
    if x.ndim == 1:
        x = x[:, None]
    if not x.size or not np.isfinite(x).all():
        raise ValueError('Áudio vazio ou não finito')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ar', str(SR),
                    '-ac', str(x.shape[1]), '-i', '-', '-c:a', codec, str(p)],
                   input=x.tobytes(), check=True)


def db(x):
    if not np.asarray(x).size:
        return -240.0
    return float(20 * np.log10(np.sqrt(np.mean(np.square(x, dtype=np.float64))) + 1e-12))


def medir_loudness(p, alvo=-16, teto=-2, lra=11):
    r = subprocess.run(['ffmpeg', '-hide_banner', '-i', str(p), '-af',
                        f'loudnorm=I={alvo}:TP={teto}:LRA={lra}:print_format=json',
                        '-f', 'null', '-'], capture_output=True, text=True, check=True)
    s = r.stderr
    d = json.loads(s[s.rindex('{'):s.rindex('}') + 1])
    if not all(np.isfinite(float(d[k])) for k in ('input_i', 'input_tp', 'input_lra', 'input_thresh')):
        raise ValueError(f'Loudness indefinida: {p}')
    return d
