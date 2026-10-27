# DESIGN.md — Vídeo-pitch do Frila (v4 documentada, base da v5)

**Para que serve.** Ser a fonte única de verdade do design do vídeo: tokens, componentes, movimento, som, ritmo e regras. Toda mudança de design da v5 começa aqui e só depois vai para o `motor/filme.html`.

**Status (26/10/2026).** Piloto de imagem do Bloco A em §25, com base na v4 (§§20–23), voz e régua oficiais aprovadas. Avaliação visual do A pendente do Fabrício. Estudo do aparelho integrado pelo PR #16; ajustes posteriores ficam em tarefa separada.

**Levantamento original (histórico; a medição desta tarefa está no §20).** Lidos: `motor/filme.html` (CSS, tokens, textos, cenas, HUD), `motor/tempos2.py`, `motor/audio2.py`, `docs/v4/STORYBOARD.md`, `docs/v4/LEIA-ME.md`, `assets/cores.json`, e a revisão de narrativa. **Não verificado:** posições e tamanhos de cada elemento por captura (só os que o código declara); níveis de volume ouvindo o MP4. Onde o texto diz "Inferência", é leitura minha.

Fontes dos tokens de marca: brand book v1 (22/10/2026), combinação C. Não confundir com o `DESIGN.md` de `frila-apresentação/Apresentação 1`, que é de outro deck e usa outra paleta (`#f6f4ef`, `#ff4d17`).

---

## 1. Conceito

Um vídeo de pitch de 76,7 s (v4) em que **um único ponto laranja atravessa todas as cenas**: é o pingo do "?" na abertura, o centro do radar, o chip que corre, o ponto do mapa, a moeda e, no fim, o pingo do "i" do logo. A imagem é calma, de massa, sem efeito de jogo; o movimento é de mola amortecida, sem quique.

Tom visual: **Praça** (sério, para todas as idades, sem infantilizar). Fundo claro como padrão; duas exceções escuras no miolo (cenas 9 a 11).

## 2. Formato e entrega

| Item | Valor | Fonte |
|---|---|---|
| Resolução | 1920×1080, 16:9 | `filme.html` (`#stage`) |
| Taxa | 60 fps, calculada a 240 quadros/s e misturada de 4 em 4 (`tmix`), o que gera o desfoque de movimento | `render.py` |
| Vídeo | H.264, `preset medium`, `crf 14`, `yuv420p`, cores bt709 | `render.py` |
| Render | 6 processos em paralelo, cada um num trecho; ~4 min para o PT | `render.py`, LEIA-ME |
| Áudio | AAC 256 kbit/s, 48 kHz, estéreo | `mux.sh` |
| Loudness medida na v4 | −16,0 LUFS integrado, pico real −2,0 dBTP, LRA 2,6 LU | `docs/v4/LEIA-ME.md` (medido pelo time em 22/10) |
| Metadados | idioma da faixa `por`; comentário "Narração com voz sintética (IA)" | `mux.sh` |
| Saída | `v5-pt/pt/frila-pitch-pt.mp4` e `.srt` | `mux.sh`, `legendas2.py` |

Determinismo: cada quadro vem de `seek(t)`, nada depende do relógio do navegador. O mesmo `tempos-pt.json` gera sempre o mesmo vídeo.

## 3. Cores

Tokens em `const C` do `filme.html`; valores e usos da marca em `assets/cores.json`.

| Token (código) | Hex | Uso no vídeo | Regra da marca |
|---|---|---|---|
| `paper` (areia) | `#F7F3EE` | Fundo claro padrão | Fundo das telas e peças claras |
| `ink` (grafite) | `#18191C` | Texto, botão escuro, chip, fundo das cenas escuras | Texto, botão escuro, fundo escuro |
| `o` (laranja-frila) | `#EA5A36` | O ponto, destaques, números-chave, preenchimentos | A marca. Texto branco só em tamanho grande |
| `ob` (laranja-queimado) | `#C2410C` | Rótulos laranja pequenos (ex.: "CONTRATANTE") pelo contraste | Botões e links; segura texto branco |
| `mut` (cinza-texto) | `#5B6068` | Texto secundário, fonte, rótulos | 5,73:1 sobre areia, 6,33:1 sobre branco |
| `line` | `#E7E1D8` | Borda de cartões e campos (2 px) | — |
| `soft` | `#F1ECE5` | Avatares, tiles numerados, fundos suaves | — |
| `map` | `#EFE9E1` | Preenchimento do mapa | — |
| `white` | `#FFFFFF` | Cartões e campos | — |
| (inline) | `#8A8F96` | Texto secundário **sobre fundo escuro** | Não consta em `cores.json` |
| (inline) | `#9C9894`, `#D8D3CC` | Textos do aviso (notificação) sobre preto | Não constam em `cores.json` |

Regras:
- **Um único acento** (laranja). Sem degradê, sem brilho, sem partícula (LEIA-ME e STORYBOARD).
- O laranja `#EA5A36` não é usado para texto pequeno sobre claro; para isso, `#C2410C`.
- Cores de estado do app (verde `#007A33`, aviso `#9E5C00`, erro `#D82020`) **não** aparecem no vídeo da v4.
- Sombras: só nos cartões e no ponto quando vira peça (`rgba(24,25,28,.06–.09)`).

## 4. Tipografia

Par 1 do brand book, licença SIL OFL 1.1, carregado de `assets/fontes/ttf/` (variáveis).

| Papel | Família | Peso | Detalhe | Fonte |
|---|---|---|---|---|
| Títulos (`.h`) | Plus Jakarta Sans (`PJS`) | 800 | `letter-spacing −0,035em`, `line-height 1,02` | CSS |
| Corpo (`AHN`) | Atkinson Hyperlegible Next | 400 a 700 | base do palco | CSS |
| Rótulo (`.k`) | AHN | 700 | 24 px, caixa alta, `+0,14em`, cinza | CSS |
| Rótulo de campo (`.lbl`) | AHN | 700 | 15 px, caixa alta, `+0,12em` | CSS |
| Botão (`.btn`) | PJS | 700 | raio 16 px | CSS |
| Legenda (`#cap`) | AHN | 600 | 40 px, `line-height 1,26`, centralizada | CSS |
| Fonte de dado (`#src`) | AHN | 400 | 19 px, cinza | CSS |
| Números grandes | PJS | 800 | `font-variant-numeric: tabular-nums` nos contadores | CSS |
| Passos | PJS 800 (número 28 px), PJS 700 (título 36 px), AHN (subtítulo 25 px) | — | lista de 4 passos | `build()` |

Menor tamanho em CSS: 14 px, no cabeçalho do aviso dentro do celular; há também um texto SVG em unidades próprias (ver seção 17).

## 5. Grade, camadas e margens

- **Palco:** 1920×1080, `overflow hidden`. Três camadas: `#world` (cenas, recebe a câmera), `#ov` (sobreposições), `#hud` (legenda e fonte, não recebem a câmera).
- **Legenda queimada:** `left 310`, largura 1300, `bottom 78`, centro. Aparece com fade e sobe 10 px; saem com desfoque leve. **Não aparece** nas cenas 1, 9 e 16 (`NOCAP`).
- **Fonte de dado:** `left 72`, `bottom 38`, largura máxima 1100. Aparece só nas cenas 3, 4 e 10, entre 0,3 s depois do início e 0,35 s antes do fim da cena.
- **Margens de cena:** o conteúdo central vive no miolo; a faixa de baixo (~190 px) é reservada para a legenda e a fonte. Nenhum elemento pode invadir essa faixa. Inferência: as cenas respeitam isso por construção; não medi cena a cena.
- **Lista de passos (cenas 6 e 7):** coluna à direita em `left 1000`, 4 linhas de `780×110` a partir de `top 262`, passo de 130 px. Telefone à esquerda: tela `352×752`, raio 50, em `(484, 104)`.
- **Mapa (cena 8):** SVG `960×552` em `(560, 264)`, contorno esquemático do DF, "escala aproximada".

## 6. Componentes

| Componente | Especificação | Onde na v4 |
|---|---|---|
| **Ponto laranja** (`#dot`) | Um único elemento: posição, largura, altura, raio, cor e sombra animados por molas. Vira pílula, chip, anel, moeda, pingo do "i" | todas |
| **Pílula do gancho** (`#pill`) | `600×104`, texto PJS 700 36 px, "Garçom · hoje, 19h · R$ 120" | c01 |
| **Pontuação "?"** (`#q`) | SVG `56×112`; o ponto laranja assenta nele | c01 |
| **Radar com rostos** | Anéis concêntricos que se desenham, avatares `.c02av`, check no centro | c02 |
| **Número contador** (`mkOdo`) | Odômetro por dígito, mola `count`; "##,##%" e "#" | c03, c04 |
| **Fileira de pessoas/bolinhas** (`#row`) | 10 itens; c03 esvazia 7, c04 pinta 9 de laranja e 1 de grafite; encolhe e o ponto continua | c03–c05 |
| **Cartão** (`.card`) | Branco, borda 2 px `line`, raio 28 | c05, c10, c12, mapa |
| **Chip** (`#chip`) | Altura 56, raio 28, grafite, PJS 700 24 px; corre pela linha pontilhada | c05 |
| **Telefone** | Tela areia `352×752`, ilha preta; 4 telas: formulário, bloqueio com aviso, candidatos, check-in | c06, c07 |
| **Campo** (`.fld`) | Branco, borda 2 px, raio 16, rótulo `.lbl` | c06 |
| **Botão** (`.btn`) | Grafite, PJS 700, raio 16; vira laranja com check ao concluir | c06, c12 |
| **Lista de 4 passos** | Tile numerado 64×64 raio 16 (`soft`); o ativo vira laranja com cartão branco e sombra suave; os outros esmaecem | c06, c07 |
| **Cursor** (`#cur`) | SVG 34×46, grafite com contorno branco; clique reduz a escala a 0,84 por 0,09 s e gera evento `clique` | c06, c07, c12 |
| **Mapa do DF** | SVG esquemático, 15 km desenhado em torno do ponto, câmera aproxima até 200 m | c08 |
| **Cartões de dado** ("Aviso até 15 km", "Presença 200 m") | Cartão branco, rótulo laranja `ob`, número PJS grande, nota cinza | c08 |
| **Cena de frase escura** | Fundo grafite, texto areia, última palavra em laranja | c09, c11 |
| **Janela de navegador** | Barra com 3 pontos e endereço; números 1,5 e 533 em PJS grande | c10 |
| **Grade de pontos** | Pontos cinza com alguns laranja | c11 |
| **Cartão de profissional** | Avatar, nome, distância, duas barras (comparecimento em bolinhas, "chamariam de novo" em traços) | c12 |
| **Linha do tempo** | Nó grafite com check (feito) e nó laranja com anel (meta), linha sólida e tracejada | c13 |
| **Moeda** | Círculo laranja "R$ 0" entre dois rótulos | c14 |
| **Logo animado** (`#c16t`) | Wordmark "frila" desenhado letra a letra; ponto pousa no pingo do "i"; saída letra a letra | c16 |

Ícones (inline SVG, traço 2–3): `pessoa`, `loja`, `check`, `cursor`.

## 7. Movimento

**Princípio:** tudo é soma de molas de forma fechada, uma por mudança de alvo (`key`/`val`). Não há bounce.

| Preset | ω (rad/s) | ζ | Uso típico |
|---|---|---|---|
| `ui` | 18 | 0,86 | entradas de elementos de interface |
| `move` | 11 | 0,82 | deslocamento do ponto e de peças |
| `soft` | 7 | 0,90 | movimentos amplos e calmos |
| `cam` | 5,5 | 0,95 | câmera |
| `pop` | 16 | 0,76 | aparição com leve ênfase |
| `count` | 5,2 | 0,985 | contadores (mola lenta) |
| `slow` | 4,2 | 0,95 | revelações longas |
| `snap` | 34 | 0,90 | cortes rápidos |

Regra do código: ζ ≥ 0,74 garante sobressinal ≤ 3 %.

Padrões de entrada e saída:
- **Elemento (`io`)**: entra subindo ~26 px com fade de 0,2 s; sai apagando em 0,22 s.
- **Texto por palavra (`wio`)**: cada palavra entra com defasagem (`stg`) e sobe ~40 px.
- **Câmera (`CAM`)**: translação e escala do `#world`; zoom do mapa de 15 km até 200 m.
- **Cursor (`CUR`)**: caminha até o alvo e clica; cada clique é um evento de som.
- **Tema (`th`)**: troca claro→escuro no início da cena 9 e escuro→claro 0,05 s antes da cena 12.
- **Redução de movimento:** não se aplica a vídeo; vale para o HTML dos slides (outro produto).

Visibilidade: a cena fica ativa de 1,0 s antes do início até 0,9 s depois do fim, para as transições se sobreporem.

## 8. O ponto laranja: trajeto

| Cena | O ponto é |
|---|---|
| 1 | pingo do "?" |
| 2 | centro do radar |
| 3 | continua na fileira de pessoas que encolhe |
| 5 | o chip que corre entre os dois cartões |
| 6–7 | o telefone encolhe até virar o ponto |
| 8 | o ponto do mapa; os círculos de 15 km e 200 m nascem dele |
| 9–11 | pontos laranja na grade escura |
| 14 | a moeda "R$ 0" |
| 16 | pousa como pingo do "i" do logo, com sino |

Fonte: `docs/v4/STORYBOARD.md`. Regra: **o ponto nunca some**; se uma cena nova não tem papel para ele, ele fica pequeno e quieto num canto de passagem.

## 9. Tema claro e escuro

