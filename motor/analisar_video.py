"""Revisão D2 do MP4 real, sem aprovação artística automática.

Uso: python motor/analisar_video.py VIDEO --tempos REGUA --saida PASTA
     [--html FONTE --raiz RAIZ] [--contrato CONTRATO] [--emendas 12.3 24.5]
Dependências: ffmpeg, ffprobe, numpy, Pillow, opencv-python-headless;
Playwright/Chromium apenas com --html. Não modifica as entradas.
Contrato: {"movimento":[{"de":1,"ate":2}],
 "presenca":[{"id":"ponto","selector":"#dot","de":1,"ate":2,"exclusivo":true}]}.
Sem contrato, uma pausa é pista editorial, nunca travada confirmada.
"""
import argparse
from collections import Counter
from fractions import Fraction
import functools
import hashlib
import http.server
import io
import json
import math
import os
from pathlib import Path
import subprocess
import threading

import cv2
import numpy as np
from PIL import Image, ImageDraw

PARAMETROS = dict(pausa_mad=.06, pausa_fracao=.0005, pausa_min_s=.60,
                  pixel_alterado=4, flash_mad=8, flash_retorno=1.5,
                  flash_luz=6, salto_mad=5, salto_fracao=.18,
                  salto_fluxo_px=90, texto_opacidade=.5, texto_intersecao_px=6)


def gravar(path, obj):
    Path(path).write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n')


def ocorrencia(tipo, de, ate, evidencia, confianca='suspeita'):
    return dict(tipo=tipo, de=round(de, 6), ate=round(ate, 6),
                confianca=confianca, evidencia=evidencia)


def analisar_quadros(quadros, fps):
    """Pixels em escala de cinza, na cadência nativa. Retorna pistas e métricas."""
    p = PARAMETROS
    achados, metricas, anteriores = [], [], []
    anterior = retrasado = None
    pausa = None
    for i, atual in enumerate(quadros):
        t = i / fps
        if anterior is None:
            anterior = atual
            continue
        delta = cv2.absdiff(atual, anterior)
        mad = float(delta.mean())
        fracao = float(np.mean(delta > p['pixel_alterado']))
        luz = float(atual.mean() - anterior.mean())
        fluxo = 0.
        # Fluxo é auxiliar; áreas que mudam de conteúdo não têm identidade garantida.
        if mad > 1:
            pontos = cv2.goodFeaturesToTrack(anterior, 80, .02, 8)
            if pontos is not None and len(pontos) >= 8:
                novos, status, _ = cv2.calcOpticalFlowPyrLK(anterior, atual, pontos, None)
                bons = status.reshape(-1) == 1
                if bons.sum() >= 8:
                    fluxo = float(np.median(np.linalg.norm((novos-pontos)[bons], axis=2))) * 1920 / atual.shape[1]
        metricas.append(dict(t=round(t,6), mad=round(mad,5), fracao=round(fracao,6),
                             luz=round(luz,5), fluxo_px=round(fluxo,3)))
        parado = mad < p['pausa_mad'] and fracao < p['pausa_fracao']
        if parado and pausa is None:
            pausa = (i-1)/fps
        if not parado and pausa is not None:
            if (i-1)/fps-pausa >= p['pausa_min_s']:
                achados.append(ocorrencia('pausa_a_revisar', pausa, (i-1)/fps,
                    'Baixa alteração do quadro inteiro; pode ser repouso intencional.'))
            pausa = None
        if retrasado is not None:
            volta = float(cv2.absdiff(atual, retrasado).mean())
            if (mad > p['flash_mad'] and anteriores[-1]['mad'] > p['flash_mad']
                and volta < p['flash_retorno'] and abs(luz) > p['flash_luz']
                and luz * anteriores[-1]['luz'] < 0):
                achados.append(ocorrencia('cintilacao', (i-1)/fps, t,
                    dict(mad_entrada=anteriores[-1]['mad'], mad_saida=mad, retorno=volta), 'alta_raster'))
        base = max(.25, float(np.median([v['mad'] for v in anteriores[-4:]] or [0])))
        if (mad > p['salto_mad'] and fracao > p['salto_fracao'] and mad > base*4) or fluxo > p['salto_fluxo_px']:
            achados.append(ocorrencia('salto', t, t,
                dict(mad=mad, fracao=fracao, fluxo_px=fluxo,
                     observacao='Pode ser corte/transformação deliberada; exige revisão.')))
        anteriores.append(dict(mad=mad,luz=luz))
        anteriores = anteriores[-4:]
        retrasado, anterior = anterior, atual
    if pausa is not None and metricas and metricas[-1]['t']-pausa >= p['pausa_min_s']:
        achados.append(ocorrencia('pausa_a_revisar', pausa, metricas[-1]['t'],
            'Baixa alteração do quadro inteiro até o fim; não comprova defeito.'))
    return achados, metricas


