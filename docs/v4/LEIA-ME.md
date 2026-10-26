# Frila: vídeo-pitch v4 (22/10/2026)

A v4 refaz o vídeo inteiro: animação nova, voz nativa em inglês, trilha nova. O roteiro, os números e as fontes são os mesmos da v3 (menos o concorrente da cena 10, trocado no refinamento), e o vídeo continua sem pedido no fim.

**Refinamento de 22/10/2026 (pedido do Cauê)**
- **Sobreposições:** nenhum elemento cobre outro nem cobre texto. Corrigidos: as fotos da cena 2 (agora fora dos anéis), a linha e o selo da cena 5, as pessoas do check-in, os marcadores do mapa, o cadeado e as linhas da cena 13. A fileira de bolinhas agora encolhe inteira e só o ponto laranja continua. Para conferir, há o `motor2/sobreposicoes.py` (ver "Como refazer").
- **Concorrente da cena 10:** saiu a Freela Serviços, porque o nome confundia com Frila. Entrou a eStaff: 1,5 milhão de cadastrados e 533 mil disponíveis, como a empresa declara em https://estaff.com.br (acessado em 22/10/2026). A cena ganhou uma animação nova, sem travar.
- **Logo final:** cada letra se desenha inteira, da esquerda para a direita, e o "a" fecha. Na saída, cada letra sobe e some inteira, sem sobrar pedaço de traço.
- **Cantos:** saíram as marcas dos 4 cantos e o texto de canto (o "HUD").
- **Voz em português:** 12 frases tinham o fim cortado. Foram regravadas com um pouco mais de tempo (de 8% a 18% mais lentas que antes) e só ficou a versão em que o Whisper ouve a frase até a última palavra e o som termina caindo. Relatório em `vozes/teste/ritmo/relatorio.json`; as frases antigas estão em `vozes/frases/pt-v4-antes-do-refinamento/` e a primeira tentativa em `vozes/frases/pt-refinamento-folga/`.
- **Duração:** o PT passou de 68,9 s para 76,7 s (mais folga entre as frases); o EN continua com 72,8 s.

**O que mudou da v3 para a v4**
- **Movimento:** cada quadro é calculado a partir do tempo. As molas são amortecidas e não quicam. Há zoom de câmera, formas que viram outras formas e um cursor que toca os botões. Um único ponto laranja liga as 15 cenas e termina como o pingo do i do logo.
- **Fluidez:** 60 fps com desfoque de movimento (240 quadros por segundo misturados de 4 em 4), em vez de 30 fps.
- **Paleta e marca:** paleta da marca, sem degradê, brilho nem partícula.
- **Voz em inglês:** a voz nova é americana nativa (Kokoro, voz `af_heart`). A da v3 era a voz em português lendo inglês.
- **Voz em português:** é a mesma da v3. As frases das cenas 11 e 13 foram regravadas em 22/10 porque "cadastra" saía cortado e "meta" soava como "método". As antigas estão em `vozes/frases/pt-v4-substituidas/`.
- **Trilha nova:** "Talent in the Air", remontada por compassos para os cortes caírem no tempo da música.

| Arquivo | O que é |
|---|---|
| `pt/frila-pitch-pt.mp4` | 76,7 s, 15 cenas, cerca de 11 MB |
| `en/frila-pitch-en.mp4` | 72,8 s, 15 cenas, cerca de 10 MB |
| `pt/frila-pitch-pt.srt`, `en/frila-pitch-en.srt` | Legenda em arquivo (20 blocos cada), com o mesmo texto e os mesmos tempos da legenda queimada |
| `STORYBOARD.md` | Cena a cena: tempo, imagem e fala nos dois idiomas |
| `motor2/` | O que gera a v4 (ver "Como refazer") |
| `musica/talent-in-the-air-diego-nava-mixkit.mp3` | A trilha original, sem cortes |
| `vozes/frases/pt/`, `vozes/frases-kokoro/en/` | A voz, uma frase por arquivo |
| `provas/v4/` | Provas da v4 (lista abaixo) |

