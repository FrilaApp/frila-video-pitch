"""v4: trilha remontada, voz e efeitos de UI, mix final por idioma.

- Música: "Talent in the Air" (Diego Nava, Mixkit, Mixkit Stock Music Free License), em video/musica/.
  Remontada por compassos: cada item de tempos-<L>.json["musica"] diz de onde (src) o compasso sai da trilha e onde (v) ele entra no vídeo.
  Emendas com 6 ms de crossfade; o último compasso apaga até o fim.
- Voz: as frases aparadas (cache/voz/<L>/*.npy) entram no "ini" de cada fala.
- Efeitos: sintetizados aqui, um por evento de eventos-<L>.json (o render grava os cliques, toques e pousos que a imagem faz).
- A música abaixa 11 dB quando a voz fala. Mix final a -16 LUFS integrado, pico -1,5 dBTP.
Uso: .venv/bin/python audio2.py [pt|en]   →  cache/mix-<L>.wav
"""
import json, pathlib, subprocess, sys
import numpy as np

AQUI = pathlib.Path(__file__).resolve().parent
VIDEO = AQUI.parent
SR = 48000
TRILHA = VIDEO / "musica/talent-in-the-air-diego-nava-mixkit.mp3"
XF = int(.006 * SR)
VOZ_RMS_DB = -20
MUSICA_RMS_DB = -24
DUCK_DB = -11
rng = np.random.default_rng(7)


def ler(p, canais):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(p), "-f", "f32le", "-ac", str(canais), "-ar", str(SR), "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.float32).reshape(-1, canais).astype(float)


def db(x):
    return 20 * np.log10(np.sqrt(np.mean(np.square(x))) + 1e-12)


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
def clique():
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


def swish():
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


def grave():
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
def musica(T, N):
    src = ler(TRILHA, 2)
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


def voz(T, L, N):
    v = np.zeros(N)
    for f in T["falas"]:
        soma(v, f["ini"], np.load(AQUI / f"cache/voz/{L}/{f['cena']}-{f['k']}.npy").astype(float))
    return v


def ducking(v, N, bloco=480):
    """Ganho da música: abaixa 150 ms antes da fala, segura 250 ms e volta em ~400 ms."""
    nb = len(v) // bloco
    at = np.sqrt(np.mean(np.square(v[:nb * bloco].reshape(nb, bloco)), axis=1)) > 10 ** (-45 / 20)
    a = at.astype(float)
    adiante = np.concatenate([a[15:], np.zeros(15)])
    segura = np.convolve(a, np.ones(25), mode="full")[:len(a)] > 0
    alvo = np.convolve(np.maximum(adiante, segura).astype(float), np.ones(40) / 40, mode="same")
    g = np.repeat(10 ** (DUCK_DB * np.clip(alvo, 0, 1) / 20), bloco)
    falando = np.repeat(at, bloco)
    pad = N - len(g)
    return np.concatenate([g, np.full(pad, g[-1])]), np.concatenate([falando, np.zeros(pad, bool)])


def efeitos(L, N):
    s = np.zeros(N)
    for e in json.loads((AQUI / f"eventos-{L}.json").read_text()):
        f, g = EFEITOS[e["tipo"]]
        soma(s, e["t"], f(), g * e.get("forca", 1))
    return s


def salvar(p, x):
    x = np.asarray(x, dtype=np.float32)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", str(x.shape[1]), "-i", "-",
                    "-c:a", "pcm_s24le", str(p)], input=x.tobytes(), check=True)


def loudnorm(entrada, saida):
    filtro = "loudnorm=I=-16:TP=-1.5:LRA=11"
    r = subprocess.run(["ffmpeg", "-v", "info", "-i", str(entrada), "-af", filtro + ":print_format=json", "-f", "null", "-"],
                       capture_output=True, text=True, check=True).stderr
    m = json.loads(r[r.rindex("{"):r.rindex("}") + 1])
    f2 = (f"{filtro}:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}"
          f":measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true"
          # limitador sobreamostrado: segura o pico real em -1,5 dBTP sem mexer na loudness
          ",aresample=192000,alimiter=limit=0.74:attack=1:release=60:level=false,aresample=48000")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(entrada), "-af", f2, "-ar", str(SR), "-c:a", "pcm_s24le", str(saida)],
                   check=True)


def main(L):
    T = json.loads((AQUI / f"tempos-{L}.json").read_text())
    N = int(round(T["total"] * SR))
    v = voz(T, L, N)
    g, falando = ducking(v, N)
    v *= 10 ** ((VOZ_RMS_DB - db(v[falando])) / 20)
    mus = musica(T, N)
    mus *= 10 ** ((MUSICA_RMS_DB - db(mus[~falando])) / 20)
    m = mus * g[:, None]
    sfx = efeitos(L, N) * 10 ** ((MUSICA_RMS_DB + 3) / 20) / .1
    mix = m + (v + sfx)[:, None]
    k = int(.02 * SR)
    mix[-k:] *= np.linspace(1, 0, k)[:, None]
    mix /= max(1.0, np.abs(mix).max() / .98)
    bruto = AQUI / f"cache/mix-bruto-{L}.wav"
    salvar(bruto, mix)
    loudnorm(bruto, AQUI / f"cache/mix-{L}.wav")
    print(f"{L}: voz {db(v[falando]):.1f} dB RMS, música sob a voz {db(m[falando]):.1f} dB RMS "
          f"(voz {db(v[falando]) - db(m[falando]):.1f} dB acima), música sem voz {db(m[~falando]):.1f} dB")


if __name__ == "__main__":
    for L in sys.argv[1:] or ("pt",):
        main(L)