def colisoes_texto(textos):
    pares = []
    for i, a in enumerate(textos):
        for b in textos[i+1:]:
            if min(a['o'], b['o']) < PARAMETROS['texto_opacidade']:
                continue
            if a['id'] == b['id'] or a['id'] in b.get('pais',[]) or b['id'] in a.get('pais',[]):
                continue
            w = min(a['r'],b['r'])-max(a['l'],b['l'])
            h = min(a['b'],b['b'])-max(a['t'],b['t'])
            if w >= 2 and h >= 2 and w*h >= PARAMETROS['texto_intersecao_px']:
                pares.append(dict(a=a['texto'], b=b['texto'], area=round(w*h,2)))
    return pares


def agrupar(amostras, fps=12):
    """Agrupa só ocorrências consecutivas, nunca cobre lacunas entre aparições."""
    saida = []
    for a in sorted(amostras, key=lambda x:x['de']):
        if (saida and a['tipo']==saida[-1]['tipo'] and a.get('chave')==saida[-1].get('chave')
            and a['de']-saida[-1]['ate'] <= 1.5/fps):
            saida[-1]['ate'] = a['ate']
        else:
            saida.append(dict(a))
    return saida


def aplicar_contrato(achados, quadros, contrato):
    resultado = []
    for a in achados:
        resultado.append(a)
        if a['tipo'] == 'pausa_a_revisar':
            for janela in contrato.get('movimento',[]):
                de, ate = max(a['de'],janela['de']), min(a['ate'],janela['ate'])
                if ate-de >= PARAMETROS['pausa_min_s']:
                    resultado.append(ocorrencia('travada',de,ate,
                        dict(pausa=a, expectativa=janela), 'contrato_e_raster'))
    estados = []
    por_id = {}
    for janela in contrato.get('presenca',[]):
        por_id.setdefault(janela['id'],[]).append(janela)
    for nome, janelas in por_id.items():
        for q in quadros:
            e = q['elementos'].get(nome)
            permitidas = [j for j in janelas if j['de']<=q['t']<=j['ate']]
            minimo = max((j.get('opacidade_min',.05) for j in permitidas),default=.05)
            visivel = bool(e and e['o']>=minimo and e['w']>.5 and e['h']>.5)
            exclusivo = any(j.get('exclusivo') for j in janelas)
            tipo = 'sumiço' if permitidas and not visivel else ('nascimento' if not permitidas and visivel and exclusivo else None)
            if tipo:
                evidencia = dict(id=nome,expectativa=permitidas or janelas,
                                 opacidade_observada=e['o'] if e else 0)
                a = ocorrencia(tipo,q['t'],q['t'],evidencia,'contrato_e_fonte')
                a['chave'] = nome
                estados.append(a)
    return resultado + agrupar(estados)


def instantes_corte(t, duracao, fps):
    # Rótulos sempre são PTS de frames reais, inclusive quando o corte cai entre dois.
    ultimo = math.ceil(duracao*fps-1e-5)-1
    n0 = max(0, math.ceil((t-.5)*fps-1e-6))
    n1 = min(ultimo, math.floor((t+.5)*fps+1e-6))
    n = math.ceil(t*fps-1e-6)
    indices = [n0+math.ceil(k*fps/12-1e-6) for k in range(13)] + [n-1,n]
    return sorted(set(round(i/fps,6) for i in indices if n0<=i<=n1))


def metadados(video):
    d = json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0',
        '-show_entries','stream=width,height,r_frame_rate,avg_frame_rate,duration','-of','json',str(video)]))['streams'][0]
    if d['avg_frame_rate'] != d['r_frame_rate']:
        raise ValueError('Vídeo com taxa variável exige mapa de PTS; não inferir tempos por índice.')
    d['fps'] = float(Fraction(d['r_frame_rate']))
    d['duration'] = float(d['duration'])
    return d