- Claro: fundo `#F7F3EE`, texto `#18191C`, secundário `#5B6068`.
- Escuro (cenas 9 a 11): fundo `#18191C`, texto `#F7F3EE`, secundário `#8A8F96`. O HUD (legenda e fonte) acompanha por interpolação de cor (`th`).
- O corte para o escuro é **seco** e marcado com o som `grave`; a volta ao claro também.

## 10. Legenda

- Texto = o campo `legenda` do `roteiro.json`; a fala (voz) é o campo `fala`. Podem diferir (números por extenso na fala, algarismos na legenda).
- Uma legenda por frase, presa ao início exato da frase falada (`leg_ini` = início − 0,05 s).
- `leg_fim` = início da próxima frase − 0,05 s, ou fim da frase + 0,6 s, no máximo até 0,12 s antes do fim da cena.
- Mesmo texto e mesmos tempos vão para o `.srt`.
- Fora da legenda: cenas 1, 9 e 16, em que o texto já está em tela.

## 11. Ritmo e tempos

Grade da trilha: 122 BPM medidos; 1 tempo `P = 0,491835 s`; 1 compasso `BAR = 4P ≈ 1,967 s`.

| Constante (`tempos2.py`) | Valor | Efeito |
|---|---|---|
| `ENTRADA["c01-gancho"]` | 2P | o gancho espera o ponto assentar |
| `ENTRADA_PADRAO` | P/2 | demais cenas começam a falar meio tempo depois do corte |
| `PAUSA` | 0,10 s | entre frases da mesma cena |
| `CAUDA` | 0,30 s | respiro depois da última frase |
| `NO_COMPASSO` | c05, c09, c12 | cenas que começam em compasso, porque a música muda de seção |
| `DURACAO_MIN` | por cena (2,9 a 6,9 s) | piso de duração |

Regras: cenas começam num tempo da grade; frases começam num meio tempo; **o vídeo termina no fim de um compasso**; a cena anterior a um corte de compasso estica até ele.

## 12. Áudio (parte do design)

**Trilha:** "Talent in the Air" (Diego Nava, Mixkit, licença Mixkit Stock Music Free), remontada por compassos: intro até a cena 5, groove até a 9, quebra até a 12, groove de novo até o fim; cada bloco termina no compasso de virada da própria trilha (7, 23, 31). Último compasso apaga até o silêncio. A licença não cobre TV, rádio, CD/DVD nem remix.

**Mix (código):**
- Alvo de voz −20 dB RMS; alvo de música −24 dB RMS.
- Ducking: a música cai 11 dB, começa 150 ms **antes** da fala, segura 250 ms e volta em ~400 ms.
- Efeitos: ancorados 3 dB acima do nível-alvo da música, cada um com o peso da tabela abaixo.
- Fade de 20 ms no fim; limiter; normalização para ~−16 LUFS.

**Efeitos, um por evento da imagem** (`eventos-pt.json`, gravado pelo `render.py`):

| Evento | Som | Peso | Quando |
|---|---|---|---|
| `clique` | clique curto | 0,55 | cursor toca botão (`click()`) |
| `tick` | tique | 0,35 | avatares acendem (c02), fileira e bolinhas se preenchendo (c03, c04), passos do fluxo (c06, c07), barras do cartão (c12) |
| `roll` | tiques em sequência | 0,5 | contadores girando (c03; números da c10) |
| `pop` | pop | 0,5 | aparições com ênfase: pílula e "?" (c01), escolha do rosto (c02), pouso na c05, círculo de 200 m (c08), segundo item da c13 |
| `swish` | swish | 0,4 | transições de peça: c01, c05, fluxo, círculo de 15 km (c08), virada da moeda (c14) |
| `ok` | sino curto | 0,35 | confirmações: vaga publicada, escolhido, check-in, c12, primeiro item da c13 |
| `aviso` | sino de notificação | 0,45 | o aviso entra na ilha do celular |
| `grave` | grave | 0,7 | corte para o escuro (c09) e volta ao claro (antes da c12) |
| `pouso` | baque + sino em Fá | 0,5 | ponto vira o pingo do "i" (c16) |

Fonte dos gatilhos: chamadas `ev(...)` no `filme.html`. Os sons são sintetizados em `audio2.py` (sem sample de terceiros).

**Voz (v5):** ElevenLabs, voz Fernanda, `eleven_multilingual_v2`, 24 kHz mono por frase; conferência pelo Scribe. Aviso "Narração com voz sintética (IA)" na cena final e nos metadados.

### Infraestrutura v5 autorizada (T4, 26/10/2026)

A implementação segue `PLANO-AUDIO.md` §H e `motor/mixagem.json`: preservar o
bruto por padrão, sem fades em fala; stems independentes de voz, música e efeitos;
ducking dos dois fundos antes do primeiro som; `grave` subordinado à palavra.
Premix é a soma exata dos stems ducked. Master em duas passagens, sem limiter
fixo adicional, alvo −16 LUFS ±0,5 e pico real ≤−1,5 dBTP no AAC decodificado.
A configuração e o QA acompanham cada sessão. A montagem musical/cenas ainda
é a v4 até T5; esta infraestrutura não aprova voz, sincronismo ou escuta da v5.

## 13. Inventário de cenas da v4 (15 cenas, 76,7 s no PT)

| # | Id | Função na narrativa | Imagem | Duração PT |
|---|---|---|---|---|
| 1 | c01-gancho | Gancho | "Faltou gente / no turno de hoje" palavra por palavra; pílula cai; ponto vira o "?" | 3,4 s |
| 2 | c02-promessa | Promessa | "Gente perto. Turno coberto." + radar com rostos | 3,9 s |
| 3 | c03-rotatividade | Dado | 73,49% conta; 10 pessoas, 7 se esvaziam; fonte Abrasel/Monitor Mercantil | 4,9 s |
| 4 | c04-contratar | Dado | "9 em 10"; 9 bolinhas laranja e 1 grafite; fonte Abrasel | 5,4 s |
| 5 | c05-o-que-e | Definição | dois cartões ligados por linha pontilhada; chip corre | 4,9 s |
| 6 | c06-passos-a | Solução | telefone "Nova vaga" → "Publicar" → aviso; passos 01 e 02 | 6,9 s |
| 7 | c07-passos-b | Solução | "Candidatos" → escolha → "Check-in" e Sim/Não; passos 03 e 04; telefone vira o ponto | 5,9 s |
| 8 | c08-mapa | Solução | mapa do DF, 15 km, zoom até 200 m, cartões | 7,9 s |
| 9 | c09-cadastro | Contraste | fundo escuro, "Cadastro não é turno." | 2,95 s |
| 10 | c10-concorrente | Dado | janela eStaff: 1,5 milhão e 533 mil; fonte do site em 22/10/2026 | 6,9 s |
| 11 | c11-contraste | Tese | grade de pontos, "Quem aparece, não quem se cadastra." | 3,9 s |
| 12 | c12-confianca | Solução | cartão do profissional, barras, "Escolher" | 4,9 s |
| 13 | c13-estagio | Estágio | linha do tempo 20/10/2026 → 13/11/2026 | 4,4 s |
| 14 | c14-gratis | Preço | moeda "R$ 0", "Grátis no piloto" | 2,95 s |
| 16 | c16-logo | Assinatura | logo desenhado, "Turno combinado, regra clara.", aviso de voz sintética | 7,4 s |

A numeração pula o 15, que era o pedido de piloto (saiu na v3).

## 14. Mapa da v5 (14 momentos; montagem visual aplicada, régua provisória)

Fonte: `NARRATIVA-v5-100s.md` e `roteiro.json`. Marca o que reaproveita da v4, o que adapta e o que é novo. **Os ids das cenas mudam** (`v01` a `v14`): `NOCAP` e tema `th` já usam os ids novos no `filme.html`. `NO_COMPASSO`, `DURACAO_MIN`, `ENTRADA` e seções musicais de `tempos2.py` ficam para T5; não foram alterados por T6.

| v5 | Momento | Componentes | Origem |
|---|---|---|---|
| v01 | Gancho, Dor 1 | Pílula, "?", ponto; tag "Exemplo" | **reaproveita** c01 (pílula sem preço: ajuste) |
| v02 | Dor 1, dado | Contador "9 em 10", 9+1 bolinhas, fonte | **reaproveita** c04 |
| v03 | Dor 2, confiança | Fundo escuro, janela eStaff, "Cadastro não é turno" | **adapta** c09 + c10 numa cena só |
| v04 | Dor 3, rotatividade | 73,49%, fileira, vaga nova reaparece | **adapta** c03 (sem "equipe inteira trocada") |
| v05 | Virada | Dois cartões / chip, mockup, três marcas | **adapta** c05; **novo:** marcas das dores |
| v06 | Solução 1 | Telefone formulário + aviso; mapa 15 km | **reaproveita** c06 + parte de c08, **com a diretriz D1** (zoom + parallax) |
| v07 | Solução 2 | Candidatos + check-in 200 m | **reaproveita** c07 + cartão c12, **com D1**; tag "Exemplo" |
| v08 | Teaser | Pergunta grande, contador vazio "— vezes por ano", ponto pairando | **novo** |
| v09 | Solução 3 | Avaliação Sim/Não → histórico ilustrativo | **adapta** fim de c07, **com D1**; **novo:** histórico |
| v10 | O dado | 22 pontos cinza, só o do Frila com check; rodapé da pesquisa | **novo** (usa a grade de pontos da c11) |
| v11 | A meta | Três contadores (`mkOdo`), tag "Meta do piloto · hipótese a calibrar" | **novo** (reaproveita o odômetro) |
| v12 | A estratégia | Mapa da c08: círculo de 15 km, 3 pontos-âncora, pontos menores, cresce até o DF; números só na tela | **adapta** c08 |
| v13 | Fecho | Off-white calmo; relógio do gancho volta | **novo** |
| v14 | Assinatura | Logo A1; contato `frila.org@gmail.com` em texto pequeno | **reaproveita** c16 + linha de contato |

Sai da v4: c11 (grade "Quem aparece…"), c13 (estágio), c14 (preço R$ 0).

### D1 em detalhe: mockup em foco com parallax e zoom (valores iniciais **propostos**, a validar por captura com o Cauê)

- **Zoom de foco:** a câmera (`CAM`, mola `cam`) aproxima da tela do aparelho. A tela tem 752 px de altura num palco de 1080; escala **1,20 a 1,30** deixa o aparelho com ~90% da altura do quadro. Entrada em ~0,6 s; saída antes do corte.
- **Parallax:** camadas com fator de deslocamento diferente durante o zoom e o movimento da câmera: fundo e mapa **0,6×**, lista de passos **0,85×**, aparelho **1,0×**, cursor e ponto laranja **1,1×**. Deslocamento máximo de ~30 px, para não parecer tremor.
- **Lista de 4 passos:** esmaece e desloca para fora do foco enquanto o zoom está no máximo; volta ao final da cena. Nunca cobre a tela do aparelho.
- **Faixa da legenda** permanece livre (regra herdada); se o zoom invadir, reduzir a escala.
- **Verificar** com `scripts/pipeline.sh quadros` e `sobreposicoes.py` (regra "nada cobre nada").

## 15. Regras de ouro

1. **Um acento só:** laranja `#EA5A36`.
2. **Sem degradê, brilho, partícula, HUD de canto ou marcas de canto.** (Removidos na v4.)
3. **Nada cobre nada.** Nenhum elemento cobre outro nem cobre texto. Conferir com `sobreposicoes.py` (passo 1/15 s). Sobreposições intencionais ficam na lista: anéis concêntricos, botão no trilho, realce que desliza entre passos, cursor sobre botão, ponto dentro do anel.
4. **Mola amortecida, sem quique** (ζ ≥ 0,74).
5. **O ponto laranja liga as cenas** e termina no pingo do "i".
6. **Dado com fonte aberta na tela** (rodapé `#src`); dado declarado por empresa diz "como a empresa declara" e a data de acesso.
7. **Telas de exemplo vão marcadas "Exemplo"**; nada de métrica que o app não tenha.
8. **Texto grande e curto.** Hierarquia clara; legível projetado; contraste AA (grafite sobre areia 15,91:1).
9. **Corte no compasso.** Cena nova entra num tempo da grade; o corte da seção de música cai num compasso.
10. **Sem número de economia** nem promessa de resultado que a fonte não sustenta.
11. **Sem pedido final.**

## 16. Qualidade: como conferir

| O quê | Como | Saída |
|---|---|---|
| Composição de cada cena | `fotos.py pt cenas` (3 quadros por cena) | `motor/cache/fotos/pt/` |
| Quadro específico | `fotos.py pt 12.5 30` | idem |
| Sobreposições | `sobreposicoes.py pt` | `motor/cache/sobreposicoes-pt.json` |
| Voz inteira e sem corte | `vozes/eleven.py conferir` | `vozes/conferencia.json` |
| Áudio final | `ffmpeg ebur128` no MP4; alvo ≈ −16 LUFS, pico ≤ −2 dBTP | relatório |
| Fala no MP4 final | Scribe sobre o áudio do MP4 | transcrição |
| Texto da tela | conferir contra `roteiro.json` (campo `legenda`) | — |

Checklist por cena nova: tokens da seção 3; fonte e tamanho da seção 4; fora da faixa da legenda; ponto presente; evento de som para cada clique, toque e pouso; sem sobreposição; tag "Exemplo" onde houver dado ilustrativo.

## 16b. Diretrizes do Cauê para a v5 (26/10/2026)

Entram aqui antes de virar código. Status: **definidas, não implementadas**.

