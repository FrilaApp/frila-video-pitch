"""Auditoria offline A1–A5 e A8. Sinais do mix são suspeitas; ouvido decide.

python motor/analisar_emendas.py ARQUIVO [--manifesto JSON] [--scribe JSON] --saida DIR
Sem manifesto: descobre candidatos no sinal e no Scribe, sem alegar conhecer tomadas.
Não acessa API. Saída 2: bloqueio objetivo; 0: sem bloqueio, podendo haver pendências.
`--falas JSON` fornece o texto de origem para A8; aprovação artística é do Fabrício.
"""
import argparse
from difflib import SequenceMatcher
import json
from pathlib import Path
import sys

import numpy as np

try:
    from .audio_util import SR, db, gravar_json, hash_arquivo, ler, salvar
except ImportError:
    from audio_util import SR, db, gravar_json, hash_arquivo, ler, salvar
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from vozes.manifesto import frases, normal

PASSO = 480  # 10 ms, resolução declarada; não é precisão fonética.


def validar_palavras(palavras, duracao):
    for w in palavras:
        if not (np.isfinite(w['start']) and np.isfinite(w['end']) and
                0 <= w['start'] <= w['end'] <= duracao + .001):
            raise ValueError('Tempos Scribe inválidos ou fora do arquivo')
    return sorted(palavras, key=lambda w: (w['start'], w['end']))


def ler_scribe(caminho, arquivo):
    """Resposta absoluta vinculada por hash ou relatório de trechos do pipeline."""
    caminho, arquivo = Path(caminho), Path(arquivo)
    d = json.loads(caminho.read_text())
    if d.get('sha256') != hash_arquivo(arquivo):
        raise ValueError('Scribe: hash do arquivo diverge ou ausente')
    if 'words' in d or 'palavras' in d:
        if d.get('resposta_scribe') and hash_arquivo(caminho.parent / d['resposta_scribe']) != d['scribe_sha256']:
            raise ValueError('Scribe: hash da resposta bruta diverge')
        return [w for w in d.get('words', d.get('palavras', [])) if w.get('type', 'word') == 'word']
    palavras = []
    for f in d['frases']:
        trecho = Path(f['trecho'])
        if not trecho.is_absolute():
            trecho = caminho.parent / trecho
        if hash_arquivo(trecho) != f['sha256_trecho']:
            raise ValueError('Scribe: hash de trecho diverge')
        offset = f['ini_amostra'] / SR
        for w in f['palavras']:
            if w.get('type', 'word') == 'word':
                palavras.append({**w, 'start': w['start'] + offset,
                                 'end': w['end'] + offset, 'trecho_scribe': str(trecho),
                                 'segmento_scribe': f.get('id')})
    # Trechos com contexto podem repetir a mesma palavra, com pequena variação de timestamp.
    unicas = []
    for w in sorted(palavras, key=lambda w: w['start']):
        if not any(u['text'].casefold() == w['text'].casefold() and
                   abs(u['start'] - w['start']) < .08 for u in unicas[-8:]):
            unicas.append(w)
    return unicas


def ler_falas(caminho):
    """Texto de origem: roteiro, manifesto do pipeline ou metadata da tomada."""
    d = json.loads(Path(caminho).read_text())
    if d.get('cenas') and isinstance(d['cenas'][0], dict):
        return [{'id': c['id'], 'fala': c['pt']['fala']} for c in d['cenas']]
    if 'fala' in d:
        return [{'id': d.get('bloco', d.get('id', 'tomada')), 'fala': d['fala']}]
    return [{'id': f['id'], 'fala': f['fala']} for f in d.get('falas', d.get('frases', []))]


