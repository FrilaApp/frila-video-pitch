#!/usr/bin/env bash
# scripts/verificar.sh
# Comando canônico de verificação pré-commit / pré-PR para o time de agentes e humanos.
# Executa a suíte de portões determinísticos do Nível 1 (Bloqueia) do Playbook.
# Uso: ./scripts/verificar.sh [--pre-pr]

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "=========================================================="
echo "  [SI-LS] Verificação Automatizada de Orquestração (Nível 1)"
echo "=========================================================="

# 1. Localiza interpretador Python no .venv correto
PYTHON_EXEC=""
if [ -x "$ROOT_DIR/.venv/bin/python3" ]; then
    PYTHON_EXEC="$ROOT_DIR/.venv/bin/python3"
elif [ -x "$ROOT_DIR/../frila-video-pitch/.venv/bin/python3" ]; then
    PYTHON_EXEC="$ROOT_DIR/../frila-video-pitch/.venv/bin/python3"
elif [ -n "${VIRTUAL_ENV:-}" ] && [ -x "$VIRTUAL_ENV/bin/python3" ]; then
    PYTHON_EXEC="$VIRTUAL_ENV/bin/python3"
else
    echo "❌ [F1] .venv não encontrado em $ROOT_DIR/.venv nem no repositório base!"
    echo "    Execute 'scripts/setup.sh' ou configure o symlink com 'scripts/worktree.sh'."
    exit 1
fi

echo "✓ Interpretador: $PYTHON_EXEC"

# 2. Conferência de Dependências e Imports (AST check contra requirements.txt)
echo "--- [1/5] Verificando paridade de dependências..."
"$PYTHON_EXEC" "$ROOT_DIR/scripts/check_dependencies.py"

# 3. Lint de Roteiro (Regra A8: sem dois-pontos na fala, integridade de blocos)
echo "--- [2/5] Verificando integridade de roteiro e locução..."
"$PYTHON_EXEC" "$ROOT_DIR/scripts/lint_roteiro.py"

# 4. Lint de Cópia e Prevenção de Alucinação (Regras D6/D7)
echo "--- [3/5] Verificando conformidade de cópia de tela..."
"$PYTHON_EXEC" "$ROOT_DIR/scripts/lint_copy.py"

# 5. Varredura de Segurança e Binários Proibidos no Git
echo "--- [4/5] Varrendo segredos e arquivos proibidos..."
FORBIDDEN_FILES=$(git status --porcelain 2>/dev/null | grep -E '\.(wav|mp3|mp4|aac)$|motor/cache/' || true)
if [ -n "$FORBIDDEN_FILES" ]; then
    echo "❌ ARQUIVOS PROIBIDOS DETECTADOS NO REPOSITÓRIO:"
    echo "$FORBIDDEN_FILES"
    echo "    Regra do AGENTS.md: nunca commitar áudio, vídeo ou cache. Adicione ao .gitignore."
    exit 1
fi

# Verifica vazamento acidental de chaves de API
if git grep -I -E "sk_[a-zA-Z0-9]{20,}|ELEVENLABS_API_KEY\s*=\s*['\"][a-zA-Z0-9]{15,}['\"]" -- ':!*.jsonl' ':!*.env.example' 2>/dev/null; then
    echo "❌ POSSÍVEL CHAVE DE API ENCONTRADA NO CÓDIGO!"
    echo "    Regra do AGENTS.md: Chaves ficam estritamente em variáveis de ambiente."
    exit 1
fi
echo "✓ Repositório limpo de binários pesados e credenciais."

# 6. Execução Determinística de Testes Unitários (todos os conjuntos: tests/, motor/tests/, emendas e voz por bloco)
echo "--- [5/5] Executando testes unitários no ambiente do projeto..."
"$PYTHON_EXEC" -m unittest discover -s "$ROOT_DIR/tests"
"$PYTHON_EXEC" -m unittest discover -s "$ROOT_DIR/motor/tests"
"$PYTHON_EXEC" -m unittest "$ROOT_DIR/motor/test_emendas.py" "$ROOT_DIR/vozes/test_blocos.py"

echo ""
echo "=========================================================="
echo "  ✅ TODAS AS VERIFICAÇÕES DO NÍVEL 1 PASSARAM COM SUCESSO"
echo "  Pronto para commit ou abertura de PR no branch atual."
echo "=========================================================="
