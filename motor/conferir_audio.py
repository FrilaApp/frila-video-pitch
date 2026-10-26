"""QA offline por estágio. Não chama Scribe e nunca aprova a escuta do Cauê.

Uso: python motor/conferir_audio.py SESSAO [--final arquivo.mp4] [--trechos]
O código de saída indica falhas técnicas; voz sem limites confirmados é inconclusiva.
"""
import argparse
import json
from pathlib import Path
import subprocess

import numpy as np
try:
    from .audio_util import SR, db, ler, salvar, hash_arquivo, hash_json, gravar_json, medir_loudness
except ImportError:
    from audio_util import SR, db, ler, salvar, hash_arquivo, hash_json, gravar_json, medir_loudness


def diagnostico(x):
    """Métricas são pistas; energia na borda não prova palavra truncada."""
    x = np.asarray(x)
    if not x.size or not np.isfinite(x).all():
        return {'valido': False, 'motivo': 'vazio/não finito'}
    mono = x.mean(axis=1) if x.ndim == 2 else x
    perto_teto = (np.abs(x) >= .999)
    if perto_teto.ndim == 2:
        perto_teto = perto_teto.any(axis=1)
    clip = bool(np.any(perto_teto[:-2] & perto_teto[1:-1] & perto_teto[2:]))
    blocos = [mono[i:i + 480] for i in range(0, len(mono), 480)]
    return {'valido': bool(np.max(np.abs(x)) > 1e-7), 'amostras': len(x), 'rms_dbfs': db(x),
            'rms_10ms_inicio_dbfs': db(mono[:480]), 'rms_10ms_fim_dbfs': db(mono[-480:]),
            'media_absoluta_5ms_inicio_dbfs': float(20 * np.log10(np.mean(np.abs(mono[:240])) + 1e-12)),
            'media_absoluta_5ms_fim_dbfs': float(20 * np.log10(np.mean(np.abs(mono[-240:])) + 1e-12)),
            'blocos_10ms_ativos': sum(db(b) > -60 for b in blocos), 'clipping_3_amostras': clip,
            'alerta_borda': db(mono[:480]) > -55 or db(mono[-480:]) > -55}


def diferenca_db(voz, fundo):
    return None if db(fundo) < -100 else db(voz) - db(fundo)


