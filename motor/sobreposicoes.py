"""Refinamento (22/10): procura sobreposições no filme inteiro, a cada 1/15 s.

Junta, em cada quadro, tudo que está visível (opacidade efetiva > 0,05, já recortado pelos pais com overflow escondido):
- texto: o retângulo justo de cada trecho de texto;
- forma: caixa com fundo ou borda, e linhas, círculos e caminhos do SVG (o ponto laranja entra como círculo).
Acusa texto sobre texto, texto sobre forma e forma sobre forma quando um não está dentro do outro no HTML
(o texto dentro do próprio cartão não conta). Para círculo só de contorno, só conta se tocar no traço.
Uso: .venv/bin/python sobreposicoes.py pt|en [passo_s]   →  cache/sobreposicoes-<L>.json e um resumo na tela.
"""
import json, sys, pathlib
from fotos import servidor, abrir, AQUI
from playwright.sync_api import sync_playwright

COLETA = r"""() => {
  const st = document.querySelector('#stage'), R0 = {l:0, t:0, r:1920, b:1080};
  const inter = (a, b) => ({l:Math.max(a.l,b.l), t:Math.max(a.t,b.t), r:Math.min(a.r,b.r), b:Math.min(a.b,b.b)});
  const vazio = a => a.r - a.l < .5 || a.b - a.t < .5;
  const cs = new Map(); const css = e => { let c = cs.get(e); if (!c) { c = getComputedStyle(e); cs.set(e, c); } return c; };
  function estado(el) {   // opacidade efetiva e recorte dos pais
    let o = 1, clip = R0;
    for (let e = el; e && e !== st; e = e.parentElement) {
      const c = css(e); if (c.display === 'none' || c.visibility === 'hidden') return null;
      o *= parseFloat(c.opacity);
      if (e !== el && (c.overflowX !== 'visible' || c.overflowY !== 'visible')) { const r = e.getBoundingClientRect(); clip = inter(clip, {l:r.left, t:r.top, r:r.right, b:r.bottom}); }
    }
    return o > .05 ? {o, clip} : null;
  }
  const nome = el => { const sc = el.closest('.sc'); const tx = (el.textContent || '').trim().replace(/\s+/g, ' ').slice(0, 32);
    return (sc ? sc.id + ' ' : '') + el.tagName.toLowerCase() + (el.id ? '#' + el.id : '') + (el.classList.length ? '.' + [...el.classList].join('.') : '') + (tx ? ' "' + tx + '"' : ''); };
  const it = [];
  // texto
  const w = document.createTreeWalker(st, NodeFilter.SHOW_TEXT);
  for (let n = w.nextNode(); n; n = w.nextNode()) {
    if (!n.textContent.trim()) continue;
    const el = n.parentElement, s = estado(el); if (!s) continue;
    const c = css(el); if (c.color === 'rgba(0, 0, 0, 0)') continue;
    const rg = document.createRange(); rg.selectNodeContents(n);
    if (el.closest('.os')) continue;   // dígitos do contador: rolam atrás de uma janela
    for (const r of rg.getClientRects()) { const h = r.bottom - r.top, a = inter(s.clip, {l:r.left + 1, t:r.top + h * .2, r:r.right - 1, b:r.bottom - h * .16}); if (!vazio(a)) it.push({k:'texto', el, a, o:s.o}); }
  }
  // formas
  for (const el of st.querySelectorAll('*')) {
    const tag = el.tagName.toLowerCase(); if (['svg','g','text','tspan','span'].includes(tag) && !(tag === 'span' && !el.textContent.trim())) continue;
    let forma = false, circ = null, temSup = false;
    const c = css(el), r = el.getBoundingClientRect(); if (!r.width && !r.height) continue;
    let a = {l:r.left, t:r.top, r:r.right, b:r.bottom};
    if (el instanceof SVGElement) {
      if (!['line','circle','path','rect','polyline','polygon','ellipse'].includes(tag)) continue;
      const sw = c.stroke !== 'none' ? parseFloat(c.strokeWidth) || 0 : 0, temFundo = c.fill !== 'none' && parseFloat(c.fillOpacity) > .05;
      if (!sw && !temFundo) continue;
      const k = el.ownerSVGElement.getScreenCTM().a, p = sw * k / 2; a = {l:a.l - p, t:a.t - p, r:a.r + p, b:a.b + p};
      if (tag === 'circle') circ = {x:(r.left + r.right) / 2, y:(r.top + r.bottom) / 2, r:r.width / 2, sw:sw * k, cheio:temFundo};
      if (parseFloat(c.strokeOpacity) < .05 && !temFundo) continue;
      forma = true;
    } else {
      if (el.children.length && [...el.childNodes].some(n => n.nodeType === 3 && n.textContent.trim())) {}
      const bg = c.backgroundColor, temBg = bg !== 'rgba(0, 0, 0, 0)' && bg !== 'transparent';
      const bw = ['Top','Right','Bottom','Left'].some(s => parseFloat(c['border' + s + 'Width']) > 0 && c['border' + s + 'Color'] !== 'rgba(0, 0, 0, 0)');
      forma = temBg || bw; temSup = temBg && r.width > 60 && r.height > 60;
      if (forma && parseFloat(c.borderTopLeftRadius) >= Math.min(r.width, r.height) / 2 - .5 && Math.abs(r.width - r.height) < 1) circ = {x:(r.left + r.right) / 2, y:(r.top + r.bottom) / 2, r:r.width / 2, sw:0, cheio:true};
    }
    if (!forma) continue;
    const s = estado(el); if (!s) continue;
    a = inter(s.clip, a); if (vazio(a)) continue;
    if ((a.r - a.l) * (a.b - a.t) > 1920 * 1080 * .6) continue;   // fundos de tela inteira
    it.push({k:'forma', el, a, o:s.o, circ, sup:temSup});
  }
  // pares
  const toca = (A, B) => {
    const i = inter(A.a, B.a); if (i.r - i.l < 2 || i.b - i.t < 2) return 0;
    for (const [P, Q] of [[A, B], [B, A]]) if (P.circ) {
      const c = P.circ, q = Q.a, nx = Math.max(q.l, Math.min(c.x, q.r)), ny = Math.max(q.t, Math.min(c.y, q.b));
      const dmin = Math.hypot(nx - c.x, ny - c.y), dmax = Math.max(...[[q.l,q.t],[q.r,q.t],[q.l,q.b],[q.r,q.b]].map(([x,y]) => Math.hypot(x - c.x, y - c.y)));
      if (dmin > c.r - 1.5) return 0;
      if (!c.cheio && dmax < c.r - c.sw / 2 - 1.5) return 0;
    }
    return (i.r - i.l) * (i.b - i.t);
  };
  const out = [];
  for (let i = 0; i < it.length; i++) for (let j = i + 1; j < it.length; j++) {
    const A = it[i], B = it[j];
    if (A.el === B.el || A.el.contains(B.el) || B.el.contains(A.el)) continue;
    if (A.k === 'texto' && B.k === 'texto' && A.el.parentElement === B.el.parentElement && A.el.classList.contains('w')) continue;
    const dentro = (P, Q) => P.sup && Q.a.l >= P.a.l - 1 && Q.a.r <= P.a.r + 1 && Q.a.t >= P.a.t - 1 && Q.a.b <= P.a.b + 1;
    if (dentro(A, B) || dentro(B, A)) continue;
    const ar = toca(A, B); if (ar < 6) continue;
    out.push([A.k + ' × ' + B.k, nome(A.el), nome(B.el), Math.round(ar), +Math.min(A.o, B.o).toFixed(2)]);
  }
  return out;
}"""


