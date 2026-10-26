#!/bin/bash
# Baixa a trilha "Talent in the Air" (Diego Nava, Mixkit Stock Music Free License) e confere o arquivo.
# A trilha NÃO está no repositório: a licença não permite redistribuir o arquivo. Texto da licença: https://mixkit.co/license/modal/musicFree
set -euo pipefail
cd "$(dirname "$0")/.."
ARQ=musica/talent-in-the-air-diego-nava-mixkit.mp3
TAM=3653843
SHA=29a93bdd8ff4ebfe1eff786eb788c0bcc8c82db2338690c5bceebb7aff8eb1e5
mkdir -p musica
[ -s "$ARQ" ] || curl -fL -o "$ARQ" https://assets.mixkit.co/music/473/473.mp3
[ "$(wc -c < "$ARQ" | tr -d ' ')" = "$TAM" ] || { echo "Tamanho diferente do esperado ($TAM bytes)"; exit 1; }
[ "$(shasum -a 256 "$ARQ" | cut -d' ' -f1)" = "$SHA" ] || { echo "SHA-256 diferente do esperado"; exit 1; }
echo "Trilha ok: $ARQ"
