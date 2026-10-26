#!/bin/bash
# v4: junta a imagem (cache/filme-<L>.mp4) e o som (cache/mix-<L>.wav) no MP4 final de cada idioma.
# Vídeo copiado sem recodificar; áudio AAC 256 kbit/s a 48 kHz; faststart; idioma da faixa e aviso de voz sintética nos metadados.
# Uso: bash mux.sh [pt|en]
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p ../pt
for L in ${@:-pt}; do
  case $L in
    pt) LANG3=por; AVISO="Narração com voz sintética (IA)";;
    en) LANG3=eng; AVISO="Narrated with a synthetic (AI) voice";;
  esac
  T=$(python3 -c "import json; print(json.load(open('tempos-$L.json'))['total'])")
  ffmpeg -v error -y -i cache/filme-$L.mp4 -i cache/mix-$L.wav -map 0:v -map 1:a -c:v copy \
    -c:a aac -b:a 256k -ar 48000 -ac 2 -t "$T" -metadata:s:a:0 language=$LANG3 \
    -metadata comment="$AVISO" -movflags +faststart ../$L/frila-pitch-$L.mp4
  echo "$L ok ($T s)"
done
