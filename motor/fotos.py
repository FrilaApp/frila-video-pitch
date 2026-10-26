"""Quadros de teste: .venv/bin/python fotos.py pt 1.2 3.5 ...  (ou 'cenas' para 3 quadros por cena). Saída em cache/fotos/."""
import json, sys, os, pathlib, threading, functools, http.server
from playwright.sync_api import sync_playwright
AQUI = pathlib.Path(__file__).resolve().parent
RAIZ = AQUI.parent  # raiz do repositório (o filme.html carrega ../assets/)
os.environ.setdefault("PLAYWRIGHT_BROWSERS_PATH", str(AQUI / "browsers"))

def servidor():
    h = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(RAIZ))
    class H(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a): pass
    h = functools.partial(H, directory=str(RAIZ))
    s = http.server.ThreadingHTTPServer(("127.0.0.1", 0), h)
    threading.Thread(target=s.serve_forever, daemon=True).start()
    return s

def abrir(pw, L, url):
    b = pw.chromium.launch(args=["--force-color-profile=srgb", "--disable-lcd-text"])
    pg = b.new_page(viewport={"width": 1920, "height": 1080}, device_scale_factor=1)
    erros = []
    pg.on("pageerror", lambda e: erros.append(str(e)))
    pg.on("console", lambda m: m.type == "error" and erros.append(m.text))
    pg.goto(url)
    tempos = json.loads((AQUI / f"tempos-{L}.json").read_text())
    info = pg.evaluate("([t,l])=>window.boot(t,l)", [tempos, L])
    return b, pg, tempos, info, erros

if __name__ == "__main__":
    L = sys.argv[1]
    s = servidor()
    url = f"http://127.0.0.1:{s.server_port}/video/motor2/filme.html"
    out = AQUI / "cache/fotos" / L; out.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as pw:
        b, pg, tempos, info, erros = abrir(pw, L, url)
        print("boot", info, erros)
        if sys.argv[2] == "cenas":
            ts = []
            for c in tempos["cenas"]:
                ts += [c["ini"] + c["dur"] * k for k in (.25, .55, .85)]
        else:
            ts = [float(x) for x in sys.argv[2:]]
        for t in ts:
            pg.evaluate(f"window.seek({t})")
            pg.screenshot(path=str(out / f"{t:07.3f}.png"))
        print(len(ts), "quadros", erros)
        b.close()
