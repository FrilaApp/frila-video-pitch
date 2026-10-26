#!/bin/bash
# Prepara o ambiente do zero: venv Python, dependências e o Chromium headless do Playwright (dentro de motor/browsers).
# Pré-requisitos: FFmpeg e Python 3.12 (macOS: brew install ffmpeg python@3.12).
set -euo pipefail
cd "$(dirname "$0")/.."
command -v ffmpeg >/dev/null || { echo "Falta o FFmpeg (macOS: brew install ffmpeg)"; exit 1; }
PY=$(command -v python3.12 || command -v python3)
[ -d .venv ] || "$PY" -m venv .venv
.venv/bin/python -m pip install -q --upgrade pip
.venv/bin/python -m pip install -q -r requirements.txt
PLAYWRIGHT_BROWSERS_PATH="$PWD/motor/browsers" .venv/bin/python -m playwright install chromium
echo "Ambiente pronto. Próximo passo: scripts/trilha.sh"
