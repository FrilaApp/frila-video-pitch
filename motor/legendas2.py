"""v4: gera ../pt/frila-pitch-pt.srt e ../en/frila-pitch-en.srt de tempos-<L>.json (mesmo texto e tempos da legenda queimada).
Quebra em no máximo 2 linhas equilibradas (até 58 caracteres cada). Uso: .venv/bin/python legendas2.py
"""
import json, pathlib

AQUI = pathlib.Path(__file__).resolve().parent


def ts(s):
    ms = int(round(s * 1000))
    return f"{ms // 3600000:02}:{ms // 60000 % 60:02}:{ms // 1000 % 60:02},{ms % 1000:03}"


def duas_linhas(txt):
    """Uma linha se couber em 42; senão, corta no espaço que deixa as duas linhas mais parecidas (sem palavra órfã)."""
    if len(txt) <= 42:
        return [txt]
    espacos = [i for i, c in enumerate(txt) if c == " "]
    # prefere cortar depois de vírgula, se não desequilibrar demais
    i = min(espacos, key=lambda i: abs(len(txt) - 2 * i - 1) - (20 if txt[i - 1] in ",;:" else 0))
    return [txt[:i], txt[i + 1:]]


for L in ("pt",):
    blocos = []
    for i, f in enumerate(json.loads((AQUI / f"tempos-{L}.json").read_text())["falas"], 1):
        linhas = duas_linhas(f["legenda"])
        assert len(linhas) <= 2 and max(map(len, linhas)) <= 58, f["legenda"]
        blocos.append(f"{i}\n{ts(f['leg_ini'])} --> {ts(f['leg_fim'])}\n" + "\n".join(linhas))
    p = AQUI.parent / L / f"frila-pitch-{L}.srt"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("\n\n".join(blocos) + "\n", encoding="utf-8")
    print(p.relative_to(AQUI.parent), len(blocos), "legendas")
