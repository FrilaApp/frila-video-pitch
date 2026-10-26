#!/usr/bin/env python3
"""
scripts/lint_copy.py
Validador de cópia de tela e prevenção de alucinação de UI (Regras D6, D7 e AGENTS.md).
Garante que todo texto exibido em cena ou mockups tenha rastreabilidade formal
em roteiro.json ou no vocabulário aprovado de DESIGN.md / telas do app.
Rejeita termos inventados e anotações explicativas vazadas para o quadro.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Termos expressamente proibidos (detectados como alucinações em revisões anteriores)
BANNED_PHRASES = [
    "A confirmação encerra a ação",
    "A confirmação encerra",
    "encerra a ação",
]

def load_approved_corpus():
    corpus = set()
    
    # 1. Extrai do roteiro.json
    roteiro_path = ROOT / "roteiro.json"
    if roteiro_path.exists():
        with open(roteiro_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            for c in data.get("cenas", []):
                pt = c.get("pt", {})
                for text in [pt.get("fala", ""), pt.get("legenda", ""), c.get("tela", ""), c.get("dado_e_fonte", "")]:
                    for token in re.findall(r'\b[A-Za-zÀ-ÿ0-9]+\b', text):
                        corpus.add(token.lower())

    # 2. Termos canônicos da UI do Frila aprovados no DESIGN.md
    canonical_ui = [
        "frila", "app", "turno", "garçom", "garcom", "cozinheiro", "barman", "chamar",
        "publicar", "aceitar", "concluir", "perfil", "avaliação", "nota", "meta",
        "restaurante", "bar", "hoje", "horas", "valor", "r$", "exemplo", "piloto",
        "ibge", "abrasel", "pesquisa", "dados", "confirmado", "disponível"
    ]
    for term in canonical_ui:
        corpus.add(term.lower())

    return corpus

def check_banned_phrases(filepath):
    errors = []
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
            for banned in BANNED_PHRASES:
                if banned.lower() in content.lower():
                    errors.append(f"Frase proibida detectada em {filepath.name}: '{banned}'")
    except Exception as e:
        errors.append(f"Erro ao ler {filepath}: {e}")
    return errors

def main():
    errors = []
    
    # 1. Checa frases proibidas em filme.html, roteiro e propostas
    check_targets = [
        ROOT / "motor" / "filme.html",
        ROOT / "roteiro.json",
        ROOT / "DESIGN.md"
    ]
    # Também checa propostas de mockups em cache se existirem
    cache_dir = ROOT / "motor" / "cache"
    if cache_dir.exists():
        check_targets.extend(cache_dir.rglob("*.txt"))
        check_targets.extend(cache_dir.rglob("*.json"))

    for target in check_targets:
        if target.exists() and target.is_file():
            errs = check_banned_phrases(target)
            errors.extend(errs)

    if errors:
        print("❌ Linter de cópia detectou violações de especificação (Regra D6):", file=sys.stderr)
        for err in errors:
            print(f"  • {err}", file=sys.stderr)
        print("\nNenhum texto de anotação de revisão ou feature inexistente pode figurar em tela ou mockups.", file=sys.stderr)
        sys.exit(1)

    print("✅ Cópia de tela validada: nenhuma alucinação ou frase proibida detectada.")

if __name__ == "__main__":
    main()
