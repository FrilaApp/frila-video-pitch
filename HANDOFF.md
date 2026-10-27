# HANDOFF — vídeo-pitch do Frila v5 (PT-BR)

**Para:** Fabrício, que vai continuar e finalizar a geração do vídeo.
**De:** preparação feita em 26/10/2026 (Cauê + Claude Code, com revisões de um Codex GPT-6-Astra).
**Regra de ouro:** este arquivo é a fonte do estado. Se algo aqui divergir de outro documento, vale este; depois corrija o outro.

---

## 0. Em 1 minuto

- **O que é:** vídeo-pitch de ~80 s, 1920×1080, 60 fps, narração sintética PT-BR, treze cenas (v01–v14 sem v08), baseado na v4 aprovada com nota 8/10. O fecho fala de tempo e foco.
- **Onde estamos:** quatro tomadas aprovadas de ouvido pelo Fabrício (26/10/2026); C seed 1 tem exceção explícita para a pausa A8 de 0,600 s, mantendo a vírgula. Seleção em `vozes/selecao-blocos-pt.json`, sem alterar os brutos. Régua T5 gerada: **78,693604 s / 40 compassos**, com janelas locais por bloco. **Não há novo render final nem mixagem desta régua.** O Diretor está produzindo a imagem por blocos.
- **O que falta (em ordem):** validar a imagem de cada bloco com suas janelas → montar imagem → mixar → conferir emendas/sincronismo → Fabrício assiste e ouve o vídeo inteiro → entregar.
- **Quem decide:** o **Fabrício** (produto, texto, ouvido final), desde 26/10/2026. Dúvida de conteúdo ou número: pergunte a ele; não decida sozinho.

## 1. Entrega e definição de pronto

**Entregáveis:** `frila-pitch-pt.mp4`, `frila-pitch-pt.srt`, os **stems** de áudio (voz, música, efeitos), o `mixagem.json` e um relatório curto de QA. Arquivos grandes **não vão para o git**: entregue por Drive (ou o canal que o Fabrício indicar) e registre o link no PR.

**Pronto quando todos forem verdade:**

| # | Critério |
|---|---|
| 1 | MP4 1920×1080, 60 fps, H.264, áudio AAC 256 kbit/s 48 kHz estéreo, idioma `por`, comentário "Narração com voz sintética (IA)" |
| 2 | Duração **~80 s** (alvo 78–90 s; texto enxuto aprovado em 26/10/2026), terminando no fim de um compasso da trilha |
| 3 | Texto na tela = campo `legenda` do `roteiro.json`; `.srt` com o mesmo texto e tempos |
| 4 | Todas as frases passam na conferência (`vozes/eleven.py conferir`) **ou** têm exceção registrada aprovada de ouvido pelo Fabrício |
| 5 | Nenhuma palavra cortada no MP4 final (conferir o áudio final com o Scribe, com ~250 ms de contexto em cada lado) |
| 6 | Mix conforme `PLANO-AUDIO.md` §E: voz/música ≥ 12 dB, voz/efeitos ≥ 15 dB na coexistência, −16 LUFS (±0,5) e pico real ≤ −1,5 dBTP no AAC final |
| 7 | Mockups das cenas v06, v07 e v09 com zoom + parallax (diretriz D1 em `DESIGN.md` §14) |
| 8 | `sobreposicoes.py` sem sobreposição inesperada; a faixa da legenda livre |
| 9 | Contato `frila.org@gmail.com` só em texto na última cena, **nunca falado**; sem pedido de dinheiro, sem preço |
| 10 | **O Fabrício ouviu o vídeo inteiro e aprovou.** Conferência automática é pista, não aprovação |

## 2. Estado atual

