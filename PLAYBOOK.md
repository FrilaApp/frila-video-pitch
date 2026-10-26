# PLAYBOOK — produção do vídeo-pitch por blocos

Substitui o fluxo "tudo de uma vez" do `HANDOFF.md` §5–6. Origem: a v5 de 108 s saiu pior que a v4 (76 s) em motion e com emendas de voz audíveis. Qualidade vem antes de prazo. Quem aprova: **Fabrício**.

## 1. Papéis

| Papel | Dono de | Não toca em |
|---|---|---|
| **Maestro** (Claude Code) | Roteiro mestre, divisão em blocos, montagem final, auditoria independente de toda emenda e de toda transição | Código de áudio e de cena (só revisa) |
| **Engenheiro de Áudio** (role `Engenheiro de Áudio`) | `vozes/`, `PLANO-AUDIO.md`, `motor/audio2.py`, `motor/conferir_audio.py`, `motor/mixagem.json`, ferramenta de emendas. Gera a voz, mixa **e revisa o próprio som contra o vídeo** | `motor/filme.html`, `DESIGN.md` |
| **Diretor de Motion** (role `Diretor de Motion`) | `motor/filme.html`, `DESIGN.md`, `motor/render.py`, ferramenta de revisão de vídeo. Cenas, animação, transições, continuidade | `vozes/`, `mixagem.json` |

Cada papel trabalha no seu worktree e commita no seu branch, sem push. O Maestro abre o PR. **Quem produz também revisa, e o Maestro audita de forma independente** (mede de novo; não repete o relatório de quem fez).

## 2. Fluxo

1. **Roteiro mestre travado** (`roteiro.json`): texto, duração-alvo, ordem das cenas. Só o Fabrício muda.
2. **Bíblia de motion da v4:** o Diretor extrai de `~/Downloads/frila-pitch-pt.mp4` e de `docs/v4/` as curvas, os tempos de entrada e as regras que fizeram a v4 boa, e grava em `DESIGN.md`. É o piso de qualidade.
3. **Blocos** (proposta, o Maestro valida com a régua): **A** Abertura e dores v01–v04 · **B** Virada e soluções v05–v09 · **C** Prova e potencial v10–v12 · **D** Fecho v13–v14.
4. **Piloto no Bloco A**, de ponta a ponta (voz, imagem, mix do bloco, revisão). O Fabrício assiste e aprova antes de B, C e D. **Bloco aprovado fica congelado.**
5. **Montagem:** imagem de cada bloco em um clipe com margem de transição; **voz por bloco**; **uma única trilha de música sobre o vídeo inteiro** (nada de emenda de música entre blocos); mix e master no vídeo inteiro.
6. **QA final e escuta integral do Fabrício.**

## 3. Regras de áudio (inegociáveis)

**A1. Nenhuma frase cruza uma emenda.** Toda frase nasce, corre e termina dentro de **uma única tomada contínua**. É proibido cortar, emendar, reposicionar ou preencher com silêncio dentro de uma frase. Começar a frase no fim de um áudio e continuá-la depois de um corte é **defeito bloqueante**.

**A2. Emenda só em pausa natural.** O ponto de corte tem de cair numa pausa **entre frases**, em ambos os lados da emenda: sem palavra e sem energia de fala em ±120 ms (valor inicial; validar de ouvido). Emenda entre blocos coincide com corte de cena.

**A3. A unidade de geração é o bloco.** Voz de um bloco = uma tomada contínua (várias frases juntas) com `previous_text`/`next_text` dos blocos vizinhos. Frase com defeito: **regerar o bloco**, não remendar a frase. Exceção: regerar uma frase isolada só se ela abre ou fecha o bloco e a prosódia for ouvida em contexto.

**A4. As pausas vêm da fala.** Não se injeta silêncio artificial entre frases do mesmo bloco, e não se alinha cada frase à grade da música. As pausas do bloco são as da tomada aprovada. Pausas entre blocos são desenhadas (500 ms ou mais) e casam com o compasso.

