"""Régua e continuidade do Bloco C; geometria real em Chromium headless."""
import json
import os
from pathlib import Path
import sys
import unittest

RAIZ = Path(__file__).parents[2]
sys.path.insert(0, str(RAIZ / 'motor'))
import render
from fotos import servidor


def regua_c():
    roteiro = json.loads((RAIZ / 'roteiro.json').read_text())
    ids = ['v10-dado', 'v11-meta', 'v12-estrategia']
    limites = [0, 4.90, 12.07, 19.673416666666668]
    janelas = [[(0.44, 4.62)], [(5.18, 11.72)], [(12.42, 19.36)]]
    falas = []
    for id_, js in zip(ids, janelas):
        tx = next(c['pt']['legenda'] for c in roteiro['cenas'] if c['id'] == id_)
        for k, (a, b) in enumerate(js, 1):
            falas.append(dict(cena=id_, k=k, ini=a, fim=b, leg_ini=a-.05,
                              leg_fim=b+.1, legenda=tx))
    palavras = [dict(cena='v10-dado', text='nenhum', start=2.68, end=2.92),
                dict(cena='v11-meta', text='oito', start=6.42, end=6.62),
                dict(cena='v11-meta', text='50', start=7.8, end=8.0),
                dict(cena='v11-meta', text='nove', start=9.44, end=9.74),
                dict(cena='v12-estrategia', text='núcleo', start=13.34, end=13.72),
                dict(cena='v12-estrategia', text='bares', start=16.24, end=16.56),
                dict(cena='v12-estrategia', text='Distrito', start=18.44, end=18.84)]
    return dict(bloco='C', duracao=limites[-1], duracao_voz=19.551208333333335,
                voz_ini=.34, P=.491835, falas=falas, palavras=palavras,
                cenas=[dict(id=id_, ini=a, dur=b-a) for id_, a, b in zip(ids, limites, limites[1:])])


class BlocoC(unittest.TestCase):
    def test_regua_c_conserva_voz_e_reserva_margem(self):
        import math
        original = regua_c()
        r = render.preparar_bloco(original, margem_quadros=30)
        self.assertEqual(r['falas'], original['falas'])
        self.assertEqual(r['palavras'], original['palavras'])
        self.assertAlmostEqual(r['bloco_fim'], 19.673416666666668)
        self.assertAlmostEqual(r['total'], (math.ceil(19.673416666666668 * 60 - 1e-7) + 30) / 60)
        self.assertEqual([c['id'] for c in r['cenas']], ['v10-dado', 'v11-meta', 'v12-estrategia'])
        with self.assertRaises(ValueError):
            ruim = regua_c()
            ruim['cenas'][1]['id'] = 'v99-inexistente'
            render.preparar_bloco(ruim)

    def test_continuidade_b_c_ponto_concorrentes_metas_mapa(self):
        from playwright.sync_api import sync_playwright
        os.environ['PLAYWRIGHT_BROWSERS_PATH'] = str(RAIZ / 'motor/browsers')
        s = servidor()
        try:
            with sync_playwright() as pw:
                b = pw.chromium.launch()
                try:
                    pg = b.new_page(viewport={'width': 1920, 'height': 1080})
                    erros = []
                    pg.on('pageerror', lambda e: erros.append(str(e)))
                    pg.goto(f'http://127.0.0.1:{s.server_port}/motor/filme.html')
                    
                    r = render.preparar_bloco(regua_c(), 30)
                    info = pg.evaluate('r=>window.boot(r, "pt")', r)
                    self.assertEqual(info['bloco'], 'C')
                    
                    # 1. Continuidade inicial no t=0
                    pg.evaluate('()=>window.seek(0)')
                    estado0 = pg.evaluate('()=>window.estadoBlocoC()')
                    self.assertAlmostEqual(estado0['ponto']['x'], 660, delta=1.0)
                    self.assertAlmostEqual(estado0['ponto']['y'], 480, delta=1.0)
                    self.assertAlmostEqual(estado0['ponto']['w'], 380, delta=1.0)
                    self.assertAlmostEqual(estado0['ponto']['h'], 780, delta=1.0)
                    self.assertEqual(estado0['fundo'], 'rgb(247, 243, 238)')
                    self.assertEqual(estado0['camera'], [1, 0, 0, 1, 0, 0])
                    
                    # 2. v10: Ponto Frila em (1525, 540) com check ativo após 2.8s
                    pg.evaluate('()=>window.seek(3.0)')
                    estado10 = pg.evaluate('()=>window.estadoBlocoC()')
                    self.assertAlmostEqual(estado10['ponto']['x'], 1525, delta=1.0)
                    self.assertAlmostEqual(estado10['ponto']['y'], 540, delta=1.0)
                    self.assertAlmostEqual(estado10['ponto']['w'], 72, delta=1.0)
                    check_op = float(pg.locator('#dot .check').evaluate('(e)=>getComputedStyle(e).opacity'))
                    self.assertGreater(check_op, 0.9)
                    # 22 pontos da grade presentes
                    n_pontos = pg.locator('.c-ponto-concorrente').count()
                    self.assertEqual(n_pontos, 22)
                    
                    # 3. v11: Meta do piloto (3 contadores)
                    pg.evaluate('()=>window.seek(11.0)')
                    v11_op = float(pg.locator('#c-v11').evaluate('(e)=>getComputedStyle(e).opacity'))
                    self.assertGreater(v11_op, 0.9)
                    
                    # 4. v12: Estratégia de expansão (mapa do DF ativo)
                    pg.evaluate('()=>window.seek(16.0)')
                    v12_op = float(pg.locator('#c-v12').evaluate('(e)=>getComputedStyle(e).opacity'))
                    self.assertGreater(v12_op, 0.9)
                    fase = pg.locator('#c-fase').text_content().strip()
                    self.assertIn('restaurantes', fase.lower())
                    
                    # 5. Ausência de cursor em toda a extensão
                    for t in (0, 1.5, 4.0, 7.5, 11.0, 14.0, 18.0):
                        pg.evaluate('t=>window.seek(t)', t)
                        has_cursor = pg.evaluate('()=>!!document.querySelector("#cur")')
                        self.assertFalse(has_cursor, f'Cursor detectado em t={t}')
                    
                    # 6. Reversibilidade e determinismo de seek
                    pg.evaluate('()=>window.seek(3.0)')
                    antes = pg.screenshot()
                    pg.evaluate('()=>window.seek(14.0)')
                    pg.evaluate('()=>window.seek(3.0)')
                    self.assertEqual(pg.screenshot(), antes)
                    
                    # 7. Margem de 30 frames congelada
                    pg.evaluate('()=>window.seek(19.673416666666668)')
                    fim = pg.evaluate('()=>window.estadoBlocoC()')
                    pg.evaluate('()=>window.seek(20.10)')
                    fim_margem = pg.evaluate('()=>window.estadoBlocoC()')
                    self.assertEqual(fim_margem['ponto'], fim['ponto'])
                    self.assertEqual(fim_margem['camera'], fim['camera'])
                    self.assertEqual(fim_margem['fundo'], fim['fundo'])
                    
                    self.assertEqual(erros, [])
                finally:
                    b.close()
        finally:
            s.shutdown()
            s.server_close()


if __name__ == '__main__':
    unittest.main()