| Item | Estado | Onde |
|---|---|---|
| Texto enxuto, 13 cenas sem v08 | **Aprovado** (Fabrício, 26/10/2026); texto de ~100 s é histórico | `roteiro.json`, `PLAYBOOK.md` |
| Design do vídeo (v4 documentada, mapa v4→v5, diretriz D1) | Pronto | `DESIGN.md` |
| Plano de áudio | T4 validada com sinais sintéticos; quatro vozes aprovadas. Mix/render novo pendentes | `PLANO-AUDIO.md` §§H/L, `motor/mixagem.json` |
| Régua oficial T5 | 13 cenas, 78,693604 s; cortes entre blocos nos compassos 13/23/33, fim no 40; dez janelas menores que o planejamento antigo, reportadas ao Diretor | `motor/tempos2.py`, `vozes/regua_blocos.py`, `motor/cache/blocos-regua/` |
| `preparar` (preparação da voz) | Preserva bruto por padrão, sem fades; corte/padding auditáveis testados offline. Régua/IDs da T5 preservados | `motor/tempos2.py`, `PLANO-AUDIO.md` §H |
| Voz ElevenLabs (script de geração e conferência) | Pronto e testado (2 frases + 20 frases de teste) | `vozes/eleven.py` |
| Roteiro da v5 aplicado no `roteiro.json` | **Sim** (T2); v4 em `docs/v4/roteiro-v4.json` | `roteiro.json` |
| Voz por bloco | **A/B/C seed 1/D aprovados de ouvido**. C seed 2 descartada, preservada imutável | `vozes/selecao-blocos-pt.json`, `PLANO-AUDIO.md` §L |
| Cenas novas (v01–v14) no `filme.html` | **Montadas e conferidas em ensaio T6**, sem voz; régua provisória separada | `motor/filme.html`, `scripts/tempos-provisorios.py`, `docs/QA-CENAS-v5.md` |
| D1 em v06, v07 e v09 (T7) | **Implementado e aprovado** (Fabrício, 26/10/2026): escala 1,10 após medir invasão da faixa em 1,20 | `DESIGN.md` §19 e capturas em `motor/cache/qa-v5/` |
| Render, mix, QA, entrega | **Não** | — |

**Decididas pelo Fabrício em 26/10/2026 (tarde): texto enxuto de 13 cenas (sem o teaser v08), ~80 s; a v4 (nota 8/10) é a base visual; produção por blocos (`PLAYBOOK.md`). O fluxo T4–T12 desta página é o antigo; vale o PLAYBOOK.** Antes: texto final aprovado; nota "Frila em teste no iPhone" mantida; histórico de profissional novo fora do vídeo; assinatura "Turno combinado, regra clara" mantida; metas do piloto em público com a tag "hipótese a calibrar".

**Pendente** (o vídeo não pode ir para anúncio pago sem ela):
1. **Licença do ElevenLabs:** presume-se que o plano usado permita uso comercial, **mas isso não foi conferido** na página de preços. Confirmar antes de usar em anúncio pago.

## 3. Mapa do repositório

```
HANDOFF.md              este arquivo
README.md               visão geral
NARRATIVA-v5-100s.md    roteiro atual (fonte da narrativa)
roteiro.json            o roteiro da v5 no formato do motor (aprovado)
DESIGN.md               design do vídeo: tokens, componentes, movimento, som, ritmo, regras
PLANO-AUDIO.md          plano de engenharia sonora
AGENTS.md               regras do repositório
requirements.txt        numpy, playwright
scripts/                setup.sh, trilha.sh, pipeline.sh
assets/                 fontes (OFL) e tokens de cor usados pelo motor
motor/                  imagem e som: filme.html, tempos2.py, render.py, audio2.py, mux.sh, fotos.py, sobreposicoes.py, legendas2.py
vozes/eleven.py         voz e conferência (ElevenLabs)
docs/v4/                STORYBOARD, LEIA-ME, tempos e eventos da v4 (referência de leitura)
docs/historico/         propostas anteriores, revisão do Codex e o diário de preparação
```

Não está no repositório (de propósito): a **trilha musical** (licença Mixkit; baixe com `scripts/trilha.sh`), **áudios, vídeos e caches** (`.gitignore`), **chaves**, e o dossiê de investidor (mistura números do `frila-docs`, que é privado).

## 4. Começar do zero (≈ 15 min)

**Requisitos:** macOS (Apple Silicon testado), FFmpeg, Python 3.12 ou 3.14 (os dois foram testados), git. O render usa 6 processos do Chromium: ~4 min no Mac do Cauê para 76 s; espere ~5 min para 100 s.

```sh
git clone https://github.com/FrilaApp/frila-video-pitch.git && cd frila-video-pitch
scripts/setup.sh        # venv + numpy + playwright + Chromium em motor/browsers
scripts/trilha.sh       # baixa a trilha e confere tamanho e SHA-256
```

**Chave do ElevenLabs.** Não existe no repositório e **não deve** existir. Use `export ELEVENLABS_API_KEY=...` ou grave em `~/.config/elevenlabs/chave` (modo 600). Peça a chave ao Cauê por canal seguro ou use a sua. Confira o saldo: `.venv/bin/python vozes/eleven.py saldo` (o plano usado até aqui é Starter, 40.000 caracteres/mês; o roteiro tem ~1.300 caracteres por geração completa).

**Voz atual:** Ana Dias (`MZxV5lN3cv7hi1376O0m`), parâmetros editoriais do
PLAYBOOK A9. As quatro tomadas já foram geradas e aprovadas; **não regenerar**.
Fernanda e os testes de geração por frase eram do fluxo histórico.

