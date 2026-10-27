"""Quadros de teste: .venv/bin/python fotos.py pt 1.2 3.5 ...  (ou 'cenas' para 3 quadros por cena). Saída em cache/fotos/.
Da raiz: .venv/bin/python motor/fotos.py --estudo-aparelho exporta o estudo D6/D7/D8 documentado em DESIGN.md §24."""
import json, sys, os, pathlib, threading, functools, http.server, time
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
    tempos = json.loads((AQUI / f"tempos-{L}.json").read_text())
    # v5: o render abre 6 páginas de uma vez; uma falha de rede passageira (visto 1 vez em 5 execuções) não deve derrubar tudo
    for tentativa in range(3):
        try:
            pg.goto(url)
            info = pg.evaluate("([t,l])=>window.boot(t,l)", [tempos, L])
            break
        except Exception as e:
            if tentativa == 2: raise
            erros.clear(); time.sleep(1 + tentativa)
    return b, pg, tempos, info, erros

def camera_estudo(t):
    """Câmera externa comum ao chassi/UI; parallax só nos planos externos."""
    def eio(u):
        u = max(0, min(1, u))
        return 4*u**3 if u < .5 else 1-(-2*u+2)**3/2
    foco = eio((t-.6)/.7) * (1-eio((t-2)/.9))
    return dict(zoom=1+.1*foco, x=-14*foco, y=6*foco)


def tempo_v4_estudo(t):
    """Isola o gesto da v4 para o ensaio; não é a régua de uma cena nova."""
    pontos=[(0,25.55),(.6,25.55),(1.3,25.792),(1.9,26.312),(2.1,26.55),(3.6,26.55)]
    for (a,x),(b,y) in zip(pontos,pontos[1:]):
        if t<=b:
            return x+(y-x)*max(0,min(1,(t-a)/(b-a)))
    return pontos[-1][1]


PREPARAR_ESTUDO = r"""(textos) => {
 const q=s=>document.querySelector(s),stage=q('#stage');
 for(const s of ['#pss','#ind','.stp'])document.querySelectorAll(s).forEach(e=>e.style.display='none');
 const css=document.createElement('style');css.textContent='#cur{display:none!important}';document.head.appendChild(css);
 const rotulo=document.createElement('div');rotulo.id='estudo-rotulo';
 rotulo.style.cssText='position:absolute;left:260px;top:350px;width:420px;font-family:PJS;color:#18191C;transform-origin:0 0';
 const titulo=document.createElement('div');titulo.textContent=textos.legenda;
 titulo.style.cssText='font-size:52px;font-weight:800;line-height:1.08;letter-spacing:-.035em';rotulo.appendChild(titulo);
 const exemplo=document.createElement('div');exemplo.textContent=textos.exemplo;
 exemplo.style.cssText='font:700 24px AHN;color:#5B6068;margin-top:30px';rotulo.appendChild(exemplo);stage.appendChild(rotulo);
 const acao=document.createElement('div');acao.id='estudo-acao';
 acao.style.cssText='position:absolute;left:260px;top:235px;font-family:PJS;transform-origin:0 0';
 const contador=document.createElement('div');contador.textContent='01/04';
 contador.style.cssText='font-size:32px;font-weight:800;color:#C2410C';acao.appendChild(contador);
 const tracos=document.createElement('div');tracos.style.cssText='display:flex;gap:12px;margin-top:22px';
 for(let i=0;i<4;i++){const e=document.createElement('span');e.style.cssText='display:block;width:42px;height:5px;border-radius:3px;background:'+(i?'#E7E1D8':'#EA5A36');tracos.appendChild(e);}acao.appendChild(tracos);stage.appendChild(acao);
 const camera=document.createElement('div');camera.id='estudo-camera';
 camera.style.cssText='position:absolute;inset:0;transform-origin:1100px 484px';stage.appendChild(camera);
 const corpo=document.createElement('div');corpo.id='estudo-corpo';
 corpo.style.cssText='position:absolute;inset:0;transform-origin:0 0;transform:translate(374px,-44px) scale(1.1)';
 camera.appendChild(corpo);corpo.appendChild(q('#dot'));corpo.appendChild(q('#scr'));
 window.estudoElementos={corpo,camera,rotulo,acao};
}"""