def verificar_a8(falas, palavras):
    """Fonte define a frase; pontuação ASR não pode esconder dois-pontos/pausas.

    Limite inclusivo de 0,500 s para o '~0,5' do playbook, conforme §J do plano.
    Alinhamento textual incompleto é pendência, nunca prova de ausência de falha.
    """
    esperado, etiquetas, falhas, textos = [], [], [], {}
    for f in falas:
        for i, texto in enumerate(frases(f['fala']), 1):
            fid = f'{f["id"]}:{i}'
            tokens = normal(texto)
            esperado.extend(tokens); etiquetas.extend([fid] * len(tokens)); textos[fid] = texto
            if ':' in texto:
                falhas.append({'regra': 'A8_dois_pontos', 'frase': fid, 'fala': texto,
                               'motivo': 'dois-pontos na fala', 'tempo': None})
    ouvido, donos = [], []
    for i, w in enumerate(palavras):
        tokens = normal(w['text'])
        ouvido.extend(tokens); donos.extend([i] * len(tokens))
    matcher = SequenceMatcher(None, esperado, ouvido, autojunk=False)
    rotulos = [None] * len(ouvido)
    for a, b, n in matcher.get_matching_blocks():
        rotulos[b:b + n] = etiquetas[a:a + n]
    por_palavra = [[] for _ in palavras]
    for dono, rotulo in zip(donos, rotulos):
        por_palavra[dono].append(rotulo)
    ids = [r[0] if r and None not in r and len(set(r)) == 1 else None for r in por_palavra]
    pausas = []
    for i, (a, b) in enumerate(zip(palavras, palavras[1:])):
        dur = b['start'] - a['end']
        tipo = ('indeterminada' if ids[i] is None or ids[i + 1] is None else
                'interna' if ids[i] == ids[i + 1] else 'entre_frases')
        pausa = {'ini': a['end'], 'fim': b['start'], 'duracao': dur,
                 'tempo': (a['end'] + b['start']) / 2, 'tipo': tipo,
                 'frase_antes': ids[i], 'frase_depois': ids[i + 1],
                 'palavra_antes': a, 'palavra_depois': b}
        pausas.append(pausa)
        if tipo == 'interna' and dur >= .5 - 1e-9:
            falhas.append({**pausa, 'regra': 'A8_pausa_interna', 'frase': ids[i],
                           'fala': textos[ids[i]], 'motivo': 'pausa interna ≥0,500 s'})
    completo = bool(esperado) and esperado == ouvido and all(ids)
    pendencias = []
    if not completo:
        pendencias.append('fala/Scribe ausente ou alinhamento textual incompleto')
    if any(w['end'] <= w['start'] for w in palavras):
        pendencias.append('palavra sem duração positiva no Scribe')
    if any(p['duracao'] < 0 for p in pausas):
        pendencias.append('timestamps sobrepostos')
    bloqueado = bool(falhas)
    return {'regra': 'A8', 'limite_s': .5, 'limite_inclusivo': True,
            'estado': 'falha' if bloqueado else 'inconclusivo' if pendencias else 'sem_falha',
            'bloqueado': bloqueado, 'alinhamento_completo': bool(completo),
            'falhas': falhas, 'pausas': pausas, 'pendencias': pendencias}


def caracteristicas(x):
    """RMS por banda, envelope central e fundo lateral em janelas de 10 ms."""
    x = np.asarray(x)
    if x.ndim == 1:
        x = np.column_stack([x, x])
    if not x.size or not np.isfinite(x).all() or x.shape[1] != 2:
        raise ValueError('Áudio vazio, não finito ou sem dois canais')
    mid, side = x.mean(axis=1), (x[:, 0] - x[:, 1]) / 2
    n = len(mid) // PASSO
    if n < 4:
        raise ValueError('Áudio curto demais para análise')
    m, s = mid[:n * PASSO].reshape(n, PASSO), side[:n * PASSO].reshape(n, PASSO)
    freq = np.fft.rfftfreq(PASSO, 1 / SR)
    fm = abs(np.fft.rfft(m * np.hanning(PASSO), axis=1)) ** 2
    fs = abs(np.fft.rfft(s * np.hanning(PASSO), axis=1)) ** 2
    banda = (freq >= 300) & (freq <= 4000)
    pm, ps = fm[:, banda].sum(axis=1), fs[:, banda].sum(axis=1)
    # Subtração de potência lateral: pista conservadora, não separação de voz.
    voz = 10 * np.log10(np.maximum(pm - ps, 0) / (PASSO ** 2 / 2) + 1e-14)
    bandas = np.array([fm[:, (freq >= a) & (freq < b)].sum(axis=1)
                       for a, b in [(100, 400), (400, 1000), (1000, 2500), (2500, 7000)]]).T
    espectro = bandas / (bandas.sum(axis=1, keepdims=True) + 1e-20)
    return mid, side, voz, espectro


