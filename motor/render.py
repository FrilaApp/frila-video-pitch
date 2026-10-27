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
    L, porta, q0, q1, saida, *extra = arg
    import time
    from playwright.sync_api import sync_playwright
    from fotos import abrir
    regua = extra[0] if extra else None
    # JPEG do Chromium é full-range. Converter amostras antes de sinalizar tv;
    # pix_fmt sozinho não elimina a sinalização full-range herdada do decoder.
    filtro = ("scale=1920:1080:flags=lanczos:in_range=pc:out_range=tv:out_color_matrix=bt709,"
              if regua else "scale=iw:ih:in_range=pc:out_range=tv:out_color_matrix=bt709,")
    filtro += f"tmix=frames={SUB},select='not(mod(n+1\\,{SUB}))',setpts=N/{FPS}/TB"
    filtro += ",format=yuv420p,setparams=range=limited:color_primaries=bt709:color_trc=bt709:colorspace=bt709"
    erros = []
    with sync_playwright() as pw:
        if regua:
            b = pw.chromium.launch(args=["--force-color-profile=srgb", "--disable-lcd-text"])
            pg = b.new_page(viewport={"width":1920, "height":1080}, device_scale_factor=2)
            pg.on('pageerror', lambda e: erros.append(str(e)))
            url = f"http://127.0.0.1:{porta}/motor/filme.html"
            for tentativa in range(5):
                try:
                    pg.goto(url)
                    pg.evaluate('r=>window.boot(r,"pt")', regua)
                    break
                except Exception:
                    if tentativa == 4: raise
                    time.sleep(0.5 * (tentativa + 1))
        else:
            b, pg, _, _, erros = abrir(pw, L, f"http://127.0.0.1:{porta}/motor/filme.html")
        ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "image2pipe", "-framerate", str(FPS*SUB), "-c:v", "mjpeg", "-i", "-",
            "-vf", filtro, "-r", str(FPS), "-an", "-c:v", "libx264", "-preset", "medium", "-crf", "14", "-pix_fmt", "yuv420p",
            "-color_range", "tv", "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709", str(saida)], stdin=subprocess.PIPE)
        try:
            for q in range(q0, q1):
                t = (q+1)/(FPS*SUB) - (SUB-1)/(2*FPS*SUB)
                pg.evaluate('(t)=>window.seek(t)', t)
                ff.stdin.write(pg.screenshot(type="jpeg", quality=94))
                if regua and (q-q0) % 480 == 0:
                    print(f'{saida.name}: {q-q0}/{q1-q0} subquadros', flush=True)
        finally:
            b.close()
            ff.stdin.close()
            retorno = ff.wait()
        if retorno: raise RuntimeError(f'FFmpeg falhou no trecho {saida}')
    return saida, erros


def preparar_bloco(regua, margem_quadros=15):
    """Conserva o relógio oficial e acrescenta apenas margem de imagem no fim."""
    import copy
    import math
    bloco = regua.get('bloco')
    if bloco not in ('A', 'B', 'C', 'D'):
        raise ValueError('Somente os blocos A, B, C e D foram autorizados nesta etapa.')
    if margem_quadros < 12:
        raise ValueError('A margem de transição exige pelo menos 12 quadros.')
    r = copy.deepcopy(regua)
    nomes = (['v01-gancho', 'v02-dor1', 'v03-dor2', 'v04-dor3'] if bloco == 'A'
             else ['v05-virada', 'v06-solucao1', 'v07-solucao2', 'v09-solucao3'] if bloco == 'B'
             else ['v10-dado', 'v11-meta', 'v12-estrategia'] if bloco == 'C'
             else ['v13-fecho', 'v14-assinatura'])
    if [c['id'] for c in r['cenas']] != nomes:
        raise ValueError(f'Régua do {bloco} deve conter exatamente {nomes}, em ordem.')
    fim = 0.
    for c in r['cenas']:
        if not all(math.isfinite(c[k]) for k in ('ini', 'dur')) or c['dur'] <= 0 or abs(c['ini']-fim) > 1e-6:
            raise ValueError('Régua com lacuna, sobreposição ou duração inválida.')
        fim = c['ini'] + c['dur']
    nominal = r.get('duracao', r.get('total'))
    if nominal is None or abs(fim-nominal) > 1e-6:
        raise ValueError('Cenas não cobrem a duração oficial.')
    for f in r['falas']:
        c = next((c for c in r['cenas'] if c['id'] == f['cena']), None)
        if not c or not c['ini'] <= f['ini'] < f['fim'] <= c['ini']+c['dur']:
            raise ValueError('Fala fora de sua janela oficial.')
    r.update(total=(math.ceil(nominal*FPS-1e-7)+margem_quadros)/FPS,
             bloco_fim=nominal, voz_duracao=r.get('duracao_voz', nominal),
             P=regua.get('P', .491835), margem_quadros=margem_quadros)
    r['cenas'][-1]['dur'] = r['total']-r['cenas'][-1]['ini']
    r['cenas'][-1]['fim'] = r['total']
    return r


