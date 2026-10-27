# Pronúncia da locução: palavras de risco e forma foneticamente familiar

**Status:** proposta do Maestro (26/10/2026), a validar **de ouvido** pelo Fabrício antes da regeneração das vozes por bloco. Nenhuma forma abaixo é "certa" sem escuta: são **candidatas**, e a regra é testar antes de gerar o bloco.
**Objetivo:** português do Brasil neutro, formal, editorial, **sem sotaque regional**. O modelo tende a ler com som neutro/achatado, ou com a fonética errada, palavras de marca, estrangeirismos, números e terminações. Corrigimos **antes** de gerar, escrevendo a fala na forma mais familiar de se pronunciar.

## 1. Como a correção entra, sem mudar o texto aprovado

- O `roteiro.json` e a **legenda não mudam** (ortografia normal). A forma fonética vale **só na `fala`**, no momento da geração, a partir de `vozes/pronuncia.json` (palavra → forma de fala, voz, status, nota). O manifesto de cada bloco registra quais substituições foram aplicadas.
- O conferidor (Scribe) mapeia a forma fonética de volta à palavra original, para a conferência literal continuar valendo.
- **Teste antes de gerar:** cada palavra de risco é gerada isolada, numa frase-veículo curta, nas duas vozes (Ana v3, Gabriel v2), para o Fabrício ouvir e escolher a forma (kit curto, teto de ~1.000 caracteres). Só depois os blocos são gerados.
- Fica proibido alterar uma palavra do texto aprovado para "soar melhor": só grafia fonética da mesma palavra.

## 2. Prioridade 1: marca, estrangeirismo, termo do setor

| Palavra (cena) | Risco de soar neutro ou errado | Forma candidata na fala | Observação |
|---|---|---|---|
| **Frila** (v05, v06, v13, v14; 4 vezes na fala) | Leitura inglesa ("fraila"), ou "Fri-lá" com a tônica errada. O Scribe escreve "Freela" | **Fríla** (tônica no "ri") · alternativas: Fri-la | A marca é a palavra mais repetida; precisa de uma única pronúncia fixa nos 4 blocos |
| **check-in** (v07) | Leitura inglesa "chék-in" | **tchéquin** · alternativa: chéquim | Como se fala no Brasil: "tchékin" |
| **Abrasel** (v02) | "s" lido /s/ em vez de /z/ e o "l" final lido como /l/ | **Abrazéu** (só se a leitura direta falhar) | A Ana v2 já falou "abraséu" (o Scribe escreveu "Abraseu"): testar "Abrasel" primeiro |
| **meta** (v11, "Meta do piloto") | Virava "o meta" ou "método" na v4 e na v5 | **méta** (é aberto) | Conferir também que "piloto" não vire "pilotó" |
| **piloto** (v11) | tônica | manter "piloto" | só verificar |

## 3. Prioridade 1: números (a locução é de números)

| Palavra (cena) | Risco | Forma candidata |
|---|---|---|
| **dezenove** (v01) | "o" fechado ou tônica errada | **dezenóve** |
| **cinquenta** (v11) | "cin-quen-ta" lido sem o "u" ou com "k" duro | manter; fallback **cinkuenta** |
| **setenta por cento** (v04) | "por cento" colado, perde o peso | manter; **reforço de ênfase** (§5) |
| **dez** (v02, v11) | "dêz" ou "dêiz" em vez de /dɛs/ | **déis** só se falhar |
| **oito** (v11) | "ôito" aberto | manter; verificar |
| **quinze, vinte e dois, milhão e meio** | baixo risco | manter |

## 4. Prioridade 2: terminações e palavras longas

| Palavra (cena) | Risco | Forma candidata |
|---|---|---|
| **Federal** (v12, final) | "federál" com /l/ (português europeu) em vez de /aw/ | **Federau** só se falhar |
| **cuida** (v13, o fecho) | hiato "cu-í-da" em vez do ditongo /ˈkuj.dɐ/ | manter; fallback **cúida** (a testar: pode piorar) |
| **comparecimento** (v10) | tônica deslocada ("comparecíMENto") | manter; fallback hifenizar |
| **rotatividade** (v04) | "r" inicial vibrante demais; final "-dade" lido "-dadi" | manter; verificar |
| **negócio** (v13) | "ne-gó-ci-o" em quatro sílabas | manter; verificar |
| **histórico, estudamos, restaurantes, cadastrados, Distrito** | "s" de coda chiado (/ʃ/), sotaque regional: o pedido é **/s/ limpo** | só por seleção de tomada; sem grafia |
| **conecta, perto** (v05) | "e" aberto vs fechado: "conécta", "pérto" | manter; verificar |

## 5. Onde o modelo tende a falar "neutro" e a emoção some (direção, não grafia)

São as palavras que o **mapa narrativo** pede com peso e que o modelo costuma ler sem ênfase, e as terminações que "caem": o remédio é a **direção da fala** por cena (parâmetros e, no `eleven_v3`, tags), e a conferência de ouvido:

- **Ênfase pedida pelo mapa:** conecta, perto (v05, pico 1); avisa, quinze (v06); histórico, check-in (v07); novo (v09, a pergunta); nenhum, medido (v10); oito, cinquenta, nove em cada dez (v11); Distrito Federal (v12); menos, mais, cuida (v13, pico 3); clara (v14).
- **Final de frase que "cai" e soa estranho:** a vogal final átona (turno, gente, ano, perto, vaga, cuida, clara) perde energia ou muda de tom. Conferir cada fecho de frase de ouvido.
- **"chamaria de novo?"** (v09): tem de **subir** como pergunta, não como afirmação.

## 6. O que o Fabrício decide

Escutando o kit curto de pronúncia: para cada palavra, **qual forma fica** (a original, a candidata ou outra). Isso vira `vozes/pronuncia.json` com status `aprovada`, e só então os 4 blocos são gerados.