ATUALIZAR_ESTUDO = r"""([t,camera,legenda])=>{
 (window.seekV4||window.seek)(t);
 const e=window.estudoElementos;
 e.camera.style.transform=`translate(${camera.x}px,${camera.y}px) scale(${camera.zoom})`;
 for(const [el,fator] of [[e.rotulo,.35],[e.acao,1.1]])
   el.style.transform=`translate(${camera.x*fator}px,${camera.y*fator}px) scale(${1+(camera.zoom-1)*fator})`;
 const cp=document.querySelector('#cap');cp.textContent=legenda;cp.style.opacity='1';cp.style.transform='none';cp.style.bottom='28px';
 function estado(s){const el=document.querySelector(s),r=el.getBoundingClientRect();let o=1;
   for(let p=el;p;p=p.parentElement){const c=getComputedStyle(p);o*=Number(c.opacity);if(c.display==='none'||c.visibility==='hidden')o=0;}
   return {x:r.x,y:r.y,w:r.width,h:r.height,o};}
 return {chassi:estado('#dot'),tela:estado('#scr'),ilha:estado('#isl'),campo:estado('#fF'),
   botao:estado('#pub'),confirmacao:estado('#pubB'),rotulo:estado('#estudo-rotulo'),acao:estado('#estudo-acao'),
   cursor_visivel:estado('#cur').o>0,zoom:camera.zoom};
}"""


def fonte_estudo(fonte, regua, legenda):
    """HTML auxiliar usa a mesma câmera amostrada do MP4; boot aguarda fontes/plano."""
    amostras=[dict(referencia_s=tempo_v4_estudo(n/60),camera=camera_estudo(n/60)) for n in range(216)]
    wrapper = '<script>\nconst bootOriginal=window.boot;window.seekV4=window.seek;\n'
    wrapper += 'const prepararEstudo='+PREPARAR_ESTUDO+';const atualizarEstudo='+ATUALIZAR_ESTUDO+';\n'
    wrapper += 'const reguaV4='+json.dumps(regua,ensure_ascii=False)+';\n'
    wrapper += 'const amostrasEstudo='+json.dumps(amostras)+';\n'
    wrapper += 'const textosEstudo='+json.dumps(dict(legenda=legenda,exemplo='Exemplo'),ensure_ascii=False)+';\n'
    wrapper += 'window.boot=async()=>{const info=await bootOriginal(reguaV4,"pt");window.seekV4(25.55);prepararEstudo(textosEstudo);return info};\n'
    wrapper += 'window.seek=t=>{const a=amostrasEstudo[Math.max(0,Math.min(215,Math.floor(t*60+1e-6)))];return atualizarEstudo([a.referencia_s,a.camera,textosEstudo.legenda])};\n</script>'
    return fonte.replace('<head>','<head><base href="/motor/">',1).replace('</body>',wrapper+'</body>')


