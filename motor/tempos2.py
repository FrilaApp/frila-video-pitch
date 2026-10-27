"""Régua oficial PT: quatro tomadas aprovadas, treze cenas e palavras Scribe.

.venv/bin/python motor/tempos2.py [--bloco A]
Seleção versionada em vozes/selecao-blocos-pt.json; sem API, edição de voz ou mix.
Cortes internos na metade das pausas; só fronteiras de blocos seguem compassos.
O gerador por frase abaixo permanece como compatibilidade com roteiros legados
sem audio_blocos_aprovados. Não é o caminho de produção do roteiro atual.
"""
import json, math, pathlib, re, subprocess
import numpy as np
import sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from vozes.regua_blocos import (gerar_oficial, janela_bloco, ler_selecao,
                                validar_excecoes_a8)
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "vozes"))
from manifesto import frases_do_roteiro
try:
    from .audio_util import gravar_json, hash_arquivo
except ImportError:
    from audio_util import gravar_json, hash_arquivo

AQUI = pathlib.Path(__file__).resolve().parent
VIDEO = AQUI.parent
SR = 48000
P = 0.491835                     # período do tempo (s), regressão linear das batidas da trilha
O = 1.014                        # primeiro tempo forte da trilha (s)
BAR = 4 * P
VOZES = {"pt": VIDEO / "vozes/frases/pt", "en": VIDEO / "vozes/frases-kokoro/en"}
ENTRADA = {"c01-gancho": 2 * P}  # o gancho espera o ponto laranja assentar (2 tempos); as outras cenas falam meio tempo depois do corte
ENTRADA_PADRAO = P / 2
PAUSA = 0.10
CAUDA = 0.30
NO_COMPASSO = {"c05-o-que-e", "c09-cadastro", "c12-confianca"}
DURACAO_MIN = {"c01-gancho": 3.4, "c02-promessa": 3.4, "c03-rotatividade": 3.9, "c04-contratar": 3.4, "c05-o-que-e": 3.9, "c06-passos-a": 0,
               "c07-passos-b": 5.4, "c08-mapa": 5.9, "c09-cadastro": 2.9, "c10-concorrente": 5.4, "c11-contraste": 3.4,
               "c12-confianca": 4.9, "c13-estagio": 3.9, "c14-gratis": 2.9, "c16-logo": 6.8}


def sobe(t, passo):
    return math.ceil(round(t / passo, 6)) * passo


def ler(p):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(p), "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.float32)


def preparar(x, limites=None, confirmado=False, cortar=False, aprovado=False):
    """Conserva o bruto; corte exige limites e aprovação explícitos, sem fades."""
    x = np.asarray(x, dtype=np.float32)
    if x.ndim != 1 or not x.size or not np.isfinite(x).all():
        raise ValueError("Frase vazia, não finita ou com canais inválidos")
    if np.max(np.abs(x)) <= 1e-7:
        raise ValueError("Frase sem atividade: revisão obrigatória")
    if confirmado and limites is None:
        raise ValueError("Limites confirmados ausentes")
    ini, fim = limites if confirmado else (0, len(x))
    if not 0 <= ini < fim <= len(x):
        raise ValueError("Limites acústicos inválidos")
    a, b = 0, len(x)
    if cortar:
        if not (confirmado and aprovado):
            raise ValueError("Corte exige limites confirmados e aprovação")
        a, b = max(0, ini - round(.08 * SR)), min(len(x), fim + round(.16 * SR))
        retirado = np.r_[x[:a], x[b:]]
        if retirado.size and np.max(np.abs(retirado)) > 10 ** (-60 / 20):
            raise ValueError("Corte contém energia acima de −60 dBFS")
    pi = max(0, round(.08 * SR) - (ini - a)) if confirmado else 0
    pf = max(0, round(.16 * SR) - (b - fim)) if confirmado else 0
    y = np.pad(x[a:b], (pi, pf))
    return y, {"corte_ini": a, "corte_fim": len(x) - b, "padding_ini": pi,
               "padding_fim": pf, "amostras_bruto": len(x), "amostras_preparado": len(y),
               "fala_ini_amostra": pi + ini - a, "fala_fim_amostra": pi + fim - a,
               "limites_confirmados": confirmado, "fades": [], "ganho_db": 0}


def frases(texto):
    return re.split(r"(?<=[.?!])\s+", texto.strip())


