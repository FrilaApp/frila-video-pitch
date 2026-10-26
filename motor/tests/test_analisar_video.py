"""Casos adversariais para o detector D2; não dependem de cenas do Frila."""
import importlib.util
import pathlib
import unittest
import numpy as np

CAMINHO = pathlib.Path(__file__).parents[1] / 'analisar_video.py'

class Detectores(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if CAMINHO.exists():
            spec = importlib.util.spec_from_file_location('analise', CAMINHO)
            cls.m = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(cls.m)
        else:
            cls.m = None

    def modulo(self):
        self.assertIsNotNone(self.m, 'Ferramenta D2 ainda não implementada')
        return self.m

    def test_flash_de_um_quadro_tem_instante_correto(self):
        m = self.modulo()
        frames = [np.zeros((90,160), np.uint8) for _ in range(90)]
        frames[30] = np.full((90,160), 220, np.uint8)
        achados, _ = m.analisar_quadros(iter(frames), 60)
        flashes = [x for x in achados if x['tipo'] == 'cintilacao']
        self.assertEqual(len(flashes), 1)
        self.assertAlmostEqual(flashes[0]['de'], .5)

    def test_pausa_nao_vira_travada_sem_expectativa(self):
        m = self.modulo()
        frames = [np.full((90,160), 80, np.uint8) for _ in range(90)]
        a, _ = m.analisar_quadros(iter(frames), 60)
        self.assertTrue(any(x['tipo'] == 'pausa_a_revisar' for x in a))
        self.assertFalse(any(x['tipo'] == 'travada' for x in a))
        b = m.aplicar_contrato(a, [], {'movimento':[{'de':0,'ate':1.4}]})
        self.assertTrue(any(x['tipo'] == 'travada' for x in b))

    def test_corte_grande_e_marcado_como_salto_suspeito(self):
        m = self.modulo()
        rng = np.random.default_rng(7)
        a = rng.integers(0,255,(90,160),dtype=np.uint8)
        b = np.roll(a, 35, axis=1)
        achados, _ = m.analisar_quadros(iter([a]*15+[b]*15), 60)
        self.assertTrue(any(x['tipo'] == 'salto' and x['de'] == .25 for x in achados))

    def test_contrato_pega_ausencia_e_presenca_fora_da_janela(self):
        m = self.modulo()
        quadros = [{'t':i/12,'elementos':{'ponto':{'o':1,'x':20,'y':20,'w':20,'h':20}} if i not in (5,6) else {}} for i in range(18)]
        a = m.aplicar_contrato([], quadros, {'presenca':[{'id':'ponto','de':.25,'ate':1,'exclusivo':True}]})
        self.assertTrue(any(x['tipo'] == 'sumiço' for x in a))
        self.assertTrue(any(x['tipo'] == 'nascimento' for x in a))

    def test_contrato_detecta_aparelho_quase_apagado_na_emenda(self):
        m = self.modulo()
        q = [{'t':1,'elementos':{'telefone':{'o':.2,'x':20,'y':20,'w':200,'h':700}}}]
        a = m.aplicar_contrato([],q,{'presenca':[{'id':'telefone','de':.8,'ate':1.2,'opacidade_min':.5}]})
        self.assertTrue(any(x['tipo']=='sumiço' for x in a))

    def test_selector_de_continuidade_escolhe_instancia_visivel(self):
        m = self.modulo()
        import os
        os.environ['PLAYWRIGHT_BROWSERS_PATH'] = str(CAMINHO.parent / 'browsers')
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            b = pw.chromium.launch()
            pg = b.new_page(viewport={'width':1920,'height':1080})
            pg.set_content('<div id="stage"><div class="phone" style="display:none"></div><div class="phone" style="position:absolute;left:100px;top:100px;width:200px;height:700px;background:black"></div></div>')
            q = pg.evaluate(m.COLETA,{'telefone':'.phone'})
            b.close()
        self.assertIn('telefone',q['elementos'])
        self.assertEqual(q['elementos']['telefone']['w'],200)

    def test_janelas_exclusivas_do_mesmo_id_formam_uniao(self):
        m = self.modulo()
        qs = [{'t':t,'elementos':{'ponto':{'x':20,'y':20,'w':20,'h':20,'o':1}}} for t in [.5,1.5,2.5]]
        janelas = [{'id':'ponto','de':0,'ate':1,'exclusivo':True},
                   {'id':'ponto','de':2,'ate':3,'exclusivo':True}]
        a = m.aplicar_contrato([],qs,{'presenca':janelas})
        self.assertEqual([x['de'] for x in a if x['tipo']=='nascimento'],[1.5])

    def test_presenca_ignora_aparelho_totalmente_encoberto(self):
        m = self.modulo()
        import os
        os.environ['PLAYWRIGHT_BROWSERS_PATH'] = str(CAMINHO.parent / 'browsers')
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            b = pw.chromium.launch()
            pg = b.new_page(viewport={'width':1920,'height':1080})
            pg.set_content('<div id="stage"><div id="phone" style="position:absolute;left:100px;top:100px;width:200px;height:700px;background:black"></div><div style="position:absolute;inset:0;background:white"></div></div>')
            q = pg.evaluate(m.COLETA,{'telefone':'#phone'})
            b.close()
        self.assertNotIn('telefone',q['elementos'])

    def test_regua_rejeita_lacunas_ordem_ids_e_duracao_invalida(self):
        m = self.modulo()
        self.assertTrue(hasattr(m,'validar_regua'))
        meta = {'duration':1,'fps':60}
        casos = [
            [{'id':'a','ini':0,'dur':.5}],
            [{'id':'a','ini':.5,'dur':.5},{'id':'b','ini':0,'dur':.5}],
            [{'id':'a','ini':0,'dur':.5},{'id':'a','ini':.5,'dur':.5}],
            [{'id':'a','ini':0,'dur':float('nan')}],
        ]
        for cenas in casos:
            with self.subTest(cenas=cenas), self.assertRaises(ValueError):
                m.validar_regua({'total':1,'cenas':cenas},meta)
        m.validar_regua({'total':1,'cenas':[{'id':'a','ini':0,'dur':.5},{'id':'b','ini':.5,'dur':.5}]},meta)

    def test_selector_explicito_substitui_default_sem_mascarar_ausencia(self):
        m = self.modulo()
        self.assertTrue(hasattr(m,'seletores_acompanhados'))
        import os
        os.environ['PLAYWRIGHT_BROWSERS_PATH'] = str(CAMINHO.parent / 'browsers')
        from playwright.sync_api import sync_playwright
        contrato = {'presenca':[{'id':'ponto','selector':'#outro','de':0,'ate':1}]}
        with sync_playwright() as pw:
            b = pw.chromium.launch()
            pg = b.new_page(viewport={'width':1920,'height':1080})
            pg.set_content('<div id="stage"><div id="dot" style="position:absolute;left:100px;top:100px;width:20px;height:20px;background:black"></div></div>')
            q = pg.evaluate(m.COLETA,m.seletores_acompanhados(contrato))
            b.close()
        q['t'] = .5
        a = m.aplicar_contrato([],[q],contrato)
        self.assertTrue(any(x['tipo']=='sumiço' for x in a))

    def test_textos_colidem_mas_linhas_separadas_nao(self):
        m = self.modulo()
        textos = [{'id':'a','texto':'Um','l':0,'t':0,'r':80,'b':30,'o':1},
                  {'id':'b','texto':'Dois','l':60,'t':10,'r':120,'b':40,'o':1},
                  {'id':'c','texto':'Três','l':0,'t':60,'r':80,'b':90,'o':1}]
        pares = m.colisoes_texto(textos)
        self.assertEqual([(x['a'],x['b']) for x in pares], [('Um','Dois')])

    def test_texto_encoberto_por_fundo_opaco_nao_colide(self):
        m = self.modulo()
        import os
        os.environ['PLAYWRIGHT_BROWSERS_PATH'] = str(CAMINHO.parent / 'browsers')
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            b = pw.chromium.launch()
            pg = b.new_page(viewport={'width':1920,'height':1080})
            pg.set_content('<div id="stage"><span style="position:absolute;left:40px;top:40px">ENCObERTO</span><div style="position:absolute;left:0;top:0;width:600px;height:400px;background:#18191C"></div><span style="position:absolute;left:40px;top:40px;color:white">VISÍVEL</span></div>')
            q = pg.evaluate(m.COLETA,{})
            b.close()
        self.assertEqual([x['texto'] for x in q['textos']], ['VISÍVEL'])

    def test_mp4_real_preserva_flash_de_um_quadro_a_60fps(self):
        self.modulo()
        import json, subprocess, sys, tempfile
        with tempfile.TemporaryDirectory() as pasta:
            pasta = pathlib.Path(pasta)
            video = pasta / 'controle.mp4'
            quadros = np.full((120,90,160), 80, dtype=np.uint8)
            quadros[30] = 220
            subprocess.run(['ffmpeg','-v','error','-f','rawvideo','-pix_fmt','gray',
                '-s','160x90','-r','60','-i','-','-c:v','libx264','-pix_fmt','yuv420p',str(video)],
                input=quadros.tobytes(),check=True)
            regua = pasta/'tempos.json'
            regua.write_text(json.dumps({'total':2,'cenas':[{'id':'controle','ini':0,'dur':2}]}))
            subprocess.run([sys.executable,str(CAMINHO),str(video),'--tempos',str(regua),
                '--saida',str(pasta/'resultado'),'--sem-artefatos'],check=True,capture_output=True)
            relatorio = json.loads((pasta/'resultado/achados.json').read_text())
            flashes = [a for a in relatorio['achados'] if a['tipo']=='cintilacao']
            self.assertEqual(len(flashes),1)
            self.assertAlmostEqual(flashes[0]['de'],.5,places=5)
            self.assertEqual(relatorio['amostragem']['raster_fps'],60)

    def test_faixa_amostra_frames_reais_sem_deslocar_meio_intervalo(self):
        m = self.modulo()
        self.assertTrue(hasattr(m,'amostras_cena'), 'Faixa ainda usa fps sem controlar frame selecionado')
        import subprocess, tempfile
        with tempfile.TemporaryDirectory() as pasta:
            video = pathlib.Path(pasta)/'relogio.mp4'
            frames = np.stack([np.full((90,160),40+i,np.uint8) for i in range(120)])
            subprocess.run(['ffmpeg','-v','error','-f','rawvideo','-pix_fmt','gray','-s','160x90',
                '-r','60','-i','-','-c:v','libx264','-pix_fmt','yuv420p',str(video)],input=frames.tobytes(),check=True)
            amostras = list(m.amostras_cena(video,.203,.8,60))
            self.assertAlmostEqual(amostras[0][0],13/60)
            esperado = np.array(m.quadro(video,13/60,320),dtype=float)
            self.assertLess(np.abs(np.array(amostras[0][1],dtype=float)-esperado).mean(),1)
            self.assertAlmostEqual(amostras[1][0]-amostras[0][0],1/12)

    def test_corte_fora_da_grade_rotula_somente_frames_existentes(self):
        m = self.modulo()
        ts = m.instantes_corte(3.4428,76.733333,60)
        self.assertTrue(all(abs(t*60-round(t*60))<.0001 for t in ts))
        self.assertIn(3.433333,ts)
        self.assertIn(3.45,ts)

    def test_faixa_inclui_os_dois_lados_e_limita_inicio(self):
        m = self.modulo()
        ts = m.instantes_corte(.2, 2, 60)
        self.assertEqual(ts[0], 0)
        self.assertIn(round(.2-1/60,6), ts)
        self.assertIn(.2, ts)
        self.assertLessEqual(ts[-1], .7)

if __name__ == '__main__':
    unittest.main()
