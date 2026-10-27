"""Régua e continuidade do Bloco D; geometria real em Chromium headless."""
import json
import math
import os
from pathlib import Path
import sys
import unittest

RAIZ = Path(__file__).parents[2]
sys.path.insert(0, str(RAIZ / 'motor'))
import render
from fotos import servidor


def regua_d():
    caminho = Path('/Users/fabriciotosta/dev/video-frila/fvp-audio-blocos/motor/cache/blocos-regua/D.json')
    if caminho.exists():
        return json.loads(caminho.read_text())
    roteiro = json.loads((RAIZ / 'roteiro.json').read_text())
    ids = ['v13-fecho', 'v14-assinatura']
    limites = [0, 5.81, 13.771374999999992]
    janelas = [
        [(0.30, 1.78, 'Menos tempo procurando gente.'),
         (2.22, 3.52, 'Mais tempo no seu negócio.'),
         (4.06, 5.54, 'Deixa que o Frila cuida.')],
        [(6.08, 6.42, 'Frila.'),
         (7.00, 8.80, 'Combinou? Pode contar. Dos dois lados.')]
    ]
    falas = []
    for id_, js in zip(ids, janelas):
        for k, (a, b, tx) in enumerate(js, 1):
            falas.append(dict(cena=id_, k=k, ini=a, fim=b, leg_ini=a-.05,
                              leg_fim=b+.1, legenda=tx))
    palavras = [
        dict(cena='v13-fecho', text='Menos', start=0.30, end=0.58),
        dict(cena='v13-fecho', text='tempo', start=0.62, end=0.84),
        dict(cena='v13-fecho', text='procurando', start=0.94, end=1.42),
        dict(cena='v13-fecho', text='gente', start=1.48, end=1.78),
        dict(cena='v13-fecho', text='mais', start=2.22, end=2.44),
        dict(cena='v13-fecho', text='tempo', start=2.50, end=2.72),
        dict(cena='v13-fecho', text='negócio', start=3.04, end=3.52),
        dict(cena='v13-fecho', text='Deixa', start=4.06, end=4.30),
        dict(cena='v13-fecho', text='cuida', start=5.24, end=5.54),
        dict(cena='v14-assinatura', text='Frila', start=6.08, end=6.42),
        dict(cena='v14-assinatura', text='Turno', start=7.00, end=7.22),
        dict(cena='v14-assinatura', text='combinado', start=7.26, end=7.82),
        dict(cena='v14-assinatura', text='regra', start=8.14, end=8.44),
        dict(cena='v14-assinatura', text='clara', start=8.50, end=8.80)
    ]
    return dict(bloco='D', duracao=limites[-1], duracao_voz=9.2,
                voz_ini=.24, P=.491835, falas=falas, palavras=palavras,
                cortes_cena=[5.81],
                cenas=[dict(id=id_, ini=a, dur=b-a) for id_, a, b in zip(ids, limites, limites[1:])])


