"""Régua offline de tomadas aprovadas: legendas não recortam a voz."""
import json
from pathlib import Path
import wave

from motor.analisar_emendas import ler_scribe, validar_palavras, verificar_a8
from motor.audio_util import SR, gravar_json, hash_arquivo
from vozes.manifesto import frases_do_roteiro, normal


def validar_excecoes_a8(a8, excecoes, sha256):
    if a8['pendencias']:
        raise ValueError('A8 inconclusiva: ' + '; '.join(a8['pendencias']))
    usadas = []
    for falha in a8['falhas']:
        aceite = next((e for e in excecoes
                       if e.get('sha256') == sha256 and e.get('aprovador') == 'Fabrício'
                       and e.get('data') == '2026-10-26'
                       and e.get('regra') == falha['regra']
                       and all(abs(e.get(k, -1) - falha.get(k, -2)) < 1e-8
                               for k in ('ini', 'fim', 'duracao'))), None)
        if not aceite:
            raise ValueError('Falha A8 sem exceção de ouvido específica para esta tomada')
        usadas.append(aceite)
    if len(usadas) != len(excecoes):
        raise ValueError('Exceção A8 não corresponde à medição atual')
    return usadas


def ler_selecao(raiz, caminho=None):
    raiz = Path(raiz)
    caminho = Path(caminho) if caminho else raiz / 'vozes/selecao-blocos-pt.json'
    selecao = json.loads(caminho.read_text())
    roteiro = json.loads((raiz / 'roteiro.json').read_text())
    if [b['id'] for b in selecao['blocos']] != [b['id'] for b in roteiro['blocos']]:
        raise ValueError('Seleção e blocos do roteiro divergem')
    cenas = {c['id']: c for c in roteiro['cenas']}
    dados = []
    for item, bloco in zip(selecao['blocos'], roteiro['blocos']):
        ouvido = item['aprovacao_ouvido']
        if not (ouvido['aprovado'] and ouvido['aprovador'] == 'Fabrício' and ouvido['data']):
            raise ValueError('Bloco sem aprovação de ouvido registrada')
        arquivos = {k: raiz / item[k] for k in ('arquivo', 'metadados', 'scribe')}
        for k, campo in [('arquivo', 'sha256'), ('metadados', 'metadados_sha256'), ('scribe', 'scribe_sha256')]:
            if hash_arquivo(arquivos[k]) != item[campo]:
                raise ValueError(f'Hash da seleção diverge: {item["id"]}/{k}')
        meta = json.loads(arquivos['metadados'].read_text())
        cs = [cenas[cid] for cid in bloco['cenas']]
        if (meta['bloco'] != item['id'] or meta['cenas'] != bloco['cenas']
                or meta['fala'] != ' '.join(c['pt']['fala'] for c in cs)):
            raise ValueError('Texto/cenas da tomada e roteiro divergem')
        with wave.open(str(arquivos['arquivo'])) as w:
            duracao = w.getnframes() / w.getframerate()
        palavras = validar_palavras(ler_scribe(arquivos['metadados'], arquivos['arquivo']), duracao)
        a8 = verificar_a8([{'id': item['id'], 'fala': meta['fala']}], palavras)
        aceites = validar_excecoes_a8(a8, item['excecoes_a8'], item['sha256'])
        dados.append({'selecao': item, 'cenas': cs, 'meta': meta, 'palavras': palavras,
                      'duracao': duracao, 'a8': a8, 'excecoes_aplicadas': aceites,
                      'arquivo': str(arquivos['arquivo'].resolve())})
    return roteiro, selecao, dados