**Reproduzir T5 offline** (requer as tomadas selecionadas no disco, sem API):
```sh
.venv/bin/python motor/tempos2.py --bloco A
.venv/bin/python motor/tempos2.py
./scripts/verificar.sh
```
T5 verifica hashes, texto/Scribe e exceções antes de exportar. O render novo
depende das cenas adaptadas pelo Diretor às treze janelas atuais.

## 5. Como o pipeline funciona

```
roteiro.json + vozes/selecao-blocos-pt.json ──► quatro WAVs imutáveis e Scribe (24 kHz, tomada por bloco)
      │                                         │
      │                                         ▼
      │                              motor/tempos2.py  ──► motor/tempos-pt.json (régua: cenas, falas, música)
      │                                                          │
      ▼                                                          ▼
  motor/filme.html  ◄── window.boot(tempos) + seek(t) ── motor/render.py ──► cache/filme-pt.mp4 + eventos-pt.json
                                                                                  │ (cliques, toques, pousos)
                                              motor/audio2.py (voz + trilha + efeitos) ◄┘
                                                          │
                                                          ▼
                                    motor/mux.sh ──► pt/frila-pitch-pt.mp4     motor/legendas2.py ──► pt/frila-pitch-pt.srt
```

- **Cada quadro é calculado** por `seek(t)`; nada depende do relógio. O mesmo `tempos-pt.json` gera sempre o mesmo vídeo.
- **Fala vs legenda:** `fala` é o que a voz diz; `legenda` é o texto na tela. Mesma contagem de frases por cena para alinhamento textual. `falas` da régua são janelas de legenda; `audio_blocos` são quatro inserções de WAV completo. Não criar áudios por frase para esse roteiro.
- **`eventos-pt.json` sai do render** e o `audio2.py` precisa dele (os efeitos acompanham o que a imagem faz). Mudou só ganho/ducking? Não precisa re-renderizar.
- Atalho: `scripts/pipeline.sh voz|conferir|tempos|quadros|imagem|audio|mux|tudo`.

## 6. Plano de trabalho

Esforço: **P** pequeno (≤ 2 h), **M** médio (meio dia), **G** grande (1 a 2 dias). São estimativas relativas, não compromissos.

| # | Tarefa | O que mexe | Aceite | Esf. | Depende de |
|---|---|---|---|---|---|
| T1 | **Ambiente + teste de fumaça** (§4) | — | `setup.sh` e `trilha.sh` sem erro; `conferir c01 c02` com 2/2 ok. O teste de render só é possível depois de T3 (o `tempos2.py` precisa de todas as frases) | P | — |
| T2 | **Aprovação do texto** e aplicar no `roteiro.json` | `git mv roteiro.json docs/v4/roteiro-v4.json`; `git mv roteiro-v5-100s.json roteiro.json` | Fabrício aprovou (26/10/2026); contagem de frases fala=legenda ok | P | Cauê |
| T3 | **Concluída: quatro tomadas contínuas aprovadas**, sem novas gerações | `vozes/selecao-blocos-pt.json` | A/B/C seed 1/D; exceção de ouvido A8 de C registrada | M | T2 |
| T4 | **Infra de áudio** do `PLANO-AUDIO.md` §F passos 1–3, 5–7: trilhas separadas, `mixagem.json`, `preparar` que preserva o bruto, ducking novo, QA por estágio, master em 2 passagens | `motor/tempos2.py`, `motor/audio2.py`, `vozes/eleven.py`, novo `motor/conferir_audio.py`, `mixagem.json` | Null test da soma dos stems; margens por frase medidas; `grave` não mascara palavra; LUFS/TP no alvo | G | pode começar já, em paralelo |
| T5 | **Régua oficial gerada**, cortes internos no meio das pausas, voz preservada | `motor/tempos2.py`, `vozes/regua_blocos.py` | 13 cenas, 78,693604 s, 40 compassos; janelas locais e cenas apertadas em `PLANO-AUDIO.md` §L | M | T3 |
| T6 | **Cenas novas no `filme.html`** (v01–v14), reaproveitando componentes da v4 conforme `DESIGN.md` §14: textos em `TX`, uma `planX/runX` por cena, sons com `ev(...)` | `motor/filme.html` | Cada cena confere nos quadros de teste; fonte e margens do `DESIGN.md` §3–5 | G | pode começar já |
| T7 | **D1: zoom + parallax** nos mockups das cenas v06, v07, v09 | `motor/filme.html` (câmera `CAM`, camadas) | Aparelho ~90% da altura; lista de passos nunca cobre a tela; legenda livre; valores iniciais em `DESIGN.md` §14, **aprovado em 1,10 pelo Fabrício** | M | T6 |
| T8 | **Render** | `scripts/pipeline.sh imagem` | `cache/filme-pt.mp4` e `eventos-pt.json`; `sobreposicoes.py pt` limpo | M | T5, T6, T7 |
| T9 | **Mix e master** | `scripts/pipeline.sh audio` (já com a infra de T4) | Critérios 4–6 da §1 | M | T4, T8 |
| T10 | **Mux, legenda, metadados** | `scripts/pipeline.sh mux` | MP4 e `.srt` conforme a §1 | P | T9 |
| T11 | **QA completo** e **escuta do Fabrício** (voz isolada, mix, celular, notebook, fones, mono; o vídeo inteiro sem ler legenda) | relatório de QA | Critérios 1–10 da §1 | M | T10 |
| T12 | **Entrega:** arquivos finais no Drive, PR com atualização deste `HANDOFF.md` (estado) e do `DESIGN.md` | — | PR aprovado pelo Fabrício | P | T11 |