def pixels(video, fps):
    cmd = ['ffmpeg','-v','error','-i',str(video),'-an','-vf','scale=480:270',
           '-pix_fmt','gray','-f','rawvideo','-']
    proc = subprocess.Popen(cmd,stdout=subprocess.PIPE)
    try:
        while True:
            raw = proc.stdout.read(480*270)
            if not raw:
                break
            if len(raw) != 480*270:
                raise RuntimeError('Quadro incompleto na decodificação.')
            yield np.frombuffer(raw,np.uint8).reshape(270,480)
        if proc.wait():
            raise RuntimeError('ffmpeg falhou ao ler o vídeo.')
    finally:
        proc.stdout.close()
        if proc.poll() is None:
            proc.terminate()
            proc.wait()


def quadro(video, t, largura=480):
    raw = subprocess.check_output(['ffmpeg','-v','error','-ss',str(t),'-i',str(video),
        '-frames:v','1','-vf',f'scale={largura}:-1','-f','image2pipe','-vcodec','png','-'])
    return Image.open(io.BytesIO(raw)).convert('RGB')


def folha(imagens, destino, titulo, colunas=6):
    w, h = imagens[0][1].size
    tela = Image.new('RGB',(colunas*w,38+math.ceil(len(imagens)/colunas)*(h+24)), '#F7F3EE')
    d = ImageDraw.Draw(tela)
    d.text((12,10),titulo,fill='#18191C')
    for i,(t,im) in enumerate(imagens):
        x, y = (i%colunas)*w,38+(i//colunas)*(h+24)
        tela.paste(im,(x,y))
        d.text((x+8,y+h+5),f'{t:.6f} s',fill='#18191C')
    tela.save(destino)


def clipe(video, de, ate, destino):
    subprocess.run(['ffmpeg','-v','error','-y','-ss',str(de),'-i',str(video),'-t',str(ate-de),
        '-an','-c:v','libx264','-preset','ultrafast','-crf','20',str(destino)],check=True)


COLETA = r"""(seletores) => {
 const all=[...document.querySelectorAll('#stage *')];
 const ids=new Map(all.map((e,i)=>[e,String(i)]));
 const inter=(a,b)=>({l:Math.max(a.l,b.l),t:Math.max(a.t,b.t),r:Math.min(a.r,b.r),b:Math.min(a.b,b.b)});
 const rect=r=>({l:r.left,t:r.top,r:r.right,b:r.bottom});
 function estado(el){let o=1,clip={l:0,t:0,r:1920,b:1080};
  for(let e=el;e;e=e.parentElement){const c=getComputedStyle(e);
   if(c.display==='none'||c.visibility==='hidden')return null;
   o*=parseFloat(c.opacity);
   if(e!==el&&(c.overflowX!=='visible'||c.overflowY!=='visible'))clip=inter(clip,rect(e.getBoundingClientRect()));
  }return o>.05?{o,clip}:null;}
 // Um retângulo geométrico pode estar sob uma superfície opaca (ex.: mapa sob #dot).
 // A pilha de pintura evita acusar colisão de texto que não chega ao MP4.
 function descoberto(el,a,borda=false){
  const pontos=[[.25,.3],[.5,.5],[.75,.7],...(borda?[[.01,.5],[.99,.5],[.5,.01],[.5,.99]]:[])];
  return pontos.some(([u,v])=>{
   const pilha=document.elementsFromPoint(a.l+(a.r-a.l)*u,a.t+(a.b-a.t)*v);
   for(const top of pilha){
    if(top===el||el.contains(top))return true;
    if(top.contains(el))continue;
    const c=getComputedStyle(top),e=estado(top);if(!e||e.o<.98)continue;
    const bg=c.backgroundColor,alfa=bg.startsWith('rgba')?parseFloat(bg.split(',')[3]):(bg==='transparent'?0:1);
    if(alfa>=.98)return false;
   }
   return true;
  });
 }
 const textos=[],elementos={};
 const walker=document.createTreeWalker(document.querySelector('#stage'),NodeFilter.SHOW_TEXT);
 for(let n=walker.nextNode();n;n=walker.nextNode()){
  const el=n.parentElement,tx=n.textContent.trim(); if(!tx||el.closest('.os'))continue;
  const e=estado(el);if(!e)continue;
  const range=document.createRange();range.selectNodeContents(n);
  const pais=[];for(let p=el.parentElement;p;p=p.parentElement)pais.push(ids.get(p));
  for(const r of range.getClientRects()){
   const h=r.height,a=inter(e.clip,{l:r.left+1,t:r.top+h*.2,r:r.right-1,b:r.bottom-h*.16});
   if(a.r-a.l>1&&a.b-a.t>1&&descoberto(el,a))textos.push({...a,id:ids.get(el),pais,texto:tx,o:e.o});
  }
 }
 for(const [nome,selector]of Object.entries(seletores)){
  for(const el of document.querySelectorAll(selector)){
   const e=estado(el);if(!e)continue;
   const r=inter(e.clip,rect(el.getBoundingClientRect()));
   if(r.r>r.l&&r.b>r.t&&descoberto(el,r,true)&&(!elementos[nome]||e.o>elementos[nome].o))
    elementos[nome]={x:r.l,y:r.t,w:r.r-r.l,h:r.b-r.t,o:e.o,transform:getComputedStyle(el).transform};
  }
 }
 return {textos,elementos};
}"""


def seletores_acompanhados(contrato):
    seletores = {'ponto':'#dot','tela':'#scr','mundo':'#world'}
    declarados = {}
    for j in contrato.get('presenca',[]):
        declarados.setdefault(j['id'],[]).append(j.get('selector','#'+j['id']))
    seletores.update({nome:', '.join(dict.fromkeys(valores)) for nome,valores in declarados.items()})
    return seletores


def fonte(html, raiz, regua, video, saida, contrato):
    from playwright.sync_api import sync_playwright
    os.environ.setdefault('PLAYWRIGHT_BROWSERS_PATH',str(Path(__file__).resolve().parent/'browsers'))
    # O arquivo fornecido é servido na URL original: caminhos ../assets continuam válidos.
    class Handler(http.server.SimpleHTTPRequestHandler):
        def log_message(self,*args):
            pass
        def do_GET(self):
            if self.path.split('?')[0]=='/motor/filme.html':
                raw=html.read_bytes()
                self.send_response(200)
                self.send_header('Content-Type','text/html; charset=utf-8')
                self.end_headers()
                self.wfile.write(raw)
            else:
                super().do_GET()
    server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(raiz)))
    threading.Thread(target=server.serve_forever,daemon=True).start()
    seletores=seletores_acompanhados(contrato)
    quadros, erros, correspondencia = [], [], []
    try:
        with sync_playwright() as pw:
            b=pw.chromium.launch(args=['--force-color-profile=srgb','--disable-lcd-text'])
            try:
                pg=b.new_page(viewport={'width':1920,'height':1080},device_scale_factor=1)
                pg.on('pageerror',lambda e:erros.append(str(e)))
                pg.goto(f'http://127.0.0.1:{server.server_port}/motor/filme.html')
                pg.evaluate('([t])=>window.boot(t,"pt")',[regua])
                for i in range(math.ceil(regua['total']*12)):
                    t=i/12
                    pg.evaluate('(t)=>window.seek(t)',t)
                    q=pg.evaluate(COLETA,seletores)
                    quadros.append(dict(t=round(t,6),**q))
                for c in regua['cenas']:
                    t=c['ini']+c['dur']*.55
                    pg.evaluate('(t)=>window.seek(t)',t)
                    fonte_im=Image.open(io.BytesIO(pg.screenshot())).convert('L').resize((480,270))
                    real_im=quadro(video,t).convert('L')
                    mad=float(np.abs(np.array(fonte_im,dtype=float)-np.array(real_im,dtype=float)).mean())
                    correspondencia.append(dict(cena=c['id'],t=t,mad=round(mad,3)))
            finally:
                b.close()
    finally:
        server.shutdown()
        server.server_close()
    if erros:
        raise RuntimeError('Falha na fonte HTML: '+str(erros))
    gravar(saida/'geometria.json',quadros)
    achados=[]
    for q in quadros:
        for par in colisoes_texto(q['textos']):
            a=ocorrencia('sobreposicao_texto',q['t'],q['t'],par,'geometria_da_fonte')
            a['chave']=par['a']+' | '+par['b']
            achados.append(a)
    # A–B–A em presença ou retângulo: flash de estado na fonte, não opinião sobre duração.
    for a,b,c in zip(quadros,quadros[1:],quadros[2:]):
        for nome in seletores:
            ea,eb,ec=[q['elementos'].get(nome) for q in (a,b,c)]
            if bool(ea)==bool(ec) and bool(eb)!=bool(ea):
                x=ocorrencia('nascimento' if eb else 'sumiço',b['t'],b['t'],
                    dict(id=nome,observacao='Estado isolado A–B–A; verificar intenção.'),'suspeita_fonte')
                x['chave']=nome
                achados.append(x)
    return quadros,agrupar(achados),dict(caminho=str(html),sha256=hashlib.sha256(html.read_bytes()).hexdigest(),
        erros=erros,comparacao_parcial_mp4=correspondencia,
        limite='Comparação em 55% de cada cena; não garante identidade em todos os quadros.')


