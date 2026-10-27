"""IDs compartilhados de fala/legenda e tomadas imutáveis, sem acesso à API."""
import hashlib
import json
from pathlib import Path
import re
import shutil
import unicodedata


def frases(texto):
    return [f for f in re.split(r'(?<=[.?!])\s+', texto.strip()) if f]


def frases_do_roteiro(roteiro, filtro=(), idioma='pt'):
    itens = []
    for c in roteiro['cenas']:
        falas, legendas = frases(c[idioma]['fala']), frases(c[idioma]['legenda'])
        if len(falas) != len(legendas) or not falas:
            raise ValueError(f"Fala/legenda com contagem divergente ou vazia: {c['id']}")
        for k, (fala, legenda) in enumerate(zip(falas, legendas), 1):
            fid = f"{c['id']}-{k}"
            if not filtro or any(v in (fid, c['id'], c['id'].split('-')[0]) for v in filtro):
                itens.append({'id': fid, 'cena': c['id'], 'k': k, 'fala': fala, 'legenda': legenda})
    if filtro and not itens:
        raise ValueError('Filtro sem frases correspondentes')
    return itens


def guardar_tomada(arquivo, raiz, metadados):
    arquivo = Path(arquivo)
    digest = hashlib.sha256(arquivo.read_bytes()).hexdigest()
    destino = Path(raiz) / arquivo.stem / f'{digest}.wav'
    destino.parent.mkdir(parents=True, exist_ok=True)
    if not destino.exists():
        shutil.copyfile(arquivo, destino)
    meta = destino.with_suffix('.json')
    if not meta.exists():
        meta.write_text(json.dumps({**metadados, 'sha256': digest}, ensure_ascii=False, indent=2) + '\n')
    return destino

UNID = "zero um dois três quatro cinco seis sete oito nove dez onze doze treze quatorze quinze dezesseis dezessete dezoito dezenove".split()
DEZ = "_ _ vinte trinta quarenta cinquenta sessenta setenta oitenta noventa".split()
CENT = "_ cento duzentos trezentos quatrocentos quinhentos seiscentos setecentos oitocentos novecentos".split()


def extenso(n):
    """0 a 999.999, só para comparar o que o Scribe escreve em algarismos com o texto da fala."""
    if n >= 1000:
        m, r = divmod(n, 1000)
        return ("mil" if m == 1 else extenso(m) + " mil") + (" e " + extenso(r) if r and (r < 100 or r % 100 == 0) else " " + extenso(r) if r else "")
    if n == 100:
        return "cem"
    if n >= 100:
        c, r = divmod(n, 100)
        return CENT[c] + (" e " + extenso(r) if r else "")
    if n >= 20:
        d, u = divmod(n, 10)
        return DEZ[d] + (" e " + UNID[u] if u else "")
    return UNID[n]


def normal(t):
    """Põe fala e transcrição na mesma forma: sem acento, números por extenso, "19h" = dezenove horas, 'Freela'=Frila, 'pra'=para, formas fonéticas -> ortografia canônica."""
    t = re.sub(r"(\d+)\s*%", lambda m: m.group(1) + " por cento", t.lower())
    t = re.sub(r"(\d+)\s*h\b", r"\1 horas", t)
    t = re.sub(r"\d+", lambda m: extenso(int(m.group())), t)
    t = t.replace("km", "quilômetros").replace(" m ", " metros ")
    t = unicodedata.normalize("NFD", t)
    t = "".join(ch for ch in t if unicodedata.category(ch) != "Mn")
    t = t.replace("freela", "frila").replace("e-staff", "estaff").replace("da staff", "da estaff")
    # Mapeamento fonético reverso para conferência de áudio/Scribe (PRONUNCIA-FALA)
    t = re.sub(r"\btchequin\b|\bchequim\b|\btchekin\b", "check in", t)
    t = re.sub(r"\babrazeu\b", "abrasel", t)
    t = re.sub(r"\bfederau\b", "federal", t)
    t = re.sub(r"\bcinkuenta\b", "cinquenta", t)
    t = re.sub(r"\bdeis\b", "dez", t)
    return [("para" if w == "pra" else w) for w in re.findall(r"[a-z0-9]+", t)]