**Atualização T6 (26/10/2026):** montagem visual v01–v14 concluída para ensaio. `scripts/tempos-provisorios.py` gera uma régua marcada PROVISÓRIA, sem áudio, a 2,3 palavras/s (107,4196 s). `tempos2.py`, `aparar`, ducking e roteiros não foram alterados. D1 aplicado com redução documentada para 1,10, aprovada pelo Fabrício. Os 42 quadros, a varredura de sobreposições e a conferência de determinismo estão registrados em `docs/QA-CENAS-v5.md`. Após T2/T3/T5, repetir quadros, varredura e validação visual antes do render final.

**Ordem sugerida:** T1 → (T2 em paralelo com T4 e T6) → T3 → T5 → T7 → T8 → T9 → T10 → T11 → T12. T4 e T6 não dependem do texto final; os ajustes de áudio e as cenas visuais podem andar antes da voz.

**Mapa musical atual de T5:** tensão v01–v04; groove v05–v07, v09 e v10–v12; calma v13–v14, com −2 dB. A v08 foi removida. Há uma receita musical global por compassos; nenhuma trilha ou mix foi gerada nesta tarefa. O clima e as emendas efetivas dependem da escuta do mix futuro.

## 7. Decisões já tomadas (não reabrir sem o Fabrício)

- **Uma versão só**, ~100 s. Sem versão curta separada.
- **Narrativa:** três dores seguidas (urgência → confiança → rotatividade), uma virada, soluções na mesma ordem em mockup, teaser no meio, depois dado, meta, estratégia, fecho em tempo e foco. Sem pedido final, sem preço.
- **Voz:** Fernanda (ElevenLabs). Conferência pelo Scribe do ElevenLabs. O OmniVoice e o Whisper CLI da v4 **não são mais usados**.
- **Contato** `frila.org@gmail.com` só na tela do último frame.
- **Não** usar: "eStaff declara 31 clientes no DF", faixas de R$ em milhões, "conversas em andamento", nomes de âncoras, qualquer menção a programas de fomento.
- **Áudio:** prioridade da voz sobre efeitos e música; preservar os brutos; sem fades obrigatórios sobre a fala; pausas naturais (a grade de música serve a cortes, não a cada frase).
- **Design:** um único acento laranja `#EA5A36`; um ponto laranja atravessa todas as cenas; mola amortecida sem quique; sem degradê, brilho nem partícula.

## 8. Regras de conteúdo

- Todo número tem fonte aberta e está marcado: **dado** (com fonte), **inferência** (conta nossa) ou **hipótese `[H]`**. Meta do piloto é meta, não resultado. O Frila hoje tem **receita zero** e o **piloto só começa em 13/11/2026**.
- Dados do vídeo e onde estão: Abrasel (9 em 10; 73,49%, dez/2024 a nov/2025), site da eStaff "como a empresa declara" (acesso 22/10/2026), pesquisa interna de 22 concorrentes (01/10/2026), números de mercado e metas do piloto (`frila-docs`, repositório **privado**: `produto/01-O-PROBLEMA.md`, `02-O-NEGOCIO.md` §10.3, `07-MODELO-DE-NEGOCIO.md`). As fontes primárias (Receita, IBGE, lojas de app) não foram reabertas durante esta preparação.
- Tela de exemplo vai marcada "Exemplo"; nada de métrica ou função que o app não tenha.
- "Nenhum dos 22 apps" vale para os 22 estudados em 01/10/2026, não para o mercado inteiro.