def intervalos(mask):
    limites = np.flatnonzero(np.diff(np.r_[False, mask, False]))
    return [(int(a), int(b)) for a, b in limites.reshape(-1, 2)]


def detectar(x, palavras):
    """Gera candidatos sem régua/manifesto. Não limita a contagem aos casos esperados."""
    mid, side, v, espectro = caracteristicas(x)
    candidatos = []
    def add(t, sinal, confianca):
        if .12 < t < len(mid) / SR - .12:
            candidatos.append({'tempo': float(t), 'sinais': [sinal], 'confianca': confianca,
                               'origem': 'detectada'})
    # Pausas do ASR: inclui continuações de frase; pontuação não é ground truth.
    for a, b in zip(palavras, palavras[1:]):
        pausa = b['start'] - a['end']
        if .2 <= pausa <= 1.2:
            curta = .21 - 1e-6 <= pausa <= .29 + 1e-6
            mesma = a.get('segmento_scribe') is not None and a.get('segmento_scribe') == b.get('segmento_scribe')
            continuacao = mesma and not a['text'].rstrip().endswith(('.', '?', '!'))
            add((a['end'] + b['start']) / 2,
                'pausa_curta_uniforme_scribe' if curta else 'pausa_scribe',
                .74 if continuacao and pausa >= .45 else (.60 if curta else .32))
    # Valas de energia locais: contexto dos dois lados precisa estar mais alto.
    # A mediana de 30 ms remove oscilações isoladas sem esconder cortes de 40–200 ms.
    suave = np.median(np.lib.stride_tricks.sliding_window_view(np.pad(v, (1, 1), mode='edge'), 3), axis=1)
    for a, b in intervalos(suave < -55):
        dur = (b - a) * .01
        if a < 12 or b + 12 >= len(v) or not .04 <= dur <= 1.2:
            continue
        viz = min(float(np.max(suave[max(0, a - 20):a])), float(np.max(suave[b:b + 20])))
        profundidade = viz - float(np.median(suave[a:b]))
        if profundidade < 25 or viz < -34:
            continue
        t = (a + b) * .005
        interna = any(w['start'] < a * .01 and w['end'] > b * .01 for w in palavras)
        # Oclusivas /p,t,k/ também criam valas dentro de palavras. Só perda
        # extrema ganha prioridade alta; as demais permanecem na fila secundária.
        add(t, 'queda_dentro_palavra' if interna else 'pausa_acustica',
            .90 if interna and profundidade > 65 else (.50 if interna else .28))
        candidatos[-1].update(pausa_acustica={'ini': a * .01, 'fim': b * .01, 'duracao': dur})
    # Saltos entre janelas de 40 ms: o espectro deve mudar junto com o nível.
    for k in range(12, len(v) - 12):
        antes, depois = np.mean(espectro[k - 4:k], axis=0), np.mean(espectro[k:k + 4], axis=0)
        salto = float(np.sum(abs(antes - depois)))
        nivel = abs(db(mid[k * PASSO:(k + 4) * PASSO]) - db(mid[(k - 4) * PASSO:k * PASSO]))
        piso = max(db(mid[k * PASSO:(k + 4) * PASSO]), db(mid[(k - 4) * PASSO:k * PASSO]))
        if salto > .85 and nivel > 12 and piso < -40:
            interna = any(w['start'] + .03 < k * .01 < w['end'] - .03 for w in palavras)
            add(k * .01, 'salto_espectro_nivel', .40 if interna else .24)
    # Clique: derivada extrema em comparação com os 20 ms vizinhos, não só amplitude.
    dif = np.abs(np.diff(mid))
    for a, b in intervalos(dif > .06):
        k = a + int(np.argmax(dif[a:b])); lo, hi = max(0, k - 480), min(len(dif), k + 480)
        if dif[k] > 15 * (np.percentile(dif[lo:hi], 90) + 1e-6):
            add((k + 1) / SR, 'clique_amostral', .85)
    # Agrupa apenas candidatos detectados próximos; emendas declaradas nunca são fundidas.
    grupos = []
    for c in sorted(candidatos, key=lambda c: -c['confianca']):
        grupo = next((g for g in grupos if abs(g['tempo'] - c['tempo']) < .12), None)
        if grupo:
            grupo['sinais'] = sorted(set(grupo['sinais'] + c['sinais']))
            if 'pausa_acustica' in c:
                grupo['pausa_acustica'] = c['pausa_acustica']
        else:
            grupos.append(c)
    return sorted(grupos, key=lambda c: c['tempo'])