def main():
    L = sys.argv[1]
    passo = float(sys.argv[2]) if len(sys.argv) > 2 else 1 / 15
    s = servidor()
    url = f"http://127.0.0.1:{s.server_port}/motor/filme.html"
    achados = {}
    with sync_playwright() as pw:
        b, pg, tempos, info, erros = abrir(pw, L, url)
        n = int(tempos["total"] / passo)
        for i in range(n + 1):
            t = round(i * passo, 3)
            pg.evaluate(f"window.seek({t})")
            for tipo, a, bb, area, op in pg.evaluate(COLETA):
                k = f"{tipo} | {a} | {bb}"
                e = achados.setdefault(k, {"de": t, "ate": t, "quadros": 0, "visiveis": 0, "area_max": 0, "opac_max": 0})
                e["ate"] = t; e["quadros"] += 1; e["visiveis"] += op > .5; e["area_max"] = max(e["area_max"], area); e["opac_max"] = max(e["opac_max"], op)
        b.close()
    lista = sorted(achados.items(), key=lambda kv: kv[1]["de"])
    (AQUI / f"cache/sobreposicoes-{L}.json").write_text(json.dumps(dict(lista), ensure_ascii=False, indent=1))
    print(L, "erros:", erros, "| pares:", len(lista))
    for k, e in lista:
        if not e["visiveis"]: continue
        print(f"{e['de']:6.2f}–{e['ate']:6.2f}  q{e['quadros']:4d}/{e['visiveis']:<4d}  área {e['area_max']:6d}  op {e['opac_max']:.2f}  {k}")


main()