Especificações dos dois MP4:
- 1920x1080 a 60 fps, H.264 com cores bt709, legenda queimada.
- Áudio AAC a 256 kbit/s, 48 kHz, estéreo.
- Nos metadados: o idioma da faixa e o aviso "Narração com voz sintética (IA)" ("Narrated with a synthetic (AI) voice" no EN).

## Provas (`provas/v4/`)
- `folha-meio-de-cena-<pt,en>.png`: 3 quadros por cena, para ver o movimento.
- `folha-cortes-<pt,en>.png`: os quadros dos cortes entre as cenas.
- `whisper-en.txt`: o Whisper large-v3-turbo transcreve o inglês. Todas as frases saíram certas; a transcrição escreve "Frila" como "Freela", que é a mesma pronúncia.
- `whisper-pt.txt`: a transcrição do PT de antes da correção.
- `whisper-pt-cenas-11-e-13-corrigidas.txt`: as duas frases regravadas, conferidas no MP4 final.
- `whisper-pt-refinamento.txt`: o PT final do refinamento. Todas as frases saem completas. Duas observações: o Whisper escreve "da Staff" porque o "da é-Staff" se junta na fala rápida (com a palavra eStaff como dica, ele ouve "da eStaff"); e as últimas linhas repetidas em 72,56 s, com duração zero, são um erro conhecido do Whisper, não fala.

## Som
Medido nos MP4 finais (ffmpeg ebur128):

| | Loudness integrada | Pico real | LRA |
|---|---|---|---|
| PT | -16,0 LUFS | -2,0 dBTP | 2,6 LU |
| EN | -16,1 LUFS | -1,9 dBTP | 2,5 LU |

- A voz fica cerca de 15 dB acima da música enquanto fala. A música abaixa 11 dB 150 ms antes de cada frase e volta devagar depois.
- Os efeitos (clique, tique, contador, pouso do ponto) são sintetizados em `motor2/audio2.py`, um para cada coisa que a imagem faz naquele quadro. Não há sample de terceiros.

