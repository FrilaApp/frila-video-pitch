"""Stems v5, ducking por intervalo e master em duas passagens.

Uso: .venv/bin/python motor/audio2.py pt [--regua ... --eventos ... --saida ...]
Não gera voz nem acessa API. A configuração pública fica em motor/mixagem.json.
"""
import argparse
import json
import pathlib
import shutil
import subprocess

import numpy as np
try:
    from .audio_util import SR, db, ler, salvar, hash_arquivo, hash_json, gravar_json, medir_loudness
except ImportError:
    from audio_util import SR, db, ler, salvar, hash_arquivo, hash_json, gravar_json, medir_loudness

AQUI = pathlib.Path(__file__).resolve().parent
VIDEO = AQUI.parent
TRILHA = VIDEO / "musica/talent-in-the-air-diego-nava-mixkit.mp3"
XF = int(.006 * SR)


def tempo(n):
    return np.arange(n) / SR


def env(n, decai, ataque=.001):
    t = tempo(n)
    e = np.exp(-t / decai)
    a = max(1, int(ataque * SR))
    e[:a] *= np.linspace(0, 1, a)
    return e


def soma(buf, t0, x, ganho=1.0):
    i = int(round(t0 * SR))
    if i >= len(buf) or i + len(x) <= 0:
        return
    if i < 0:
        x, i = x[-i:], 0
    x = x[: len(buf) - i]
    buf[i:i + len(x)] += ganho * x


def passa_baixa(x, fc):
    fc = np.broadcast_to(np.asarray(fc, dtype=float), x.shape)
    a = 1 - np.exp(-2 * np.pi * fc / SR)
    y, s = np.empty_like(x), 0.0
    for i in range(len(x)):
        s += a[i] * (x[i] - s)
        y[i] = s
    return y


def passa_alta(x):
    return np.diff(x, prepend=0.0)


def sino(f, dur, brilho=1.0):
    t = tempo(int(dur * SR))
    x = sum(np.sin(2 * np.pi * f * h * t) * np.exp(-t * (7 + 10 * h / brilho)) / h for h in range(1, 5))
    return x * np.minimum(1, t / .002)


# ---------- efeitos de UI: curtos, secos, sem eco ----------
def clique(rng=None):
    rng = rng if rng is not None else np.random.default_rng(7)
    n = int(.035 * SR)
    t = tempo(n)
    corpo = np.sin(2 * np.pi * 1700 * t) * env(n, .005, .0002)
    estalo = passa_alta(rng.standard_normal(n)) * env(n, .002, .0001) * .5
    return corpo * .7 + estalo


def tique():
    n = int(.025 * SR)
    return np.sin(2 * np.pi * 3000 * tempo(n)) * env(n, .004, .0002) * .5


def pop():
    n = int(.11 * SR)
    t = tempo(n)
    f = 380 + 600 * (1 - np.exp(-t / .018))
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, .03) * .8


def swish(rng=None):
    rng = rng if rng is not None else np.random.default_rng(7)
    n = int(.3 * SR)
    t = tempo(n)
    fc = 500 + 4200 * np.sin(np.pi * t / t[-1]) ** 2
    e = np.sin(np.pi * t / t[-1]) ** 2
    return passa_baixa(passa_alta(rng.standard_normal(n)), fc) * e * 1.3


def ok():
    x = np.zeros(int(.5 * SR))
    for d, f in ((0, 1318.5), (.065, 1975.5)):
        s = sino(f, .4) * .5
        i = int(d * SR)
        x[i:i + len(s)] += s
    return x


def aviso():
    x = np.zeros(int(.8 * SR))
    for d, f in ((0, 1568), (.13, 2093)):
        s = sino(f, .6, 1.5) * .6
        i = int(d * SR)
        x[i:i + len(s)] += s
    return x


def grave(rng=None):
    rng = rng if rng is not None else np.random.default_rng(7)
    n = int(.7 * SR)
    t = tempo(n)
    f = 38 + 50 * np.exp(-t / .08)
    corpo = np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, .22, .004)
    ar = passa_baixa(rng.standard_normal(n), 900) * env(n, .12, .02) * .6
    return corpo + ar