def janela_bloco(bloco, cenas, palavras, duracao_voz, voz_ini, duracao, ini_global):
    palavras = validar_palavras(palavras, duracao_voz)
    itens = frases_do_roteiro({'cenas': cenas})
    tokens, donos = [], []
    for f in itens:
        ts = normal(f['fala']); tokens.extend(ts); donos.extend([f['id']] * len(ts))
    if tokens != normal(' '.join(w['text'] for w in palavras)):
        raise ValueError('Texto e Scribe divergem; não gerar régua parcial')
    por_frase = {f['id']: [] for f in itens}
    cursor = 0
    locais = []
    for w in palavras:
        n = len(normal(w['text'])); fid = donos[cursor]
        if any(x != fid for x in donos[cursor:cursor+n]):
            raise ValueError('Palavra Scribe atravessa frases da fonte')
        cursor += n
        f = next(f for f in itens if f['id'] == fid)
        local = {**w, 'start': w['start'] + voz_ini, 'end': w['end'] + voz_ini,
                 'start_origem': w['start'], 'end_origem': w['end'],
                 'frase': fid, 'cena': f['cena']}
        por_frase[fid].append(local); locais.append(local)
    falas = [{**f, 'ini': por_frase[f['id']][0]['start'],
              'fim': por_frase[f['id']][-1]['end'], 'bloco': bloco} for f in itens]
    por_cena = {c['id']: [w for w in locais if w['cena'] == c['id']] for c in cenas}
    cortes = [(por_cena[a['id']][-1]['end'] + por_cena[b['id']][0]['start']) / 2
              for a,b in zip(cenas,cenas[1:])]
    limites = [0., *cortes, duracao]
    if any(b <= a for a,b in zip(limites,limites[1:])):
        raise ValueError('Corte não crescente ou duração insuficiente do bloco')
    janelas = []
    for i,c in enumerate(cenas):
        ws = por_cena[c['id']]; ini,fim = limites[i:i+2]
        if ws[0]['start'] < ini or ws[-1]['end'] > fim:
            raise ValueError('Palavra fora da cena')
        janelas.append({'id': c['id'], 'bloco': bloco, 'ini': ini, 'fim': fim, 'dur': fim-ini,
                        'janela_s_roteiro': c['janela_s'], 'apertada': fim-ini < c['janela_s'],
                        'palavras': ws})
        fs = [f for f in falas if f['cena'] == c['id']]
        for k,f in enumerate(fs):
            f['leg_ini'] = max(ini, f['ini'] - .05)
            f['leg_fim'] = min(fs[k+1]['ini'] - .05 if k+1<len(fs) else f['fim'] + .6, fim-.12)
            if f['leg_fim'] <= f['leg_ini']:
                raise ValueError('Legenda sem janela positiva')
    return {'versao':1,'bloco':bloco,'relogio':'tempo zero = início visual do bloco',
            'ini_global':ini_global,'duracao':duracao,'voz_ini':voz_ini,
            'voz_fim':voz_ini+duracao_voz,'duracao_voz':duracao_voz,
            'cauda_voz_apos_bloco_s':max(0.,voz_ini+duracao_voz-duracao),
            'nota_cauda':'Cauda não verbal pode atravessar corte visual; WAV inteiro, sem corte/fade.',
            'cenas':janelas,'falas':falas,'palavras':locais,
            'cortes_cena':cortes,'aprovacao_regua':None}


def _musica(limites, bar, origem=1.014):
    def trecho(n, primeiro, ultimo, virada, loop):
        corpo = list(range(primeiro,ultimo+1))
        while len(corpo) < n-1: corpo += list(range(*loop))
        return corpo[:n-1]+[virada]
    a,_,c,fim = limites[1:]
    fontes = (trecho(a,0,6,7,(1,7)) + trecho(c-a,8,22,23,(9,23))
              + [32+i%16 for i in range(fim-c)])
    return [{'v':i*bar,'src':origem+s*bar,
             'secao':'tensao' if i<a else 'groove' if i<c else 'calma',
             'ganho_db':-2 if i>=c else 0} for i,s in enumerate(fontes)]


