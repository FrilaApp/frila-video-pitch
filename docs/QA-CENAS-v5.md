# QA visual T6 e preparação T7 — 26/10/2026

**Ensaio provisório, sem voz.** As cenas v01–v14 estão montadas em `motor/filme.html`; o roteiro continua como rascunho. Não houve chamada ao ElevenLabs, geração/mixagem de áudio nem render de MP4 final. `tempos2.py`, `aparar`, ducking e os dois roteiros não foram alterados nesta tarefa.

## Reprodução

No worktree `fvp-cenas`, com os links locais do ambiente principal:

```sh
.venv/bin/python scripts/tempos-provisorios.py
scripts/pipeline.sh quadros
(cd motor && ../.venv/bin/python sobreposicoes.py pt)
```

O primeiro comando lê `roteiro.json`, estima a fala em **2,3 palavras/s**, adiciona entrada/pausas/cauda e respeita `janela_s` como piso visual. Produz `motor/tempos-pt.json` ignorado, com `_provisorio: true`, **14 cenas, 28 frases e 107,4196 s**. `musica` fica vazia. Não usa os WAVs, não gera silêncio artificial nem importa `tempos2.py`. Não usar essa régua para mixagem ou entrega; T5 definirá pausas, duração e compassos a partir das tomadas aprovadas.

`filme.html` recusa uma régua que não contenha v01–v14 e informa como gerar o ensaio. A régua v4 produzida pelo `tempos2.py` atual não serve à nova montagem. Isso é uma dependência explícita de T5, não uma migração silenciosa do roteiro.

## Conferências executadas

- `scripts/pipeline.sh quadros`: **42 PNGs** (25%, 55%, 85% de cada cena), zero erros de console/JavaScript.
- Inspeção visual das 14 cenas e de estados adicionais por frase: gancho/“?”, janela eStaff/tese, publicação/aviso/candidatura, histórico/escolha/check-in, avaliação/histórico, mapa e fecho.
- `sobreposicoes.py pt` original, no filme inteiro a cada **1/15 s**: **13 pares de formas esperados**, zero pares envolvendo texto. Não houve alteração do detector nem exclusão automática de achados.
- Conferência local em Chromium: mesmos PNGs após `seek` em ordem inversa e após um novo `boot`; eventos idênticos, ordenados e dentro da régua. **14 instantes comparados**, 43 eventos.
- D1 amostrado em **328 instantes** entre entrada e saída de v06/v07/v09: aparelho inteiro, topo mínimo **16,396 px**, base máxima **843,604 px**, sempre antes de y=890; lista de passos sempre à direita, separada da tela. Legenda e fonte permanecem em `#hud`, fora da câmera.
- Revisão independente de código/conteúdo: um defeito encontrado (check de v10 encoberto pelo ponto), corrigido e reconferido. O check agora é filho do ponto em `#ov` e desaparece fora de v10.

As 13 ocorrências geométricas pertencem aos seguintes grupos; todas foram examinadas:

| Cena | Par | Por que é esperado |
|---|---|---|
| v05 | caminhos do ícone de loja | Traços do mesmo ícone SVG herdado se encontram. |
| v06/v07/v09 | cursor × botão/aparelho | O cursor entra na tela e toca a margem dos botões; não cobre letras. |
| v12 | contorno/preenchimento do DF × ponto, raio, âncoras e pontos menores | Marcadores e raio estão sobre o mapa; o detector usa o retângulo do caminho preenchido. |
| v12 | raio × ponto | O raio nasce do centro laranja; uma amostra durante a expansão. |
| v14 | traços do logo | Encontros intencionais dos traços do wordmark A1 herdado. |

## D1 e aprovação visual pendente

A escala inicial **1,20** mediu 902,40 px de altura, de y=3,80 a y=906,20: invadia **16,20 px** da faixa reservada. A redução prevista em DESIGN §14 foi aplicada e documentada antes de alterar o motor: escala **1,10**, centro visual y=430, altura 827,20 px (~77% do quadro). Os fatores permanecem: mapa/fundo 0,6; passos 0,85; aparelho 1; cursor/ponto 1,1. Deslocamentos de parallax limitados a 30 px; lista esmaece e sai lateralmente durante o foco; câmera volta antes do corte.

**Escala D1 1,10 aprovada pelo Fabrício em 26/10/2026.** A referência inicial de aparelho com ~90% da altura cedeu à faixa da legenda. Nenhuma nova decisão de conteúdo ficou bloqueada; as pendências editoriais do HANDOFF §2 continuam com o Cauê.

## Capturas e evidências locais (não commitadas)

Raiz absoluta das evidências:

`/Users/fabriciotosta/dev/video-frila/fvp-cenas/motor/cache/qa-v5/`

| Arquivo/pasta | Conteúdo |
|---|---|
| `folha-14.png` | Um quadro-chave por cena, com id e instante. |
| `v01-gancho.png` … `v14-assinatura.png` | Os 14 quadros-chave em 1920×1080. |
| `folha-42.png` | Os 42 quadros padrão do pipeline. |
| `folha-21-1.png`, `folha-21-2.png` | A mesma sequência dividida para leitura. |
| `v03-frase-*.png`, `v06-frase-*.png`, `v07-frase-*.png`, `v09-frase-*.png`, `v12-frase-*.png`, `v13-frase-*.png` | Estados complementares por frase. |
| `limites-d1-1.20.json` | Medidas do ensaio inicial em 1,20. |
| `limites-d1.json`, `integracao.json` | Medidas atuais e resultado de determinismo/limites. |
| `sobreposicoes.txt` | Saída completa da varredura original. |
| `conferir.py`, `verificar.py`, `folhas.py` | Scripts locais que geram as capturas adicionais e verificam o ensaio. |

Os PNGs padrão também ficam em `motor/cache/fotos/pt/`. A listagem integral de pares está em `motor/cache/sobreposicoes-pt.json`. A régua e os eventos exportados em `motor/tempos-pt.json` / `motor/eventos-pt.json` são **provisórios** e ignorados pelo git. Todos esses arquivos precisam ser gerados novamente após T5; nenhum sincronismo de áudio foi aprovado por este ensaio.

Não foram executados formatter ou linter; a verificação de sintaxe/execução foi feita pelo Chromium e `git diff --check`. Não foi renderizado vídeo contínuo nem conferido sincronismo/nível sonoro, pois faltam a voz e a régua oficial.