def pouso():
    """O ponto vira o pingo do i: um baque curto e um sino em Fá que segura."""
    n = int(.25 * SR)
    t = tempo(n)
    baque = np.sin(2 * np.pi * np.cumsum(110 - 50 * (1 - np.exp(-t / .04))) / SR) * env(n, .06)
    x = np.zeros(int(2.4 * SR))
    x[:n] += baque * .8
    for k, m in enumerate((77, 81, 84)):
        s = sino(440 * 2 ** ((m - 69) / 12), 2.2, 2) * .3
        i = int(k * .018 * SR)
        x[i:i + len(s)] += s
    return x


def spr(t, w, z):
    if t <= 0:
        return 0.0
    wd = w * np.sqrt(1 - z * z)
    return 1 - np.exp(-z * w * t) * (np.cos(wd * t) + z * w / wd * np.sin(wd * t))


def roll():
    """Contador girando: um tique a cada 1/16 do caminho, na mesma mola 'count' do contador na tela."""
    x = np.zeros(int(2.0 * SR))
    passos = 16
    k, t = 1, 0.0
    while k <= passos and t < 1.95:
        if spr(t, 5.2, .985) >= k / passos:
            s = tique() * (.55 + .45 * (1 - k / passos))
            i = int(t * SR)
            x[i:i + len(s)] += s
            k += 1
        t += 1 / SR * 16
    return x


EFEITOS = {"clique": (clique, .55), "tick": (tique, .35), "pop": (pop, .5), "swish": (swish, .4), "roll": (roll, .5),
           "ok": (ok, .35), "aviso": (aviso, .45), "grave": (grave, .7), "pouso": (pouso, .5)}


# ---------- montagem ----------
def montagem_musical(T, n, trilha, plano):
    """Trechos contínuos; só saltos declarados recebem crossfade, nunca a voz."""
    src = ler(trilha, 2)
    if plano.get('sha256') and hash_arquivo(trilha) != plano['sha256']:
        raise ValueError('Hash da trilha diverge da montagem analisada')
    bar = T['bar']; origem = plano['origem_s']
    trechos = plano['trechos']; meio = round(plano['crossfade_ms'] * SR / 2000)
    m = np.zeros((n, 2), dtype=np.float32)
    anterior = None
    for s in trechos:
        a, b = (round(s[k] * bar * SR) for k in ('ini_compasso', 'fim_compasso'))
        i = round((origem + s['origem_compasso'] * bar) * SR)
        if a != (anterior[1] if anterior else 0) or not 0 <= a < b <= n or i < 0 or i+b-a > len(src):
            raise ValueError('Trecho musical fora da fonte ou montagem descontínua')
        m[a:b] = src[i:i+b-a]
        if anterior:
            pa, pb, pi = anterior
            if abs(pi + pb-pa-i) > 1:
                l, r = a-meio, a+meio
                if l < 0 or r > n or i-meio < 0 or pi+r-pa > len(src):
                    raise ValueError('Crossfade sem contexto na fonte')
                if any(f['ini'] < r/SR and f['fim'] > l/SR for f in T['falas']):
                    raise ValueError('Crossfade musical coincide com fala')
                u = np.linspace(0, 1, r-l, dtype=np.float32)
                u = (u*u*(3-2*u))[:, None]
                m[l:r] = src[pi+l-pa:pi+r-pa]*(1-u) + src[i-meio:i+meio]*u
        anterior = (a,b,i)
    if not anterior or anterior[1] != n:
        raise ValueError('Montagem musical não cobre a régua inteira')
    fade = round(plano.get('fade_final_ms', 0)*SR/1000)
    if fade:
        m[-fade:] *= np.linspace(1,0,fade,dtype=np.float32)[:,None]
    return m


def musica(T, N, trilha=TRILHA):
    src = ler(trilha, 2)
    m = np.zeros((N, 2))
    barra = int(round(T["bar"] * SR))
    rampa = np.linspace(0, 1, XF)[:, None]
    for i, b in enumerate(T["musica"]):
        a, v = int(round(b["src"] * SR)), int(round(b["v"] * SR))
        pedaco = src[a:a + barra + XF].copy()
        if i:
            pedaco[:XF] *= rampa
        pedaco[-XF:] *= rampa[::-1]
        pedaco = pedaco[: N - v]
        m[v:v + len(pedaco)] += pedaco
    # o último compasso apaga devagar, para o logo terminar no silêncio
    ult = int(round(T["musica"][-1]["v"] * SR))
    m[ult:] *= np.linspace(1, 0, N - ult)[:, None] ** 1.6
    return m


def semente_evento(e):
    identidade = e.get('id', {k: e[k] for k in ('tipo', 't', 'cena') if k in e})
    return int(hash_json(identidade)[:16], 16)