def estudo_aparelho():
    """Exporta apenas o estudo autorizado D6/D7/D8, sem alterar o filme ou sua régua."""
    import io, math, re, subprocess
    from PIL import Image
    from analisar_video import COLETA, folha, quadro
    out=AQUI/'cache/mockup-aparelho-d6-d7';out.mkdir(parents=True,exist_ok=True)
    roteiro=json.loads((RAIZ/'roteiro.json').read_text())
    cena=next(c for c in roteiro['cenas'] if c['id']=='v06-solucao1')
    legenda=cena['pt']['legenda'].split('. ')[0]+'.'
    assert legenda=='Você publica a vaga.', 'Mudança de roteiro exige revisar o estudo documentado.'
    assert any('Exemplo' in c.get('tela','') for c in roteiro['cenas'])
    fonte=subprocess.check_output(['git','show','4efa75a:motor/filme.html'],cwd=RAIZ).decode()
    # Base explícita mantém o carregamento das fontes da referência na URL do estudo.
    (out/'referencia-v4.html').write_text(fonte.replace('<head>','<head><base href="/motor/">',1))
    regua=json.loads((RAIZ/'docs/v4/tempos-pt.json').read_text())
    (out/'estudo.html').write_text(fonte_estudo(fonte,regua,legenda))
    (out/'tempos-estudo.json').write_text(json.dumps(dict(total=3.6,cenas=[dict(id='estudo',ini=0,dur=3.6)])))
    contrato=dict(presenca=[dict(id='chassi',selector='#dot',de=0,ate=3.6,opacidade_min=.999),
        dict(id='tela',selector='#scr',de=0,ate=3.6,opacidade_min=.999)],
        movimento=[dict(de=.6,ate=1.3),dict(de=2,ate=2.9)])
    (out/'contrato.json').write_text(json.dumps(contrato,indent=2))
    servidor_http=servidor()
    video=pathlib.Path.home()/'Downloads/frila-pitch-pt.mp4'
    def normalizar(txt):
        return re.sub(r'\s+',' ',txt).strip().casefold()
    # Fragmentos são necessários porque o horário é formado por três nós no DOM v4.
    permitidos=['01/04',legenda,'Exemplo','Contratante','Nova vaga','Função','Garçom',
        'Horário','19h às','23','h','Endereço','Plano Piloto','Valor','R$ 120','Publicar','Vaga publicada']
    permitidos={normalizar(t) for t in permitidos}
    instantes=[(.2,'01-apresentar'),(1.3,'02-acao'),(3.4,'03-retorno')]
    permitidos_antes=permitidos|{normalizar(x) for x in ['4 passos','01','02','03','04',
        'Contratante publica a vaga','função, horário, endereço, valor','Profissional recebe o aviso',
        'até 15 km','Contratante escolhe quem vai','vê o histórico','Os dois lados conferem',
        'check-in, sim ou não','O contratante publica a vaga.']}
    origens={}
    def origem(strings, fonte, campo):
        for string in strings:
            origens[normalizar(string)]=dict(fonte=fonte,campo=campo)
    origem(['01/04'],'docs/v4/COPIA-NOVA-VAGA.md','formato solicitado pelo Fabrício; quatro passos da v4')
    origem([legenda],'roteiro.json','v06-solucao1.pt.legenda, primeira frase')
    origem(['Exemplo'],'roteiro.json','v07-solucao2.tela, tag literal')
    for string,campo in [('Contratante','role'),('Nova vaga','t'),('Função','f1'),
                         ('Garçom','v1'),('Horário','f2'),('Endereço','f3'),
                         ('Plano Piloto','v3'),('Valor','f4'),('R$ 120','v4'),
                         ('Publicar','b'),('Vaga publicada','b2')]:
        origem([string],'docs/v4/COPIA-NOVA-VAGA.md; 4efa75a:motor/filme.html',
               'TX.pt.form.'+campo+'; tela Nova vaga da referência v4')
    origem(['19h às','23','h'],'docs/v4/COPIA-NOVA-VAGA.md; 4efa75a:motor/filme.html',
           'TX.pt.form.v2 + #hora=23 + h; composição 19h às 23h no instante da referência')
    origem(['4 passos'],'docs/v4/roteiro-v4.json','c06-passos-a.pt.legenda')
    origem(['O contratante publica a vaga.'],'docs/v4/roteiro-v4.json','c06-passos-a.pt.legenda')
    origem(['01','02','03','04'],'docs/v4/COPIA-NOVA-VAGA.md; 4efa75a:motor/filme.html',
           'build(), numeração da lista dos quatro passos')
    for i,passo in enumerate([('Contratante publica a vaga','função, horário, endereço, valor'),
                             ('Profissional recebe o aviso','até 15 km'),
                             ('Contratante escolhe quem vai','vê o histórico'),
                             ('Os dois lados conferem','check-in, sim ou não')]):
        for j,string in enumerate(passo):
            origem([string],'docs/v4/COPIA-NOVA-VAGA.md; 4efa75a:motor/filme.html',
                   f'TX.pt.steps[{i}][{j}], lista de referência v4')
    if permitidos_antes-origens.keys():
        raise ValueError('String permitida sem origem no manifesto.')
    frames=[];observadas=set();observadas_antes=set();faixa=[];erros=[]
    with sync_playwright() as pw:
        b=pw.chromium.launch(args=['--force-color-profile=srgb','--disable-lcd-text'])
        try:
            pg=b.new_page(viewport={'width':1920,'height':1080},device_scale_factor=1)
            pg.on('pageerror',lambda e:erros.append(str(e)))
            pg.goto(f'http://127.0.0.1:{servidor_http.server_port}/motor/cache/mockup-aparelho-d6-d7/referencia-v4.html')
            pg.evaluate('t=>window.boot(t,"pt")',regua)
            pg.evaluate('t=>window.seek(t)',25.55)
            pg.evaluate(PREPARAR_ESTUDO,dict(legenda=legenda,exemplo='Exemplo'))
            ff=subprocess.Popen(['ffmpeg','-v','error','-y','-f','image2pipe','-framerate','60',
                '-c:v','mjpeg','-i','-','-an','-c:v','libx264','-preset','medium','-crf','16',
                '-pix_fmt','yuv420p','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709',
                str(out/'zoom-continuo.mp4')],stdin=subprocess.PIPE)
            try:
                for n in range(216):
                    t=n/60;tv=tempo_v4_estudo(t);camera=camera_estudo(t)
                    estado=pg.evaluate(ATUALIZAR_ESTUDO,[tv,camera,legenda])
                    textos=pg.evaluate(COLETA,{})['textos']
                    strings=sorted({normalizar(x['texto']) for x in textos})
                    novas=set(strings)-permitidos
                    if novas:
                        raise ValueError(f'Texto sem origem no frame {n}: {novas}')
                    observadas.update(strings)
                    r=estado['chassi']
                    z=camera['zoom']
                    esperado=dict(x=1100+camera['x']-209*z,y=484+camera['y']-429*z,w=418*z,h=858*z,o=1)
                    if any(abs(r[k]-v)>.03 for k,v in esperado.items()) or estado['cursor_visivel']:
                        raise ValueError(f'Chassi/cursor perdeu contrato em {t}: {estado}')
                    tela=estado['tela']
                    if abs(tela['w']/r['w']-352/380)>.0001:
                        raise ValueError(f'Escala da UI separada do chassi em {t}')
                    for nome in ('botao','confirmacao'):
                        v=estado[nome]
                        if v['x']<tela['x'] or v['x']+v['w']>tela['x']+tela['w']+.01:
                            raise ValueError(f'{nome} saiu da tela em {t}')
                    frames.append(dict(frame=n,t=t,referencia_s=tv,**estado,textos=strings))
                    jpeg=pg.screenshot(type='jpeg',quality=94);ff.stdin.write(jpeg)
                    if n%5==0:
                        faixa.append((t,Image.open(io.BytesIO(jpeg)).convert('RGB').resize((320,180))))
                    if n%60==0:print('estudo',n,'/216 frames',flush=True)
                if 'nova vaga' not in frames[0]['textos'] or 'nova vaga' not in frames[-1]['textos']:
                    raise RuntimeError('Os campos precisam estar presentes na apresentação e no retorno.')
                if erros:raise RuntimeError(erros)
            finally:
                ff.stdin.close()
                if ff.wait():raise RuntimeError('Falha ao codificar o clipe de estudo.')
            pngs=[]
            pg_antes=b.new_page(viewport={'width':1920,'height':1080},device_scale_factor=1)
            pg_antes.goto(f'http://127.0.0.1:{servidor_http.server_port}/motor/cache/mockup-aparelho-d6-d7/referencia-v4.html')
            pg_antes.evaluate('t=>window.boot(t,"pt")',regua)
            for t,nome in instantes:
                tv=tempo_v4_estudo(t)
                # Comparar o mesmo frame da referência, com PTS existente no MP4.
                tf=math.ceil(tv*60-1e-6)/60
                pg_antes.evaluate('t=>window.seek(t)',tf)
                strings_antes={normalizar(x['texto']) for x in pg_antes.evaluate(COLETA,{})['textos']}
                if strings_antes-permitidos_antes:
                    raise ValueError(f'Texto da referência sem origem: {strings_antes-permitidos_antes}')
                observadas_antes.update(strings_antes)
                pg.evaluate(ATUALIZAR_ESTUDO,[tf,camera_estudo(t),legenda])
                depois=Image.open(io.BytesIO(pg.screenshot())).convert('RGB')
                antes=quadro(video,tf,1920)
                par=Image.new('RGB',(3840,1080));par.paste(antes,(0,0));par.paste(depois,(1920,0))
                par.save(out/f'{nome}.png');depois.save(out/f'{nome}-depois.png')
                antes.save(out/f'{nome}-antes.png')
                pngs.append(dict(arquivo=f'{nome}.png',estudo_s=t,referencia_s=tf))
            for i in range(0,len(faixa),36):
                folha(faixa[i:i+36],out/f'faixa-12fps-{i//36+1:02d}.png','Estudo D6/D7/D8 · 12 fps')
        finally:
            b.close();servidor_http.shutdown();servidor_http.server_close()
    manifesto=dict(base='main 41b406b',fonte_v4='4efa75a:motor/filme.html',fps=60,duracao_s=3.6,
        tipo='câmera sobre chassi e UI, parallax externo, sem cursor; estudo isolado',strings_observadas=sorted(observadas),
        strings_permitidas=sorted(permitidos),strings_antes=sorted(observadas_antes),
        origens_strings={s:origens[s] for s in sorted(observadas|observadas_antes)},
        pngs=pngs,frames=frames,erros=erros)
    (out/'manifesto.json').write_text(json.dumps(manifesto,ensure_ascii=False,indent=2)+'\n')
    indice="""<!doctype html><html lang="pt-BR"><meta charset="utf-8"><title>Estudo do aparelho · D6/D7</title>
<style>body{font:18px/1.5 system-ui;max-width:1500px;margin:32px auto;padding:0 24px;background:#F7F3EE;color:#18191C}video,img{width:100%;height:auto}a{color:#C2410C}</style>
<h1>Estudo do aparelho · D6/D7</h1><p>Antes (v4) à esquerda; proposta à direita. Anotações de revisão ficam nesta página, fora dos quadros. Este estudo de 3,6 s não é um bloco montado nem uma emenda implementada.</p>
<video src="zoom-continuo.mp4" controls muted playsinline preload="metadata"></video>
<p><a href="zoom-continuo.mp4">Abrir o clipe a60 fps, sem áudio</a> · <a href="manifesto.json">Manifesto de strings, frames e geometria</a></p>
"""
    for item in pngs:
        nome=item['arquivo']
        indice+=f'<p>Estudo {item["estudo_s"]:.2f} s · referência v4 {item["referencia_s"]:.3f} s</p><a href="{nome}"><img src="{nome}" alt="V4 e proposta lado a lado"></a>'
    (out/'index.html').write_text(indice+'</html>')
    print('ok',out,flush=True)


if __name__ == "__main__":
    if sys.argv[1] == "--estudo-aparelho":
        estudo_aparelho()
        raise SystemExit(0)
    L = sys.argv[1]
    s = servidor()
    url = f"http://127.0.0.1:{s.server_port}/motor/filme.html"
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