| # | Diretriz | O que significa no design | Status |
|---|---|---|---|
| D1 | **Mockup com foco na tela do dispositivo** | Quando um mockup está em cena (v06, v07 e v09 da v5), a tela do aparelho é o protagonista. Câmera faz **zoom-in de foco** na tela e as camadas (aparelho, fundo, lista de passos, ponto) se movem com **parallax** em profundidades diferentes, para mostrar o device com volume | Implementado para ensaio em `filme.html`; parâmetros e medidas em §19, aprovação por captura pendente |
| D2 | **Ducking cuidadoso com o voice-over** | A música e os efeitos nunca disputam com a voz; margem mínima entre voz e música em cada frase | Em planejamento (`PLANO-AUDIO.md`, Astra) |
| D3 | **Trilhas de áudio separadas desde a geração** | Voz, música e efeitos saem como arquivos próprios; mudar um não refaz os outros | Em planejamento (`PLANO-AUDIO.md`) |
| D4 | **Sem cortes de fala** | Nenhuma sílaba comida pelo corte automático, pela geração por frase ou pela mixagem | Evidências na seção 17; plano em `PLANO-AUDIO.md` |

**Para D1, perguntas de design a fechar** (antes de implementar): quanto de zoom (a tela do aparelho ocupa que fração da altura do quadro?); quais camadas entram no parallax e com que deslocamento relativo; o zoom acompanha o cursor/ação ou fica fixo na tela; como o zoom entra e sai (mola `cam`, ω 5,5, ζ 0,95, já existe); o que acontece com a lista de 4 passos ao lado quando o zoom aumenta (some, esmaece ou sai do quadro). **Regra herdada que continua valendo:** nada cobre nada, e a faixa da legenda fica livre.

## 17. Observações para o critique de design (não resolvidas)

Levantadas lendo o código e os slides exportados; **nenhuma foi corrigida**.

1. **Lógica das bolinhas.** A cena 3 esvazia 7 de 10 pessoas (para "7 em 10"); a cena 4 pinta 9 de 10 de laranja (para "9 em 10"). Um lê "o que sobra", o outro "o que acontece".
2. **Cartão de profissional** (Bruno T., 18 de 20 turnos, 10 de 12 chamariam de novo) aparece como dado real; a v5 propõe a tag "Exemplo".
3. **Cartão "Presença"** diz "check-in e check-out a até 200 m do local", mas a fala só cita o check-in.
4. **Tokens fora do brand book:** `#8A8F96`, `#9C9894` e `#D8D3CC` são usados inline e não constam em `cores.json`.
5. **Texto pequeno:** 14 px no cabeçalho do aviso dentro do celular e um texto de SVG com `font-size="11"` (em unidades do SVG; não identifiquei onde aparece nem o tamanho final em tela). Conferir leitura projetada.
6. **Cena de abertura sem logo;** a marca só aparece na cena 16.
7. **Os PNGs de `frila-apresentação/Apresentação 2/slides/img-pt/` parecem quadros deste vídeo.** Inferência: têm a legenda queimada e a mesma composição de telefone e lista de passos. Se for isso, o slide 9 (candidatos/check-in sobrepostos) é um quadro de transição, não um erro de desenho do vídeo. Não confirmei a origem dos PNGs.
8. **Corte de fala no MP4 entregue.** O Scribe transcreveu "Castro não é turno" (cena 9, 43,53 s), embora o arquivo bruto da frase diga "Cadastro" (conferido). O efeito `grave` (peso 0,7) começa 285 ms antes da voz e, pela duração no código, sobrepõe ~415 ms dela; os efeitos não sofrem ducking. É **hipótese** de mascaramento: falta comparar com e sem o efeito.
9. **Frases brutas da v4 estão limpas** (110 a 205 ms de silêncio no fim, começo a −55 dBFS): a geração por frase não cortou a voz da v4. O problema é de mixagem.
10. **Voz do ElevenLabs entra quase sem silêncio** (10 a 100 ms antes; começo a −37..−53 dBFS). O corte automático da v4 (−45 dBFS, 30 ms antes) descartava 40 a 60 ms de voz fraca em 12 de 20 frases; prova: "Turno combinado" virou "termo combinado" depois de aparar, e estava certo no bruto. Na v5 não há corte automático: `preparar()` (`motor/tempos2.py`) conserva o bruto, sem fades; corte só com limites confirmados e aprovação (`PLANO-AUDIO.md` §H).
11. **Pausas entre frases** na v4: 0,21 a 0,34 s na mesma cena (quantizadas a meio tempo da grade de música) e 0,55 a 2,42 s entre cenas. Conferir se alguma pausa soa artificial.
12. **Tempo de leitura:** cenas de dado têm 2,9 a 5,4 s; conferir se os números têm tempo de pousar antes de a voz seguir.

## 18. Histórico

- 26/10/2026: documento criado a partir da v4. Nenhuma mudança de design aplicada.
- 26/10/2026: diretrizes D1 a D4 do Cauê (seção 16b) e observações 8 a 11 sobre cortes de fala. Engenharia sonora delegada ao Astra (`PLANO-AUDIO.md`).
- 26/10/2026: narrativa passou a `NARRATIVA-v5-100s.md` (14 momentos, ~100 s). A seção 14 ficou desatualizada; contato `frila.org@gmail.com` entra na cena final, em texto pequeno, sem fala.


## 19. Implementação visual T6 e preparação T7 — 26/10/2026

Escopo autorizado: cenas v01–v14 conforme §14 e narrativa de 100 s, sem promover o rascunho a roteiro aprovado. `roteiro.json`, voz e régua oficial permanecem pendentes. Cada cena tem `planVXX`/`runVXX`, textos em `TX.pt` e eventos `ev(...)`. O tema escuro fica apenas em v03; a faixa a partir de y=890 fica reservada ao HUD (legenda/fonte), com exceção do rodapé da assinatura, que não tem legenda queimada.

Reutilizar os tokens, molas, odômetros, pílula, cartões, telas de telefone, janela eStaff, mapa esquemático e traços do logo da v4. v04 usa cartões de escala que trocam, sem converter rotatividade em probabilidade individual. Os 22 pontos de v10 representam somente os concorrentes pesquisados; o ponto do Frila fica separado e recebe o check. Valores de perfis e vagas são os exemplos herdados, sempre com a tag “Exemplo”. As três âncoras do mapa são esquemáticas, sem nomes ou contratos inferidos. Metas continuam marcadas como hipótese; números de mercado mantêm a atribuição da narrativa (fontes primárias ainda não reabertas).

D1: iniciar o ensaio com escala 1,20 e mola `cam`, entrada de aproximadamente 0,6 s; testar também os quadros de saída. Camadas de mapa/fundo 0,6×, passos 0,85×, aparelho 1,0×, cursor/ponto 1,1×; limitar deslocamento de parallax a 30 px. A lista esmaece e sai lateralmente no foco, voltando ao final. Se 1,20 atingir a faixa da legenda ou recortar o aparelho, reduzir a escala e registrar o valor medido aqui antes da alteração no motor.

A régua de ensaio é explicitamente **PROVISÓRIA**, estimada a 2,3 palavras/s com pausas e mínimos visuais de `janela_s`, sem áudio nem grade musical oficial. Script separado em `scripts/tempos-provisorios.py`; saída ignorada `motor/tempos-pt.json`. Não importa nem altera `tempos2.py`, não produz voz, não monta música e não serve à mixagem/entrega final. As capturas e relatórios ficam somente em `motor/cache/`.


**Conferência D1 inicial:** a captura com escala 1,20 mediu aparelho de 902,40 px, y=3,80 até y=906,20 nas três cenas, invadindo 16,20 px da faixa reservada (y=890). Aplicada escala **1,10**, centro visual y=430: altura medida 827,20 px (aproximadamente 77% do quadro), aparelho inteiro e legenda livre. É a redução prevista em §14; a referência “~90%” cede à faixa da legenda. Escala 1,10 aprovada pelo Fabrício em 26/10/2026. Evidência local: `motor/cache/qa-v5/limites-d1-1.20.json`.


**Resultado do ensaio:** 14 cenas, 28 frases estimadas, 43 eventos visuais. A régua provisória soma 107,4196 s (não atende nem pretende substituir a duração oficial de T5). `NOCAP` = v01, v13 e v14, conforme `legenda_queimada` do rascunho. 42 quadros padrão, estados adicionais por frase e buscas fora de ordem conferidos em Chromium; sem erros. Nos 328 instantes amostrados dos mockups, topo mínimo y=16,396 e base máxima y=843,604, com lista de passos separada do aparelho. O zoom volta a 1 antes de cada corte.

A varredura original `sobreposicoes.py pt` a cada 1/15 s encontrou **13 pares geométricos esperados, zero pares de texto**: cursor tocando botões/aparelho; traços do ícone de loja e do logo; mapa sob seus marcadores/círculo; círculo nascendo do ponto. Não foram adicionados filtros ao detector. Detalhes, reprodução e caminhos das capturas em `docs/QA-CENAS-v5.md`. A duração real ainda depende da voz e da régua oficial. Rodapé da v12 sem citar arquivo do repositório (só "Dados · CNPJs ativos no DF; IBGE 2024."), aprovado pelo Fabrício em 26/10/2026.

## 20. Retomada da v4 — bíblia de motion medida (26/10/2026)

**Esta seção rege a retomada.** A v5 de 108 s foi reprovada pelo Fabrício. §§14, 16b e 19 são histórico do ensaio rejeitado, não autorização para usá-lo como base. O roteiro será enxugado pelo Maestro para ~80 s e aprovado pelo Fabrício. Nenhuma nova cena, voz ou régua definitiva entra nesta tarefa. Entrega: documentação, propostas estáticas e instrumento de revisão; sem push.

### Fontes e distinção entre dado e julgamento

Fonte executável: `git show 4efa75a:motor/filme.html`, preservada apenas em cache para a inspeção. Régua e eventos: `docs/v4/tempos-pt.json`, `docs/v4/eventos-pt.json`; descrição: `docs/v4/STORYBOARD.md`. Referência visual: `/Users/fabriciotosta/Downloads/frila-pitch-pt.mp4`, **76,733333 s, 1920×1080, 60 fps**, medidos com ffprobe nesta tarefa. V5 somente para calibração (arquivada em 26/10/2026; também há cópia da v4 em `/Users/fabriciotosta/dev/video-frila/referencias/v4-nota-8/`): `/Users/fabriciotosta/dev/video-frila/referencias/v5-reprovada/frila-pitch-pt.mp4`, **108,200 s de imagem / 108,204 s de contêiner**. A nota 8/10 é avaliação do Fabrício, não resultado do detector.

### Curvas reais, sem substituir por curvas genéricas

A função `spr(t,p)` da fonte é a resposta ao degrau de segunda ordem: `1 − exp(−ζωt)·[cos(ωd t)+(ζω/ωd)sin(ωd t)]`, `ωd=ω√(1−ζ²)`, zero para t≤0. `val` soma a resposta de cada mudança de alvo à posição anterior: a velocidade não é reiniciada a cada cena. Presets lidos em `PR`:

| Preset | ω | ζ | Onde se lê o uso |
|---|---:|---:|---|
| ui | 18 | 0,86 | texto, botão, indicador dos passos |
| move | 11 | 0,82 | ponto, mudança de forma, cursor |
| soft | 7 | 0,90 | chip, arrasto, caminhada, expansão escura |
| cam | 5,5 | 0,95 | zoom 2,6× do mapa, reposicionamento amplo |
| pop | 16 | 0,76 | rostos e confirmações |
| count | 5,2 | 0,985 | odômetros, separados da velocidade dos títulos |
| slow | 4,2 | 0,95 | preset declarado; não implica uso em toda cena |
| snap | 34 | 0,90 | troca de cor e desaparecimento deliberado do ponto |

A expressão “sem quique” nos docs significa amortecimento alto, não sobressinal matematicamente zero: ζ<1 permite sobressinal. Não aumentar a elasticidade. Há também `eo(u)=1−(1−u)³` e `eio(u)=4u³ / 1−(−2u+2)³/2`, com `u` limitado a [0,1]. `fade` usa `eo`; não é CSS ease. `g(t,div)` arredonda para `P/div`, com **P=0,491835 s** na régua v4.

Entradas reais: `io`: opacidade 0→1 em **0,20 s**, posição sobe **26 px** por `ui`; saída em **0,22 s**, sem reversão da trajetória. `wio`: fade **0,16 s**, sobe **40 px** (46 no gancho, 50 no contraste), palavras defasadas conforme a fala; saída defasada **0,03 s/palavra**, fade **0,20 s**. Cursor: compressão para **0,84**, retorno acionado após **0,09 s**. Isso é coreografia de filme; limites de duração para UI interativa não substituem estes valores.

### Régua e respiração por cena

Tempos abaixo são absolutos da régua v4; gatilhos relativos vêm das funções `planC*`/`runC*`. `f.ini` e `f.fim` referem-se à fala arquivada, não ao roteiro atual.