def amostras_cena(video, ini, fim, fps):
    """Amostra frames reais a 12 fps; rótulos registram a grade efetiva do MP4."""
    inicio = math.ceil(ini*fps-1e-6)/fps
    comando = ['ffmpeg','-v','error','-ss',f'{inicio:.9f}','-i',str(video),
               '-t',str(fim-inicio),'-vf','scale=320:180',
               '-pix_fmt','rgb24','-f','rawvideo','-']
    proc = subprocess.Popen(comando,stdout=subprocess.PIPE)
    n = k = 0
    try:
        while True:
            raw = proc.stdout.read(320*180*3)
            if not raw:
                break
            if len(raw) != 320*180*3:
                raise RuntimeError('Faixa com quadro incompleto.')
            if n >= math.ceil(k*fps/12-1e-6):
                yield inicio+n/fps, Image.frombytes('RGB',(320,180),raw)
                k += 1
            n += 1
        if proc.wait():
            raise RuntimeError('Falha ao extrair faixa.')
    finally:
        proc.stdout.close()
        if proc.poll() is None:
            proc.terminate()
            proc.wait()


def artefatos(video, regua, meta, saida, emendas):
    pasta=saida/'faixas'; pasta.mkdir(exist_ok=True)
    clipes=saida/'clipes'; clipes.mkdir(exist_ok=True)
    manifesto_faixas=[]
    for c in regua['cenas']:
        ini,fim=c['ini'],min(meta['duration'],c['ini']+c['dur'])
        lote=[]; pagina=1; i=0; ts=[]
        for t,im in amostras_cena(video,ini,fim,meta['fps']):
            lote.append((t,im));ts.append(round(t,6));i+=1
            if len(lote)==36:
                folha(lote,pasta/f'{c["id"]}-{pagina:02d}.png',f'{c["id"]} | 12 fps | página {pagina}')
                lote=[];pagina+=1
        if lote:
            folha(lote,pasta/f'{c["id"]}-{pagina:02d}.png',f'{c["id"]} | 12 fps | página {pagina}')
        manifesto_faixas.append(dict(cena=c['id'],amostras=ts))
        clipe(video,max(0,ini-.5),min(meta['duration'],fim+.5),clipes/f'{c["id"]}.mp4')
        print('faixa',c['id'],i,'quadros',flush=True)
    gravar(saida/'faixas.json',manifesto_faixas)
    cortes=sorted(set([c['ini'] for c in regua['cenas'][1:]]+emendas))
    pasta=saida/'cortes';pasta.mkdir(exist_ok=True)
    manifesto=[]
    for t in cortes:
        ts=instantes_corte(t,meta['duration'],meta['fps'])
        folha([(v,quadro(video,v,480)) for v in ts],pasta/f'{t:010.6f}.png',f'Corte/emenda {t:.6f} s | ±0,5 s')
        clipe(video,max(0,t-.5),min(meta['duration'],t+.5),pasta/f'{t:010.6f}.mp4')
        manifesto.append(dict(corte=t,amostras=ts,emenda=t in emendas))
    gravar(saida/'cortes.json',manifesto)


