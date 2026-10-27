# Transcrição da interface e textos reutilizados no Bloco D

Fonte: `roteiro.json` (cenas v13-fecho, v14-assinatura), `docs/v4/STORYBOARD.md` (c16),
`NARRATIVA-v5-100s.md` e decisões do Fabrício de 26/10/2026 e 27/10/2026.

| Origem | Literais visíveis em tela |
|---|---|
| roteiro.json (v13-fecho) | Menos tempo procurando gente. · Mais tempo no seu negócio. · Deixa que o Frila cuida. · Menos tempo procurando gente · Mais tempo no seu negócio · Deixa que o Frila cuida |
| roteiro.json (v14-assinatura) / STORYBOARD c16 / NARRATIVA-v5 | Frila · Combinou? Pode contar. Dos dois lados. · frila.org@gmail.com · Narração com voz sintética (IA). Frila em teste no iPhone. · Narração com voz sintética (IA). |

## Observações de conformidade (Regra D6)
1. Nenhum texto ou número inventado:
   - Em `v13-fecho`, as frases são estritamente as da fala oficial do `roteiro.json`, dispostas no centro da tela em ritmo de espelho ("Menos...", "Mais...", "Deixa que o Frila cuida."). Promessa de marca sem números nem selos inventados.
   - Em `v14-assinatura`, a tag de assinatura passa para "Combinou? Pode contar. Dos dois lados.", conforme nova fala de roteiro.json (adendo de 27/10/2026).
   - O e-mail `frila.org@gmail.com` provém da especificação de tela do roteiro (`'frila.org@gmail.com' discreto embaixo (só na tela)`) e de `NARRATIVA-v5-100s.md`.
   - O rodapé legal `Narração com voz sintética (IA). Frila em teste no iPhone.` provém da v4/c16 e do roteiro (`'Narração com voz sintética (IA)'`).
2. Sem duplicidade de legenda/título:
   - Conforme `NOCAP` e a diretriz expressa, a legenda inferior é suprimida em v13 e v14, pois o texto focal já ocupa a posição nobre em tela.
3. Sem cursor (Regra D8): ausência absoluta de `#cur` em todo o Bloco D.
4. Transição contínua C→D: o ponto laranja herda a posição (1258, 515), tamanho 24×24 e cor de `estado-fim-C.json`, navegando suavemente para o centro onde o relógio se desdobra.
5. Pouso final e saída: em v14, o ponto laranja realiza seu voo e pousa como o pingo da letra "i" no logo A1 (`E.idot`, x=957, y=338, raio 17 px), estabilizando em `estado-fim-D.json` por 30 frames de margem final.
