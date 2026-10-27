"""Módulo de pronúncia e fonética familiar para síntese de voz (Tarefas 6+).
Aplica substituições fonéticas aprovadas estritamente na fala (texto enviado ao TTS),
mantendo roteiro.json e legendas intactos, e provê mapeamento reverso para o conferidor.
"""
import json
import re
import unicodedata
from pathlib import Path

AQUI = Path(__file__).resolve().parent
PRONUNCIA_JSON = AQUI / "pronuncia.json"


def carregar_pronuncia(caminho=None):
    p = Path(caminho) if caminho else PRONUNCIA_JSON
    if not p.exists():
        return {}
    return json.loads(p.read_text(encoding="utf-8"))


def ajustar_caixa(original, substituta):
    """Preserva a capitalização do original na palavra substituta."""
    if not original or not substituta:
        return substituta
    if original.isupper():
        return substituta.upper()
    if original[0].isupper():
        return substituta[0].upper() + substituta[1:]
    return substituta.lower()


def aplicar_pronuncia(texto, voz="ambas", apenas_aprovadas=True, dicionario=None):
    """Substitui palavras do texto pelas formas fonéticas configuradas.
    
    Retorna tupla: (texto_transformado, lista_de_substituicoes).
    Garante:
    - Palavra inteira preservada com boundary adequado (incluindo termos com hífen);
    - Preservação da caixa da primeira letra (ou maiúsculas integrais);
    - Substituição atômica sem colisão ou re-substituição em cascata.
    """
    if dicionario is None:
        dicionario = carregar_pronuncia()
        
    substituicoes_feitas = []
    if not dicionario or not texto:
        return texto, substituicoes_feitas

    # Filtrar regras pertinentes
    regras = []
    for palavra, dados in dicionario.items():
        status = dados.get("status")
        if apenas_aprovadas and status != "aprovada":
            continue
        regra_voz = dados.get("voz", "ambas")
        if regra_voz != "ambas" and voz != "ambas" and regra_voz != voz:
            continue
        forma = dados.get("forma")
        if not forma or forma == palavra:
            continue
        regras.append((palavra, forma, dados))

    if not regras:
        return texto, substituicoes_feitas

    # Ordenar por tamanho do termo decrescente para priorizar termos mais longos
    regras.sort(key=lambda r: len(r[0]), reverse=True)

    # Identificar ocorrências que não se sobreponham
    # Termos podem conter letras, números e hifens (ex: check-in)
    padroes = []
    mapa_regras = {}
    for idx, (palavra, forma, dados) in enumerate(regras):
        chave_regra = f"__REGRA_{idx}__"
        padrao = r'(?<![\w-])' + re.escape(palavra) + r'(?![\w-])'
        padroes.append(f"(?P<G{idx}>{padrao})")
        mapa_regras[f"G{idx}"] = (palavra, forma, dados)

    regex_combinado = re.compile("|".join(padroes), re.IGNORECASE)

    def _substituir(match):
        for group_name, valor in match.groupdict().items():
            if valor is not None:
                palavra_orig, forma_nova, dados = mapa_regras[group_name]
                forma_com_caixa = ajustar_caixa(valor, forma_nova)
                substituicoes_feitas.append({
                    "termo": palavra_orig,
                    "original": valor,
                    "substituicao": forma_com_caixa,
                    "status": dados.get("status"),
                    "voz": dados.get("voz")
                })
                return forma_com_caixa
        return match.group(0)

    texto_resultado = regex_combinado.sub(_substituir, texto)
    return texto_resultado, substituicoes_feitas


def mapa_reverso_fonetico(dicionario=None):
    """Retorna mapa de termos fonéticos normalizados -> termo original canônico.
    Usado por normal() no ASR/conferência literal.
    """
    if dicionario is None:
        dicionario = carregar_pronuncia()

    def _limpar(s):
        s = unicodedata.normalize("NFD", s.lower())
        s = "".join(ch for ch in s if unicodedata.category(ch) != "Mn")
        return re.sub(r"[^\w\s-]", "", s).strip()

    mapa = {
        "freela": "frila",
        "tchequin": "check-in",
        "chequim": "check-in",
        "tchekin": "check-in",
        "abrazeu": "abrasel",
        "cinkuenta": "cinquenta",
        "deis": "dez",
        "federau": "federal"
    }

    for palavra, dados in dicionario.items():
        forma = dados.get("forma")
        if forma:
            chave = _limpar(forma)
            valor = _limpar(palavra)
            if chave and valor:
                mapa[chave] = valor

    return mapa