def validar_regua(regua, meta):
    """Impede que uma entrega parcial seja apresentada como revisão integral."""
    tolerancia = 1/meta['fps']
    total = regua.get('total',0)
    if not math.isfinite(total) or total<=0 or abs(total-meta['duration'])>2*tolerancia:
        raise ValueError('Duração da régua difere do MP4 em mais de dois quadros ou é inválida.')
    cenas = regua.get('cenas',[])
    if not cenas:
        raise ValueError('Régua sem cenas.')
    anterior = 0
    ids = set()
    for c in cenas:
        nome, ini, dur = c['id'], c['ini'], c['dur']
        if not isinstance(nome,str) or not nome or '/' in nome or nome in ids:
            raise ValueError('Identificador de cena inválido ou repetido.')
        if not math.isfinite(ini) or not math.isfinite(dur) or ini<0 or dur<=0:
            raise ValueError('Cena com início/duração inválidos.')
        if abs(ini-anterior)>tolerancia:
            raise ValueError('Cenas fora de ordem, com lacuna ou sobreposição maior que um frame.')
        ids.add(nome)
        anterior = ini+dur
    if abs(anterior-total)>tolerancia:
        raise ValueError('Cenas não cobrem a duração total da régua.')


def main():
    parser=argparse.ArgumentParser(description=__doc__,formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('video',type=Path)
    parser.add_argument('--tempos',required=True,type=Path)
    parser.add_argument('--saida',required=True,type=Path)
    parser.add_argument('--html',type=Path)
    parser.add_argument('--raiz',type=Path,default=Path(__file__).resolve().parents[1])
    parser.add_argument('--contrato',type=Path)
    parser.add_argument('--emendas',type=float,nargs='*',default=[])
    parser.add_argument('--sem-artefatos',action='store_true',help='Recalcular métricas; não satisfaz sozinho a entrega D2.')
    args=parser.parse_args()
    regua=json.loads(args.tempos.read_text())
    meta=metadados(args.video)
    try:
        validar_regua(regua,meta)
    except (ValueError,KeyError,TypeError) as erro:
        parser.error(str(erro))
    args.saida.mkdir(parents=True,exist_ok=True)
    contrato=json.loads(args.contrato.read_text()) if args.contrato else {}
    achados,metricas=analisar_quadros(pixels(args.video,meta['fps']),meta['fps'])
    gravar(args.saida/'metricas.json',metricas)
    quadros=[];origem=None
    if args.html:
        quadros,geometria,origem=fonte(args.html.resolve(),args.raiz.resolve(),regua,args.video,args.saida,contrato)
        achados+=geometria
    if contrato.get('presenca') and not args.html:
        parser.error('Contrato de presença exige --html; pixels não identificam seletores.')
    achados=aplicar_contrato(achados,quadros,contrato)
    cortes=[c['ini'] for c in regua['cenas'][1:]]+args.emendas
    for a in achados:
        a['perto_de_corte']=any(a['de']-.5<=c<=a['ate']+.5 for c in cortes)
        a['cena']=next((c['id'] for c in reversed(regua['cenas']) if c['ini']<=a['de']),None)
    cenas=[]
    for c in regua['cenas']:
        ms=[m for m in metricas if c['ini']<=m['t']<c['ini']+c['dur']]
        pausas=[a for a in achados if a['tipo']=='pausa_a_revisar']
        estatico=sum(max(0,min(c['ini']+c['dur'],a['ate'])-max(c['ini'],a['de'])) for a in pausas)
        cenas.append(dict(**c,pausa_s=round(estatico,3),fracao_pausa=round(estatico/c['dur'],4),
            mad_mediana=round(float(np.median([m['mad'] for m in ms])),5)))
    relatorio=dict(video=str(args.video.resolve()),regua=str(args.tempos.resolve()),metadados=meta,
        parametros=PARAMETROS,amostragem=dict(raster_fps=meta['fps'],geometria_fps=12,faixas_fps=12),
        fonte=origem,contrato=contrato,cobertura=dict(raster=True,texto=bool(args.html),
            horario_semantico=bool(contrato),limites=[
                'Pixels não revelam intenção. Pausas e saltos são pistas, não reprovação.',
                'Sem contrato não se confirma nascimento/sumiço fora de hora nem movimento esperado.',
                'Geometria da fonte exige conferência contra o MP4; odômetros recortados não entram no teste de texto.',
                'Não detecta cortes de voz, qualidade artística ou todo erro local de movimento.']),
        resumo=dict(Counter(a['tipo'] for a in achados)),cenas=cenas,achados=sorted(achados,key=lambda a:a['de']))
    gravar(args.saida/'achados.json',relatorio)
    if not args.sem_artefatos:
        artefatos(args.video,regua,meta,args.saida,args.emendas)
    print(json.dumps(relatorio['resumo'],ensure_ascii=False),flush=True)


if __name__=='__main__':
    main()
