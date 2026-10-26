"""v4: mede as frases e monta a régua de cada idioma (tempos-pt.json, tempos-en.json) sobre a grade da trilha.

Trilha: "Talent in the Air" (Diego Nava, Mixkit), 122 BPM medidos com librosa: 1 tempo = 0,4918 s, 1 compasso = 1,967 s.
Cada idioma tem a própria régua (o inglês fala mais devagar); a música é remontada por compassos para cada régua (audio2.py).
- Cenas começam num tempo da grade; c05, c09 e c12 começam num compasso, porque nelas a música muda de seção.
- Frases começam num meio tempo. O vídeo termina no fim de um compasso.
Uso: .venv/bin/python tempos2.py
"""
import json, math, pathlib, re, subprocess
import numpy as np

AQUI = pathlib.Path(__file__).resolve().parent
VIDEO = AQUI.parent
SR = 48000
P = 0.491835                     # período do tempo (s), regressão linear das batidas da trilha
O = 1.014                        # primeiro tempo forte da trilha (s)
BAR = 4 * P
VOZES = {"pt": VIDEO / "vozes/frases/pt", "en": VIDEO / "vozes/frases-kokoro/en"}
ENTRADA = {"c01-gancho": 2 * P}  # o gancho espera o ponto laranja assentar (2 tempos); as outras cenas falam meio tempo depois do corte
ENTRADA_PADRAO = P / 2
PAUSA = 0.10
CAUDA = 0.30
NO_COMPASSO = {"c05-o-que-e", "c09-cadastro", "c12-confianca"}
DURACAO_MIN = {"c01-gancho": 3.4, "c02-promessa": 3.4, "c03-rotatividade": 3.9, "c04-contratar": 3.4, "c05-o-que-e": 3.9, "c06-passos-a": 0,
               "c07-passos-b": 5.4, "c08-mapa": 5.9, "c09-cadastro": 2.9, "c10-concorrente": 5.4, "c11-contraste": 3.4,
               "c12-confianca": 4.9, "c13-estagio": 3.9, "c14-gratis": 2.9, "c16-logo": 6.8}


def sobe(t, passo):
    return math.ceil(round(t / passo, 6)) * passo


def ler(p):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(p), "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.float32)


def aparar(x, limiar_db=-60, folga=0.06, folga_fim=0.12, rampa_ini=0.008, rampa_fim=0.04):
    """v5: corta só o silêncio das pontas, sem comer a consoante fraca do começo nem a cauda do fim.
    A v4 usava -45 dBFS, 30 ms antes e 70 ms depois; com a voz do ElevenLabs (quase sem silêncio antes) isso comia 40 a 60 ms
    do início de 12 das 20 frases (ex.: 'Turno' virava 'termo'). Agora: limiar -60 dBFS, 60 ms antes, 120 ms depois,
    entrada em 8 ms (sem estalo) e saída em 40 ms."""
    env = np.convolve(np.abs(x), np.ones(240) / 240, mode="same")
    vivo = np.nonzero(env > 10 ** (limiar_db / 20))[0]
    a = max(0, vivo[0] - int(folga * SR))
    b = min(len(x), vivo[-1] + int(folga_fim * SR))
    y = x[a:b].copy()
    n = min(len(y), int(rampa_fim * SR)); y[-n:] *= np.linspace(1, 0, n)
    m = min(len(y), int(rampa_ini * SR)); y[:m] *= np.linspace(0, 1, m)
    return y


def frases(texto):
    return re.split(r"(?<=[.?!])\s+", texto.strip())


def secoes(cenas, total):
    """Remonta a trilha por compassos: intro até c05, groove até c09, quebra até c12, groove de novo até o fim.
    Cada bloco termina no compasso de virada da própria trilha (7, 23, 31), para a virada cair no corte."""
    ini = {c["id"]: round(c["ini"] / BAR) for c in cenas}
    n_total = round(total / BAR)
    a, b, c = ini["c05-o-que-e"], ini["c09-cadastro"], ini["c12-confianca"]

    def bloco(n, primeiro, ultimo_util, virada, laço):
        if n <= 0:
            return []
        corpo = list(range(primeiro, ultimo_util + 1))
        while len(corpo) < n - 1:
            corpo += list(range(*laço))
        return corpo[: n - 1] + [virada]

    barras = (list(range(8 - a, 8)) if a <= 8 else bloco(a, 0, 6, 7, (1, 7))) \
        + bloco(b - a, 8, 22, 23, (9, 23)) \
        + bloco(c - b, 24, 30, 31, (25, 31)) \
        + [32 + (i % 16) for i in range(n_total - c)]
    return [{"v": round(i * BAR, 4), "src": O + s * BAR} for i, s in enumerate(barras)]


def main():
    roteiro = json.loads((VIDEO / "roteiro.json").read_text())["cenas"]
    for L in ("pt",):
        limpo = AQUI / "cache/voz" / L
        limpo.mkdir(parents=True, exist_ok=True)
        cenas, falas, t = [], [], 0.0
        for c in roteiro:
            if c["id"] in NO_COMPASSO:
                t = sobe(t, BAR)
            ini = t + ENTRADA.get(c["id"], ENTRADA_PADRAO)
            lista = []
            for k, leg in enumerate(frases(c[L]["legenda"]), 1):
                x = aparar(ler(VOZES[L] / f"{c['id']}-{k}.wav"))
                np.save(limpo / f"{c['id']}-{k}.npy", x)
                d = len(x) / SR
                lista.append({"cena": c["id"], "k": k, "ini": round(ini, 3), "fim": round(ini + d, 3), "legenda": leg})
                ini = sobe(ini + d + PAUSA, P / 2)
            dur = max(sobe(lista[-1]["fim"] + CAUDA - t, P), sobe(DURACAO_MIN.get(c["id"], 0), P))
            if c is roteiro[-1]:
                dur = sobe(t + dur, BAR) - t
            cenas.append({"id": c["id"], "ini": round(t, 4), "dur": round(dur, 4)})
            falas += lista
            t += dur
        # a cena anterior a um corte de compasso estica até ele
        for i in range(len(cenas) - 1):
            cenas[i]["dur"] = round(cenas[i + 1]["ini"] - cenas[i]["ini"], 4)
        for i, f in enumerate(falas):
            cena = next(c for c in cenas if c["id"] == f["cena"])
            prox = falas[i + 1]["ini"] if i + 1 < len(falas) and falas[i + 1]["cena"] == f["cena"] else None
            f["leg_ini"] = round(f["ini"] - 0.05, 3)
            f["leg_fim"] = round(prox - 0.05 if prox else min(f["fim"] + 0.6, cena["ini"] + cena["dur"] - 0.12), 3)
        total = round(t, 4)
        saida = {"lang": L, "P": P, "bar": BAR, "total": total, "cenas": cenas, "falas": falas, "musica": secoes(cenas, total)}
        (AQUI / f"tempos-{L}.json").write_text(json.dumps(saida, ensure_ascii=False, indent=1))
        print(L, "total", total, " ".join(f'{c["id"][:3]}@{c["ini"]:.1f}' for c in cenas))


main()