class BlocoD(unittest.TestCase):
    def test_regua_d_conserva_voz_e_reserva_margem(self):
        original = regua_d()
        r = render.preparar_bloco(original, margem_quadros=30)
        self.assertEqual(r['falas'], original['falas'])
        self.assertEqual(r['palavras'], original['palavras'])
        self.assertAlmostEqual(r['bloco_fim'], 13.771374999999992)
        esperado_total = (math.ceil(13.771374999999992 * 60 - 1e-7) + 30) / 60
        self.assertAlmostEqual(r['total'], esperado_total)
        self.assertEqual([c['id'] for c in r['cenas']], ['v13-fecho', 'v14-assinatura'])
        with self.assertRaises(ValueError):
            ruim = regua_d()
            ruim['cenas'][1]['id'] = 'v99-inexistente'
            render.preparar_bloco(ruim)

    def test_continuidade_c_d_relogio_fecho_logo_a1_pouso(self):
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

                    r = render.preparar_bloco(regua_d(), 30)
                    info = pg.evaluate('r=>window.boot(r, "pt")', r)
                    self.assertEqual(info['bloco'], 'D')

                    # 1. Continuidade inicial no t=0 herdada de estado-fim-C.json
                    pg.evaluate('()=>window.seek(0)')
                    estado0 = pg.evaluate('()=>window.estadoBlocoD()')
                    self.assertAlmostEqual(estado0['ponto']['x'], 1258, delta=1.0)
                    self.assertAlmostEqual(estado0['ponto']['y'], 515, delta=1.0)
                    self.assertAlmostEqual(estado0['ponto']['w'], 24, delta=1.0)
                    self.assertAlmostEqual(estado0['ponto']['h'], 24, delta=1.0)
                    self.assertEqual(estado0['fundo'], 'rgb(247, 243, 238)')
                    self.assertEqual(estado0['camera'], [1, 0, 0, 1, 0, 0])

                    # 2. v13: Relógio sem pressa e frases de espelho
                    pg.evaluate('()=>window.seek(1.0)')
                    v13_op = float(pg.locator('#d-v13').evaluate('(e)=>getComputedStyle(e).opacity'))
                    self.assertGreater(v13_op, 0.9)
                    relogio_op = float(pg.locator('#d-relogio').evaluate('(e)=>getComputedStyle(e).opacity'))
                    self.assertGreater(relogio_op, 0.9)

                    # Frase 1 visível aos 1.0s
                    f1 = pg.locator('#d-f1').text_content().strip()
                    self.assertIn('Menos tempo', f1)

                    # Frase 2 visível aos 2.8s
                    pg.evaluate('()=>window.seek(2.8)')
                    f2 = pg.locator('#d-f2').text_content().strip()
                    self.assertIn('Mais tempo', f2)

                    # Frase 3 visível aos 4.8s
                    pg.evaluate('()=>window.seek(4.8)')
                    f3 = pg.locator('#d-f3').text_content().strip()
                    self.assertIn('Frila cuida', f3)

                    # Sem legenda duplicada no rodapé (NOCAP)
                    cap_op = float(pg.locator('#cap').evaluate('(e)=>getComputedStyle(e).opacity'))
                    self.assertEqual(cap_op, 0.0)

                    # 3. v14: Assinatura e Logo A1
                    pg.evaluate('()=>window.seek(7.5)')
                    v14_op = float(pg.locator('#d-v14').evaluate('(e)=>getComputedStyle(e).opacity'))
                    self.assertGreater(v14_op, 0.9)

                    # Pouso do ponto no pingo do "i" de Frila
                    pg.evaluate('()=>window.seek(9.0)')
                    estado14 = pg.evaluate('()=>window.estadoBlocoD()')
                    # Pingo do 'i': idot=(957, 338) aproximadamente
                    self.assertAlmostEqual(estado14['ponto']['x'], 957, delta=6.0)
                    self.assertAlmostEqual(estado14['ponto']['y'], 338, delta=6.0)

                    # Tag de assinatura, contato e rodapé
                    tag_tx = pg.locator('#d-tag').text_content().strip()
                    self.assertEqual(tag_tx, 'Combinou? Pode contar. Dos dois lados.')
                    contato_tx = pg.locator('#d-contato').text_content().strip()
                    self.assertEqual(contato_tx, 'frila.org@gmail.com')

                    # 4. Ausência de cursor em toda a extensão (D8)
                    for t in (0, 1.0, 3.0, 5.5, 7.5, 9.5, 13.0):
                        pg.evaluate('t=>window.seek(t)', t)
                        has_cursor = pg.evaluate('()=>!!document.querySelector("#cur")')
                        self.assertFalse(has_cursor, f'Cursor detectado em t={t}')

                    # 5. Reversibilidade e determinismo de seek
                    pg.evaluate('()=>window.seek(3.0)')
                    antes = pg.screenshot()
                    pg.evaluate('()=>window.seek(9.0)')
                    pg.evaluate('()=>window.seek(3.0)')
                    self.assertEqual(pg.screenshot(), antes)

                    # 6. Margem de 30 frames congelada
                    pg.evaluate('()=>window.seek(13.771374999999992)')
                    fim = pg.evaluate('()=>window.estadoBlocoD()')
                    pg.evaluate('()=>window.seek(14.20)')
                    fim_margem = pg.evaluate('()=>window.estadoBlocoD()')
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
