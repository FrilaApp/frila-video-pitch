# Mapa narrativo: emoção e intenção da locução

**Status:** **aprovado pelo Fabrício em 26/10/2026** (nada abaixo muda o texto aprovado do `roteiro.json`; só a direção de interpretação). Ajustes de intensidade só com pedido dele.
**Origem:** escuta da prévia de 26/10/2026. A voz é boa em dialeto e junções, mas a interpretação ficou **neutra demais** nos momentos que importam (virada, features, fecho).

## 1. Princípios

1. **Contraste, não repetição.** Emoção só se percebe contra o fundo neutro. Poucos picos, bem distribuídos; o resto é firme e claro.
2. **Intenção por frase**: cada frase tem um verbo de atuação (apresentar, duvidar, revelar, convidar, acolher).
3. **Os parâmetros de interpretação são ritmo, entonação e terminação**, em faixas curtas (±5% de velocidade, subida ou descida de final de frase, peso de ênfase), nunca teatrais. Tom editorial e publicitário, **sem sotaque regional**.
4. **A imagem sinaliza o mesmo gatilho**: o pico da voz coincide com a chegada do elemento visual (a vaga virando mockup, a assinatura), e a pausa antes do pico é o que o prepara.
5. **O texto não muda.** Vale A1 a A9 do PLAYBOOK; pausas internas de frase continuam ≤ 0,5 s.

## 2. Curva de intensidade (0 = neutro, 5 = máximo)

```
v01 v02 v03 v04 | v05 v06 v07 v09 | v10 v11 v12 | v13 v14
 2   1   2   2  |  4   3   3   3  |  3   2   3  |  4   2
                  ^pico 1 (virada)        ^pico 2 (dado)  ^pico 3 (fecho)
```

Três picos: **v05** (a virada, a promessa do Frila), **v10** (o diferencial: "nenhum mostra comparecimento medido") e **v13** (o fecho caloroso). Os demais ficam entre 1 e 3.

## 3. Mapa por cena

| Cena | Intenção | Int. | Ritmo | Entonação e terminação | Ênfase | Pausa antes / depois |
|---|---|---|---|---|---|---|
| **v01** gancho | Tensão contida, urgência | 2 | Frases curtas, levemente rápido | "Hoje, dezenove horas." descendente seco (o relógio); "Faltou gente no turno." final suspenso, problema em aberto | "dezenove", "faltou" | 0,4 s / 0,6 s |
| **v02** dor 1 | Dado factual, firme | 1 | Estável | Descendente de fato; sem drama | "nove em cada dez" | 0,6 s / 0,6 s |
| **v03** dor 2 | Ceticismo | 2 | Moderado; frase final mais lenta | "Uma plataforma declara um milhão e meio de cadastrados." levemente incrédula; "Cadastro não é turno." sentença, descendente firme | "milhão e meio", "turno" | 0,5 s / **0,8 s** (ressoar) |
| **v04** dor 3 | Gravidade | 2 | Mais lento no número | "setenta por cento" com peso; "em um ano" grave, descendente; a energia cai um degrau no fim da dor | "setenta por cento" | 0,5 s / **1,0 s** (respiro antes da virada) |
| **v05** virada | **Pico 1: o anúncio.** Calor, abertura, promessa | **4** | Um pouco mais cadenciado, claro | A voz "abre" (cor mais calorosa, sorriso na voz); sobe em "conecta" e em "perto", terminação ascendente-resolvida | "conecta", "perto" | **1,0 s** / 0,5 s |
| **v06** solução 1 | Demonstração clara, ágil | 3 | Cadenciado (publica / avisa) | "Você publica a vaga." objetiva; "O Frila avisa…" um grau mais viva; "quinze quilômetros" nítido | "avisa", "quinze" | 0,4 s / 0,5 s |
| **v07** solução 2 | A feature-chave (histórico) | 3 | Desacelera em "histórico" | Sobe levemente em "você vê o histórico" (descoberta); "check-in" claro e curto | "histórico", "check-in" | 0,4 s / 0,5 s |
| **v09** solução 3 | Convite, pergunta genuína | 3→2 | Leve | A pergunta "chamaria de novo?" **ascendente de verdade**, deixada no ar | "novo" | 0,4 s / 0,7 s |
| **v10** dado | **Pico 2: a descoberta moderada** | 3 | Estável, com micro-suspense antes de "nenhum" | "nenhum mostra comparecimento medido." firme, descendente, confiante | "nenhum", "medido" | 0,6 s / 0,6 s |
| **v11** meta | Confiança, objetivo | 2 | Cadência de lista, números marcados | Números com peso crescente; "nove em cada dez profissionais presentes." fecha firme | "oito", "cinquenta", "nove em cada dez" | 0,5 s / 0,5 s |
| **v12** estratégia | Expansão, ambição | 2→3 | Cada frase um pouco mais aberta | Terminações sustentadas; "o Distrito Federal." ascendente-resolvida | "quinze quilômetros", "Distrito Federal" | 0,5 s / 0,9 s |
| **v13** fecho | **Pico 3: calor e alívio** | **4** | Mais lento, acolhedor | "Menos…" / "Mais…" espelhados (descendente / ascendente); "Deixa que o Frila cuida." íntimo, suave, descendente conclusivo | "menos", "mais", "cuida" | 0,7 s / 0,6 s |
| **v14** assinatura | Marca, calma | 2 | Pausado | "Combinou?" curta, sobe como pergunta; "Pode contar." firme e baixa; "Dos dois lados." suave; "Frila." isolada, com pausa curta antes, descendente conclusiva | "contar", "dois lados", "Frila" | 0,6 s / fecho |

As pausas são alvos de direção, não substituem a régua (que continua definida pelas pausas reais da tomada); servem para **pedir** a pausa na geração e para o mix saber onde a música respira.

## 4. Como isso entra na produção

- **Texto de direção** na geração: marcas de interpretação por frase (formato definido pelo Engenheiro de Áudio depois de testar o que o modelo e a conta suportam) e, se o modelo permitir, ajustes por bloco de velocidade e expressividade.
- **Música** acompanha a curva: respira nas pausas marcadas (v04→v05, v12→v13), sobe nos picos, recua nos trechos de dado. Ver proposta de revisão do mix (A6) no `PLANO-AUDIO.md`.
- **Revisão**: o Fabrício ouve e diz, cena a cena, se a intensidade está certa. A curva é ajustável sem mexer no texto.
