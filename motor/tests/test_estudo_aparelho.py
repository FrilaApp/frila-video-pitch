"""Regressões D7/D8 sobre a fonte real v4; aprovação artística exige vídeo."""
import importlib.util
import json
from pathlib import Path
import subprocess
import unittest


class CameraDoEstudo(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path = Path(__file__).parents[1] / 'fotos.py'
        spec = importlib.util.spec_from_file_location('fotos_estudo', path)
        cls.f = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.f)

    def test_camera_continua_e_retorna_ao_enquadramento_geral(self):
        for t in (0, .2, .6, 2.9, 3.6):
            self.assertEqual(self.f.camera_estudo(t)['zoom'], 1)
        self.assertAlmostEqual(self.f.camera_estudo(1.3)['zoom'], 1.1)
        zs = [self.f.camera_estudo(i / 60)['zoom'] for i in range(217)]
        self.assertLess(max(abs(b - a) for a, b in zip(zs, zs[1:])), .008)
        self.assertTrue(all(a <= b for a, b in zip(zs[:78], zs[1:79])))
        self.assertTrue(all(a >= b for a, b in zip(zs[120:], zs[121:])))

    def test_acao_isolada_preserva_tempo_de_pressao_e_confirmacao(self):
        for t, tv in [(0, 25.55), (1.3, 25.792), (1.9, 26.312), (3.6, 26.55)]:
            self.assertAlmostEqual(self.f.tempo_v4_estudo(t), tv)

    def test_chassi_ui_e_ilha_crescem_juntos_sem_cursor_ou_recorte(self):
        from playwright.sync_api import sync_playwright
        raiz = Path(__file__).parents[2]
        fonte = subprocess.check_output(['git', 'show', '4efa75a:motor/filme.html'], cwd=raiz).decode()
        regua = json.loads((raiz / 'docs/v4/tempos-pt.json').read_text())
        servidor = self.f.servidor()
        try:
            with sync_playwright() as pw:
                b = pw.chromium.launch()
                try:
                    pg = b.new_page(viewport={'width': 1920, 'height': 1080})
                    pg.goto(f'http://127.0.0.1:{servidor.server_port}/docs/v4/COPIA-NOVA-VAGA.md')
                    pg.set_content(self.f.fonte_estudo(fonte, regua, 'Você publica a vaga.'))
                    pg.evaluate('r=>window.boot(r,"pt")', {'total': 3.6, 'cenas': [{'id': 'estudo', 'ini': 0, 'dur': 3.6}]})
                    pg.evaluate('()=>window.seek(0)')
                    medir = r'''()=>{
                      const r=s=>{const x=document.querySelector(s).getBoundingClientRect();return {x:x.x,y:x.y,w:x.width,h:x.height}};
                      const o=s=>{let o=1;for(let e=document.querySelector(s);e;e=e.parentElement){const c=getComputedStyle(e);if(c.display==='none')return 0;o*=Number(c.opacity)}return o};
                      return {corpo:r('#dot'),tela:r('#scr'),ilha:r('#isl'),campo:r('#fF'),botao:r('#pub'),confirmacao:r('#pubB'),cursor:o('#cur'),publicar:o('#pubA'),publicada:o('#pubB')};
                    }'''
                    estados = []
                    for n in range(216):
                        t = n / 60
                        pg.evaluate(self.f.ATUALIZAR_ESTUDO, [self.f.tempo_v4_estudo(t), self.f.camera_estudo(t), 'Você publica a vaga.'])
                        e = pg.evaluate(medir)
                        estados.append(e)
                        corpo, tela = e['corpo'], e['tela']
                        self.assertEqual(e['cursor'], 0, f'Cursor visível em {t}s')
                        self.assertGreaterEqual(corpo['x'], 0)
                        self.assertGreaterEqual(corpo['y'], 0)
                        self.assertLessEqual(corpo['y'] + corpo['h'], 980)
                        self.assertAlmostEqual(tela['w'] / corpo['w'], 352 / 380, places=4)
                        self.assertAlmostEqual(e['ilha']['w'] / corpo['w'], 110 / 380, places=4)
                        self.assertAlmostEqual((e['campo']['y'] - tela['y']) / tela['h'], 190 / 752, places=4)
                        for nome in ('botao', 'confirmacao'):
                            r = e[nome]
                            self.assertGreaterEqual(r['x'], tela['x'])
                            self.assertLessEqual(r['x'] + r['w'], tela['x'] + tela['w'])
                            self.assertGreaterEqual(r['y'], tela['y'])
                            self.assertLessEqual(r['y'] + r['h'], tela['y'] + tela['h'])
                    self.assertAlmostEqual(estados[78]['corpo']['w'] / estados[0]['corpo']['w'], 1.1, places=4)
                    self.assertEqual(estados[0]['publicar'], 1)
                    self.assertEqual(estados[0]['publicada'], 0)
                    self.assertGreater(estados[-1]['publicada'], .99)
                    self.assertEqual(estados[-1]['publicar'], 0)
                    pg.evaluate(self.f.ATUALIZAR_ESTUDO, [25.55, self.f.camera_estudo(0), 'Você publica a vaga.'])
                    self.assertEqual(pg.evaluate(medir), estados[0], 'seek deve ser reversível')
                finally:
                    b.close()
        finally:
            servidor.shutdown()
            servidor.server_close()
