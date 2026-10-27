"""Contrato do piloto A: régua local, objeto contínuo, cópia e margem de imagem."""
import importlib.util
import json
from pathlib import Path
import unittest

RAIZ = Path(__file__).parents[2]
IDS = ['v01-gancho', 'v02-dor1', 'v03-dor2', 'v04-dor3']


def regua_teste():
    roteiro = json.loads((RAIZ / 'roteiro.json').read_text())
    cenas = [dict(id=nome, ini=a, dur=b-a) for nome, a, b in zip(IDS, [0, 6.039166666666667, 13.449166666666667, 19.399166666666666], [6.039166666666667, 13.449166666666667, 19.399166666666666, 25.575416666666666])]
    falas = []
    janelas = [[(.06, 1.74), (2.12, 3.3)], [(3.86, 10.66)], [(11.32, 14.84), (15.5, 16.68)], [(17.2, 22.26)]]
    for nome, js in zip(IDS, janelas):
        texto = next(c['pt']['legenda'] for c in roteiro['cenas'] if c['id'] == nome)
        partes = texto.split('. ')
        for k, ((a, b), legenda) in enumerate(zip(js, partes), 1):
            if not legenda.endswith(('.', '?', '!')): legenda += '.'
            falas.append(dict(cena=nome, k=k, ini=a+2.4591666666666665, fim=b+2.4591666666666665, leg_ini=max(0, a+2.4591666666666665-.05), leg_fim=b+2.4591666666666665+.15, legenda=legenda))
    return dict(bloco='A', duracao=25.575416666666666, duracao_voz=22.894875, voz_ini=2.4591666666666665, P=.491835, cenas=cenas, falas=falas)


class PilotoA(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location('render_estudo', RAIZ / 'motor/render.py')
        cls.render = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.render)

    def test_regua_reserva_quinze_frames_sem_retimar_a_voz(self):
        self.assertTrue(hasattr(self.render, 'preparar_bloco'))
        r = self.render.preparar_bloco(regua_teste(), margem_quadros=15)
        self.assertEqual(r['bloco'], 'A')
        self.assertEqual(r['voz_duracao'], 22.894875)
        self.assertAlmostEqual(r['total'], 25.833333333333332)
        self.assertEqual(r['falas'], regua_teste()['falas'])
        self.assertEqual(len(r['cenas']), 4)
        self.assertAlmostEqual(r['cenas'][-1]['ini']+r['cenas'][-1]['dur'], r['total'])
        with self.assertRaises(ValueError): self.render.preparar_bloco(regua_teste(), margem_quadros=11)
        ruim = regua_teste(); ruim['cenas'][1]['ini'] += .5
        with self.assertRaises(ValueError): self.render.preparar_bloco(ruim)

    def test_motor_parcial_preserva_ponto_cortes_margem_e_seek(self):
        import os
        import functools
        import http.server
        import threading
        os.environ['PLAYWRIGHT_BROWSERS_PATH'] = str(RAIZ / 'motor/browsers')
        from playwright.sync_api import sync_playwright
        server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(RAIZ)))
        threading.Thread(target=server.serve_forever, daemon=True).start()
        try:
            with sync_playwright() as pw:
                b = pw.chromium.launch()
                try:
                    pg = b.new_page(viewport={'width': 1920, 'height': 1080})
                    pg.goto(f'http://127.0.0.1:{server.server_port}/motor/filme.html')
                    r = self.render.preparar_bloco(regua_teste())
                    info = pg.evaluate('r=>window.boot(r,"pt")', r)
                    self.assertEqual(info['bloco'], 'A')
                    self.assertEqual(pg.locator('#dot').count(), 1)
                    self.assertEqual(pg.locator('.sc').count(), 4)
                    medir = """()=>{const d=document.querySelector('#dot'),r=d.getBoundingClientRect();return {x:r.x,y:r.y,w:r.width,h:r.height,o:getComputedStyle(d).opacity,cam:getComputedStyle(document.querySelector('#world')).transform,cursor:!!document.querySelector('#cur')&&getComputedStyle(document.querySelector('#cur')).display!=='none'}}"""
                    for corte in (6.039166666666667, 13.449166666666667, 19.399166666666666):
                        qs = []
                        for t in (corte-1/60, corte, corte+1/60):
                            pg.evaluate('t=>window.seek(t)', t); qs.append(pg.evaluate(medir))
                        for a, c in zip(qs, qs[1:]):
                            self.assertLess(abs(c['x']-a['x']), 90)
                            self.assertLess(abs(c['y']-a['y']), 90)
                            self.assertEqual(c['o'], '1')
                            self.assertFalse(c['cursor'])
                            self.assertIn(c['cam'], ('none', 'matrix(1, 0, 0, 1, 0, 0)'))
                    from motor.analisar_video import COLETA
                    corte = 13.449166666666667
                    for n in range(-30, 61):
                        t = corte+n/60
                        pg.evaluate('t=>window.seek(t)', t)
                        self.assertIn('ponto', pg.evaluate(COLETA, {'ponto': '#dot'})['elementos'], f'Ponto encoberto em {t}')
                    pg.evaluate('()=>window.seek(19.05)')
                    self.assertEqual(pg.evaluate("()=>getComputedStyle(document.querySelector('#a-nao .w:last-child')).color"), 'rgb(234, 90, 54)')
                    for n in range(120):
                        pg.evaluate('t=>window.seek(t)', r['bloco_fim']-2+n/60)
                        area = pg.evaluate("""()=>{const d=document.querySelector('#dot').getBoundingClientRect(),r=document.querySelector('#a-rot-n').getBoundingClientRect();return Math.max(0,Math.min(d.right,r.right)-Math.max(d.left,r.left))*Math.max(0,Math.min(d.bottom,r.bottom)-Math.max(d.top,r.top))}""")
                        self.assertEqual(area, 0, 'Ponto cruza a caixa do percentual na saída')
                    pg.evaluate('()=>window.seek(25.575416666666666)'); fim = pg.evaluate(medir)
                    pg.evaluate('()=>window.seek(25.82)'); self.assertEqual(pg.evaluate(medir), fim)
                    self.assertAlmostEqual(fim['x']+fim['w']/2, 960, places=1)
                    self.assertAlmostEqual(fim['y']+fim['h']/2, 760, places=1)
                    pg.evaluate('()=>window.seek(5)'); antes = pg.screenshot()
                    pg.evaluate('()=>window.seek(20)'); pg.evaluate('()=>window.seek(5)')
                    self.assertEqual(pg.screenshot(), antes)
                finally:
                    b.close()
        finally:
            server.shutdown(); server.server_close()