**A5. Toda emenda é analisada, sem exceção.** Para cada emenda a ferramenta (`motor/analisar_emendas.py`, a ser criada) gera o trecho de ±2 s e reprova se houver: palavra truncada ou energia de fala no ponto de corte; clique ou descontinuidade; diferença de ruído de fundo maior que 3 dB entre os dois lados; pausa antes ou depois fora de 0,2–1,2 s; frase com início e fim em tomadas diferentes. **Reprovou, bloqueia.** O Scribe lista as palavras com tempos ao redor da emenda.

**A6. Mix.** A voz tem prioridade sobre música e efeitos; brutos preservados, sem fade em fala; limiares de `PLANO-AUDIO.md` mantidos (voz/música ≥ 12 dB, voz/efeitos ≥ 15 dB e voz/fundo ≥ 10 dB, medidos em fala ativa, voz ≥ referência −10 dB). Efeito que cai sobre palavra sai do lugar ou é silenciado, e o Maestro e o Fabrício são avisados da perda.

**A7. Scribe é pista, não aprovação.** A escuta decide.

## 4. Regras de imagem e motion (inegociáveis)

**D1. A v4 é o piso.** Cena nova parte dos componentes e das curvas da v4. Reescrever do zero exige justificativa registrada no `DESIGN.md` e aprovação do Fabrício. Cada bloco passa por **comparação lado a lado** com a mesma cena da v4 (mesmos instantes).

**D2. Revisão é em vídeo, não em quadro parado.** Para cada bloco o Diretor gera: faixa de quadros a 12 fps por cena; quadros de ±0,5 s em torno de cada corte e de cada emenda de bloco; e a análise de movimento (`motor/analisar_video.py`, a ser criada) com: **travada** (quadros iguais onde devia haver movimento), **salto** (mudança brusca de posição ou escala), **cintilação**, **elemento que some ou nasce fora de hora** e **sobreposição de texto**. Resultado vira lista de achados por instante.

**D3. Continuidade entre blocos.** O último quadro do bloco N e o primeiro do bloco N+1 compartilham o estado dos elementos que atravessam o corte (o ponto laranja, o fundo, o aparelho). Cada bloco tem margem de transição de pelo menos 12 quadros. Corte seco só com decisão registrada.

**D4. Duração não é desculpa.** A cena não é esticada para caber na voz: a voz entra na cena, a cena respira no ritmo do design. Se a voz exigir mais tempo, o Diretor refaz a coreografia da cena (não só segura o quadro) e avisa o Maestro.

**D5. Sem bloco novo antes do bloco anterior aprovado pelo Fabrício.**

## 5. Regras do Maestro

- **Verificar por medição própria**, nunca só pelo relatório de quem produziu. Todo número que eu repito foi medido por mim.
- **Nunca aprovar movimento por quadro parado** nem emenda sem ter ouvido ou analisado o trecho.
- **Gate técnico passou não significa aprovado.** O que decide é a escuta e o olhar do Fabrício.
- Reportar falha com números; não afrouxar limiar para passar sem registro e sem avisar o Fabrício.
- Um agente por área de arquivos. Conflito entre branches é resolvido pelo Maestro.
- Se um agente ficar sem cota ou for reiniciado, o Maestro repassa o estado completo; nada de contexto só na cabeça de um agente.

## 6. Ferramentas a criar (primeiras tarefas)

| Ferramenta | Dono | Entrega |
|---|---|---|
| `motor/analisar_emendas.py` | Engenheiro de Áudio | Lista toda emenda de um bloco ou do vídeo, extrai ±2 s, aplica A1–A5, devolve `emendas.json` com aprovado ou reprovado e o motivo |
| `motor/analisar_video.py` | Diretor de Motion | Faixas de quadros a 12 fps, quadros em torno de cortes, achados D2 em `achados.json` |
| Voz por bloco em `vozes/eleven.py` | Engenheiro de Áudio | `gerar-bloco A` gera uma tomada contínua, guarda os tempos de palavra do Scribe e as pausas |
| Render por bloco em `motor/render.py` | Diretor de Motion | `render.py pt --bloco A` gera o clipe do bloco com margens |

Antes do código, cada mudança entra no doc do seu dono (`PLANO-AUDIO.md` ou `DESIGN.md`).
