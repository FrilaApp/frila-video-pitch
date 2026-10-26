# Narrativa da v5 — versão única, ~100 s (26/10/2026)

**Esta é a fonte da narrativa a partir de agora.** Junta `docs/historico/NARRATIVA-v5-aprovada.md` (dores e soluções) com o módulo de potencial e prospecção de `NARRATIVA-v5-investidor.md`, condensado para caber em ~100 s. As outras duas ficam como histórico.
**Status:** proposta consolidada, **ainda não aplicada** no `roteiro.json`, `filme.html` ou voz.

## Decisões do Cauê (26/10/2026)
- **Uma versão de vídeo apenas** (sem versão curta separada).
- **Contato discreto no fim:** `frila.org@gmail.com`, só na tela, nunca falado.
- **Descartados:** "eStaff declara 31 clientes no DF", "conversas em andamento" com âncoras (não há âncoras nomeadas), a faixa de R$ 11,9 a R$ 71,2 mi, versão curta.
- **Duração-alvo:** em torno de 100 s.
- **Metas do piloto (8 semanas, 50 vagas, 90%):** mantidas como meta, com a tag "hipótese a calibrar". Interpretei "4. pode ignorar" como "sem objeção"; se era para cortar, a cena P2 sai e o vídeo encurta ~7,5 s.

## Roteiro (14 momentos, 204 palavras faladas (contagem por espaços))

| # | Momento | Fala (voz da Fernanda) | Tela | Janela |
|---|---|---|---|---|
| 1 | **Gancho, Dor 1** | Hoje, dezenove horas. Faltou gente no turno. | Cartão "Garçom · hoje, 19h" cai; ponto vira o "?". Tag "Exemplo" | 4,0 s |
| 2 | **Dor 1, dado** | Segundo a Abrasel, nove em cada dez empresários de bares e restaurantes acham difícil contratar. | "9 em 10", 9 laranja + 1 grafite. Fonte: Abrasel, 30/04/2025 | 6,0 s |
| 3 | **Dor 2, confiança** | E quem se candidata, dá para contar? Uma plataforma declara um milhão e meio de cadastrados. Cadastro não é turno. | Fundo escuro; janela eStaff: 1,5 milhão cadastrados · 533 mil disponíveis, "como a empresa declara, acesso em 22/10/2026" | 9,0 s |
| 4 | **Dor 3, rotatividade** | E a equipe não fica: nos bares e restaurantes, a rotatividade passou de setenta por cento em um ano. | "73,49%" enorme; "dez/2024 a nov/2025"; cartões de escala mudam e a vaga nova reaparece | 7,5 s |
| 5 | **Virada** | Mapeamos essas dores. O Frila conecta quem precisa de gente a profissionais perto. | Vaga do gancho vira o mockup; três marcas das dores | 6,0 s |
| 6 | **Solução 1** | Você publica a vaga. O Frila avisa quem está perto, até quinze quilômetros. | Mockup em foco (zoom + parallax): Nova vaga → publicada → aviso → candidatura; mapa 15 km | 6,5 s |
| 7 | **Solução 2** | Antes de escolher, você vê o histórico. No local, o profissional faz check-in. | Mockup em foco: cartão do candidato (tag "Exemplo") → escolha → check-in a 200 m | 7,0 s |
| 8 | **Teaser (meio)** | Há um número que não achamos em pesquisa pública: quantas vezes falta alguém no turno. | Pergunta grande; contador vazio "— vezes por ano" | 6,0 s |
| 9 | **Solução 3** | Depois do turno, os dois lados avaliam: chamaria de novo? O histórico ajuda na próxima escolha. | Mockup em foco: avaliação Sim/Não → histórico ilustrativo | 7,5 s |
| 10 | **P1, o dado** | Cada turno com check-in vira dado. Dos vinte e dois apps que estudamos, nenhum mostra comparecimento medido. | 22 pontos cinza; só o do Frila ganha o check. Rodapé: "Pesquisa interna de 22 concorrentes, 01/10/2026" | 7,5 s |
| 11 | **P2, a meta** | Meta do piloto: oito semanas, cinquenta vagas por semana e nove em cada dez profissionais presentes. | Três contadores, tag "Meta do piloto · hipótese a calibrar" | 7,5 s |
| 12 | **P3, a estratégia** | Núcleo de quinze quilômetros, com âncoras em eventos e buffets. Depois, bares e restaurantes. Depois, o Distrito Federal. | Mapa da cena 8: círculo de 15 km, 3 pontos-âncora, pontos menores, cresce até o DF. Só na tela: "23.271 empresas ativas no DF" e "~1.300 restaurantes e bares com 10+ pessoas · IBGE 2024" | 9,0 s |
| 13 | **Fecho** | Menos tempo procurando gente. Mais tempo no seu negócio. Deixa que o Frila cuida. Foque no essencial. | Off-white, calmo; o relógio do gancho volta sem pressa | 8,0 s |
| 14 | **Assinatura** | Frila. Turno combinado, regra clara. | Logo A1; **"frila.org@gmail.com"** discreto embaixo; "Narração com voz sintética (IA)" | 6,0 s |