def medir_frase(v, m, e, a, b, cfg):
    p = cfg['protecao']; w = round(cfg['qa']['janela_ms'] * SR / 1000)
    passo = round(cfg['qa']['passo_ms'] * SR / 1000)
    ref = v[a:b]; ativo = np.abs(ref[:, 0]) > 10 ** (-60 / 20)
    referencia = db(ref[ativo]) if ativo.any() else db(ref)
    fundo = m + e
    janelas, fracas = [], []
    ultimo = max(a, b - w)
    inicios = sorted(set([*range(a, ultimo + 1, passo), ultimo]))
    for i in inicios:
        j = min(b, i + w)
        coexistem = np.max(np.abs(e[i:j]), axis=1) > 1e-5
        vm, vf = diferenca_db(v[i:j], m[i:j]), diferenca_db(v[i:j], fundo[i:j])
        ve = diferenca_db(v[i:j][coexistem], e[i:j][coexistem]) if coexistem.any() else None
        registro = {'ini': i / SR, 'fim': j / SR, 'voz_dbfs': db(v[i:j]), 'voz_musica_db': vm,
                    'voz_efeitos_db': ve, 'voz_fundo_db': vf}
        janelas.append(registro)
        if registro['voz_dbfs'] < referencia - 20:
            fracas.append(registro)
    coexistencia = [r['voz_efeitos_db'] for r in janelas if r['voz_efeitos_db'] is not None]
    minimo_local = [r['voz_fundo_db'] for r in janelas
                    if r['voz_dbfs'] >= referencia - 20 and r['voz_fundo_db'] is not None]
    vm = diferenca_db(v[a:b], m[a:b]); vf = diferenca_db(v[a:b], fundo[a:b])
    bordas = []
    for nome, i, j in [('início', a, min(b, a + round(p['inicio_frase_ms'] * SR / 1000))),
                       ('fim', max(a, b - round(p['fim_frase_ms'] * SR / 1000)), b)]:
        pico = float(20 * np.log10(np.max(np.abs(e[i:j])) + 1e-12))
        bordas.append({'borda': nome, 'fundo_dbfs': db(fundo[i:j]), 'efeito_pico_dbfs': pico,
                       'ok': db(fundo[i:j]) <= referencia - p['fundo_nas_bordas_abaixo_ref_voz_db'] + .01
                       and pico <= referencia - p['pico_efeito_nas_bordas_abaixo_ref_voz_db'] + .01})
    ve = min(coexistencia) if coexistencia else None
    local = min(minimo_local) if minimo_local else None
    ok = (vm is None or vm >= p['margem_voz_musica_min_db']) and (ve is None or ve >= p['margem_voz_efeitos_min_db'])
    ok &= (vf is None or vf >= p['margem_voz_fundo_min_db']) and (local is None or local >= p['margem_voz_fundo_min_db'])
    ok &= all(r['ok'] for r in bordas)
    ok &= abs(referencia - cfg['voz']['rms_ativo_alvo_dbfs']) <= cfg['voz']['tolerancia_db']
    return {'ok': bool(ok), 'referencia_voz_dbfs': referencia, 'voz_musica_db': vm,
            'voz_efeitos_coexistencia_min_db': ve, 'voz_fundo_db': vf,
            'voz_fundo_local_min_db': local, 'bordas': bordas, 'janelas': janelas,
            'trechos_fracos_para_escuta': fracas,
            'mono_voz_fundo_db': diferenca_db(v[a:b].mean(axis=1), fundo[a:b].mean(axis=1))}


def atraso_amostras(ref, teste):
    """Correlação de trecho limitado; sinal positivo indica atraso do derivado."""
    ref = ref[:min(len(ref), 8 * SR)].mean(axis=1).astype(float)
    teste = teste[:len(ref)].mean(axis=1).astype(float)
    tamanho = 1 << (len(ref) + len(teste) - 1).bit_length()
    c = np.fft.irfft(np.conj(np.fft.rfft(ref, tamanho)) * np.fft.rfft(teste, tamanho), tamanho)
    limite = round(.05 * SR)
    desloc = np.arange(-limite, limite + 1)
    return int(desloc[np.argmax(c[desloc % tamanho])])


def conferir_final(arquivo, cfg, referencia=None):
    m = medir_loudness(arquivo)
    i, tp = float(m['input_i']), float(m['input_tp'])
    x = ler(arquivo, 2)
    atraso = atraso_amostras(referencia, x) if referencia is not None else None
    probe = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'a:0', '-show_entries',
                            'stream=codec_name,sample_rate,channels,start_time,duration', '-of', 'json', str(arquivo)],
                           capture_output=True, text=True, check=True)
    stream = json.loads(probe.stdout)['streams'][0]
    formato_ok = stream['codec_name'] == 'aac' and int(stream['sample_rate']) == SR and stream['channels'] == 2
    duracao_ok = referencia is None or (len(x) >= len(referencia) and len(x) - len(referencia) < 1024
                    and abs(float(stream.get('duration', -1)) - len(referencia) / SR) <= .01)
    origem_ok = abs(float(stream.get('start_time', -1))) <= .01
    return {'arquivo': str(arquivo), 'sha256': hash_arquivo(arquivo), 'integrado_lufs': i,
            'true_peak_dbtp': tp, 'lra_lu': float(m['input_lra']), 'amostras_decodificadas': len(x),
            'atraso_amostras': atraso, 'atraso_ms': atraso / SR * 1000 if atraso is not None else None,
            'stream': stream, 'duracao_ok': duracao_ok, 'origem_ok': origem_ok,
            'ok': formato_ok and duracao_ok and origem_ok and abs(i - cfg['master']['integrado_lufs']) <= cfg['qa']['lufs_tolerancia_lu']
            and tp <= cfg['master']['true_peak_aac_max_dbtp']
            and (atraso is None or abs(atraso) <= round(.01 * SR))}