def render_bloco(args):
    import hashlib
    import math
    from fotos import servidor
    regua_original = json.loads(args.regua.read_text())
    if args.bloco != regua_original.get('bloco'):
        raise ValueError('Bloco solicitado difere da régua fornecida.')
    regua = preparar_bloco(regua_original, args.margem_quadros)
    pasta = args.saida or AQUI/f'cache/bloco-{args.bloco.lower()}-imagem'
    pasta.mkdir(parents=True, exist_ok=True)
    (pasta/'regua-oficial.json').write_text(json.dumps(regua_original, ensure_ascii=False, indent=2)+'\n')
    (pasta/'tempos.json').write_text(json.dumps(regua, ensure_ascii=False, indent=2)+'\n')
    fonte = (AQUI/'filme.html').read_text()
    (pasta/'filme.html').write_text(fonte.replace('<head>', '<head><base href="/motor/">', 1))
    if args.bloco == 'A':
        contrato = dict(presenca=[dict(id='ponto', selector='#dot', de=0, ate=regua['total'], opacidade_min=.999)],
            movimento=[dict(de=a, ate=b) for a,b in [( .24,1.7), (regua.get('voz_ini',0)+1.87,regua['cenas'][1]['ini']+.8),
                (regua['cenas'][1]['ini']+.5,regua['cenas'][1]['ini']+1.8),
                (regua['cenas'][2]['ini']-.5,regua['cenas'][2]['ini']+2.57),
                (regua['falas'][-2]['ini']-.5,regua['cenas'][3]['ini']+.4),
                (regua['cenas'][3]['ini']+.4,regua['cenas'][3]['ini']+3.45),
                (regua['bloco_fim']-2.1,regua['bloco_fim']-.2)]])
    elif args.bloco == 'B':
        contrato = dict(presenca=[
            dict(id='chassi', selector='#dot', de=0, ate=regua['total'], opacidade_min=.999),
            dict(id='tela', selector='#scr', de=2.2, ate=regua['total'], opacidade_min=.999)],
            movimento=[dict(de=a,ate=b) for a,b in [(.12,2.2),(2.5,3.65),(4.45,5.6),
                (6.16,7.2),(8.42,9.2),(10.14,11.04),(12.74,13.44),
                (14.1,15.4),(16.05,16.8),(17.1,17.4),(18.45,19.62)]])
    elif args.bloco == 'C':
        c11 = regua['cenas'][1]['ini']
        c12 = regua['cenas'][2]['ini']
        contrato = dict(presenca=[
            dict(id='ponto', selector='#dot', de=0, ate=regua['total'], opacidade_min=.999)],
            movimento=[dict(de=a, ate=b) for a,b in [(.1, 1.8), (2.5, 3.5),
                (c11-.2, c11+.9), (c11+1.5, c11+3.0), (c11+3.2, c11+4.8), (c11+5.2, c11+6.5),
                (c12-.2, c12+1.0), (c12+3.0, c12+4.5), (c12+6.0, c12+7.5)]])
    elif args.bloco == 'D':
        contrato = dict(presenca=[
            dict(id='ponto', selector='#dot', de=0, ate=regua['total'], opacidade_min=.999)],
            movimento=[dict(de=a, ate=b) for a,b in [(.1, 1.8), (2.0, 3.4), (3.8, 5.4),
                (5.6, 7.0), (10.8, 11.8)]])
    else:
        contrato = {}
    (pasta/'contrato.json').write_text(json.dumps(contrato, indent=2)+'\n')
    s = servidor()
    final = pasta/f'bloco-{args.bloco.lower()}-sem-audio.mp4'
    partes = pasta/'partes'; partes.mkdir(exist_ok=True)
    n = round(regua['total']*FPS)
    passo = math.ceil(n/args.trabalhadores)
    tarefas = [(args.idioma, s.server_port, a*SUB, min(a+passo, n)*SUB,
                partes/f'p{i:02d}.mp4', regua) for i, a in enumerate(range(0, n, passo))]
    try:
        with mp.get_context('spawn').Pool(len(tarefas)) as pool:
            res = pool.map(trabalho, tarefas)
        for _, erros in res:
            if erros: raise RuntimeError('Erros na fonte do bloco: '+str(erros))
        lista = partes/'lista.txt'
        lista.write_text(''.join(f"file '{r[0].resolve()}'\n" for r in res))
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', str(lista), '-c', 'copy', '-video_track_timescale', str(FPS), str(final)], check=True)
        if args.bloco in ('A', 'B', 'C', 'D'):
            from playwright.sync_api import sync_playwright
            with sync_playwright() as pw:
                b = pw.chromium.launch()
                pg = b.new_page(viewport={"width": 1920, "height": 1080})
                pg.goto(f"http://127.0.0.1:{s.server_port}/motor/filme.html")
                pg.evaluate('r=>window.boot(r,"pt")', regua)
                pg.evaluate('t=>window.seek(t)', regua['bloco_fim'])
                fim = pg.evaluate(f'()=>window.estadoBloco{args.bloco}()')
                b.close()
            (pasta/f'estado-fim-{args.bloco}.json').write_text(json.dumps(fim, ensure_ascii=False, indent=2)+'\n')
    finally:
        s.shutdown(); s.server_close()
    manifesto = dict(bloco=args.bloco, arquivo=str(final.resolve()), frames=n, fps=FPS, subquadros=SUB,
        deviceScaleFactor=2, reducao='Lanczos 3840×2160 → 1920×1080 antes da mistura temporal',
        duracao_render=regua['total'], fim_nominal=regua['bloco_fim'],
        margem_quadros=regua['margem_quadros'], regua_origem=str(args.regua.resolve()),
        regua_sha256=hashlib.sha256(args.regua.read_bytes()).hexdigest(),
        html_sha256=hashlib.sha256(fonte.encode()).hexdigest(),
        camera=('identidade no ancestral comum #world' if args.bloco in ('A', 'D')
                else 'matriz única em #b-camera, chassi+tela+ilha+UI' if args.bloco == 'B'
                else 'identidade no mundo (#world); transformações e mapa vetoriais (#c-mapa, #dot)'),
        audio=False, voz_arquivo=regua_original.get('arquivo'), voz_sha256=regua_original.get('sha256'))
    (pasta/'manifesto-render.json').write_text(json.dumps(manifesto, ensure_ascii=False, indent=2)+'\n')
    print('ok', final, flush=True)


if __name__ == "__main__":
    if '--bloco' in sys.argv:
        import argparse
        parser = argparse.ArgumentParser(description='Imagem por bloco com régua oficial e margem de transição.')
        parser.add_argument('idioma', choices=['pt'])
        parser.add_argument('--bloco', choices=['A', 'B', 'C', 'D'], required=True)
        parser.add_argument('--regua', type=pathlib.Path, required=True)
        parser.add_argument('--saida', type=pathlib.Path)
        parser.add_argument('--margem-quadros', type=int, default=15)
        parser.add_argument('--trabalhadores', type=int, default=N_TRAB, choices=range(1, N_TRAB+1))
        render_bloco(parser.parse_args())
        raise SystemExit(0)
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
