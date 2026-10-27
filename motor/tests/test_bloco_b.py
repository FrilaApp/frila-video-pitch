"""Régua e continuidade do B; geometria real em Chromium headless."""
import json
import os
from pathlib import Path
import sys
import unittest

RAIZ = Path(__file__).parents[2]
sys.path.insert(0, str(RAIZ / 'motor'))
import render
from fotos import servidor


def regua_b():
    roteiro = json.loads((RAIZ / 'roteiro.json').read_text())
    ids = ['v05-virada', 'v06-solucao1', 'v07-solucao2', 'v09-solucao3']
    limites = [0, 4.32, 9.94, 15.65, 19.673395833333334]
    janelas = [[(.2, 4.12)], [(4.52, 5.64), (6.1, 9.66)],
               [(10.22, 12.54), (13.04, 15.32)], [(15.98, 19.42)]]
    falas = []
    for id_, js in zip(ids, janelas):
        tx = next(c['pt']['legenda'] for c in roteiro['cenas'] if c['id'] == id_)
        for k, ((a, b), texto) in enumerate(zip(js, tx.split('. ')), 1):
            if not texto.endswith(('.', '?')): texto += '.'
            falas.append(dict(cena=id_, k=k, ini=a, fim=b, leg_ini=a-.05,
                              leg_fim=b+.1, legenda=texto))
    palavras = [dict(cena='v05-virada', text='conecta', start=.74, end=1.24),
                dict(cena='v06-solucao1', text='publica', start=4.84, end=5.18),
                dict(cena='v06-solucao1', text='avisa', start=6.58, end=7.02),
                dict(cena='v06-solucao1', text='até', start=8.42, end=8.64),
                dict(cena='v07-solucao2', text='check-in.', start=14.94, end=15.32),
                dict(cena='v09-solucao3', text='Chamaria', start=18.62, end=19)]
    return dict(bloco='B', duracao=limites[-1], duracao_voz=19.922708333333333,
                voz_ini=.08, P=.491835, falas=falas, palavras=palavras,
                cenas=[dict(id=id_, ini=a, dur=b-a) for id_, a, b in zip(ids, limites, limites[1:])])


class BlocoB(unittest.TestCase):
    def test_regua_b_conserva_voz_e_reserva_margem(self):
        original = regua_b()
        r = render.preparar_bloco(original, margem_quadros=30)
        self.assertEqual(r['falas'], original['falas'])
        self.assertEqual(r['palavras'], original['palavras'])
        self.assertEqual(r['voz_duracao'], original['duracao_voz'])
        self.assertAlmostEqual(r['bloco_fim'], 19.673395833333334)
        self.assertAlmostEqual(r['total'], 20.183333333333334)
        self.assertAlmostEqual(original['cenas'][-1]['dur'], 4.023395833333334)
        with self.assertRaises(ValueError):
            ruim = regua_b(); ruim['cenas'][2]['id'] = 'v08-inexistente'
            render.preparar_bloco(ruim)

    def test_chassi_continuo_camera_comum_copia_e_estado_a(self):
        from playwright.sync_api import sync_playwright
        os.environ['PLAYWRIGHT_BROWSERS_PATH'] = str(RAIZ / 'motor/browsers')
        s = servidor()
        try:
            with sync_playwright() as pw:
                b = pw.chromium.launch()
                try:
                    pg = b.new_page(viewport={'width':1920,'height':1080})
                    erros = []; pg.on('pageerror', lambda e: erros.append(str(e)))
                    pg.goto(f'http://127.0.0.1:{s.server_port}/motor/filme.html')
                    from motor.tests.test_bloco_a import regua_teste
                    a = render.preparar_bloco(regua_teste())
                    pg.evaluate('r=>window.boot(r,"pt")', a)
                    pg.evaluate('t=>window.seek(t)', a['bloco_fim'])
                    quadro_a = pg.screenshot()
                    r = render.preparar_bloco(regua_b(), 30)
                    info = pg.evaluate('r=>window.boot(r,"pt")', r)
                    self.assertEqual(info['bloco'], 'B')
                    pg.evaluate('()=>window.seek(0)')
                    estado = pg.evaluate('()=>window.estadoBlocoB()')
                    self.assertAlmostEqual(estado['ponto']['x'], 959.9983800039402)
                    self.assertAlmostEqual(estado['ponto']['y'], 760.0001618292611)
                    self.assertEqual(estado['vaga'], dict(x=660,y=588,w=600,h=104,o='1',texto='Garçom · hoje, 19h'))
                    self.assertEqual(estado['fundo'], 'rgb(247, 243, 238)')
                    self.assertEqual(estado['camera'], [1,0,0,1,0,0])
                    self.assertTrue(pg.screenshot() == quadro_a, 'Primeiro quadro B difere do estado final de A')
                    pg.evaluate('()=>window.chassiInicial=document.querySelector("#dot")')
                    medir = r'''()=>{
                     const d=document.querySelector('#dot'),a=d.getBoundingClientRect(),s=document.querySelector('#scr').getBoundingClientRect();
                     let o=1;for(let e=d;e;e=e.parentElement){const c=getComputedStyle(e);o*=Number(c.opacity);if(c.display==='none')o=0;}
                     return {x:a.x,y:a.y,w:a.width,h:a.height,sw:s.width,sh:s.height,o,
                      mesmo:d===window.chassiInicial,n:document.querySelectorAll('#dot').length,
                      comum:d.parentElement===document.querySelector('#scr').parentElement,
                      titulo:!!document.querySelector('#b-titulo'),cursor:!!document.querySelector('#cur')};
                    }'''
                    anterior = None
                    for n in range(260, 1181):
                        t=n/60; pg.evaluate('t=>window.seek(t)',t)
                        a=pg.evaluate(medir)
                        self.assertTrue(a['mesmo']); self.assertEqual(a['n'],1)
                        self.assertTrue(a['comum']); self.assertEqual(a['o'],1)
                        self.assertFalse(a['titulo']); self.assertFalse(a['cursor'])
                        self.assertAlmostEqual(a['sw']/a['w'],352/380,places=4)
                        self.assertAlmostEqual(a['sh']/a['h'],752/780,places=4)
                        self.assertGreaterEqual(a['y'],17)
                        self.assertLessEqual(a['y']+a['h'],963)
                        if anterior:
                            self.assertLess(abs(a['x']-anterior['x']),5)
                            self.assertLess(abs(a['h']-anterior['h']),8)
                        anterior=a
                    pg.evaluate('()=>window.seek(5)')
                    self.assertEqual(pg.locator('#b-rotulo').text_content().strip(),'Exemplo')
                    pg.evaluate('()=>window.seek(18.6)')
                    self.assertGreater(float(pg.locator('#b-avaliacao').evaluate('(e)=>getComputedStyle(e).opacity')),.99)
                    pg.evaluate('()=>window.seek(19.673395833333334)')
                    fim=pg.evaluate('()=>window.estadoBlocoB()')
                    pg.evaluate('()=>window.seek(20.17)')
                    self.assertEqual(pg.evaluate('()=>window.estadoBlocoB()'),fim)
                    pg.evaluate('()=>window.seek(11.2)'); antes=pg.screenshot()
                    pg.evaluate('()=>window.seek(17)');pg.evaluate('()=>window.seek(11.2)')
                    self.assertEqual(pg.screenshot(),antes)
                    self.assertEqual(erros,[])
                finally:
                    b.close()
        finally:
            s.shutdown();s.server_close()