def conferir_sessao(sessao, cfg=None, final=None, trechos=False):
    sessao = Path(sessao)
    cfg = cfg or json.loads((sessao / 'mixagem.json').read_text())
    man = json.loads((sessao / 'manifesto.json').read_text())
    falhas, avisos, frases = [], [], []
    derivados = {}
    recibo = sessao / 'master.json'
    if recibo.exists():
        receita = json.loads(recibo.read_text())
        if receita['premix_sha256'] == man['premix_sha256'] and receita['config_sha256'] == man['config_sha256']:
            for nome in ('master', 'aac-decodificado'):
                path = sessao / f'{nome}.wav'
                if path.exists():
                    derivados[nome] = ler(path, 2)
    if final:
        derivados['aac-final'] = ler(final, 2)
    from_config = hash_json(cfg)
    if from_config != man['config_sha256']:
        falhas.append('Configuração diferente da sessão; refazer mix')
    arrays = {k: ler(p, 2) for k, p in man['stems'].items()}
    if any(len(x) != man['amostras'] for x in arrays.values()):
        raise ValueError('Stems com durações diferentes da sessão')
    for k, p in man['stems'].items():
        if hash_arquivo(p) != man['sha256_stems'][k]:
            falhas.append(f'Stem alterado: {k}')
    v, m, e = (arrays[k] for k in ('voz', 'musica-duck', 'efeitos-duck'))
    premix = ler(sessao / 'premix.wav', 2)
    if len(premix) != man['amostras']:
        raise ValueError('Premix com duração diferente da sessão')
    null = float(np.max(np.abs((v + m + e).astype(np.float32) - premix)))
    if null > 1e-6 or hash_arquivo(sessao / 'premix.wav') != man['premix_sha256']:
        falhas.append('Null test ou hash do premix falhou')
    for f in man['frases']:
        x = ler(f['preparado'], 1)
        p = Path(f['arquivo'])
        fonte = np.load(p).reshape(-1, 1) if p.suffix == '.npy' else ler(p, 1)
        if hash_arquivo(p) != f['sha256_preparado_fonte']:
            falhas.append(f"Fonte preparada alterada: {f['id']}")
        fidelidade = float(np.max(np.abs(x - (fonte * 10 ** (f['ganho_db'] / 20)).astype(np.float32))))
        a, b = f['arquivo_ini_amostra'], f['arquivo_fim_amostra']
        montagem = float(np.max(np.abs(v[a:b] - x)))
        raw_qa, preparacao_erro = None, None
        if f.get('bruto'):
            raw = ler(f['bruto'], 1)
            raw_qa = diagnostico(raw)
            if hash_arquivo(f['bruto']) != f['sha256']:
                falhas.append(f"Bruto alterado: {f['id']}")
            # Referência reamostrada antes de qualquer corte/fade; remove só padding registrado.
            ci, cf = f.get('corte_ini', 0), f.get('corte_fim', 0)
            pi, pf = f.get('padding_ini', 0), f.get('padding_fim', 0)
            esperado = np.pad(raw[ci:len(raw) - cf], ((pi, pf), (0, 0)))
            preparacao_erro = float(np.max(np.abs(esperado - fonte))) if esperado.shape == fonte.shape else 1.
        ai, bi = f['fala_ini_absoluta'], f['fala_fim_absoluta']
        medidas = medir_frase(v, m, e, ai, bi, cfg)
        estagios = {'geracao': raw_qa or {'estado': 'bruto não informado'},
                    'preparacao': {'erro_maximo_amostra': preparacao_erro, **diagnostico(fonte)},
                    'bus_voz': {'erro_maximo_amostra': montagem, 'ganho_erro_maximo': fidelidade},
                    'premix': {'null_maximo': null}}
        for nome, derivado in derivados.items():
            estagios[nome] = {**diagnostico(derivado[a:b]), 'scribe': 'pendente',
                             'alinhamento_global_em': 'master.json', 'escuta': 'pendente'}
        ok = medidas['ok'] and fidelidade <= 1e-6 and montagem <= 1e-6 and (preparacao_erro is None or preparacao_erro <= 1e-6)
        if not ok:
            falhas.append(f"Integridade/margem falhou: {f['id']}")
        if not f['limites_confirmados']:
            avisos.append(f"{f['id']}: limites acústicos não confirmados; arquivo inteiro protegido")
        if raw_qa and (raw_qa['alerta_borda'] or raw_qa['clipping_3_amostras']):
            avisos.append(f"{f['id']}: revisar borda/clipping do bruto")
        frases.append({'id': f['id'], 'fala': f.get('fala'), 'estagios': estagios, 'medidas': medidas,
                       'scribe': 'pendente', 'escuta': 'pendente'})
        if trechos:
            i, j = max(0, ai - round(.25 * SR)), min(len(v), bi + round(.25 * SR))
            variantes = {'voz': v, 'voz-musica': v + m, 'voz-efeitos': v + e, 'premix': premix}
            variantes.update(derivados)
            for nome, arr in variantes.items():
                salvar(sessao / 'ab' / f"{f['id']}-{nome}.wav", arr[i:j])
            gravar_json(sessao / 'ab' / f"{f['id']}.json", {'offset_amostra': i, 'offset_s': i / SR,
                        'contexto_s': .25, 'ganho_adicional_db': 0})
    colisoes = []
    for ev in man['eventos']:
        for f in man['frases']:
            a, b = f['fala_ini_absoluta'] / SR, f['fala_fim_absoluta'] / SR
            sobreposicao = max(0, min(b, ev['t'] + ev['duracao']) - max(a, ev['t']))
            if sobreposicao:
                i, j = round(max(a, ev['t']) * SR), round(min(b, ev['t'] + ev['duracao']) * SR)
                colisoes.append({**ev, 'frase': f['id'], 'sobreposicao_temporal_s': sobreposicao,
                                 'pico_bus_efeitos_dbfs': float(20 * np.log10(np.max(np.abs(e[i:j])) + 1e-12)),
                                 'voz_efeitos_db': diferenca_db(v[i:j], e[i:j]),
                                 'palavras_afetadas': 'pendente de voz/Scribe/escuta'})
    resultado = {'tecnico_ok': not falhas, 'estado': 'divergência' if falhas else 'inconclusivo' if avisos else 'apto para escuta',
                 'null_maximo': null, 'falhas': falhas, 'avisos': avisos, 'frases': frases,
                 'colisoes': colisoes, 'aprovacao_cauê': None}
    if final:
        resultado['final'] = conferir_final(final, cfg, premix)
        if not resultado['final']['ok']:
            resultado['tecnico_ok'] = False; resultado['estado'] = 'divergência'
            resultado['falhas'].append('AAC final fora de LUFS/TP/alinhamento')
    gravar_json(sessao / 'qa.json', resultado)
    return resultado


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('sessao', type=Path); ap.add_argument('--final', type=Path)
    ap.add_argument('--trechos', action='store_true')
    args = ap.parse_args()
    r = conferir_sessao(args.sessao, final=args.final, trechos=args.trechos)
    print(json.dumps({k: r[k] for k in ('estado', 'tecnico_ok', 'null_maximo', 'falhas', 'avisos')}, ensure_ascii=False, indent=2))
    raise SystemExit(0 if r['tecnico_ok'] else 1)