def sintetizar_evento(e):
    """Seed por identidade, independente da ordem, ganho e posição na lista."""
    seed = semente_evento(e)
    func, peso = EFEITOS[e['tipo']]
    x = func(np.random.default_rng(seed)) if func in (clique, grave, swish) else func()
    return np.asarray(x * peso, dtype=np.float32), seed


def mesclar(intervalos, pausa):
    unidos = []
    for a, b in sorted(intervalos):
        if unidos and a - unidos[-1][1] <= pausa:
            unidos[-1] = (unidos[-1][0], max(b, unidos[-1][1]))
        else:
            unidos.append((a, b))
    return unidos


def envoltoria(n, intervalos, cfg, protecao):
    """Rampas em dB; patamar pronto antes da fala, sem abrir em pausas curtas."""
    atenuacao = np.zeros(n, dtype=np.float32)

    def aplicar(a, b, profundidade):
        p0 = a - cfg['inicio_rampa_antes_ms'] / 1000
        p1 = a - cfg['atenuacao_completa_antes_ms'] / 1000
        p2 = b + cfg['segura_ms'] / 1000
        p3 = p2 + cfg['volta_ms'] / 1000
        i, j = max(0, round(p0 * SR)), min(n, round(p3 * SR) + 1)
        if j <= i:
            return
        t = np.arange(i, j) / SR
        # smoothstep evita mudanças abruptas de inclinação.
        ataque = np.clip((t - p0) / max(p1 - p0, 1 / SR), 0, 1)
        retorno = np.clip((p3 - t) / max(p3 - p2, 1 / SR), 0, 1)
        curva = np.minimum(ataque * ataque * (3 - 2 * ataque), retorno * retorno * (3 - 2 * retorno))
        atenuacao[i:j] = np.maximum(atenuacao[i:j], profundidade * curva)

    base = cfg['profundidade_db']
    for a, b in mesclar(intervalos, protecao['mesclar_pausas_ate_ms'] / 1000):
        aplicar(a, b, base)
    borda = min(cfg.get('maximo_db', 99), base + cfg.get('extra_nas_bordas_db', 0))
    for a, b in intervalos:
        aplicar(a, min(b, a + protecao['inicio_frase_ms'] / 1000), borda)
        aplicar(max(a, b - protecao['fim_frase_ms'] / 1000), b, borda)
    return np.power(10., -atenuacao / 20).astype(np.float32)


def cache_wav(raiz, nome, receita, produzir):
    """Cache por conteúdo e versão da receita; mantém os stems correntes legíveis."""
    chave = hash_json({'receita': receita, 'versao_motor': 2})
    arquivo = raiz / 'objetos' / f'{nome}-{chave}.wav'
    if not arquivo.exists():
        salvar(arquivo, produzir())
    return arquivo, chave


