#!/usr/bin/env bash
# scripts/worktree.sh
# Cria e provisiona worktrees determinísticos com link para o .venv e verificação imediata.
# Uso: ./scripts/worktree.sh <nome-do-worktree> <branch>
# Exemplo: ./scripts/worktree.sh ../fvp-motion feat/motion-v4

set -euo pipefail

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [ "$#" -lt 2 ]; then
    echo "Uso: $0 <caminho-do-worktree> <branch>"
    echo "Exemplo: $0 ../fvp-motion feat/motion-v4"
    exit 1
fi

TARGET_DIR="$1"
BRANCH="$2"

echo "Provisionando worktree em '$TARGET_DIR' no branch '$BRANCH'..."

# 1. Cria o worktree no git se ainda não existir
if [ ! -d "$TARGET_DIR" ]; then
    git -C "$BASE_DIR" worktree add "$TARGET_DIR" "$BRANCH"
else
    echo "Diretório '$TARGET_DIR' já existe. Verificando configuração..."
fi

# 2. Cria link simbólico canônico para o .venv compartilhado
echo "Vinculando ambiente virtual .venv compartilhado..."
ln -sfn "$BASE_DIR/.venv" "$TARGET_DIR/.venv"

# 2b. Navegadores do Playwright e trilha (ficam fora do git)
[ -d "$BASE_DIR/motor/browsers" ] && ln -sfn "$BASE_DIR/motor/browsers" "$TARGET_DIR/motor/browsers"
[ -d "$BASE_DIR/musica" ] && ln -sfn "$BASE_DIR/musica" "$TARGET_DIR/musica"

# 3. Executa verificação de integridade no novo worktree
echo "Validando paridade de ambiente no novo worktree..."
"$TARGET_DIR/scripts/verificar.sh"

echo "✅ Worktree '$TARGET_DIR' configurado e 100% operacional no branch '$BRANCH'."