| Cena | Janela (s) | Coreografia lida na fonte; saída / ligação |
|---|---|---|
| c01 | 0–3,4428 | pílula: cor 0,24; forma 0,30; desce em 0,95; encolhe em 2,05; vai à coluna do ? em 2,10 e sobe em 2,34, sem cruzar palavras; texto sai end−0,30 |
| c02 | 3,4428–7,3775 | ponto ao radar ini+0,02; anéis a cada P/2; rostos só após `g(ini+0,1)+P+0,45`, a cada P/4; escolha em 60% da fala; ponto parte end−0,42; anéis apagam sem encolher sobre rostos |
| c03 | 7,3775–12,2959 | contador `g(f.ini+0,45,2)` com count; subtítulo 1 s depois; pessoas a cada P/8, esvaziamentos a cada P/4; texto sai end−0,22 |
| c04 | 12,2959–17,7061 | preenchimento `g(f.ini+0,25,4)` a cada P/4; subtítulo em 42% da fala; fileira converge inteira, desaparece antes de encostar; ponto continua; saída end−0,20 |
| c05 | 17,7061–22,6244 | cartão esquerdo ini+0,02, direito em 50% da fala, chip em 60%, pouso +0,62; texto sai end−0,40; ponto se move end−0,50, vira grafite end−0,46 e chassi end−0,38 |
| c06 | 22,6244–29,5101 | lista `g(f1.ini+0,05,2)` com P/4 entre linhas; cursor antes da segunda fala; função A−0,32, arrasto A+0,16 até A+0,82, publicar +0,38 após arrasto, confirmação +0,52 após publicar; bloqueio e aviso seguem a terceira fala |
| c07 | 29,5101–35,4121 | **mesmo telefone e lista**, candidatos ini−0,05; escolha a 62% da primeira fala +0,1; check-in segunda fala−0,30, caminhada +0,35; Sim até end−1; lista sai end−0,70, telefone encolhe end−0,62, vira laranja end−0,42 e ponto do mapa end−0,40 |
| c08 | 35,4121–43,2815 | mapa já começa a desenhar ini−0,55 durante 0,90 s; raio15 `g(f1.ini+0,15,2)`; câmera 2,6× em `g(f2.ini−0,25,2)` com cam; raio200 +0,55, caminhada +0,60; saída end−0,30 |
| c09 | 43,2815–46,2325 | ponto grafite ini−0,12, expande 3000×3000 em ini−0,04 com soft; tema ini+0,06; palavras; saída end−0,30. STORYBOARD chama de corte seco, mas a fonte faz expansão: preservar a evidência, não presumir descontinuidade |
| c10 | 46,2325–53,1182 | janela entra ini−0,15; dois slots numéricos usam count e defasagem 0,09 s/dígito; saída end−0,25 |
| c11 | 53,1182–57,0529 | grade nasce em onda radial, alguns pontos crescem após 1 s; frase em duas partes; saída end−0,28 |
| c12 | 57,0529–61,9712 | barras em 25% / 60% da fala, segmentos P/8; cursor escolhe; saída end−0,45; ponto encolhe end−0,42 e parte end−0,20 |
| c13 | 61,9712–66,3977 | nós em 22% / 62% da fala; ponto entra no check, zera tamanho A−0,02, muda posição invisível A+0,20, reaparece B−0,55; linhas guardam 12 px de folga; saída end−0,42 |
| c14 | 66,3977–69,3487 | moeda cresce ini−0,12; giro ini+0,20 com soft; rótulos em 45% da fala; encolhe 0,30 s antes de c16; saída end−0,20 |
| c16 | 69,3487–76,7262 | letras defasadas 0,13 s, traço em 0,62 s e fade em 0,30 s; pouso f1.ini+0,05; saída total−1,70, letras a cada 0,08 s saem inteiras em 0,50 s; ponto some depois (+0,75), deixando papel limpo |

### Continuidade e regras que preservam o piso

O ponto é **um único DOM `#dot`**, com trilhas globais de posição, tamanho, raio e cor: ele não nasce de novo no corte. c03→c04 conserva a fileira; c05→c06 conserva a transformação do ponto em chassi; c06→c07 conserva chassi, tela, ilha e lista (`fluxo` único); c07→c08 conserva o ponto no local (948,575); c08→c09 amplia o mesmo ponto; c09–c11 conservam o escuro; c12 devolve ao claro; c13 esconde o ponto intencionalmente dentro do check; c14→c16 conserva o ponto até o i. Nem todo ponto laranja visível é o `#dot`: mapa e grade têm marcadores próprios.

Cada raiz fica habilitada de ini−1,0 a end+0,9; isso permite sobreposição temporal das entradas/saídas, mas não prova continuidade visual por si só. A câmera é global; HUD fica fora dela. Não recriar o estado de elementos persistentes no início de um bloco. Na produção futura, reservar ≥12 quadros nas emendas (D3), medidos na taxa de saída, e registrar qualquer corte seco novo.

Regras verificáveis da fonte: textos entram antes de assentarem; ação tem preparação, execução e confirmação; contador lento não herda ui; rostos só entram depois dos anéis; linhas deixam vão para o ponto; fileira converge sem empilhar; a saída das letras opera no grupo completo. Julgamento editorial: essas relações tornam o percurso compreensível e dão hierarquia; não atribuir a nota 8/10 a uma fórmula automática. Pausas longas devem ser vistas no contexto, não apagadas só porque os pixels pararam.

## 21. Proposta de exibição do aparelho — somente estudo para aprovação

**Problema medido na v4:** chassi 380×780, centro (660,480), caixa (470,90)–(850,870): **72,22%** da altura. Tela 352×752 em (484,104). Lista/realce ocupa x≈992–1792 (800 px); dados de candidato têm 19 px, campos principais 24 px e cabeçalho do aviso 14 px. Medição da fonte e conferência no MP4 a 25,400 s. c05 é a transformação; c06–c07 têm tela; c08 é mapa, não telefone.

**Tratamento recomendado [H], três estados do mesmo passo, sem cena nova:**

1. **Apresentar:** chassi a **1,10× = 418×858 px**, centro (980,454), topo25/base883; tela 387,2×827,2. Proporção **79,44%** do quadro. Faixa y≥890 livre. Retirar a lista completa durante o foco; um único passo à esquerda em x260–690, número 01 e título curto herdado. Progresso 01/04 com 4 marcas, em vez de 4 chamadas competindo. Tela e textos continuam os da v4.
2. **Ler/agir:** aproximar a tela dentro de uma janela fixa **620×820 px em (760,40)**, recortada com cantos do aparelho; conteúdo a **1,65×**. Dados 24→39,6 px, rótulos 15→24,75 px; para o passo de candidatos, 19→31,35 px. Recorte deliberado do contexto superior/inferior conforme o alvo; não prometer aparelho inteiro a essa escala. Cursor, ilha e tela usam a mesma matriz. O estado anterior mostra o corpo completo para manter a identidade de aparelho. Campo de atenção = função/horário.
3. **Confirmar:** mesma janela e escala, foco vertical acompanha o botão Publicar; contexto residual não disputa com a confirmação. Voltar ao corpo inteiro antes de devolver ao ponto/mapa, preservando os alvos de c07.

**Zoom e parallax [H]:** usar `cam` da v4, sem nova curva. Em 0,6 s a resposta cam chega só a ~86,4% do alvo (não é assentamento completo); reservar **~1,1 s** para chegar perto do repouso, ajustando depois à voz aprovada. Pan de leitura com `soft`. Movimento diferencial horizontal máximo **18 px**: fundo 0,35×, chassi 0,80×, tela 1,00× e cursor 1,00× (cursor precisa continuar tocando o botão); rótulo do passo 0,20×. Tela dentro do recorte, sem mover o cursor independentemente do alvo. Lista completa só reaparece fora do foco se a leitura precisar; não voltar por rotina.

Alternativas consideradas [H]: só ampliar tudo a 1,10× preserva o aparelho inteiro, mas deixa 19 px em 20,9 px (ganho insuficiente); ampliar tudo a 1,65× invade a legenda. O tratamento em dois enquadramentos conserva o objeto e permite ler a ação. Os três PNGs comparativos serão **propostas estáticas**, não evidência de motion aprovado. Arquivos em `motor/cache/revisao-v4-v5/proposta-01.png` a `03.png`, v4 à esquerda, estudo à direita, com o mesmo instante/estado da ação. Não alterar `motor/filme.html` nesta tarefa.

## 22. Especificação da revisão D2 (antes da implementação)

`motor/analisar_video.py VIDEO --tempos REGUA --saida PASTA [--html FONTE] [--contrato JSON]` lê o MP4 real; não gera voz nem monta filme. Dependências do modo raster: ffmpeg/ffprobe, numpy, Pillow e OpenCV; modo fonte: Playwright e Chromium já locais. Ambiente isolado de revisão em cache; não instalar no venv compartilhado.

Entregas: contatos paginados **12 fps por cena**, imagens dos cortes/emendas em **±0,5 s** (incluindo o último/primeiro quadro efetivo), clipes de revisão por cena e por corte; `achados.json` com tempo, intervalo, tipo, evidência e grau de confiança; métricas por cena e parâmetros explícitos. Análise raster a **60 fps** para não esconder flash entre amostras de 12 fps. Resolução reduzida para métricas, frames de evidência saem do vídeo. Pausas sem expectativa declarada são `pausa_a_revisar`, não “travada confirmada”.

Detectores iniciais, iguais nas duas versões: baixa diferença por ≥0,60 s (pausa); diferença de luminância com retorno no quadro seguinte (cintilação); mudança isolada de grande área e/ou deslocamento de features (salto suspeito). Cortes conhecidos são anotados, não descartados. Semântica opcional da fonte: amostrar retângulos de texto com recorte e opacidade herdada, testar interseção entre textos sem relação de ancestralidade; acompanhar `#dot`, tela e câmera. Contrato explícito permite exigir presença/movimento numa janela e detectar nascimento/sumiço fora dela. Sem contrato, registrar lacuna de cobertura sem inventar horário “correto”. DOM é evidência auxiliar: duração compatível e fonte registrada, mas não se presume identidade entre fonte e MP4.

Validação: testes com vídeo/estados controlados que incluam pausa intencional, travada em janela de movimento, flash, salto, ausência/presença indevida e colisão de texto; calibração nos dois MP4 reais com os mesmos limiares. Não ajustar limiar para fazer a v4 passar. A v4 deve ter poucos **defeitos confirmados**, mas suas pausas e transformações continuam no relatório. A ferramenta não mede qualidade artística, não detecta emendas de voz e não aprova o vídeo. Resultado comparativo e limites reais entram aqui após a execução.

**Contrato para continuidade entre aparelhos (complemento antes do código):** além da presença conservadora dentro de uma cena, a calibração deve exigir o corpo do aparelho atravessando c06→c07 (v4) e v06→v07 (v5). Selector pode reunir as duas instâncias por vírgula; considerar a instância visível de maior opacidade efetiva. `opacidade_min: 0.5` significa exigir pelo menos metade da opacidade no corte, não declarar elemento invisível abaixo disso. A ausência nesse contrato é perda de continuidade/legibilidade, diferente de um sumiço literal. Comparar janela v4 29,25–29,75 s à v5 42,40–42,90 s, segundo D3. O limite deve constar da evidência e não mudar os limiares raster.

## 23. Calibração D2, evidências e entrega — 26/10/2026

**Execução com os mesmos limiares raster nas duas versões.** Relatórios completos em `motor/cache/revisao-v4-v5/v4/achados.json` e `v5/achados.json`; métricas nativas a 60 fps em `metricas.json`; geometria a 12 fps em `geometria.json`. Contratos conservadores e o contrato de continuidade estão em `contrato-v4.json` / `contrato-v5.json` na pasta de revisão. Artefatos não entram no git.

| Medida | V4 de referência | V5 reprovada |
|---|---:|---:|
| Janela de imagem medida | 76,733333 s | 108,200000 s |
| Pausas ≥0,60 s com baixa alteração | 21 intervalos / 27,465 s (~35,8%) | 30 intervalos / 62,299 s (~57,6%) |
| Saltos suspeitos raster (registros, não episódios) | 4 | 9 |
| Cintilação global de um quadro | 0 | 0 |
| Interseção texto↔texto visível na fonte | 0 | 0 |
| Continuidade do aparelho pelo contrato ≥50% opacidade | nenhuma quebra na janela 29,25–29,75 | quebra amostrada 42,500–42,667 s |
| Páginas de faixas / frames extraídos | 32 / 926 | 44 / 1303 |
| Cortes com PNG e clipe de ±0,5 s | 14 | 13 |
| Clipes integrais de cenas, com margens | 15 | 14 |

**Interpretação, não placar de aprovação:** a v4 fica quase limpa de defeitos objetivos neste escopo. Seus 4 alertas de salto estão em **43,317 / 43,333 / 43,350 / 43,500 s**, todos na expansão deliberada do ponto para o fundo escuro. As 21 pausas são repousos para leitura/voz, não 21 travadas comprovadas. Zero no detector de flash significa só ausência do padrão global A–B–A com os limiares declarados, não ausência de toda cintilação local. “Texto visível” usa clipping, opacidade herdada e teste de oclusão por superfícies opacas; não certifica toda colisão possível.

### Achados por instante e comparação editorial

| Instante | Evidência | Avaliação |
|---|---|---|
| v4 27,633–29,233; 30,400–31,400 | aparelho em repouso depois de aviso/escolha | na v4 a ação prepara, acontece e confirma; manter esses respiros |
| v5 38,633–40,933 | 2,300 s de baixa alteração na cena v06 | mais tempo sustentando o mesmo estado; pista de perda de ritmo, não erro de render |
| **v5 42,500–42,667**, corte 42,661521 | contrato encontra opacidade do aparelho abaixo de 0,5; em 42,583 há ausência até no limiar de 0,05; PNG do corte mostra apagamento e reapresentação | **quebra de continuidade visível em comparação à v4**. A v4 mantém o mesmo chassi em 29,5101; a v5 tem telefones por cena sob `base(t,s)` com fade de raiz. Não atribuir o sumiço à compressão |
| v5 45,750–47,217; 47,483–49,033; 49,150–50,133 | v07 soma 4,000 s de baixa alteração (47,1% da cena), contra 1,000 s (16,9%) na c07 v4 | check-in fica sustentado por mais tempo, com pouca evolução visual; a v4 encaminha a avaliação e depois transforma o telefone no ponto |
| v5 32,400–35,883 | 3,483 s de repouso na virada; v05 soma 5,150 s (77,4%) | revisar coreografia quando o texto estiver aprovado; não esticar o estado |
| v5 70,933–75,683 | repouso de 4,750 s; v10 soma 7,533 s (83,5%) | prioridade de ritmo para a fase de prova, sem montar bloco agora |
| v5 79,333–84,167 | repouso de 4,833 s após os contadores | mesma recomendação de revisão, não substituir as molas v4 |
| v5 11,150–11,183 e 20,150–20,183 | 6 dos 9 alertas de salto estão nas trocas claro/escuro; outros: 0,333, 51,167 e 84,450 | são pistas de mudança/associação de features, não prova de teletransporte. O de 0,333 coincide com entrada da pílula; 51,167 e 84,450 ficam perto de cortes. Não usar a contagem 9×4 como nota de motion |

