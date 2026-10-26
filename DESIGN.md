# DESIGN.md — Vídeo-pitch do Frila (v4 documentada, base da v5)

**Para que serve.** Ser a fonte única de verdade do design do vídeo: tokens, componentes, movimento, som, ritmo e regras. Toda mudança de design da v5 começa aqui e só depois vai para o `motor/filme.html`.

**Status (26/10/2026).** Descreve a **v4 como ela é** (lida do código, não de memória). A v5 ainda não mudou nada de design: a seção 14 mostra como a narrativa aprovada se apoia nos componentes existentes, e a seção 16 lista o que ficou em aberto para o critique.

**Como foi levantado.** Lidos: `motor/filme.html` (CSS, tokens, textos, cenas, HUD), `motor/tempos2.py`, `motor/audio2.py`, `docs/v4/STORYBOARD.md`, `docs/v4/LEIA-ME.md`, `assets/cores.json`, e a revisão de narrativa. **Não verificado:** posições e tamanhos de cada elemento por captura (só os que o código declara); níveis de volume ouvindo o MP4. Onde o texto diz "Inferência", é leitura minha.

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

## 14. Mapa da v5 (14 momentos; proposta, ainda não aplicado)

Fonte: `NARRATIVA-v5-100s.md` e `roteiro-v5-100s.json`. Marca o que reaproveita da v4, o que adapta e o que é novo. **Os ids das cenas mudam** (`v01` a `v14`): `NOCAP`, `NO_COMPASSO`, `DURACAO_MIN`, `ENTRADA` e as trilhas `th` do motor precisam ser reescritos para os ids novos.

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
| D1 | **Mockup com foco na tela do dispositivo** | Quando um mockup está em cena (cenas 6, 7 e 8 da v5), a tela do aparelho é o protagonista. Câmera faz **zoom-in de foco** na tela e as camadas (aparelho, fundo, lista de passos, ponto) se movem com **parallax** em profundidades diferentes, para mostrar o device com volume | A especificar (movimento, escala, camadas, mola) e implementar no `filme.html`, depois que as cenas novas forem montadas |
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