## 9. Armadilhas conhecidas

1. **Cortes de fala.** Na v4 entregue, "Cadastro" saiu "Castro" no MP4 embora o arquivo bruto estivesse certo: o efeito `grave` começa ~285 ms antes da voz e os efeitos **não** sofrem ducking. Hipótese a provar com A/B (`PLANO-AUDIO.md` §A2). A voz do ElevenLabs entra **quase sem silêncio** (10 a 100 ms), e o corte antigo (−45 dBFS, 30 ms) comia o início: "Turno" virou "termo". Na v5, `preparar()` conserva o bruto e só corta com limites confirmados e aprovação (`PLANO-AUDIO.md` §H).
2. **O Scribe é pista, não juiz.** Ele escreve "Frila" como "Freela" e números como algarismos; o `normal()` do `eleven.py` já trata isso. Divergência pode ser erro dele: confirme de ouvido.
3. **Frases a vigiar na voz nova:** "Meta do piloto" (na v4 "meta" virou "o meta" e "método" em outras vozes), "check-in", "Abrasel", "Frila".
4. **A voz muda a cada geração**, mesmo com o mesmo `SEED`. **Guarde as tomadas aprovadas** (pasta compartilhada), porque regerar pode mudar a voz de uma frase aprovada.
5. **Ids de cena estão fixos** em `tempos2.py` e `filme.html`. Trocar os ids sem atualizar os dois quebra a régua em silêncio.
6. **`eventos-pt.json` é gerado pelo render.** Sem ele não há efeitos.
7. **Quadros de teste são rápidos; o render completo não.** Use `quadros` enquanto monta cada cena.
8. **Render com `NetworkError`.** Apareceu 1 vez em 5 execuções durante a verificação; a abertura da página agora tenta 3 vezes. Se ainda acontecer, rode de novo. Se repetir, pare e investigue (porta do servidor local, Chromium instalado em `motor/browsers`).
9. **A trilha não pode ser redistribuída.** Não a comite; a licença não cobre TV, rádio, CD/DVD nem remix.

## 10. Como trabalhar e entregar

- **Branch + PR para `main`** (sem push direto, sem `--force`). Commits em português. Descreva no PR o que mudou e como conferiu.
- Atualize **este arquivo** (tabela da §2) a cada tarefa concluída.
- Mudou design? Registre primeiro no `DESIGN.md`. Mudou áudio? Siga o `PLANO-AUDIO.md` e registre desvios lá.
- Trabalhe com agentes (Claude Code, Codex etc.) se quiser: `AGENTS.md` traz as regras. Para **crítica de narrativa** (estilo investidor) ou de **áudio**, vale pedir uma revisão independente com o briefing dos documentos, como foi feito aqui (veja `docs/historico/REVISAO-CODEX.md`).

## 11. Contato e referências

- Decisões e aprovação: **Fabrício** (desde 26/10/2026; antes, Cauê). Contato público do Frila: frila.org@gmail.com.
- `DESIGN.md` (tudo sobre o visual e o som), `PLANO-AUDIO.md` (tudo sobre áudio), `NARRATIVA-v5-100s.md` (texto e lastro dos dados), `docs/v4/STORYBOARD.md` e `docs/v4/LEIA-ME.md` (como era a v4 e como refazer).
- `docs/historico/`: como chegamos aqui (propostas, revisões e o diário de preparação, com caminhos do Mac do Cauê que **não** existem neste repositório).


## 12. Retorno T4 — infraestrutura de áudio (26/10/2026)

Implementada no branch `feat/audio-infra`, sem API, voz v5, alteração do
`filme.html` ou dos IDs/`ENTRADA`/`NO_COMPASSO`/`secoes()` da régua. O plano e
os desvios estão em `PLANO-AUDIO.md` §H. Reproduzir com:

```sh
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python scripts/testar_audio.py
```

Ensaio sintético: null 0,0; voz/música mínima 17,57 dB; voz/efeitos mínima
16,20 dB na coexistência (override do clique documentado); voz/fundo local
mínima 14,60 dB; AAC −16,44 LUFS / −5,48 dBTP; atraso inicial medido 0 ms.
O `grave` iniciado 285,5 ms antes recebe ducking na cauda; ataque dentro da
borda é silenciado. Permanecem pendentes T3/T5, limites acústicos da voz real,
QA do MP4 após mux e escuta do Fabrício. A aprovação de palavras não é provada
por seno/ruído. Não há ajuste automático de ducking para fazer números passarem:
QA bloqueia e pede override explícito até o teto musical de 22 dB.