def montar(T, eventos, cfg, saida, trilha=TRILHA, voz_dir=None):
    saida = pathlib.Path(saida)
    saida.mkdir(parents=True, exist_ok=True)
    n = round(T['total'] * SR)
    if cfg['musica']['duck']['profundidade_db'] > cfg['musica']['duck']['maximo_db']:
        raise ValueError('Ducking musical acima do teto; revisar configuração')
    if n <= 0 or cfg['sessao']['sample_rate'] != SR:
        raise ValueError('Duração/sample rate de sessão inválidos')
    stems = saida / 'stems'; stems.mkdir(exist_ok=True)
    v = np.zeros(n, dtype=np.float32)
    frases, intervalos = [], []
    # Legendas têm janelas por frase; a voz oficial usa quatro tomadas inteiras.
    for f in T.get('audio_blocos', T['falas']):
        fid = f.get('id', f"{f['cena']}-{f['k']}")
        p = pathlib.Path(f.get('arquivo', pathlib.Path(voz_dir or AQUI / 'cache/voz/pt') / f'{fid}.npy'))
        if f.get('sha256') and hash_arquivo(p) != f['sha256']:
            raise ValueError(f'Hash da fonte vocal diverge: {fid}')
        x = np.load(p).astype(np.float32) if p.suffix == '.npy' else ler(p, 1)[:, 0]
        meta_path = p.with_suffix('.json')
        meta = json.loads(meta_path.read_text()) if meta_path.exists() else {}
        meta = {**meta, **f}
        if x.ndim != 1 or not x.size or not np.isfinite(x).all() or db(x) < -100:
            raise ValueError(f'Frase inválida: {fid}')
        a = f.get('ini_amostra', round(f['ini'] * SR)); b = a + len(x)
        if not 0 <= a < b <= n:
            raise ValueError(f'Frase cortada pelos limites da sessão: {fid}')
        confirmado = meta.get('limites_confirmados', False)
        ai, bi = (meta.get('fala_ini_amostra', 0), meta.get('fala_fim_amostra', len(x))) if confirmado else (0, len(x))
        if not 0 <= ai < bi <= len(x):
            raise ValueError(f'Limites acústicos inválidos: {fid}')
        if intervalos and (a + ai) / SR < intervalos[-1][1]:
            raise ValueError(f'Atividade vocal sobreposta: {fid}')
        op = cfg['voz'].get('frases', {}).get(fid, {})
        ativo = x[ai:bi]; ativo = ativo[np.abs(ativo) > 10 ** (-60 / 20)]
        if not ativo.size:
            raise ValueError(f'Frase sem atividade: {fid}')
        ajuste = cfg['voz']['rms_ativo_alvo_dbfs'] - db(ativo)
        if cfg['voz'].get('preservar_amostras', False):
            ganho = 0.
        else:
            ganho = op.get('ganho_db', float(np.clip(ajuste, -cfg['voz']['ajuste_automatico_max_db'],
                                                    cfg['voz']['ajuste_automatico_max_db'])))
            ganho += cfg['voz']['ganho_bus_db']
        x = (x * 10 ** (ganho / 20)).astype(np.float32)
        preparado = saida / 'frases' / f'{fid}-{hash_json([hash_arquivo(p), ganho])}.wav'
        if not preparado.exists():
            salvar(preparado, x)
        v[a:b] += x
        intervalos.append(((a + ai) / SR, (a + bi) / SR))
        frases.append({**meta, 'id': fid, 'arquivo': str(p.resolve()), 'sha256_preparado_fonte': hash_arquivo(p),
                       'preparado': str(preparado.resolve()), 'ganho_db': ganho,
                       'arquivo_ini_amostra': a, 'arquivo_fim_amostra': b,
                       'fala_ini_absoluta': a + ai, 'fala_fim_absoluta': a + bi,
                       'limites_confirmados': meta.get('limites_confirmados', False)})
    if not frases:
        raise ValueError('Sessão sem frases')
    if T.get('audio_blocos'):
        intervalos = [(f['ini'], f['fim']) for f in T['falas']]
    caminhos, chaves = {}, {}

    def stem(nome, receita, produzir):
        p, chave = cache_wav(saida, nome, receita, produzir)
        atual = stems / f'{nome}.wav'
        if not atual.exists() or hash_arquivo(atual) != hash_arquivo(p):
            shutil.copyfile(p, atual)
        caminhos[nome], chaves[nome] = str(atual.resolve()), chave
        return ler(p, 1 if nome == 'voz' else 2)

    voz = stem('voz', [hash_json(frases), n, cfg['voz']], lambda: v)
    receita_musica = [hash_arquivo(trilha), T['musica'], T['bar'], n,
                      {k: val for k, val in cfg['musica'].items() if k != 'duck'}, cfg['cenas'], T['cenas']]

    def base_musical():
        plano = cfg['musica'].get('montagem') if T.get('audio_blocos') else None
        m = montagem_musical(T, n, trilha, plano) if plano else musica(T, n, trilha)
        ativo = np.sqrt(np.mean(m * m, axis=1)) > 1e-6
        if not ativo.any():
            raise ValueError('Música sem atividade')
        m *= 10 ** ((cfg['musica']['rms_referencia_dbfs'] - db(m[ativo]) + cfg['musica']['ganho_bus_db']) / 20)
        niveis = np.zeros(n, dtype=np.float32)
        for c in T['cenas']:
            ganho = cfg['cenas'].get(c['id'], {}).get('musica_ganho_adicional_db', 0)
            niveis[round(c['ini']*SR):round((c['ini']+c['dur'])*SR)] = ganho
        for k in np.flatnonzero(np.diff(niveis)) + 1:
            a,b = max(0,k-round(.1*SR)),min(n,k+round(.1*SR))
            u = np.linspace(0,1,b-a); u=u*u*(3-2*u)
            niveis[a:b] = niveis[a]*(1-u)+niveis[b-1]*u
        m *= np.power(10.,niveis/20)[:,None]
        return m

    mb = stem('musica-base', receita_musica, base_musical)
    em = envoltoria(n, intervalos, cfg['musica']['duck'], cfg['protecao'])
    edcfg = {**cfg['efeitos'], 'profundidade_db': cfg['efeitos']['duck_db'],
             'extra_nas_bordas_db': cfg['efeitos']['duck_nas_bordas_db'] - cfg['efeitos']['duck_db']}
    ed = envoltoria(n, intervalos, edcfg, cfg['protecao'])
    np.save(saida / 'duck-musica.npy', em); np.save(saida / 'duck-efeitos.npy', ed)
    md = stem('musica-duck', [chaves['musica-base'], intervalos, cfg['musica']['duck'], cfg['protecao']],
              lambda: mb * em[:, None])
    eb = np.zeros(n, dtype=np.float32)
    inventario = []
    for e in (eventos if cfg['efeitos'].get('habilitado', True) else []):
        seed = semente_evento(e)
        receita = [e['tipo'], seed]
        amostra, _ = cache_wav(saida, 'evento', receita, lambda: sintetizar_evento(e)[0])
        x = ler(amostra, 1)[:, 0]
        fid = e.get('id', hash_json({k: e[k] for k in ('t', 'tipo')})[:16])
        op = {**cfg['efeitos'], **cfg['efeitos'].get('por_tipo', {}).get(e['tipo'], {}),
              **cfg['eventos'].get(fid, {})}
        # Referência legada fixa (-24+3 dB, dividida por 0,1), independente da música atual.
        ganho_db = op['ajuste_sobre_referencia_legada_db']
        x *= 10 ** ((-21 + ganho_db) / 20) / .1 * e.get('forca', 1)
        silenciar = any(a - cfg['protecao']['inicio_frase_ms'] / 1000 <= e['t'] <= a + cfg['protecao']['inicio_frase_ms'] / 1000
                        or b - cfg['protecao']['fim_frase_ms'] / 1000 <= e['t'] <= b + cfg['protecao']['fim_frase_ms'] / 1000
                        for a, b in intervalos)
        if silenciar:
            x *= 0
        soma(eb, e['t'], x)
        inventario.append({**e, 'id': fid, 'seed': seed, 'amostra': str(amostra.resolve()),
                           'sha256': hash_arquivo(amostra), 'ganho_db': ganho_db,
                           'silenciado': silenciar, 'duracao': len(x) / SR})
    efeitos = stem('efeitos-base', [inventario, n], lambda: np.repeat(eb[:, None], 2, axis=1))
    efeitos_duck = stem('efeitos-duck', [chaves['efeitos-base'], intervalos, edcfg, cfg['protecao']],
                        lambda: efeitos * ed[:, None])
    premix = (voz + md + efeitos_duck).astype(np.float32)
    salvar(saida / 'premix.wav', premix)
    gravar_json(saida / 'mixagem.json', cfg)
    manifesto = {'versao': 1, 'sample_rate': SR, 'amostras': n, 'regua_sha256': hash_json(T),
                 'config_sha256': hash_json(cfg), 'frases': frases, 'eventos': inventario,
                 'janelas_fala': T['falas'] if T.get('audio_blocos') else [],
                 'intervalos_duck_s': intervalos,
                 'stems': caminhos, 'chaves': chaves,
                 'sha256_stems': {k: hash_arquivo(p) for k, p in caminhos.items()},
                 'premix_sha256': hash_arquivo(saida / 'premix.wav'),
                 'aprovacao_ouvido': None, 'scribe': 'pendente; nenhuma chamada automática'}
    gravar_json(saida / 'manifesto.json', manifesto)
    return manifesto


