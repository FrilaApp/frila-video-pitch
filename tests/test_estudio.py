import json
from pathlib import Path
import tempfile
import unittest
import numpy as np

class Estudio(unittest.TestCase):
    def test_reserva_persistente_bloqueia_teto_antes_da_api(self):
        from vozes import estudio
        with tempfile.TemporaryDirectory() as tmp:
            ledger=Path(tmp)/'ledger.json'
            estudio.reservar_tts(ledger,'primeira','voz','pcm_48000',{'text':'a'*2900})
            with self.assertRaisesRegex(ValueError,'3000'):
                estudio.reservar_tts(ledger,'segunda','voz','pcm_48000',{'text':'b'*101})
            self.assertEqual(sum(x['caracteres_texto'] for x in json.loads(ledger.read_text())),2900)
            with self.assertRaisesRegex(ValueError,'solicitada'):
                estudio.reservar_tts(ledger,'primeira','voz','pcm_48000',{'text':'a'*2900})

    def test_banda_nao_confunde_grave_da_musica_com_regiao_de_fala(self):
        from vozes import estudio
        sr=48000; t=np.arange(sr)/sr
        grave=np.sin(2*np.pi*80*t).astype('float32')
        fala=np.sin(2*np.pi*1000*t).astype('float32')
        self.assertGreater(estudio.banda_db(fala)-estudio.banda_db(grave),70)
        self.assertTrue(np.array_equal(estudio.filtro_banda(fala),estudio.filtro_banda(fala)))

if __name__=='__main__': unittest.main()

class Sidechain(unittest.TestCase):
    def test_sidechain_usa_sinal_e_respeita_teto_raso(self):
        from motor import audio2
        from motor.audio_util import SR,salvar
        self.assertTrue(callable(getattr(audio2,'sidechain_raso',None)))
        with tempfile.TemporaryDirectory() as tmp:
            d=Path(tmp); x=np.zeros(3*SR,dtype='float32'); x[SR:2*SR]=.2*np.sin(np.arange(SR)*.1)
            salvar(d/'voz.wav',x)
            g=audio2.sidechain_raso(d/'voz.wav',d,8)
            self.assertEqual(len(g),len(x))
            self.assertGreaterEqual(float(g.min()),10**(-8/20)-1e-6)
            self.assertLess(float(g[round(1.5*SR)]),.6)
            self.assertGreater(float(g[round(.5*SR)]),.99)
            self.assertGreater(float(g[-1]),.9)

class Direcao(unittest.TestCase):
    def test_tags_nao_autorizam_reescrever_roteiro(self):
        from vozes import estudio
        self.assertTrue(callable(getattr(estudio,'validar_direcao',None)))
        texto='O Frila conecta quem precisa de gente a profissionais perto.'
        self.assertEqual(estudio.validar_direcao('[happy] '+texto,texto),texto)
        with self.assertRaises(ValueError): estudio.validar_direcao('[happy] O Frila resolve tudo.',texto)
        with self.assertRaises(ValueError): estudio.validar_direcao('Meta: oito semanas.','Meta: oito semanas.')
