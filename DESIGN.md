# DESIGN.md — Vídeo-pitch do Frila (v4 documentada, base da v5)

**Para que serve.** Ser a fonte única de verdade do design do vídeo: tokens, componentes, movimento, som, ritmo e regras. Toda mudança de design da v5 começa aqui e só depois vai para o `motor/filme.html`.

**Status (26/10/2026).** Retomada a partir da v4 após reprovação da v5 de 108 s. A bíblia medida, a proposta do aparelho e a calibração D2 estão em §§20–23. §§14–19 registram o ensaio anterior rejeitado; não são a base da retomada. Roteiro ~80 s e aprovação das propostas ainda pendentes. Nenhuma nova cena montada nesta tarefa.

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

Fonte executável: `git show 4efa75a:motor/filme.html`, preservada apenas em cache para a inspeção. Régua e eventos: `docs/v4/tempos-pt.json`, `docs/v4/eventos-pt.json`; descrição: `docs/v4/STORYBOARD.md`. Referência visual: `/Users/fabriciotosta/Downloads/frila-pitch-pt.mp4`, **76,733333 s, 1920×1080, 60 fps**, medidos com ffprobe nesta tarefa. V5 somente para calibração: `../fvp-tempos/pt/frila-pitch-pt.mp4`, **108,200 s de imagem / 108,204 s de contêiner**. A nota 8/10 é avaliação do Fabrício, não resultado do detector.

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
  /Users/fabriciotosta/dev/video-frila/fvp-tempos/pt/frila-pitch-pt.mp4 \
  --tempos ../fvp-tempos/motor/tempos-pt.json \
  --html ../fvp-tempos/motor/filme.html --raiz ../fvp-tempos \
  --contrato motor/cache/revisao-v4-v5/contrato-v5.json \
  --saida motor/cache/revisao-v4-v5/v5
```

Testes incluem flash de **um frame em MP4 real a 60 fps**, salto, repouso versus movimento exigido, presença/ausência fora da janela, opacidade de continuidade, escolha entre instâncias do mesmo objeto, colisão de texto, texto sob fundo opaco e precisão dos frames nas faixas/cortes. As falhas iniciais e correções não mudaram os limiares para limpar a v4: corrigidos o teste de oclusão e os rótulos de PTS (não são ajustes de sensibilidade).

Limites: detector de texto é geométrico texto↔texto, exclui odômetros sob recorte; o teste de superfície opaca amostra três pontos por trecho e não substitui conferência visual de oclusões parciais/SVG/canvas. Raster usa quadro reduzido (480×270), não garante capturar falha pequena/local. Contratos são necessários para atribuir horário/expectativa. Sem HTML, a cobertura semântica é explicitamente ausente. Sem artefatos (`--sem-artefatos`), a execução não satisfaz sozinha D2. Não há aprovação de bloco, novo filme ou validação de motion do estudo; o Fabrício decide após vídeo. Próximo passo depende da aprovação destes estudos e do roteiro pelo Fabrício.

**Revisão independente do instrumento (antes das correções):** identificados três casos a cobrir: aparelho totalmente encoberto não pode satisfazer presença visível; janelas exclusivas repetidas do mesmo id precisam formar uma união de horários permitidos; régua precisa cobrir o vídeo todo, com cenas ordenadas, duração positiva e ids únicos (tolerância de um frame entre limites arredondados). Presença considera também pontos junto à borda para não confundir o chassi visível com sua tela opaca. São correções de cobertura/contrato, sem afrouxar limiares raster. Reexecutar testes e calibração após a correção.

**Fechamento da revisão do código:** os três casos foram corrigidos e ganharam testes. A rechecagem encontrou ainda um override de selector reservado mascarado pelo default; corrigido com agrupamento separado dos selectors declarados e teste em Chromium. A suíte final tem **16 testes**. A calibração mantém os mesmos limiares e resultados da tabela; a presença considera oclusão também nos elementos acompanhados.

Índice local para revisão dos vídeos e acesso às evidências: `motor/cache/revisao-v4-v5/index.html` (191 links locais conferidos). Verificação final: 16/16 testes, recompilação Python, leitura dos dois MP4 e seus relatórios, 27 cortes com PTS na grade real e 29 clipes a 60 fps. Rechecagem independente do código confirmou as quatro correções. Isso valida o instrumento e a integridade dos artefatos; aprovação editorial continua pendente.