**Soma das janelas: ~97,5 s.** É planejamento (palavras × ritmo da v4/v5 + tempo de ver cada tela), não medida. A medida real sai da voz com a régua do `tempos2.py`.

## O que mudou em relação às propostas anteriores (para caber em ~100 s)
- Falas encurtadas sem perder o dado: candidatura (cena 6) e detalhes de histórico (cena 7) passam para a imagem; "Começa outra busca" (cena 4) vira só visual.
- Mantida a atribuição falada: "Segundo a Abrasel" e "nos bares e restaurantes", para o dado não parecer maior do que é.
- O teaser ficou depois do check-in e a Solução 3 vem em seguida; a resposta (P1) chega 2 cenas depois, o laço aberto dura ~14 s.

## Lastro de cada dado (resumo)
| Dado | Fonte |
|---|---|
| 9 em 10 acham difícil contratar | Abrasel, `01-O-PROBLEMA.md` §1 (90% "difícil ou muito difícil") |
| eStaff 1,5 milhão e 533 mil | Site da eStaff, como a empresa declara, acesso em 22/10/2026 |
| Rotatividade 73,49%, dez/2024 a nov/2025 | Abrasel, `01-O-PROBLEMA.md` §1 e §2.1 |
| Nenhuma fonte pública mede a frequência de falta | `01-O-PROBLEMA.md` §1 e §2.1 (lacuna) |
| "Nenhum dos 22 apps" | Pesquisa interna de 01/10/2026 (`07-MODELO-DE-NEGOCIO.md`, fontes [1][2]) |
| Metas do piloto | `07-MODELO-DE-NEGOCIO.md` e `02-O-NEGOCIO.md` §10.3, marcadas `[H]` |
| 23.271 empresas; ~1.300 restaurantes e bares com 10+ | `07-MODELO-DE-NEGOCIO.md` (CNPJs ativos; IBGE 2024) |

Fontes primárias não foram reabertas.

## Pendências herdadas (sem resposta; assumo o padrão abaixo salvo ordem em contrário)
1. **Estágio:** a nota "Frila em teste no iPhone" do rodapé da cena 14 fica como na v4. Se o TestFlight mudou, avisar.
2. **Histórico de profissional novo:** o vídeo não mostra esse estado; não há fala sobre ele.
3. **Assinatura "Turno combinado, regra clara":** mantida.

## Próximos passos (nada feito)
1. Cauê aprova esta versão (ou pede ajustes).
2. Opcional: crítica do Astra sobre este roteiro de 100 s.
3. Aplicar no `roteiro.json`, regravar a voz (Fernanda), conferir no Scribe.
4. Montar as cenas novas no `filme.html` (Dor 2/3 reordenadas, virada, teaser, P1, P2, P3, fecho calmo, contato) e a diretriz D1 (mockup em foco).
5. Áudio conforme o `PLANO-AUDIO.md` do Astra, depois de aprovado.
