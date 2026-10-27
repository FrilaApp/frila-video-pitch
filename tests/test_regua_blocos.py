"""Regressões da régua: frases permanecem na tomada; legendas não são cortes."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
import wave
from motor import tempos2
from motor.audio_util import hash_arquivo


class ReguaBlocos(unittest.TestCase):
    def test_cortes_locais_usam_meio_da_pausa_sem_mover_palavras(self):
        self.assertTrue(callable(getattr(tempos2, 'janela_bloco', None)),
                        'Falta exportação da janela local por bloco')
        cenas = [
            {'id':'v01-gancho','pt':{'fala':'Hoje. Faltou gente.','legenda':'Hoje. Faltou gente.'},'janela_s':4},
            {'id':'v02-dor1','pt':{'fala':'Cadastro não é turno.','legenda':'Cadastro não é turno.'},'janela_s':6}]
        palavras = [{'text':t,'start':a,'end':b,'type':'word'} for t,a,b in [
            ('Hoje.',.1,.5),('Faltou',.8,1.1),('gente.',1.2,1.6),
            ('Cadastro',2.2,2.6),('não',2.7,2.8),('é',2.9,3.),('turno.',3.1,3.5)]]
        origem=copy.deepcopy(palavras)
        d=tempos2.janela_bloco('A',cenas,palavras,4.,.5,6.,10.)
        self.assertAlmostEqual(d['cenas'][0]['fim'],2.4)
        self.assertEqual(d['cenas'][1]['ini'],d['cenas'][0]['fim'])
        self.assertEqual(palavras,origem)
        for w,raw in zip(d['palavras'],origem):
            self.assertAlmostEqual(w['start']-.5,raw['start'])
            self.assertAlmostEqual(w['end']-.5,raw['end'])
        self.assertEqual(d['ini_global'],10.)
        self.assertEqual([c['id'] for c in d['cenas']],['v01-gancho','v02-dor1'])
        self.assertAlmostEqual(d['cenas'][0]['dur'],2.4)
        self.assertTrue(d['cenas'][0]['apertada'])
        self.assertEqual(len(d['falas']),3)
        self.assertAlmostEqual(d['falas'][0]['ini'],.6)

    def test_texto_divergente_ou_frase_atravessada_nao_gera_regua(self):
        self.assertTrue(callable(getattr(tempos2,'janela_bloco',None)))
        c=[{'id':'v01','pt':{'fala':'Não falta.','legenda':'Não falta.'},'janela_s':1}]
        with self.assertRaisesRegex(ValueError,'texto|Texto|Scribe'):
            tempos2.janela_bloco('A',c,[{'text':'Falta.','start':.1,'end':.4}],1,0,2,0)

    def test_a8_so_aceita_excecao_exata_e_vinculada_a_tomada(self):
        self.assertTrue(callable(getattr(tempos2,'validar_excecoes_a8',None)))
        a8={'estado':'falha','pendencias':[],'falhas':[
            {'regra':'A8_pausa_interna','ini':6.86,'fim':7.46,'duracao':.6}]}
        aceites=[{'regra':'A8_pausa_interna','ini':6.86,'fim':7.46,
                  'duracao':.6,'sha256':'take-c1','aprovador':'Fabrício','data':'2026-10-26'}]
        self.assertEqual(len(tempos2.validar_excecoes_a8(a8,aceites,'take-c1')),1)
        for hash_take in ['take-c2','']:
            with self.assertRaises(ValueError): tempos2.validar_excecoes_a8(a8,aceites,hash_take)
        outro=copy.deepcopy(a8); outro['falhas'][0]['ini']=7.36
        with self.assertRaises(ValueError): tempos2.validar_excecoes_a8(outro,aceites,'take-c1')
        dois=copy.deepcopy(a8); dois['falhas'].append({'regra':'A8_pausa_interna','ini':16.1,'fim':16.62,'duracao':.52})
        with self.assertRaises(ValueError): tempos2.validar_excecoes_a8(dois,aceites,'take-c1')

    def test_regua_oficial_separa_legendas_de_quatro_eventos_vocais(self):
        with tempfile.TemporaryDirectory() as tmp:
            raiz=Path(tmp); (raiz/'vozes').mkdir()
            roteiro={'cenas':[],'blocos':[]}
            selecao={'blocos':[],'regua':{'P':.491835,'bar':1.96734,
                     'compassos_limites':[0,13,23,33,40],
                     'recuos_voz_s':{'A':2.459175,'B':.08,'C':.34,'D':.24}}}
            hashes={}
            for nome,dur,ultimo in [('A',22.894875,22.26),('B',19.922708,19.34),
                                     ('C',19.551208,19.02),('D',8.962917,8.48)]:
                ids=[nome+'1',nome+'2']
                roteiro['blocos'].append({'id':nome,'cenas':ids})
                for cid,texto in zip(ids,['Uma.','Duas.']):
                    roteiro['cenas'].append({'id':cid,'pt':{'fala':texto,'legenda':texto},'janela_s':1})
                wav=raiz/f'{nome}.wav'
                with wave.open(str(wav),'wb') as w:
                    w.setparams((1,2,24000,0,'NONE','not compressed'))
                    w.writeframes(b'\x01\x00'*round(dur*24000))
                palavras=[{'text':'Uma.','start':.12,'end':.36},
                          {'text':'Duas.','start':ultimo-.4,'end':ultimo}]
                scribe=raiz/f'{nome}-scribe.json'; scribe.write_text(json.dumps({'words':palavras}))
                meta=raiz/f'{nome}.json'
                meta.write_text(json.dumps({'bloco':nome,'cenas':ids,'fala':'Uma. Duas.',
                    'sha256':hash_arquivo(wav),'palavras':palavras,
                    'resposta_scribe':scribe.name,'scribe_sha256':hash_arquivo(scribe)}))
                selecao['blocos'].append({'id':nome,'arquivo':wav.name,'metadados':meta.name,
                    'scribe':scribe.name,'sha256':hash_arquivo(wav),
                    'metadados_sha256':hash_arquivo(meta),'scribe_sha256':hash_arquivo(scribe),
                    'aprovacao_ouvido':{'aprovado':True,'aprovador':'Fabrício','data':'2026-10-26'},
                    'excecoes_a8':[]})
                hashes[wav]=hash_arquivo(wav)
            (raiz/'roteiro.json').write_text(json.dumps(roteiro))
            (raiz/'vozes/selecao-blocos-pt.json').write_text(json.dumps(selecao))
            a=tempos2.gerar_oficial(raiz,'A')
            self.assertEqual(a['bloco'],'A')
            self.assertFalse((raiz/'motor/cache/blocos-regua/B.json').exists())
            t=tempos2.gerar_oficial(raiz)
            self.assertEqual(len(t['audio_blocos']),4)
            self.assertEqual(len(t['falas']),8)
            self.assertEqual(len(t['cenas']),8)
            self.assertEqual(len(t['musica']),40)
            self.assertEqual([c['secao'] for c in t['musica']],['tensao']*13+['groove']*20+['calma']*7)
            self.assertAlmostEqual(t['total']/t['bar'],40,places=5)
            for f in t['fronteiras_blocos']:
                self.assertGreaterEqual(f['pausa_scribe_s'],.5)
                self.assertLessEqual(f['pausa_scribe_s'],1.2)
                self.assertGreaterEqual(f['tempo']-f['ultima_palavra_fim'],.12)
                self.assertGreaterEqual(f['primeira_palavra_ini']-f['tempo'],.12)
                self.assertGreaterEqual(f['folga_arquivos_s'],0)
            self.assertEqual(hashes,{p:hash_arquivo(p) for p in hashes})
            alvo=next(iter(hashes)); alvo.write_bytes(b'adulterado')
            with self.assertRaisesRegex(ValueError,'Hash'):
                tempos2.gerar_oficial(raiz)


if __name__=='__main__': unittest.main()