def analisar(x, palavras, manifesto=None):
    mid, side, energia, espectro = caracteristicas(x)
    duracao = len(mid) / SR
    palavras = validar_palavras(palavras, duracao)
    manifesto = manifesto or {}
    declaradas = manifesto.get('emendas')
    candidatos = ([{'sinais': ['manifesto'], 'confianca': 1., 'origem': 'manifesto', **e}
                   for e in declaradas] if declaradas is not None else detectar(x, palavras))
    saida = []
    for c in candidatos:
        t = float(c['tempo'])
        if not np.isfinite(t) or not 0 < t < duracao:
            raise ValueError('Emenda fora do arquivo')
        k = round(t * SR)
        vizinhas = [w for w in palavras if w['end'] >= t - 2 and w['start'] <= t + 2]
        anteriores = [w for w in palavras if w['end'] <= t]
        seguintes = [w for w in palavras if w['start'] >= t]
        a = max(anteriores, key=lambda w: w['end']) if anteriores else None
        b = min(seguintes, key=lambda w: w['start']) if seguintes else None
        atravessadas = [w for w in palavras if w['start'] < t < w['end']]
        pausa = b['start'] - a['end'] if a and b and not atravessadas else None
        motivos, pendencias = [], []
        if not palavras:
            pendencias.append('Scribe ausente: palavra/frase não verificadas')
        protegidas = [w for w in palavras if w['start'] < t + .12 and w['end'] > t - .12]
        if protegidas:
            motivos.append('palavra/energia de fala na proteção ±120 ms (pista Scribe)')
        if any(w['end'] == w['start'] for w in vizinhas):
            pendencias.append('palavra Scribe com duração zero; intervalo fonético indeterminado')
        if pausa is None:
            pendencias.append('pausa entre palavras não mensurável')
        elif pausa < .2 - 1e-6 or pausa > 1.2 + 1e-6:
            motivos.append('pausa fora de 0,2–1,2 s')
        # Energia só é atribuída à fala quando coincide com palavras. Mix isolado é ambíguo.
        janela = energia[max(0, int((t - .12) * 100)):min(len(energia), int((t + .12) * 100) + 1)]
        e = float(np.max(janela)) if janela.size else -140.
        if e > -55 and not protegidas:
            pendencias.append('energia central em ±120 ms; mix não separa fala de música/efeitos')
        # Fundo lateral, ou mix mono se não há componente lateral. Estima, não prova ruído.
        fundo = side if db(side) > -100 else mid
        esq = fundo[max(0, k - round(.12 * SR)):max(0, k - round(.02 * SR))]
        dire = fundo[min(len(fundo), k + round(.02 * SR)):min(len(fundo), k + round(.12 * SR))]
        delta = abs(db(esq) - db(dire))
        if delta > 3:
            motivos.append('diferença de fundo >3 dB (estimativa no mix)')
        salto = float(abs(mid[k] - mid[k - 1]))
        d = np.abs(np.diff(mid[max(0, k - 480):min(len(mid), k + 480)]))
        clique = salto > .02 and salto > 15 * (float(np.percentile(d, 90)) + 1e-6)
        if clique or 'clique_amostral' in c['sinais']:
            motivos.append('clique/descontinuidade amostral')
        if 'salto_espectro_nivel' in c['sinais']:
            motivos.append('descontinuidade conjunta de espectro e nível')
        if 'queda_dentro_palavra' in c['sinais']:
            motivos.append('queda de energia dentro de palavra Scribe')
        frases = manifesto.get('frases', [])
        grupos = {}
        for f in frases:
            grupos.setdefault(f['id'], []).append(f)
        divididas = [fid for fid, fs in grupos.items()
                     if (len({f['tomada'] for f in fs}) > 1 or c['origem'] == 'manifesto')
                     and min(f['ini'] for f in fs) < t < max(f['fim'] for f in fs)]
        if c.get('tomada_antes') and c.get('tomada_depois') and c['tomada_antes'] != c['tomada_depois']:
            divididas += [f['id'] for f in frases if f['ini'] < t < f['fim']]
        divididas = sorted(set(divididas))
        if divididas:
            motivos.append('frase atravessa emenda declarada ou tomadas diferentes: ' + ', '.join(divididas))
        if not frases:
            pendencias.append('proveniência das tomadas ausente: A1 não comprovável')
        if c.get('entre_blocos'):
            if pausa is None or pausa < .5 - 1e-6:
                motivos.append('pausa entre blocos menor que 500 ms')
            if not any(abs(t - corte) <= 1 / 60 for corte in manifesto.get('cortes_cena', [])):
                motivos.append('emenda entre blocos sem corte de cena correspondente')
        frame = min(max(1, int(t * 100)), len(espectro) - 1)
        espectro_delta = float(np.sum(abs(np.mean(espectro[max(0, frame - 4):frame], axis=0) -
                                          np.mean(espectro[frame:frame + 4], axis=0))))
        medidas = {'pausa_scribe_s': pausa, 'fundo_delta_db': delta,
                   'fundo_antes_dbfs': db(esq), 'fundo_depois_dbfs': db(dire),
                   'espectro_delta_l1': espectro_delta,
                   'fundo_metodo': 'lateral' if fundo is side else 'mono/mid',
                   'energia_central_max_dbfs': e, 'salto_amostral': salto}
        saida.append({**c, 'tempo': t, 'palavras': vizinhas, 'medidas': medidas,
                      'frase_dividida_comprovada': bool(divididas),
                      'classe': 'violação comprovada de A1' if divididas else 'suspeita acústica/temporal',
                      'aprovado': not motivos and not pendencias, 'motivos': motivos,
                      'pendencias': pendencias, 'aprovacao_ouvido': None})
    return sorted(saida, key=lambda c: (-c['confianca'], c['tempo']))