O `achados.json` da v5 contém **dois registros de sumiço referentes ao mesmo episódio**: contrato de continuidade (42,500–42,667) e estado isolado A–B–A (42,583). Não são duas quebras diferentes. Nenhum nascimento fora da janela foi identificado nos contratos limitados desta calibração; a detecção desse caso foi exercitada nos testes controlados. Não foi fornecido um contrato de movimento obrigatório para cada elemento, portanto os repousos reais não foram promovidos a “travadas”.

**Conferência da fonte auxiliar:** um frame em 55% de cada cena foi comparado ao MP4. MAD em cinza 480×270: v4 **0,835–1,850**, v5 **2,071–2,780** em escala 0–255. Isso apoia o alinhamento, mas não prova identidade ao longo de toda a cena. A perda de continuidade acima também foi conferida nos quadros do MP4, não inferida só do DOM. Não foi feita avaliação de áudio nesta tarefa.

### Onde revisar

- Propostas finais: `motor/cache/revisao-v4-v5/proposta-01.png` (**24,500 s**, corpo inteiro), `proposta-02.png` (**25,400 s**, leitura), `proposta-03.png` (**26,500 s**, confirmação). Cada arquivo tem **3840×1160**, comparação 1920×1080 de cada lado mais cabeçalho; versões `-antes.png` e `-depois.png` também disponíveis. Todos são estados da v4 transformados para estudo; o motor de produção está intacto.
- Medidas verificadas do estudo: corpo inteiro **418×858 px em (771,25)**; foco com janela **(760,40)–(1380,860)** e tela a 1,65×. Pan do grupo, relativo à janela: **(−777,5; −235)** na leitura e **(−777,5; −580)** na confirmação, evitando cortar palavras/ação. Cursor usa a mesma transformação. Parallax e zoom em movimento continuam **propostos**, não validados pelos PNGs.
- Comparação dos mesmos instantes relativos de c06/v06 e c07/v07: `comparacao-aparelho-publicar-01.png` a `03.png` e `comparacao-aparelho-escolher-01.png` a `03.png` (24 pares no total). Percentuais de progresso são iguais; cada lado informa seu tempo absoluto, arredondado ao frame real. Narrativas não são idênticas, por isso comparar também preparação/ação/repouso, sem supor que 55% sempre contenha o mesmo gesto.
- Faixas completas: `v4/faixas/` e `v5/faixas/`, **12 fps**, até 36 imagens/página. `faixas.json` registra o PTS real de cada imagem. A amostragem usa frames existentes, sem a seleção no meio do intervalo feita pelo filtro `fps`.
- Cortes: `v4/cortes/029.510100.png` / `.mp4` versus `v5/cortes/042.661521.png` / `.mp4`; demais cortes nas mesmas pastas. O manifesto `cortes.json` registra amostras em ±0,5 s e os frames imediatamente antes/depois. `--emendas` permite acrescentar emendas de bloco quando existirem.
- Vídeos por cena: `v4/clipes/` e `v5/clipes/`, na cadência original e sem áudio, com 0,5 s de margem de cada lado (≥12 frames a 60 fps, salvo extremos do filme). São material de revisão, não o futuro render de blocos.

### Reprodução, testes e limites

Ambiente isolado desta tarefa: `motor/cache/qa-venv` (numpy, Pillow, OpenCV e Playwright); Chromium em `motor/browsers`, ffmpeg/ffprobe no PATH. Não modificado o venv compartilhado. Preparação em outra máquina: criar um venv de revisão e instalar `numpy pillow opencv-python-headless playwright`; apontar `PLAYWRIGHT_BROWSERS_PATH` para o Chromium local. Para a v4, guardar a fonte de `git show 4efa75a:motor/filme.html` em cache e servir os assets da raiz do repo.

```sh
motor/cache/qa-venv/bin/python -m unittest discover -s motor/tests -v
motor/cache/qa-venv/bin/python motor/analisar_video.py \
  /Users/fabriciotosta/Downloads/frila-pitch-pt.mp4 \
  --tempos docs/v4/tempos-pt.json \
  --html motor/cache/revisao-v4-v5/filme-v4.html \
  --contrato motor/cache/revisao-v4-v5/contrato-v4.json \
  --saida motor/cache/revisao-v4-v5/v4
motor/cache/qa-venv/bin/python motor/analisar_video.py \
  /Users/fabriciotosta/dev/video-frila/referencias/v5-reprovada/frila-pitch-pt.mp4 \
  --tempos /Users/fabriciotosta/dev/video-frila/referencias/v5-reprovada/tempos-pt.json \
  --html /Users/fabriciotosta/dev/video-frila/referencias/v5-reprovada/filme-v5.html \
  --contrato motor/cache/revisao-v4-v5/contrato-v5.json \
  --saida motor/cache/revisao-v4-v5/v5
```

Testes incluem flash de **um frame em MP4 real a 60 fps**, salto, repouso versus movimento exigido, presença/ausência fora da janela, opacidade de continuidade, escolha entre instâncias do mesmo objeto, colisão de texto, texto sob fundo opaco e precisão dos frames nas faixas/cortes. As falhas iniciais e correções não mudaram os limiares para limpar a v4: corrigidos o teste de oclusão e os rótulos de PTS (não são ajustes de sensibilidade).

Limites: detector de texto é geométrico texto↔texto, exclui odômetros sob recorte; o teste de superfície opaca amostra três pontos por trecho e não substitui conferência visual de oclusões parciais/SVG/canvas. Raster usa quadro reduzido (480×270), não garante capturar falha pequena/local. Contratos são necessários para atribuir horário/expectativa. Sem HTML, a cobertura semântica é explicitamente ausente. Sem artefatos (`--sem-artefatos`), a execução não satisfaz sozinha D2. Não há aprovação de bloco, novo filme ou validação de motion do estudo; o Fabrício decide após vídeo. Próximo passo depende da aprovação destes estudos e do roteiro pelo Fabrício.

**Revisão independente do instrumento (antes das correções):** identificados três casos a cobrir: aparelho totalmente encoberto não pode satisfazer presença visível; janelas exclusivas repetidas do mesmo id precisam formar uma união de horários permitidos; régua precisa cobrir o vídeo todo, com cenas ordenadas, duração positiva e ids únicos (tolerância de um frame entre limites arredondados). Presença considera também pontos junto à borda para não confundir o chassi visível com sua tela opaca. São correções de cobertura/contrato, sem afrouxar limiares raster. Reexecutar testes e calibração após a correção.

**Fechamento da revisão do código:** os três casos foram corrigidos e ganharam testes. A rechecagem encontrou ainda um override de selector reservado mascarado pelo default; corrigido com agrupamento separado dos selectors declarados e teste em Chromium. A suíte final tem **16 testes**. A calibração mantém os mesmos limiares e resultados da tabela; a presença considera oclusão também nos elementos acompanhados.

Índice local para revisão dos vídeos e acesso às evidências: `motor/cache/revisao-v4-v5/index.html` (191 links locais conferidos). Verificação final: 16/16 testes, recompilação Python, leitura dos dois MP4 e seus relatórios, 27 cortes com PTS na grade real e 29 clipes a 60 fps. Rechecagem independente do código confirmou as quatro correções. Isso valida o instrumento e a integridade dos artefatos; aprovação editorial continua pendente.

## 24. Estudo corrigido — câmera sobre o conjunto, D6/D7/D8