def masterizar(saida, cfg):
    """Normalização real em duas passagens e aceite sobre o AAC decodificado."""
    try:
        from .conferir_audio import conferir_final, atraso_amostras
    except ImportError:
        from conferir_audio import conferir_final, atraso_amostras
    saida = pathlib.Path(saida)
    entrada, destino = saida / 'premix.wav', saida / 'master.wav'
    premix = ler(entrada, 2)
    if cfg['master']['limitador_extra']:
        raise ValueError('Limiter extra exige implementação/A-B aprovados; não está habilitado')
    c = cfg['master']; alvo = c['integrado_lufs']; teto = c['true_peak_pcm_alvo_dbtp']
    tentativas = []
    for tentativa in range(3):
        m = medir_loudness(entrada, alvo, teto, c['lra_parametro_lu'])
        filtro = (f"loudnorm=I={alvo}:TP={teto}:LRA={c['lra_parametro_lu']}"
                  f":measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}"
                  f":measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true:print_format=json")
        r = subprocess.run(['ffmpeg', '-hide_banner', '-y', '-i', str(entrada), '-af', filtro,
                            '-ar', str(SR), '-c:a', 'pcm_s24le', str(destino)],
                           capture_output=True, text=True, check=True)
        passagem2 = json.loads(r.stderr[r.stderr.rindex('{'):r.stderr.rindex('}') + 1])
        master = ler(destino, 2)
        if len(master) != len(premix):
            raise ValueError('Master mudou o número de amostras; não truncar para esconder')
        atraso = atraso_amostras(premix, master)
        pcm = medir_loudness(destino)
        aac = saida / 'verificacao.m4a'
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(destino), '-c:a', 'aac',
                        '-b:a', '256k', '-ar', str(SR), '-ac', '2',
                        '-metadata:s:a:0', 'language=por', '-metadata',
                        'comment=Narração com voz sintética (IA)', str(aac)], check=True)
        resultado = conferir_final(aac, cfg, premix)
        salvar(saida / 'aac-decodificado.wav', ler(aac, 2))
        tentativas.append({'teto_solicitado_dbtp': teto, 'aac': resultado,
                           'pcm_lufs': float(pcm['input_i']), 'pcm_dbtp': float(pcm['input_tp'])})
        rel = {'passagem1': m, 'passagem2': passagem2, 'filtro': filtro, 'tentativas': tentativas,
               'aac': resultado, 'pcm': pcm, 'master_atraso_amostras': atraso,
               'premix_sha256': hash_arquivo(entrada), 'master_sha256': hash_arquivo(destino),
               'config_sha256': hash_json(cfg), 'limitador_extra': False}
        gravar_json(saida / 'master.json', rel)
        pcm_ok = float(pcm['input_tp']) <= c['true_peak_pcm_alvo_dbtp'] + .05
        if resultado['ok'] and pcm_ok and abs(atraso) <= round(.01 * SR):
            return rel
        if float(resultado['true_peak_dbtp']) > c['true_peak_aac_max_dbtp'] or not pcm_ok:
            teto -= .5
        else:
            break
    raise ValueError('Master/AAC fora dos limites; ver master.json (não aceito)')


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('idioma', nargs='?', default='pt')
    ap.add_argument('--regua', type=pathlib.Path); ap.add_argument('--eventos', type=pathlib.Path)
    ap.add_argument('--config', type=pathlib.Path, default=AQUI / 'mixagem.json')
    ap.add_argument('--saida', type=pathlib.Path); ap.add_argument('--trilha', type=pathlib.Path, default=TRILHA)
    ap.add_argument('--voz-dir', type=pathlib.Path)
    args = ap.parse_args()
    cfg = json.loads(args.config.read_text())
    T = json.loads((args.regua or AQUI / f'tempos-{args.idioma}.json').read_text())
    eventos = (json.loads((args.eventos or AQUI / f'eventos-{args.idioma}.json').read_text())
               if cfg['efeitos'].get('habilitado', True) else [])
    saida = args.saida or AQUI / f'cache/audio/{args.idioma}'
    montar(T, eventos, cfg, saida, args.trilha, args.voz_dir or AQUI / f'cache/voz/{args.idioma}')
    try:
        from .conferir_audio import conferir_sessao
    except ImportError:
        from conferir_audio import conferir_sessao
    qa = conferir_sessao(saida, cfg)
    if not qa['tecnico_ok']:
        raise ValueError('QA de stems bloqueou master: ' + '; '.join(qa['falhas']))
    rel = masterizar(saida, cfg)
    qa_final = conferir_sessao(saida, cfg, final=saida / 'verificacao.m4a')
    if not qa_final['tecnico_ok']:
        raise ValueError('QA final bloqueou a saída; ver qa.json')
    if args.saida is None:
        # Compatível com mux.sh; a sessão/stems continua sendo a origem auditável.
        shutil.copyfile(saida / 'master.wav', AQUI / f'cache/mix-{args.idioma}.wav')
    print(f"{args.idioma}: {rel['aac']['integrado_lufs']:.2f} LUFS; "
          f"{rel['aac']['true_peak_dbtp']:.2f} dBTP no AAC. QA: {saida / 'qa.json'}")


if __name__ == '__main__':
    main()