def executar(arquivo, saida, scribe=None, manifesto=None, falas=None):
    arquivo, saida = Path(arquivo).resolve(), Path(saida).resolve()
    x = ler(arquivo, 2)
    palavras = ler_scribe(scribe, arquivo) if scribe else []
    m = json.loads(Path(manifesto).read_text()) if manifesto else None
    if m and m.get('sha256') != hash_arquivo(arquivo):
        raise ValueError('Manifesto sem hash correspondente ao arquivo auditado')
    emendas = analisar(x, palavras, m)
    textos = ler_falas(falas) if falas else [f for f in (m or {}).get('frases', []) if 'fala' in f]
    a8 = verificar_a8(textos, palavras)
    def extrair(t, p):
        a, b = max(0, round((t - 2) * SR)), min(len(x), round((t + 2) * SR))
        salvar(p, x[a:b])
        return {'trecho': str(p), 'trecho_ini': a / SR, 'trecho_fim': b / SR,
                'trecho_sha256': hash_arquivo(p)}
    for i, c in enumerate(emendas, 1):
        p = saida / 'trechos' / f'{i:03d}-{c["tempo"]:.3f}s.wav'
        c.update(extrair(c['tempo'], p))
        c['bloqueia'] = c['frase_dividida_comprovada'] or (c['origem'] == 'manifesto' and bool(c['motivos']))
    for i, falha in enumerate(a8['falhas'], 1):
        if falha['tempo'] is not None:
            p = saida / 'a8' / f'{i:03d}-{falha["tempo"]:.3f}s.wav'
            falha.update(extrair(falha['tempo'], p))
    bloqueado = a8['bloqueado'] or any(c['bloqueia'] for c in emendas)
    completo = bool(m and m.get('emendas') is not None)
    r = {'arquivo': str(arquivo), 'sha256': hash_arquivo(arquivo), 'duracao': len(x) / SR,
         'metodo': 'heurísticas offline; confiança ordinal, não probabilidade; resolução de envelope 10 ms',
         'scribe': str(Path(scribe).resolve()) if scribe else None,
         'scribe_sha256': hash_arquivo(scribe) if scribe else None,
         'manifesto': str(Path(manifesto).resolve()) if manifesto else None,
         'manifesto_sha256': hash_arquivo(manifesto) if manifesto else None,
         'falas': str(Path(falas).resolve()) if falas else None,
         'falas_sha256': hash_arquivo(falas) if falas else None,
         'parametros': {'protecao_s': .12, 'pausa_min_s': .2, 'pausa_max_s': 1.2,
                        'fundo_delta_max_db': 3, 'energia_pendente_dbfs': -55,
                        'envelope_passo_s': .01, 'vala_limiar_dbfs': -55,
                        'vala_profundidade_min_db': 25, 'vala_duracao_min_s': .04,
                        'agrupamento_candidatos_s': .12},
         'completude_comprovada': completo,
         'bloqueado': bloqueado, 'a8': a8,
         'apto_para_escuta': not bloqueado and completo and a8['estado'] == 'sem_falha'
                            and all(c['aprovado'] for c in emendas),
         'aprovado': False,  # Aprovação artística é exclusiva do Fabrício (PLAYBOOK §5b).
         'aprovacao_ouvido': None, 'emendas': emendas}
    gravar_json(saida / 'emendas.json', r)
    linhas = [f'{len(emendas)} candidatos; bloqueio objetivo: {bloqueado}; A8: {a8["estado"]}; escuta pendente.',
              'Confiança é ordinal. Suspeita cega informa; regra objetiva bloqueia. Fabrício aprova.']
    for falha in a8['falhas']:
        linhas.append(f'{falha["regra"]} | {falha["tempo"]} s | {falha["motivo"]} | '
                      f'{falha["frase"]} | {falha.get("trecho", "texto sem instante")}')
        if falha.get('palavra_antes'):
            linhas.append('  ' + ' | '.join(f'{w["text"]} [{w["start"]:.3f}–{w["end"]:.3f}]'
                                           for w in (falha['palavra_antes'], falha['palavra_depois'])))
    for c in emendas:
        linhas.append(f'{c["tempo"]:.6f} s | {c["confianca"]:.2f} | {c["classe"]} | ' +
                      '; '.join(c['motivos'] + c['pendencias']) + f' | {c["trecho"]}')
        linhas.append('  ' + ' | '.join(f'{w["text"]} [{w["start"]:.3f}–{w["end"]:.3f}]' for w in c['palavras']))
    (saida / 'resumo.txt').write_text('\n'.join(linhas) + '\n')
    print('\n'.join(linhas))
    return r


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('arquivo', type=Path)
    p.add_argument('--saida', type=Path, required=True)
    p.add_argument('--scribe', type=Path)
    p.add_argument('--manifesto', type=Path)
    p.add_argument('--falas', type=Path, help='Texto de origem para A8: roteiro, manifesto ou metadata da tomada')
    a = p.parse_args()
    try:
        r = executar(a.arquivo, a.saida, a.scribe, a.manifesto, a.falas)
    except (ValueError, KeyError, OSError) as e:
        p.exit(2, f'Bloqueado: {e}\n')
    return 2 if r['bloqueado'] else 0


if __name__ == '__main__':
    raise SystemExit(main())