def secoes(cenas, total):
    """Remonta a trilha por compassos: intro até c05, groove até c09, quebra até c12, groove de novo até o fim.
    Cada bloco termina no compasso de virada da própria trilha (7, 23, 31), para a virada cair no corte."""
    ini = {c["id"]: round(c["ini"] / BAR) for c in cenas}
    n_total = round(total / BAR)
    a, b, c = ini["c05-o-que-e"], ini["c09-cadastro"], ini["c12-confianca"]

    def bloco(n, primeiro, ultimo_util, virada, laço):
        if n <= 0:
            return []
        corpo = list(range(primeiro, ultimo_util + 1))
        while len(corpo) < n - 1:
            corpo += list(range(*laço))
        return corpo[: n - 1] + [virada]

    barras = (list(range(8 - a, 8)) if a <= 8 else bloco(a, 0, 6, 7, (1, 7))) \
        + bloco(b - a, 8, 22, 23, (9, 23)) \
        + bloco(c - b, 24, 30, 31, (25, 31)) \
        + [32 + (i % 16) for i in range(n_total - c)]
    return [{"v": round(i * BAR, 4), "src": O + s * BAR} for i, s in enumerate(barras)]


def main():
    documento = json.loads((VIDEO / "roteiro.json").read_text())
    if documento.get('audio_blocos_aprovados'):
        import argparse
        parser = argparse.ArgumentParser(description='Régua de tomadas contínuas aprovadas')
        parser.add_argument('--bloco', choices=list('ABCD'))
        args = parser.parse_args()
        r = gerar_oficial(VIDEO, args.bloco)
        print('Régua oficial', args.bloco or 'PT', r.get('total', r.get('duracao')))
        return
    roteiro = documento["cenas"]
    itens = {f["id"]: f for f in frases_do_roteiro(documento)}
    config = json.loads((AQUI / "mixagem.json").read_text())
    for L in ("pt",):
        limpo = AQUI / "cache/voz" / L
        limpo.mkdir(parents=True, exist_ok=True)
        cenas, falas, t = [], [], 0.0
        manifesto = []
        for c in roteiro:
            if c["id"] in NO_COMPASSO:
                t = sobe(t, BAR)
            ini = t + ENTRADA.get(c["id"], ENTRADA_PADRAO)
            lista = []
            for k, leg in enumerate(frases(c[L]["legenda"]), 1):
                fid = f"{c['id']}-{k}"
                bruto = VOZES[L] / f"{fid}.wav"
                op = config['voz'].get('frases', {}).get(fid, {})
                x, meta = preparar(ler(bruto), limites=op.get('limites_amostras'),
                                   confirmado=op.get('limites_confirmados', False),
                                   cortar=op.get('aparar', False), aprovado=op.get('corte_aprovado', False))
                selecao = bruto.with_suffix('.json')
                if selecao.exists():
                    dados = json.loads(selecao.read_text())
                    if dados.get('fala', itens[fid]['fala']) != itens[fid]['fala']:
                        raise ValueError(f"Tomada e roteiro divergentes: {fid}")
                    meta.update({chave: dados[chave] for chave in ('tomada', 'geracao', 'contexto', 'aprovada') if chave in dados})
                meta.update(itens[fid], bruto=str(bruto), sha256=hash_arquivo(bruto), sample_rate=SR)
                gravar_json(limpo / f"{fid}.json", meta)
                manifesto.append(meta)
                np.save(limpo / f"{c['id']}-{k}.npy", x)
                d = len(x) / SR
                lista.append({"cena": c["id"], "k": k, "ini": round(ini, 3), "fim": round(ini + d, 3), "legenda": leg, "id": fid, "fala": itens[fid]["fala"], "ini_amostra": round(ini * SR)})
                ini = sobe(ini + d + PAUSA, P / 2)
            dur = max(sobe(lista[-1]["fim"] + CAUDA - t, P), sobe(DURACAO_MIN.get(c["id"], 0), P))
            if c is roteiro[-1]:
                dur = sobe(t + dur, BAR) - t
            cenas.append({"id": c["id"], "ini": round(t, 4), "dur": round(dur, 4)})
            falas += lista
            t += dur
        gravar_json(limpo / "manifesto.json", manifesto)
        # a cena anterior a um corte de compasso estica até ele
        for i in range(len(cenas) - 1):
            cenas[i]["dur"] = round(cenas[i + 1]["ini"] - cenas[i]["ini"], 4)
        for i, f in enumerate(falas):
            cena = next(c for c in cenas if c["id"] == f["cena"])
            prox = falas[i + 1]["ini"] if i + 1 < len(falas) and falas[i + 1]["cena"] == f["cena"] else None
            f["leg_ini"] = round(f["ini"] - 0.05, 3)
            f["leg_fim"] = round(prox - 0.05 if prox else min(f["fim"] + 0.6, cena["ini"] + cena["dur"] - 0.12), 3)
        total = round(t, 4)
        saida = {"lang": L, "P": P, "bar": BAR, "total": total, "cenas": cenas, "falas": falas, "musica": secoes(cenas, total)}
        (AQUI / f"tempos-{L}.json").write_text(json.dumps(saida, ensure_ascii=False, indent=1))
        print(L, "total", total, " ".join(f'{c["id"][:3]}@{c["ini"]:.1f}' for c in cenas))


if __name__ == "__main__":
    main()
