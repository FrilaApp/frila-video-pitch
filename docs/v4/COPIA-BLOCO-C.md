# Transcrição da interface e textos reutilizados no Bloco C

Fonte: `roteiro.json` (cenas v10, v11, v12), `docs/v4/STORYBOARD.md` (c08, c10, c11),
`NARRATIVA-v5-100s.md` e decisões do Fabrício de 26/10/2026.

| Origem | Literais visíveis em tela |
|---|---|
| roteiro.json (v10-dado) | Comparecimento medido · Pesquisa interna de 22 concorrentes, 01/10/2026 · Frila · Dos 22 apps que estudamos, · nenhum mostra comparecimento medido. (legenda queimada suprimida por NOCAP; mantida no .srt) |
| roteiro.json (v11-meta) | Meta do piloto · hipótese a calibrar [H] · 8 · semanas · 50 · vagas por semana · 9 · em cada 10 profissionais presentes · Meta do piloto: 8 semanas, 50 vagas por semana e 9 em cada 10 profissionais presentes. |
| roteiro.json (v12-estrategia) / NARRATIVA-v5-100s.md | Estratégia de expansão · Núcleo de 15 km · Bares e restaurantes · Distrito Federal · 15 km · 23.271 · empresas ativas no DF · ~1.300 · restaurantes e bares com 10+ pessoas · IBGE 2024 · Dados · CNPJs ativos no DF; IBGE 2024. (legenda queimada suprimida por NOCAP; mantida no .srt) |
| docs/v4/COPIA-NOVA-VAGA.md | Exemplo |

## Observações de conformidade (Regra D6)
1. Nenhum texto ou número inventado:
   - "23.271" e "empresas ativas no DF" provêm de dados públicos de CNPJs ativos no DF (`07-MODELO-DE-NEGOCIO.md` e `NARRATIVA-v5-100s.md`).
   - "~1.300" e "restaurantes e bares com 10+ pessoas · IBGE 2024" provêm da pesquisa IBGE 2024.
   - O rodapé da v12 é estritamente `Dados · CNPJs ativos no DF; IBGE 2024.`, sem referenciar nomes de arquivos internos do repositório.
   - O rodapé da v10 é estritamente `Pesquisa interna de 22 concorrentes, 01/10/2026`.
   - A tag da v11 é estritamente `Meta do piloto · hipótese a calibrar [H]`.
2. Sem cursor (Regra D8): ausência de ponteiro ou cursor em todo o Bloco C.
3. Transição contínua B→C: o ponto herda a posição de repouso do aparelho de `estado-fim-B.json`.
4. Saída para D: o estado final estabiliza o ponto laranja e o fundo off-white nos 30 frames de margem, exportando `estado-fim-C.json`.
5. Supressão de legenda queimada redundante (NOCAP em v10 e v12): em 27/10/2026, a legenda duplicada em `#cap` foi removida em v10 e v12, pois a tipografia central já exibe literalmente a fala da locução; a cena v11 preserva a legenda por exibir apenas os contadores numéricos. A legenda completa em todas as cenas continua preservada no arquivo `.srt`.
