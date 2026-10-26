#!/bin/bash
# Uso: scripts/pipeline.sh <etapa> [argumentos]
#   voz [cena ...]     gera a voz (ElevenLabs) em vozes/frases/pt/   (precisa da chave; ver HANDOFF.md §4)
#   conferir [cena ..] confere cada frase gerada com o Scribe        → vozes/conferencia.json
#   tempos             monta a régua de tempos                       → motor/tempos-pt.json
#   quadros [cenas|t]  quadros de teste                              → motor/cache/fotos/pt/
#   imagem             renderiza a imagem (~4 min)                   → motor/cache/filme-pt.mp4 e eventos-pt.json
#   audio              mixa o áudio                                  → motor/cache/mix-pt.wav
#   mux                junta imagem e som e gera a legenda           → pt/frila-pitch-pt.mp4 e .srt
#   tudo               tempos → imagem → audio → mux
set -euo pipefail
cd "$(dirname "$0")/.."
PY=${PY:-.venv/bin/python}
etapa=${1:-}; shift || true
case "$etapa" in
  voz)      "$PY" vozes/eleven.py gerar "$@" ;;
  conferir) "$PY" vozes/eleven.py conferir "$@" ;;
  tempos)   (cd motor && "../$PY" tempos2.py) ;;
  quadros)  (cd motor && "../$PY" fotos.py pt "${@:-cenas}") ;;
  imagem)   (cd motor && "../$PY" render.py pt "$@") ;;
  audio)    (cd motor && "../$PY" audio2.py pt) ;;
  mux)      bash motor/mux.sh pt && (cd motor && "../$PY" legendas2.py) ;;
  tudo)     "$0" tempos && "$0" imagem && "$0" audio && "$0" mux ;;
  *)        sed -n '2,12p' "$0"; exit 1 ;;
esac
