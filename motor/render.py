"""Render do filme: .venv/bin/python render.py pt [inicio fim]
240 quadros por segundo no Chromium, 4 subquadros misturados (tmix) para 60 fps com desfoque de movimento.
Cada trabalhador renderiza um trecho contínuo (múltiplo de 4 quadros) em H.264; no fim os trechos são concatenados.
Também grava eventos-<L>.json (cliques, toques) para o audio2.py."""
import json, sys, os, pathlib, subprocess, multiprocessing as mp
AQUI = pathlib.Path(__file__).resolve().parent
os.environ.setdefault("PLAYWRIGHT_BROWSERS_PATH", str(AQUI / "browsers"))
FPS, SUB = 60, 4
N_TRAB = 6

def trabalho(arg):
    L, porta, q0, q1, saida = arg
    from playwright.sync_api import sync_playwright
    from fotos import abrir
    ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "image2pipe", "-framerate", str(FPS * SUB), "-c:v", "mjpeg", "-i", "-",
                           "-vf", f"tmix=frames={SUB},select='not(mod(n+1\\,{SUB}))',setpts=N/{FPS}/TB",
                           "-r", str(FPS), "-c:v", "libx264", "-preset", "medium", "-crf", "14", "-pix_fmt", "yuv420p",
                           "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709", str(saida)], stdin=subprocess.PIPE)
    with sync_playwright() as pw:
        b, pg, tempos, info, erros = abrir(pw, L, f"http://127.0.0.1:{porta}/motor/filme.html")
        for q in range(q0, q1):
            # o subquadro k do quadro final n cobre (n - 1 + (k+1)/4)/60: o quadro n é a média do intervalo que termina nele
            t = (q + 1) / (FPS * SUB) - 1 / (FPS * SUB) * (SUB - 1) / 2
            pg.evaluate(f"window.seek({t:.6f})")
            ff.stdin.write(pg.screenshot(type="jpeg", quality=94))
        b.close()
    ff.stdin.close(); ff.wait()
    return saida, erros

if __name__ == "__main__":
    L = sys.argv[1]
    tempos = json.loads((AQUI / f"tempos-{L}.json").read_text())
    t0, t1 = (float(sys.argv[2]), float(sys.argv[3])) if len(sys.argv) > 3 else (0, tempos["total"])
    from fotos import servidor
    s = servidor()
    n0, n1 = round(t0 * FPS), round(t1 * FPS)
    pasta = AQUI / "cache/render" / L; pasta.mkdir(parents=True, exist_ok=True)
    for v in pasta.glob("*.mp4"): v.unlink()
    passo = -(-(n1 - n0) // N_TRAB)
    tarefas = [(L, s.server_port, a * SUB, min(a + passo, n1) * SUB, pasta / f"p{i:02d}.mp4") for i, a in enumerate(range(n0, n1, passo))]
    with mp.get_context("spawn").Pool(len(tarefas)) as pool:
        res = pool.map(trabalho, tarefas)
    for _, e in res:
        if e: print("erros:", e[:3])
    lista = pasta / "lista.txt"
    lista.write_text("".join(f"file '{r[0]}'\n" for r in res))
    final = AQUI / "cache" / f"filme-{L}{'' if len(sys.argv) <= 3 else '-trecho'}.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lista), "-c", "copy", str(final)], check=True)
    # eventos de som
    from playwright.sync_api import sync_playwright
    from fotos import abrir
    with sync_playwright() as pw:
        b, pg, *_ = abrir(pw, L, f"http://127.0.0.1:{s.server_port}/motor/filme.html")
        (AQUI / f"eventos-{L}.json").write_text(json.dumps(pg.evaluate("window.eventos"), indent=0))
        b.close()
    print("ok", final)
