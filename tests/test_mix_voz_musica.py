"""Voz aprovada não muda; música é contínua entre saltos declarados."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import numpy as np
from motor import audio2
from motor.audio_util import SR,ler,salvar

ROOT=Path(__file__).resolve().parents[1]

class MixVozMusica(unittest.TestCase):
    def test_voz_bit_a_bit_e_efeitos_desligados_sem_sintese(self):
        with tempfile.TemporaryDirectory() as tmp:
            d=Path(tmp); x=(.012*np.sin(np.arange(4800)*.05)).astype('float32')
            salvar(d/'voz.wav',x); salvar(d/'musica.wav',np.tile(x,30))
            t={'total':3.,'bar':3.,'musica':[{'src':0.,'v':0.}], 'cenas':[],
               'falas':[{'id':'voz','cena':'cena','k':1,'ini':1.,'fim':1.1,
                         'arquivo':str(d/'voz.wav'),'fala':'Teste.'}]}
            cfg=json.loads((ROOT/'motor/mixagem.json').read_text())
            cfg['voz']['preservar_amostras']=True
            cfg['efeitos']['habilitado']=False
            cfg['musica'].pop('montagem',None)
            with patch.object(audio2,'sintetizar_evento',side_effect=AssertionError('efeitos devem estar desligados')):
                m=audio2.montar(t,[{'id':'proibido','tipo':'grave','t':1}],cfg,d/'sessao',trilha=d/'musica.wav')
            voz=ler(d/'sessao/stems/voz.wav',1)[:,0]
            self.assertTrue(np.array_equal(voz[SR:SR+len(x)],x))
            self.assertEqual(m['frases'][0]['ganho_db'],0)
            self.assertEqual(m['eventos'],[])
            self.assertFalse(np.any(ler(d/'sessao/stems/efeitos-duck.wav',2)))
            soma=(ler(d/'sessao/stems/voz.wav',2)+ler(d/'sessao/stems/musica-duck.wav',2)).astype('float32')
            self.assertTrue(np.array_equal(soma,ler(d/'sessao/premix.wav',2)))

    def test_compassos_contiguos_nao_recebem_crossfade(self):
        self.assertTrue(callable(getattr(audio2,'montagem_musical',None)), 'Falta montagem por trechos contínuos')
        with tempfile.TemporaryDirectory() as tmp:
            d=Path(tmp); src=(.1*np.sin(np.arange(6*SR)*.013)).astype('float32')
            salvar(d/'fonte.wav',np.column_stack([src,src]))
            plano={'origem_s':0,'crossfade_ms':40,'fade_final_ms':0,
                   'trechos':[{'ini_compasso':0,'fim_compasso':3,'origem_compasso':1}]}
            t={'bar':1.,'total':3.,'falas':[]}
            y=audio2.montagem_musical(t,3*SR,d/'fonte.wav',plano)
            self.assertTrue(np.array_equal(y[:,0],src[SR:4*SR]))

    def test_crossfade_musical_sobre_fala_bloqueia(self):
        self.assertTrue(callable(getattr(audio2,'montagem_musical',None)))
        with tempfile.TemporaryDirectory() as tmp:
            d=Path(tmp); salvar(d/'fonte.wav',np.full((5*SR,2),.1,dtype='float32'))
            plano={'origem_s':0,'crossfade_ms':40,'fade_final_ms':0,
                   'trechos':[{'ini_compasso':0,'fim_compasso':1,'origem_compasso':0},
                              {'ini_compasso':1,'fim_compasso':2,'origem_compasso':3}]}
            t={'bar':1.,'total':2.,'falas':[{'ini':.99,'fim':1.02}]}
            with self.assertRaisesRegex(ValueError,'fala|palavra'):
                audio2.montagem_musical(t,2*SR,d/'fonte.wav',plano)

if __name__=='__main__': unittest.main()