## Vozes e licenças
- **Inglês: Kokoro-82M, voz `af_heart` (inglês americano), a 1,08x.**
  - Roda local e offline pelo `mlx_audio` do VoiceStudio. O script é `vozes/gerar-en-kokoro.sh`.
  - Licença Apache-2.0, com uso comercial permitido (https://huggingface.co/hexgrad/Kokoro-82M, acessado em 22/10/2026).
  - É voz sintética, não clone de ninguém.
- **Português: OmniVoice, perfil `aprovada-T5` (`8095fc2e`), a 1,12x.** É a mesma voz da v1 à v3, aprovada de ouvido pelo Cauê em 16/10/2026.
  - O script é `vozes/gerar-frases.sh` e precisa do VoiceStudio aberto.
  - Na fala, "eStaff" é escrito "é-Staff", para a pronúncia sair certa. A tela e a legenda mostram "eStaff".
  - As 12 frases regravadas no refinamento usam o `vozes/regravar-pt-no-ritmo.py`, que tenta várias sementes e só aceita a frase completa.
  - **⚠️ Licença restrita:** os pesos do OmniVoice são **CC-BY-NC 4.0, só para uso não comercial** (https://huggingface.co/k2-fsa/OmniVoice/raw/main/README.md, acessado em 22/10/2026).
    - Pitch para investidor ou banca, sem venda, cabe na leitura usual de "não comercial".
    - Se o vídeo virar anúncio pago ou peça de venda, é preciso regravar o PT com uma voz de licença comercial ou com locutora.
- **Aviso de voz sintética:** o vídeo mostra "Narração com voz sintética (IA)" em letra pequena na cena final. O mesmo aviso está nos metadados do MP4.

## Música
- "Talent in the Air", de Diego Nava, pelo Mixkit, sob a **Mixkit Stock Music Free License** (texto em https://mixkit.co/license/modal/musicFree, acessado em 22/10/2026). Ela permite uso grátis em projetos comerciais e não comerciais, em qualquer plataforma da web ou rede social, inclusive anúncios.
  - Proibido: CD ou DVD, TV e rádio, videogame, remix, uso numa faixa só de música e registrar a trilha como sua.
  - A licença não pede crédito, mas o crédito está aqui.
  - Inferência: recortar a trilha por compassos para acompanhar o vídeo é edição para sincronizar com a imagem, não um remix lançado como música. Se o vídeo for passar na TV, a licença não cobre.
- O arquivo é https://assets.mixkit.co/music/473/473.mp3 (3.653.843 bytes, igual ao baixado).
- A trilha original dura 1:54 e tem 122 BPM. Ela foi recortada e remontada por compassos (`tempos-<L>.json`, campo `musica`), e o último compasso apaga até o silêncio.

## Como refazer
Tudo foi instalado só dentro de `motor2/`: o Python e o Playwright em `.venv/`, e o Chromium em `browsers/`. Nada foi instalado fora dessa pasta.

```sh
# 1. vozes, só se o texto mudar
bash vozes/gerar-frases.sh          # PT, com o VoiceStudio aberto
bash vozes/gerar-en-kokoro.sh       # EN
cd motor2
# 2. tempos: grade de 122 BPM, cenas, falas e compassos da trilha
.venv/bin/python tempos2.py
# 3. imagem: 6 processos em paralelo, cerca de 4 min por idioma
.venv/bin/python render.py pt
.venv/bin/python render.py en
# 4. som
.venv/bin/python audio2.py
# 5. MP4 final
bash mux.sh
# 6. legendas .srt
.venv/bin/python legendas2.py
```
Atenção: se rodar `gerar-frases.sh` com `FORCAR=1`, as 12 frases do refinamento serão regravadas sem a conferência. Depois, rode `../motor2/.venv/bin/python vozes/regravar-pt-no-ritmo.py` (de dentro de `vozes/`), que regrava e confere cada uma com o Whisper.

Para procurar sobreposições no filme inteiro (a cada 1/15 s): `.venv/bin/python sobreposicoes.py pt` (ou `en`). O resultado sai em `motor2/cache/sobreposicoes-<L>.json`. Ficam na lista, e estão certas, as sobreposições de propósito: anéis concêntricos, o botão do controle deslizante no trilho, o realce que desliza entre os passos, o cursor sobre os botões, o ponto pousando dentro do anel.

Para gerar quadros soltos para conferir, use `.venv/bin/python fotos.py pt cenas` (ou `fotos.py pt 12.5 30`). Os quadros saem em `motor2/cache/fotos/`.

Os textos dos dois idiomas, o desenho e o movimento de todas as cenas estão em `motor2/filme.html`.

## Versões anteriores (guardadas, nada foi apagado)
- `v4-antes-do-refinamento/`: os dois MP4, os dois `.srt`, o LEIA-ME e o STORYBOARD da v4 antes do refinamento de 22/10 (com a Freela Serviços). O `filme.html` de antes está em `motor2/cache/filme-v4-antes-do-refinamento.html`.
- `v4-antes-da-correcao-de-voz/`: o MP4 PT, o `.srt` PT e o MP4 EN da v4 antes da regravação das duas frases do PT e dos metadados.
- `v3-sem-pedido/`: a v3 (66 s, GSAP, 30 fps) com o LEIA-ME, o STORYBOARD, os scripts e as provas dela.
  - Os scripts da v3 também continuam soltos na raiz desta pasta, como estavam: `audio.py`, `legendas.py`, `tempos.py`, `roteiro.json`, `tempos.json`, `cenas/`, `motor/`, `vozes/cenas/` e `vozes/mix-final-*.wav`.
  - O `roteiro.json` continua sendo a fonte das falas das duas versões.
- `v2-com-pedido/`: a v2, com o pedido final.
- `v1/`: a v1.