def gerar_oficial(raiz, bloco=None):
    raiz = Path(raiz)
    roteiro, selecao, dados = ler_selecao(raiz)
    plano = selecao['regua']; bar = plano['bar']; comp = plano['compassos_limites']
    if (bar <= 0 or abs(bar-4*plano['P']) > 1e-9
            or len(comp) != len(dados)+1 or comp[0] != 0
            or any(not isinstance(v,int) for v in comp)
            or any(b<=a for a,b in zip(comp,comp[1:]))):
        raise ValueError('Grade de compassos inválida')
    amostras = [round(i*bar*SR) for i in comp]
    limites = [a/SR for a in amostras]
    if not 78 <= limites[-1] <= 90:
        raise ValueError('Régua fora do alvo de duração')
    saida = raiz / 'motor/cache/blocos-regua'
    cenas, falas, eventos, locais = [], [], [], []
    for i,d in enumerate(dados):
        nome = d['selecao']['id']
        if bloco and nome != bloco: continue
        recuo = round(plano['recuos_voz_s'][nome]*SR)/SR
        if recuo < 0:
            raise ValueError('Recuo de voz negativo')
        ini = limites[i]; dur = limites[i+1]-ini
        local = janela_bloco(nome,d['cenas'],d['palavras'],d['duracao'],recuo,dur,ini)
        local.update(arquivo=d['arquivo'],sha256=d['selecao']['sha256'],
                     scribe_sha256=d['selecao']['scribe_sha256'],
                     aprovacao_voz=d['selecao']['aprovacao_ouvido'],
                     a8_estado_medido=d['a8']['estado'],excecoes_a8=d['excecoes_aplicadas'],
                     compasso_ini=comp[i],compasso_fim=comp[i+1],
                     deslocamento_grade_s=ini-comp[i]*bar)
        # A é escrito antes de qualquer outro artefato de régua.
        gravar_json(saida/f'{nome}.json',local); locais.append(local)
        cenas += [{k:c[k] for k in ('id','bloco','dur','janela_s_roteiro','apertada')}
                  | {'ini':c['ini']+ini} for c in local['cenas']]
        falas += [{**f,**{k:f[k]+ini for k in ('ini','fim','leg_ini','leg_fim')}} for f in local['falas']]
        eventos.append({'id':f'bloco-{nome}','bloco':nome,'cena':d['cenas'][0]['id'],'k':1,
                        'ini':ini+recuo,'fim':ini+recuo+d['duracao'],
                        'ini_amostra':amostras[i]+round(recuo*SR),
                        'arquivo':d['arquivo'],'sha256':d['selecao']['sha256'],
                        'fala':d['meta']['fala'],'aprovada':True,
                        'aprovacao_ouvido':d['selecao']['aprovacao_ouvido'],
                        'excecoes_a8':d['excecoes_aplicadas']})
    if bloco:
        if not locais: raise ValueError('Bloco inexistente')
        return locais[0]
    fronteiras=[]
    for i,(a,b) in enumerate(zip(locais,locais[1:]),1):
        ultimo=a['palavras'][-1]['end']+a['ini_global']
        primeiro=b['palavras'][0]['start']+b['ini_global']
        corte=limites[i]; pausa=primeiro-ultimo
        if not .5 <= pausa <= 1.2 or min(corte-ultimo,primeiro-corte)<.12:
            raise ValueError('Fronteira sem pausa/proteção temporal válida')
        if eventos[i-1]['fim'] > eventos[i]['ini']:
            raise ValueError('WAVs completos sobrepostos')
        fronteiras.append({'de':a['bloco'],'para':b['bloco'],'tempo':corte,
                           'compasso':comp[i],'pausa_scribe_s':pausa,
                           'ultima_palavra_fim':ultimo,'primeira_palavra_ini':primeiro,
                           'folga_arquivos_s':eventos[i]['ini']-eventos[i-1]['fim'],
                           'escuta_montagem':None})
    r={'lang':'pt','P':plano['P'],'bar':bar,'total':limites[-1],
       'cenas':cenas,'falas':falas,'musica':_musica(comp,bar),
       'audio_blocos':eventos,'fronteiras_blocos':fronteiras,
       'lead_in_s':eventos[0]['ini'],'cauda_final_s':limites[-1]-eventos[-1]['fim'],
       'compassos_total':comp[-1],'selecao_sha256':hash_arquivo(raiz/'vozes/selecao-blocos-pt.json'),
       'roteiro_sha256':hash_arquivo(raiz/'roteiro.json'),
       'gerador':'motor/tempos2.py; seleção versionada; sem geração/mixagem',
       'aprovacao_regua':None}
    gravar_json(raiz/'motor/tempos-pt.json',r)
    gravar_json(saida/'resumo.json',r)
    return r