**Direção autorizada no briefing de 26/10/2026; aprovação visual pendente do Fabrício.** Base `main 41b406b` (PRs #12 e #13), branch `feat/mockup-aparelho`. Este estudo isolado substitui os ensaios rejeitados de §§21/23 e o zoom interno anterior. Não monta nenhuma cena de bloco. Preserva a geometria, tipografia, formulário, botão, confirmação e curva `eio` da fonte v4 `4efa75a:motor/filme.html`; não reescreve uma cena.

### Câmera e planos (especificação antes do código)

- **Objeto único:** chassi `#dot`, tela `#scr`, ilha e todos os filhos da UI recebem uma única transformação ancestral uniforme. Sem wrapper de zoom interno, pan, rolagem ou máscara adicional na tela. O botão mantém apenas a pressão intrínseca da v4 e seus estados nativos. Cursor `#cur` oculto por CSS `!important`, inclusive após `seek`; não é reposicionado nem substituído por marcador.
- **Plano principal:** objeto v4 de 380×780 a1,10×, caixa inicial **(891,55), 418×858**, centro **(1100,484)**. Câmera sobre esse conjunto: fator **1→1,10→1** (escala total1,10→1,21→1,10). Pan máximo **(−14,+6) px**. Pico: caixa **(856,1;18,1), 459,8×943,8**, centro **(1086,490)**, altura87,39% do quadro. Ilha, moldura, campos e botão crescem juntos. Botão24→29,04 px no pico; ganho limitado deliberadamente pela preservação das bordas. Não prometer leitura de tela inteira a distância sem avaliação do Fabrício.
- **Plano lento:** fundo areia v4 plano, sem textura ou elemento novo (movê-lo não cria sinal visual); rótulo à esquerda em(260,350), largura420, acompanha **0,35×** o pan e **0,35×** a variação de escala. Não esmaece nem compete com o aparelho.
- **Plano de ação:** contador **01/04** e quatro traços do passo, em(260,235), acompanham **1,10×** o pan e a variação de escala, ligeiramente mais rápidos que o conjunto. É sinalização externa já solicitada, não um elemento novo do app. **Nenhum filho dentro do aparelho recebe parallax próprio**: deslocar o botão independentemente violaria D7. A profundidade fica entre rótulo, aparelho e sinalização de ação, sem deformar a UI.
- **Legenda:** mesma frase aprovada de v06; fixa ao quadro, bottom28px, abaixo do limite inferior do aparelho961,9px. Nenhuma anotação de revisão dentro das imagens propostas.
- **Curva:** `eio(u)=4u³` até0,5 e `1−(−2u+2)³/2` depois; mesma cúbica da v4, sem quique, velocidades nulas nos extremos. Apresentação0–0,60s; aproximação0,60–1,30s; ação1,30–2,00s; retorno2,00–2,90s; leitura final2,90–3,60s. A duração é do estudo de enquadramento, não ajuste de cena à voz. O tempo longo de câmera segue a direção cinematográfica v4, não o limite de transição de controle de uma UI interativa.

### Demonstração sem cursor

O formulário entra no estudo já preenchido (estado v4 em25,55s). A ação é a pressão do próprio botão **Publicar**, seu carregamento e a confirmação **Vaga publicada**, com cor e check nativos. Mapa temporal: estudo0/0,60→v425,55;1,30→25,792 (pressão);1,90→26,312 (início da confirmação);2,10/3,60→26,55 (confirmação assentada). A câmera não provoca nenhuma alteração interna de layout. Não se demonstra preenchimento por ponteiro, nem se inventa toque, texto ou tela. A confirmação começa a aparecer por volta de1,92s e assenta até2,10s durante o começo do retorno; inspecionar a passagem inteira.

### Continuidade futura v06→v07

O mesmo nó do chassi e seu grupo de câmera ficam na camada persistente do fluxo, fora do fade das raízes de cena, como `fluxo` em c06/c07 da v4. O corte troca apenas o estado da interface recortada pela tela existente. Nas margens de **pelo menos12frames de cada lado**, a câmera estará no enquadramento geral, mesma caixa inicial acima, opacidade efetiva1, mesmo centro, cor, raio e dimensões; posição e velocidade são compartilhadas. Não apagar, duplicar, desmontar ou recriar o aparelho. Nenhum corte seco de câmera autorizado.

Referência obrigatória: v4 **29,5101s**, último/primeiro frame do corte e ±0,5s. Antirreferência: desaparecimento v5 **42,500–42,667s**. Este clipe não implementa nem prova a futura transição; isso será auditado quando o blocoB puder ser montado (D5).

### D6 — origem de cada string

Inventário literal arquivado em **docs/v4/COPIA-NOVA-VAGA.md**: transcrição verificável da tela v4 e da lista do lado “antes”; não alega captura de app atual. Os campos da tela foram conferidos em `TX.pt.form` da fonte v4. O manifesto deve registrar origem por string normalizada e falhar para texto não inventariado.

| Strings | Origem |
|---|---|
| `Você publica a vaga.` | `roteiro.json`, v06-solucao1.pt.legenda, primeira frase |
| `Exemplo` | `roteiro.json`, v07-solucao2.tela |
| `01/04` | formato pedido pelo Fabrício no briefing; quatro passos v4; registrado no inventário |
| `Contratante`, `Nova vaga`, `Função`, `Garçom`, `Horário`, `Endereço`, `Plano Piloto`, `Valor`, `R$ 120`, `Publicar`, `Vaga publicada` | `docs/v4/COPIA-NOVA-VAGA.md`, transcrição `TX.pt.form.role/t/f1/v1/f2/f3/v3/f4/v4/b/b2` |
| `19h às 23h` (nós `19h às ` + `23` + `h`) | mesmo inventário, composição `TX.pt.form.v2` + `#hora=23` no intervalo v425,55–26,55s |
| `4 passos`, `01`, `02`, `03`, `04` | apenas lado antes; inventário, `TX.pt.passos` e `build()` v4 |
| `Contratante publica a vaga`, `função, horário, endereço, valor`, `Profissional recebe o aviso`, `até 15 km`, `Contratante escolhe quem vai`, `vê o histórico`, `Os dois lados conferem`, `check-in, sim ou não` | apenas lado antes; inventário, `TX.pt.steps[0..3]` |
| `O contratante publica a vaga.` | apenas legenda antes; `docs/v4/roteiro-v4.json`, c06-passos-a.pt.legenda |

### Evidências e validação previstas

Pasta substituída: `motor/cache/mockup-aparelho-d6-d7/` (fora do git). Clipe **zoom-continuo.mp4**,3,60s,216frames,1920×1080,60fps,sem áudio; três PNGs comparativos3840×1080 em0,20/1,30/3,40s (v4 original à esquerda, proposta à direita; pico ampliado no segundo); manifesto com strings, caixas, escala comum e geometria local de cada frame; fonte HTML reproduzível com `boot/seek` para o analisador. Os estudos antigos não continuam publicados como proposta vigente. Os frames da v4 preservam sua evidência original, inclusive o cursor histórico apenas no lado antes.

Revisão: analisar o MP4 raster a60fps, fonte/colisões/presença a12fps, faixas12fps e janelas±0,5s nas fronteiras de câmera0,60/1,30/2,00/2,90s; sem corte entre cenas. Contrato exige chassi/tela visíveis no clipe inteiro e movimento nas rampas. Checagem adicional por frame exige escala comum, bordas dentro do quadro, botão/confirmação dentro da tela e geometria interna constante (exceto pressão nativa). Testes de regressão devem falhar para chassi fixo/UI ampliada e cursor visível. Validar `seek` reversível.

Reprodução: `.venv/bin/python motor/fotos.py --estudo-aparelho`, depois `.venv/bin/python motor/analisar_video.py motor/cache/mockup-aparelho-d6-d7/zoom-continuo.mp4 --tempos motor/cache/mockup-aparelho-d6-d7/tempos-estudo.json --html motor/cache/mockup-aparelho-d6-d7/estudo.html --contrato motor/cache/mockup-aparelho-d6-d7/contrato.json --emendas 0.6 1.3 2 2.9 --saida motor/cache/mockup-aparelho-d6-d7/analise`, seguido de `./scripts/verificar.sh` antes de commit e handoff.

Recall: detector raster recuperou o flash artificial de um frame a60fps e o caso de salto dos testes; contrato de presença recuperou o mergulho conhecido da v5 em42,500–42,667s (§23). Isso não mede recall geral (amostra pequena); não garante ausência de defeitos locais ou qualidade artística. Alertas heurísticos informam; Fabrício aprova após vídeo.

### Resultado do estudo corrigido (26/10/2026)

Clipe e três comparativos entregues em `motor/cache/mockup-aparelho-d6-d7/`: `zoom-continuo.mp4`, `01-apresentar.png`, `02-acao.png` (conjunto ampliado) e `03-retorno.png`; índice em `index.html`. PNGs de 3840×1080, tempos de estudo 0,20 / 1,30 / 3,40 s; referências reais v4 25,550 / 25,800 / 26,550 s. `ffprobe`: 216 frames, 3,600 s, 1920×1080, 60/1 fps, uma única stream de vídeo. Os estudos reprovados `revisao-v4-v5/proposta-*.png` e seu gerador foram retirados do cache; o índice anterior aponta para o novo estudo. Referências originais v4/v5 preservadas para auditoria.

**Comparação com a v4:** moldura, ilha, formulário, pressão, spinner e confirmação mantidos; aparelho antes com 380×780 px, proposta geral com 418×858 px e pico com 459,8×943,8 px. A lista grande foi substituída pelo progresso solicitado. Na proposta, nenhum cursor em qualquer um dos 216 frames. O lado antes dos comparativos é a v4 original e conserva o cursor histórico como evidência. Ganho de leitura medido no texto de botão: 24→26,4 px no geral e 29,04 px no pico. O parallax é contido: pan do rótulo (−4,9;+2,1) px, do aparelho (−14;+6) e do indicador (−15,4;+6,6), com escalas respectivas 1,035 / 1,10 / 1,11. Não é ganho de leitura por rolagem interna.

**Revisão temporal:** conferidas as 44 amostras do MP4 a 12 fps, as quatro janelas de ±0,5 s e a geometria dos 216 frames. Aproximação e retorno usam a mesma curva, sem quique; bordas não nascem/somem, formulário não desliza em relação à ilha e a confirmação fica dentro da tela. O passo não atravessa o aparelho ou a legenda. A reserva superior mínima no pico é 18,1 px; é pequena, porém preserva o contorno. Parallax discreto e legibilidade à distância continuam sujeitos ao olhar do Fabrício.

| Instante do estudo | Achado e interpretação |
|---|---|
| 0,000–0,600 s | Alerta de pausa; apresentação estática deliberada, já prevista. Sem travada em janela de movimento. |
| 0,600–1,300 s | Câmera aproxima o conjunto; caixa cresce até (856,1;18,1), 459,8×943,8. Não há escala/pan próprio de tela. |
| 1,300–1,500 s | Pressão nativa de Publicar e começo do carregamento; nenhum ponteiro. |
| 1,917–2,100 s | Vaga publicada aparece e assenta com check e cor nativos. Confirmação inteira, sem corte lateral. |
| 2,000–2,900 s | Retorno contínuo; câmera, chassi, ilha e campos voltam juntos ao enquadramento geral. |
| 2,900–3,583 s | Alerta de pausa; leitura final deliberada. Mesmo chassi inicial (891,55), 418×858, opacidade 1. |

**Analisador:** `analise/achados.json` contém somente os dois alertas de pausa acima. Zero alertas de salto, sumiço, nascimento, travada contratual, cintilação e sobreposição de texto. `analise/geometria.json` registra presença de chassi/tela a 12 fps, opacidade mínima 0,999; nenhuma ausência. Fonte auxiliar sem erro de página e MAD 1,196 (cinza 480×270) contra MP4 no instante 1,980 s; essa comparação é parcial. Para conferir a presença no próprio MP4 em todos os frames, `analise/chassi-raster.json` mede a componente conexa escura da moldura em resolução nativa: 216/216 presentes, erro máximo contra a caixa prevista **1,742 px**, tolerância declarada 2 px para rasterização/compressão. Não foi alterado nenhum limiar do analisador.

**Evidências de movimento:** `analise/faixas/estudo-01.png` e `estudo-02.png`; `analise/cortes/000.600000.png`, `001.300000.png`, `002.000000.png`, `002.900000.png` e respectivos MP4. Esses nomes “cortes” são do gerador; os quatro instantes são fronteiras da câmera, sem corte de cena. `manifesto.json` contém origens por string, estados e caixas por frame; delta máximo de fator entre frames **0,006809**. Todas as strings observadas têm origem no inventário acima; nenhuma cópia editorial nova.

**Falha encontrada e corrigida na validação:** a primeira análise com fonte falhou porque o wrapper chamava `seek` antes de aguardar o `boot` assíncrono v4. Corrigido com `await`; o teste agora inicializa o HTML exportado com uma régua de estudo, exercita o mesmo caminho usado pelo analisador e percorre os 216 estados. Regressões cobrem câmera comum (incluindo ilha), posição normalizada dos campos, botão/confirmação dentro da tela, cursor ausente e seek reversível. O teste contra o código rejeitado falhou por cursor visível e limite de zoom antigo, antes da correção. Não foi necessário mexer no filme de produção.

**Verificação:** `./scripts/verificar.sh` passou no `.venv` compartilhado: 13 testes gerais, 19 de motor e 27 de áudio/emendas/blocos, **59 ao todo**. São verificações técnicas, sem aprovação artística implícita. Não foi montado bloco, gerado áudio nem implementada a passagem v06→v07; a especificação de continuidade acima segue pendente de implementação na fase autorizada. Recall continua limitado aos casos conhecidos, sem estimativa geral. Próximo passo: auditoria independente do Maestro e avaliação do vídeo pelo Fabrício.

## 25. Piloto de imagem do Bloco A — direção antes do código (26/10/2026)

**Escopo autorizado:** quatro cenas de imagem, sem áudio, no branch `feat/bloco-a-imagem`, a partir da main. Não altera o estudo aprovado do aparelho/PR #16, nem monta B/C/D. Voz A aprovada, tomada `b92c749b…`, duração fixa do WAV **22,894875 s**. A régua oficial `../fvp-audio-blocos/motor/cache/blocos-regua/A.json` usa **zero visual** e `voz_ini=2,459166667 s`: o WAV íntegro termina em 25,354041667 s. Cortes exatos: **6,039166667 / 13,449166667 / 19,399166667 s**, fim nominal **25,575416667 s**. A correção de 10 ms da mensagem do Áudio já estava no JSON. Não se recalcula, corta ou estica a voz. A exceção de ouvido de C não pertence a este piloto.

### Mapa da v4 para as quatro cenas

| Piloto | Base v4 e componentes preservados | Adaptação de coreografia à tomada fixa |
|---|---|---|
| v01 gancho, 0–6,039166667 s | c01: título em duas linhas 116 px, pílula de 600×104, ponto global virando o pingo do `?`, palavras por `wio`, curvas `ui/move/snap` | Pílula já apresenta “Garçom · hoje, 19h” durante “Hoje, 19h.”; sem preço, conforme roteiro. “Faltou gente / no turno” acompanha a segunda frase em 4,579166667–5,759166667 s; tag Exemplo. O trajeto vai por baixo da frase antes de subir na coluna do `?`, como na v4. |
| v02 dor 1, 6,039166667–13,449166667 s | c04: 9 em 10 a 210 px, odômetro de unidades, dez círculos com o primeiro ocupado pelo mesmo ponto, nove laranja e um grafite; fonte Abrasel | Mantém o gesto de preenchimento em passos P/4, sem alongar a mola. Subtítulo se revela em duas partes durante “empresários de bares e restaurantes” e “acham difícil contratar”. Fileira converge por igual na saída, sem empilhar; ponto segue. Não esticar a contagem até o fim da fala. |
| v03 dor 2, 13,449166667–19,399166667 s | c10: janela 1100×560 em (410,190), barra de endereço, divisor, slots 1,5 / 533, rótulos e rodapé de declaração; c09: “Cadastro / não é turno.” a 160 px, entrada por palavras | A primeira frase recebe a janela e os dois contadores com defasagem curta; a janela sai antes de 17,959166667 s. A segunda frase recebe a tese, sem sobrepor seus textos à janela. O fundo muda suavemente para grafite pela trilha de tema; o mesmo ponto fica laranja e visível na lateral. A expansão preta que ocupava todo o quadro em c09 é adaptada para preservar esse elo na nova ordem. |
| v04 dor 3, 19,399166667–25,575416667 s | c03: título de rotatividade, odômetro 73,49% de 236 px, subtítulo “cerca de 7 em cada 10”, fileira original com sete substituições, fonte Abrasel | Retorno ao papel com o ponto contínuo; contador com `count`, sete trocas em P/4, período “dez/2024 a nov/2025”. A pílula da vaga reaparece após as trocas, enquanto a fileira sai, preparando o estado de entrada de B. Não reescrever como cartões novos: retoma a fileira documentada da v4 e o componente do gancho. |

Isto reaproveita composição, componentes e curvas da v4; não é reescrita de quatro cenas. A combinação de c10/c09 e a nova ordem exigem gatilhos próprios, porque a voz aprovada já chegou ao zero local. Os gestos continuam curtos e separados por leitura e novas ações sem prolongar suas curvas. Câmera **fixa** nas quatro cenas, como nas respectivas composições v4; nenhuma deriva de câmera para preencher tempo. Se algum intervalo parecer parado demais na sequência, ajustar preparação/revelação/saída e registrar, não retimar a voz.

### Continuidade, margem e D9

Um único nó `#dot`, dentro de `#world`, acumula alvos nas trilhas globais; nenhuma função de cena o recria. Troca de cena não reseta posição/velocidade. As raízes ficam habilitadas de ini−1,0 a end+0,9, como na v4, e os filhos controlam suas entradas/saídas. Os três cortes são centros de pausas, sem troca seca de enquadramento. O primeiro círculo de v02 é o ponto global; a cópia local sai antes de coincidir com ele. No escuro de v03 o ponto permanece laranja na lateral; na volta a v04 ele liga a composição ao rótulo e depois à vaga.

**Estado de entrega para B:** após 25,575416667 s, papel `#F7F3EE`, câmera identidade, vaga “Garçom · hoje, 19h” em pílula 600×104 centrada em (960,640), ponto laranja 28×28 centrado em (960,760), raio 14 e opacidade 1. O plano termina nesse estado; B deverá começar a partir dele, sem duplicar o objeto. O render inclui **15 quadros de margem final** além do primeiro limite de frame posterior à voz: `ceil(25,575416667×60)+15 = 1550 frames`, **25,833333333 s**. Nenhuma fala adicional é atribuída à margem. Capturar também o estado exato no fim nominal do bloco e as velocidades para o futuro encaixe.

**D9, lido em `git show docs/d9-camera-sem-artefatos` (`ba42ff0`).** No A a câmera não se move: uma matriz identidade no ancestral comum `#world`; ponto, títulos e traços compartilham esse espaço. Sem escala/reposição independente para simular câmera. Movimentos intrínsecos das palavras, contadores e formas preservam as curvas da v4. Render com **deviceScaleFactor 2** (3840×2160), quatro subquadros por quadro de saída, redução **Lanczos** no FFmpeg e saída 1920×1080 a 60 fps. A medida nova de cintilação de borda e calibração v4/v5/aparelho será tarefa separada após o A, conforme adendo do Fabrício para bloco sem movimento de câmera. Até calibrar, informa; não criar veto automático por serrilhado heurístico.

### D6: inventário de cópia

Usar `roteiro.json` para legendas de v02/v03/v04, frases/tela do gancho, tag Exemplo, período da rotatividade. Rótulos históricos da janela eStaff, fontes e subtítulo da rotatividade ficam transcritos em `docs/v4/COPIA-BLOCO-A.md`, com campo da fonte `4efa75a:motor/filme.html` e referência visual. Nenhum título/pergunta inventado da v5 rejeitada entra no piloto. Atribuição de empresa e fonte não é resultado de pesquisa nova: preserva a referência aprovada, sem atualizar números históricos.

| Strings visíveis | Origem |
|---|---|
| Faltou gente / no turno | recortes literais da segunda frase de v01.pt.legenda; componente de c01 |
| Garçom · hoje, 19h; Exemplo | v01.tela |
| ? (forma gráfica) | docs/v4/STORYBOARD.md, c01 |
| 9 em 10 | v02.tela; contagem intermediária é odômetro gráfico |
| empresários de bares e restaurantes / acham difícil contratar | recortes contínuos de v02.pt.legenda |
| Cadastro / não é turno. | segunda frase de v03.pt.legenda; docs/v4, c09 |
| estaff.com.br; eStaff; 1,5; milhão de cadastrados; 533; mil disponíveis | v03.tela e transcrição de c10 em docs/v4/COPIA-BLOCO-A.md |
| Rotatividade em bares e restaurantes · 12 meses; cerca de 7 em cada 10 | transcrição c03 em docs/v4/COPIA-BLOCO-A.md |
| 73,49%; dez/2024 a nov/2025 | v04.tela |
| Fonte: Abrasel, 30/04/2025.; Fonte: Abrasel, via Monitor Mercantil, 09/12/2025.; Números do site estaff.com.br, como a empresa os declara. Acesso em 22/10/2026. | transcrição dos rodapés c04/c03/c10 em docs/v4/COPIA-BLOCO-A.md |
| legendas inferiores | v02/v03/v04.pt.legenda; divididas apenas nos limites de frases/janelas oficiais, sem reescrever |

### Implementação e provas previstas

1. Adicionar modo explícito `render.py pt --bloco A --regua CAMINHO`, com validação de quatro IDs, ausência de lacunas e falas locais, margem final ≥12 frames, saída somente imagem; não criar régua provisória para o filme inteiro e não gerar eventos/áudio fora do cache do bloco.
2. Em `filme.html`, montar somente esses quatro componentes no modo A e compartilhar as funções de molas/odômetros/entrada já existentes. A inicialização não exige v08 nem os blocos seguintes. Testar seek reversível, cópia, ponto no corte e na margem, ausência de cursor e de raízes futuras.
3. Renderizar em cache/bloco-a-imagem com supersampling, analisar MP4 real a 60 fps + geometria/fonte a 12 fps; gerar faixas por cena e janelas ±0,5 s nos três cortes e no limite nominal do bloco. Revisar sequência e sincronismo contra voz aprovada em leitura, sem alterar o bruto.
4. Comparar cada cena com a equivalente v4 em **iguais segundos relativos** para ver curvas/entradas; quando a duração nova exceder a cena v4, registrar essa falta de correspondência sem congelar ou esticar a referência. v03 tem duas bases (c10/c09); comparar cada fase separadamente. Diferenças de roteiro e alinhamento de fala serão explícitas.
5. Rodar `./scripts/verificar.sh`, registrar achados por instante e limitações; rebase final na main antes do commit, sem push. Handoff ao Maestro para auditoria; só Fabrício aprova a imagem e libera B.

**Decisão de aparelho recebida durante o A:** Fabrício pediu em 26/10/2026 retirar o título lateral repetido do aparelho, mantendo 01/04, traços e Exemplo. Será registrada em §24 e implementada/testada ao tocar o aparelho no B ou próximo branch pequeno; não altera o estudo nesta tarefa.

**Preparação e pausas oficiais:** o recuo de cinco tempos recebe a transformação inicial da pílula em 0,24–0,95 s e leitura do cartão antes de “Hoje, 19h.”, que começa em 2,519166667 s. O gesto para o `?` se ancora na segunda frase, sem aumentar a duração das molas. v03 (5,950000 s) e v04 (6,176250 s) são janelas menores que o planejamento antigo do roteiro; a coreografia combina fases curtas, não comprime a fala nem importa durações da v5 rejeitada. O final conserva o estado nominal em toda a margem.

**Correções após a primeira revisão temporal, antes do novo código:** o primeiro MP4 revelou o ponto encoberto pela janela eStaff em 13,50 s (dois registros do detector para um único episódio). Mudar o trajeto: convergir primeiro abaixo da janela, em y=820, seguir para a lateral x=1740 ainda abaixo e só então subir para y=210; nunca atravessar a superfície opaca da janela. Não resolver com alteração de limiar nem com ponto sobre texto. Acrescentar regressão por pilha de pintura na janela inteira da transição.

A primeira abertura sustentava a pílula de 1,733 a 4,350 s. Para ocupar o recuo oficial com narrativa, o mesmo título de duas palavras da v4 mostra primeiro **“Hoje, 19h.”** (v01.pt.legenda, primeira frase) nos tempos dessas palavras e depois **“Faltou gente”**, durante o apagamento da primeira frase. A segunda linha continua “no turno”. Sem novo texto ou novo sistema visual. Em v02, o gesto de contagem começa em f.ini+0,25, como no gatilho original c04, e o subtítulo passa a entrar palavra por palavra conforme os tempos de “empresários de bares e restaurantes”, usando `wio` nativo; as larguras dos spans permanecem no layout. São fases adicionais de coreografia, não cenas esticadas nem câmera em deriva. “turno.” da tese mantém o laranja original; o subtítulo/período da rotatividade saem antes da pílula final para conservar respiro.

**Ajuste final de trajetória, antes do código:** as faixas do segundo MP4 mostraram o ponto cruzando a área do percentual perto de 24 s. O teste texto↔texto não cobre ponto↔número. Alterar o percurso de saída para duas fases: descer pela lateral esquerda x=380, até y=820, em fim−2,10 s; seguir sob a fileira para (960,760) em fim−1,35 s. A moldura do número não é atravessada. Adicionar regressão geométrica ponto↔caixa real do odômetro. Só o último trecho de render (21,583333–25,833333 s) muda; os alvos novos são causais e ficam depois dos outros trechos. Regravar esse trecho a 2×/240 subquadros e concatenar novamente, sem alterar os demais frames. Reexecutar D2 sobre o MP4 inteiro.

### Entrega do piloto A e revisão temporal

Pasta local fora do git: `motor/cache/bloco-a-imagem/`. Clipe **bloco-a-sem-audio.mp4**, 1920×1080, 60/1 fps, **1550 frames / 25,833333333 s**, somente vídeo. Render: Chromium a 3840×2160 por deviceScaleFactor 2, quatro subquadros por frame, redução Lanczos e mistura temporal; nenhuma câmera variável. `index.html` reúne vídeo, faixas, cortes e comparativos. `manifesto-render.json` registra hashes de fonte/régua, formato e margem; `regua-oficial.json` preserva o arquivo recebido do Áudio (hash `d2e99faf…`). SHA do WAV inteiro conferido contra a régua: íntegro, sem alteração.

**Revisão do movimento:** conferidas as **312 amostras a 12 fps**, em 11 páginas, as quatro janelas de ±0,5 s dos cortes/limite de A e os comparativos. As emendas dos seis trabalhadores do render também recebem contatos e clipes de ±0,5 s, em 4,316667 / 8,633333 / 12,950000 / 17,266667 / 21,583333 s; não são cortes criativos. O último trecho foi regravado após o ajuste de trajetória e o MP4 inteiro foi analisado outra vez. A avaliação perceptiva com a mixagem final ainda pertence ao fluxo de aprovação; esta tarefa entrega imagem e confere a sincronia pelos tempos de palavra, sem modificar a voz.

**Achados finais do analisar_video.py:** sete alertas de baixa alteração, seis registros de salto; zero sumiços, nascimentos indevidos, cintilação global, sobreposição de texto ou travada nas janelas de gesto contratadas. Contrato de presença do ponto cobre o bloco inteiro com opacidade mínima 0,999. Contrato de movimento cobre transformação/queda, trocas de palavras e fileiras, contadores, transições e saída final; as janelas de leitura ficam fora da exigência de movimento, conforme a coreografia. Nenhum limiar raster foi alterado.

| Instante local (s) | Achado e leitura editorial |
|---|---|
| 1,733333–2,466667 | Pausa de 0,733 s após a pílula assentar e antes de “Hoje”; recuo visual oficial. |
| 3,433333–4,333333 | Pausa de leitura do horário; voz “19h.” termina em 4,199167. |
| 7,850000–9,116667 | Contagem assentada durante “nove em cada dez”; prepara o subtítulo por palavras. |
| 10,800000–11,700000 | Leitura de “empresários de bares e restaurantes”, antes do verbo. |
| 11,966667–12,783333 | Leitura de “acham difícil contratar”; saída da fileira começa em 12,799167. |
| 13,283333 / 13,316667 / 13,333333 / 13,350000 / 13,366667 | Cinco alertas de salto dentro da mesma transição papel→grafite. Contatos mostram luminância monotônica, sem corte seco; fluxo associa features em meio à mudança global. São pistas heurísticas, não cinco teletransportes. |
| 16,016667–17,450000 | Leitura dos dois números declarados pela empresa; janela sai antes da segunda frase. |
| 19,300000 | Alerta de salto no retorno contínuo grafite→papel; ponto conserva o percurso sob o conteúdo. |
| 22,866667–23,483333 | Leitura do percentual e das sete trocas; saída do ponto pela margem esquerda começa em 23,475417. |
| 24,325417–25,575417 | Pílula da vaga retorna; título, número, legenda e rodapé saem. Ponto termina abaixo da vaga, sem cruzar seu texto. |
| 25,575417–25,833333 | Margem final de 15 frames completos após o primeiro frame posterior ao limite nominal; estado reservado ao início de B. |

**Falhas que a revisão corrigiu:** primeira passagem ocultava o ponto atrás da janela em 13,50 s; o detector registrou dois achados para um único episódio. Regressão por pilha de pintura falhou em 13,4825 s antes da correção. A trajetória agora segue y=820 até a lateral e só então sobe. A segunda passagem cruzava a caixa do odômetro perto de 24 s; regressão geométrica reproduziu a interseção antes da mudança para a margem esquerda. A primeira abertura tinha 2,617 s de leitura contínua; o mesmo componente de título agora apresenta a primeira frase antes da segunda, sem esticar molas. O subtítulo de v02 segue as palavras, em vez de sustentar a linha inteira por toda a enumeração.

**Conferência no raster:** `analise/ponto-raster.json` registra **225/225 frames** com croma laranja nas janelas de ±0,5 s dos três cortes e do fim de A, sem ausência. A primeira tentativa desse controle exigia RGB quase sólido e deu falso negativo em **6,133333 s**: o MP4 mostra o rastro laranja diluído pelo motion blur nativo de quatro subquadros. Inspecionado o frame e corrigido o método para contraste de croma (R−G>25, G−B>8), não o filme nem os limiares de D2; a limitação/método está registrada no JSON. Isso não estima recall geral do rastreador.

**Estado para B:** `estado-fim-A.json`, no tempo exato 25,575416667 s: papel RGB(247,243,238), câmera identidade; ponto RGB(234,90,54), centro **(959,99838;760,00016)** e diâmetro **28,00000**, raio 14, opacidade 1; pílula em **(660,588), 600×104**, texto “Garçom · hoje, 19h”, opacidade 1. O pequeno resíduo da mola é preservado, não há snapping. O tempo da cena é congelado no limite nominal durante a margem, portanto o estado não deriva. B deve herdar esse estado observado antes de iniciar o próximo gesto; B não foi montado.

### Comparação lado a lado com a v4

`comparacao-v4/` contém cinco MP4 a 60 fps e cinco contatos PNG. V4 à esquerda, A à direita; iguais segundos relativos, sem retimar/congelar a referência. O manifesto informa o trecho comparável e o excedente sem equivalente.

| Comparativo | O que permanece | Diferenças que devem ser avaliadas pelo Fabrício |
|---|---|---|
| v01-c01, relativos 0–3,433333 s | transformação e queda da pílula nos mesmos gatilhos iniciais, tipografia 116 px, cores e percurso para o `?` | sem preço; tag Exemplo; a régua nova tem recuo e duas frases, por isso em 3,3 s a v4 está saindo do gancho e A está em “Hoje, 19h.”. O gesto de “Faltou” acontece depois, nos tempos oficiais. Não são durações equivalentes. |
| v02-c04, relativos 0–5,400000 s | título 210 px, mola de unidades, círculos de 72 px/intervalo 120 px, preenchimentos P/4 e convergência uniforme | a fileira entra nesta nova ordem; subtítulo de 46 px em duas linhas e por palavras, texto maior de legenda. O corpo da contagem chega ao mesmo alvo e preserva o mesmo ritmo de gesto. |
| v03-janela-c10, relativos 0–3,900000 s | janela 1100×560, rótulos 36 px, números 150 px, barra, divisor e slots com `count` | números começam mais cedo e com 0,55 s entre grupos, pois esta fase ocupa ~4 s dentro da cena combinada; não reduzir a duração da mola. Ponto passa pela lateral e fundo chega ao grafite durante a entrada. |
| v03-tese-c09, relativos 0–1,400000 s | duas linhas a 160 px, entrada por palavras e “turno.” em laranja | palavras seguem os tempos da nova fala; tese sai mais cedo porque há outra cena na sequência. Legenda inferior é mantida como determina o roteiro atual. |
| v04-c03, relativos 0–4,916667 s | odômetro 236 px, mesma família `count`, fileira de dez círculos/mesmos sete índices trocados, subtítulo e fonte | gatilho da contagem deslocado em relação à fala, período novo do roteiro, fundo vindo do escuro. Depois do trecho comparável, a vaga reaparece e o ponto prepara B. |

Não se atribui nota automática ao piloto. As pausas acima são oportunidades de leitura, não aprovação de ritmo por contagem de pixels. Recall de D2 continua limitado aos controles conhecidos do §23: flash artificial de um frame a 60 fps, salto controlado e presença contratual recuperam os casos exercitados; o mergulho v5 conhecido foi recuperado. A revisão deste A acrescentou o caso real de oclusão do ponto e o corrigiu. Não há estimativa de recall geral; o detector não julga qualidade artística ou cada artefato local. A nova métrica de borda D9 permanece para tarefa separada por não haver movimento de câmera no A; supersampling 2× já foi aplicado.

**Cópia:** 35 strings/fragmentos observados na conferência a 12 fps, todas localizadas em roteiro.json ou docs/v4; `origens-copia.json` registra caminhos/campos. Valores intermediários dos odômetros são estados gráficos, com alvos finais históricos preservados. Sem texto inventado ou cursor. O inventário histórico novo apenas transcreve os literais usados da fonte v4, sem ampliar funções do app.

Reprodução do piloto:

```sh
.venv/bin/python motor/render.py pt --bloco A --regua ../fvp-audio-blocos/motor/cache/blocos-regua/A.json
.venv/bin/python motor/analisar_video.py motor/cache/bloco-a-imagem/bloco-a-sem-audio.mp4 --tempos motor/cache/bloco-a-imagem/tempos.json --html motor/cache/bloco-a-imagem/filme.html --contrato motor/cache/bloco-a-imagem/contrato.json --emendas 4.316666666666666 8.633333333333333 12.95 17.266666666666666 21.583333333333332 25.575416666666666 --saida motor/cache/bloco-a-imagem/analise
./scripts/verificar.sh
```

### Correção de encode do A aprovado — 26/10/2026

O Fabrício aprovou a imagem; coreografia e fonte ficam congeladas. O ffprobe do
clipe e das partes aponta `yuvj420p`, range `pc`, sem transferência/primárias,
apesar das opções de saída existentes. Corrigir a conversão do JPEG full-range
para vídeo limited-range explicitamente no filtro e no encoder: `yuv420p`,
`tv`, matriz, transferência e primárias `bt709`. Regravar os mesmos subquadros,
com a mesma régua, fonte, mistura temporal e Lanczos; não reinterpretar range
por simples troca de etiqueta. Regressão deve exercitar o encoder real e ler
o MP4 com ffprobe, rejeitando `yuvj420p`, `pc` e metadados incompletos. Conferir
também duração, contagem de frames e diferenças visuais contra o encode anterior.

**Resultado:** seis partes e clipe conferidos com ffprobe: `yuv420p`, `tv`,
`color_space/color_transfer/color_primaries=bt709`, 1550 frames, 60/1 fps,
25,833333 s, sem áudio. Fonte e régua mantêm os hashes do piloto aprovado.
SSIM sobre RGB decodificado dos 1550 pares: **0,999327**; não é identidade
bit a bit (há conversão de range e novo encode). Comparativo em
`motor/cache/bloco-a-imagem/comparacao-encode.png` e log homônimo. Regenerados
faixas, cortes e comparativos v4 a partir do novo MP4. D2 agora informa seis
pausas e sete registros de salto: mesmos episódios deliberados; a troca de
range acrescentou uma amostra heurística em **19,316667 s** e retirou a pausa
antes registrada em 22,866667–23,483333 s, sem mudança de gesto. Zero travada
contratual, sumiço, nascimento, cintilação global ou colisão de texto.

A primeira parte falhou antes de capturar imagem com `ERR_SOCKET_NOT_CONNECTED`
no servidor local; reexecutada isoladamente (1036 subquadros), seguida de
validação de todas as partes e nova concatenação. Não alterado limiar ou
coreografia. Regressão real falhou por `yuvj420p` antes da correção e passou
depois. Gate completo: **67 testes** (18 gerais, 22 de motor, 27 de áudio).

O modo completo legado da v5 não foi usado nem promovido; o piloto tem inicialização e régua parciais explícitas. Nenhum arquivo de voz/mixagem foi alterado. Sem produção de B/C/D antes da aprovação da imagem A pelo Fabrício.

**Gate final após rebase na main `038fe3b`:** `./scripts/verificar.sh` passou com **66 testes** (18 gerais, 21 de motor, 27 de áudio/emendas/blocos), dependências/cópia/roteiro e varredura de arquivos proibidos sem erro; `git diff --check` limpo. Regressões novas cobrem régua parcial/margem, cena fora de janela, ponto visível pela pilha de pintura, não cruzar o percentual, cor da tese, estado no fim e seek reversível. Artefatos em cache não entram no commit. Isso torna o piloto revisável; não substitui a auditoria independente do Maestro ou a aprovação visual do Fabrício.

## 26. Bloco B — virada e demonstração no mesmo aparelho (26/10/2026)

**Autorização:** Fabrício aprovou A e liberou B, conforme briefing do Maestro.
Branch `feat/bloco-b-imagem`, encadeado ao A `e8705ca`; A fica congelado.
Plano aplicado pelas skills brainstorming/writing-plans, dentro da direção
já especificada e autorizada. Sem Computer, push, áudio novo ou alteração
de régua. O mapa narrativo aprovado em main (`docs/MAPA-NARRATIVO.md`, PR #20)
determina v05 como pico 1, acionado em **“conecta”, 0,740 s local**.

### Base v4 → B e coreografia antes do código

Fonte executável `4efa75a:motor/filme.html`, funções `planC05/runC05`,
`planFluxo/runFluxo` e markup de `#scr` (telas A/B/C/D). Preservar tipografia,
campos, ilha, cores, pressão, spinner, confirmação, anel e marcador caminhante;
curvas `spr(ui/move/soft)` e `eio` do §20. Não usar cenas da v5 reprovada como
base. O estudo aprovado §24 governa enquadramento e câmera.

| B, segundos locais | Origem v4 | Coreografia na janela oficial |
|---|---|---|
| v05, 0–4,320 | c05→c06: vaga/chip e ponto viram telefone | Começar exatamente no estado final de A: papel, ponto e pílula 600×104 em (660,588). Sem reset. O ponto acolhe a pílula; a transformação única começa com “conecta” em 0,740. O mesmo fundo grafite da pílula torna-se chassi e revela Nova vaga, chegando ao enquadramento do estudo. A pílula mantém o texto durante a primeira parte do gesto; campos assumem a leitura. Sem nova metáfora ou título editorial. |
| v06, 4,320–9,940 | c06 / tela A→B | Formulário já preenchido ao entrar. Aproximação contínua do conjunto; pressão Publicar em “publica” (4,840), spinner e confirmação ~5,360. Troca para bloqueio e aviso com “avisa” (6,580). Raio de 15 km herda o círculo do mapa c08, como plano esquemático externo, sem mover UI dentro do aparelho. O aviso encaminha a tela C de candidatos; não inventar tela/botão de candidatura ausente na v4. |
| v07, 9,940–15,650 | c07 / tela C→D | Mesmo chassi, enquadramento geral nas margens do corte. Histórico fica em evidência por aproximação do conjunto, escolha após sua leitura. Check-in entra com a segunda frase (13,040); caminhada e anel preservados, confirmação em “check-in” (14,940). Avaliação ainda oculta. |
| v09, 15,650–19,673396 | c07 / avaliação da tela D | Mesmo chassi e estado de check-in; revelar controles em “avaliam” (17,820), selecionar Sim na pergunta (18,620), retorno ao enquadramento geral até o limite nominal. Manter o aparelho na margem ≥12 frames para C. |

**D4 / aperto informado:** v05 perdeu 1,68 s, v06 0,88 s, v07 1,29 s e
v09 3,476604 s contra as janelas antigas do roteiro. Não comprimir as molas
ou esticar a voz. Em v06 o gesto começa com o formulário preenchido; a
candidatura é a passagem aviso→lista de candidatos, sem tela textual nova.
Em v09 uma segunda reapresentação do histórico depois de Sim/Não não teria
tempo de leitura; a comparação histórica já está na v07. Avisar o Maestro
desse limite, sem alterar áudio. Não alegar que cada detalhe da tela é legível
à distância: o ganho de fonte é o do §24 e a avaliação é do Fabrício.

### Câmera, estados e cópia

Um único `#dot` torna-se chassi. `#dot` e `#scr` (incluindo ilha/UI) são filhos
do mesmo ancestral `#b-camera`; combinar escala base e câmera em **uma matriz**
nesse ancestral. No geral, escala 1,10, centro (1100,484); foco 1,21, pan
(−14,+6), retorno 1,10. Nenhum zoom, pan ou rolagem da UI. Parallax só entre
aparelho, sinalização 0,35×/1,10× e esquema de raio. Sem arredondamento por
filho durante câmera. `deviceScaleFactor=2`, redução Lanczos no encoder
TV BT.709 corrigido no A. Sem cursor em qualquer instante.

À esquerda ficam só progresso e **Exemplo**, sem repetir a legenda como
título. Quatro marcas; estados 01/04 (publicação), 02/04 (aviso), 03/04
(histórico/escolha/check-in), 04/04 (avaliação). O formato deriva da lista v4,
com registro em `docs/v4/COPIA-BLOCO-B.md`. Todos os demais literais da tela
são transcrição da v4, ou legenda atual. Auditoria de strings normalizadas
deve gerar `origens-copia.json` e falhar para literal sem origem. Nenhum
rótulo de revisão dentro do quadro.

O estado inicial usa os valores residuais exatos de `estado-fim-A.json`, não
snapping. O telefone fica fora dos fades de cena. Nos cortes v06→v07→v09,
posição, escala, opacidade e velocidade do chassi atravessam o limite;
apenas as telas mudam com entrada/saída nativas. O fim é congelado no limite
nominal durante 30 frames extras, com `estado-fim-B.json` para C. Nenhum
corte seco adicional autorizado.

**Direção confirmada pelo Maestro após o plano:** v09 termina em Sim/Não,
sem reapresentar histórico; v06 pode começar preenchida. Sim/Não estará
visível antes de “chamaria” (18,620 s). A pergunta acaba em 19,420 s;
o limite oficial vem apenas 0,253396 s depois. Resposta deve assentar
até esse limite e atravessar a margem de 30 frames: o vídeo de revisão
alcança ~0,770 s após a pergunta sem mover falas ou o limite nominal.
Os 22 pontos de v10 pertencem ao futuro C; entregar o aparelho em estado
estável para a próxima transformação, sem montar C antecipadamente.

**Revisão do preflight antes do render:** a etiqueta Exemplo herdada de A
atravessava a silhueta do telefone na primeira trajetória direta. Preservar
o mesmo nó/estilo de A e deslocar pela lateral direita, depois por y=960
abaixo do aparelho, só então subir em x=260; não atravessar a tela.
Antecipar a entrada nativa da tela para ~1,30 s, depois que o chassi a contém,
reduzindo a sustentação da silhueta vazia durante a transformação.

**Referências arquivadas pelo Fabrício:** v4 em
`../referencias/v4-nota-8/frila-pitch-pt-v4.mp4`; v5 e seus tempos/HTML em
`../referencias/v5-reprovada/`. O worktree `fvp-tempos` foi removido.
Comparações novas e Prisma devem usar esses caminhos; os antigos acima
permanecem somente como histórico das tarefas já entregues.

### Plano de implementação e evidências

- [ ] Régua B em `motor/render.py`: aceitar exatamente v05/v06/v07/v09;
  conservar falas/palavras e duração oficial; margem mínima 12; nome de
  saída por bloco. Regressão de cobertura/duração sem depender do cache.
- [ ] `motor/filme.html`: boot parcial B e fluxo persistente reutilizando
  markup/curvas v4. Regressões em Chromium headless: estado A→B exato,
  mesmo nó nos cortes, opacidade 1, geometria interna constante na câmera,
  ausência de cursor/título duplicado e `seek` reversível. A não muda.
- [ ] Exportar `motor/cache/bloco-b-imagem/bloco-b-sem-audio.mp4`, 1920×1080,
  60 fps, yuv420p/tv/BT.709 completo. Fonte, régua, contrato e manifesto
  juntos, fora do git. Conferir ffprobe e presença raster do chassi.
- [ ] Rodar D2 integral: faixas 12 fps, clipes por cena, cortes ±0,5 s,
  incluindo A→B a partir de sequência montada no limite nominal de A.
  Comparar lado a lado com v4 c05/c06/c07, mesmos segundos relativos;
  separar duração sem equivalente, sem retimar a referência.
- [ ] Prisma: `aux/motion-cintilacao`, somente analisador/testes. Métrica D9
  em resolução nativa, movimento compensado quando possível, JSON por
  instante; calibração v4/v5/estudo/A e controles positivo/negativo. Informar
  TP/FN/FP e recall da amostra; sem estimativa geral ou gate bloqueante.
  Integrar commit após revisão e registrar método/limites aqui.
- [ ] Rever sequências temporais, escala/velocidade e achados por segundo,
  registrar falhas sem mudar limiares. `./scripts/verificar.sh`, commit
  sem mídia/cache/push e handoff ao Maestro via `maestri ask`.
