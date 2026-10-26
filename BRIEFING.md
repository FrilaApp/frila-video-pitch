# Vídeo-pitch do Frila, v5 (só PT-BR)

**Escopo (26/10/2026, pedido do Cauê):** nova versão do vídeo de apresentação, **somente em português do Brasil**. Entrega rápida e de qualidade. EN, slides, `.key` e site ficam fora.

**Base:** a v4 (76,7 s, 15 cenas, 60 fps), guardada em `../v4-final-26-10/`. Nada da v4 foi alterado.
**Pilotagem:** o Cauê dirige a narrativa; eu executo. Nenhuma cena, fala ou número muda sem ele pedir.

## Como o vídeo é feito (pipeline que já existe)
| Etapa | Onde | Depende de |
|---|---|---|
| Fonte das falas e legendas | `../roteiro.json` (campos `pt.fala` e `pt.legenda` por cena) | nada |
| Voz PT (**ElevenLabs**, troca de 26/10) | `vozes/eleven.py gerar` → `vozes/frases/pt/<cena>-<n>.wav` (24 kHz, mono, uma frase por arquivo) | chave em `~/.config/elevenlabs/chave` |
| Conferência (**Scribe**, no lugar do Whisper CLI) | `vozes/eleven.py conferir` → `vozes/conferencia.json` (compara o texto ouvido com a fala e mede o silêncio no fim) | idem |
| Tempos (grade 122 BPM, cenas, compassos da trilha) | `../motor2/tempos2.py` → `tempos-pt.json` | nada |
| Imagem (texto, desenho e movimento) | `../motor2/filme.html` + `render.py pt` (~4 min) | `.venv` e Chromium, em `motor2/` |
| Som (trilha, efeitos, mix) | `../motor2/audio2.py` | nada |
| MP4 e legenda | `../motor2/mux.sh`, `legendas2.py` | ffmpeg |
| Conferência da imagem | `fotos.py pt cenas`, `sobreposicoes.py pt` | nada |
| Conferência da fala no MP4 final | Scribe, passando o áudio do MP4 pelo mesmo endpoint de `eleven.py` | chave |

Mudou só o texto de uma cena → regravar só as frases dela, rodar `tempos2.py`, `render.py pt`, `audio2.py`, `mux.sh` (cerca de 6 a 8 min).
Mudou o desenho ou o movimento → editar a cena em `filme.html`, conferir com `fotos.py` e renderizar.

## Estado do ambiente (conferido em 26/10/2026)
| Item | Estado |
|---|---|
| `motor2/.venv` (Python 3.12 + Playwright) | ok |
| Chromium headless em `motor2/browsers/` | presente |
| ffmpeg com libx264 e VideoToolbox | ok |
| `whisper-cli` | ok |
| Disco livre | 236 GB |
| ElevenLabs (chave, plano Starter) | ok: 17.311 de 40.000 caracteres usados no mês; a fala inteira da v4 usa cerca de 600 |
| Scribe (transcrição) | ok, testado em 26/10 |
| VoiceStudio e Whisper CLI | **não são mais necessários** na v5 |
| **Voz da narração** | **Fernanda** (`7iqXtOF3wl3pomwXFY7G`), aprovada pelo Cauê em 26/10; é o padrão do `eleven.py` |
| Cópia isolada do motor | `v5-pt/motor/` (código copiado do `motor2`, caminhos ajustados, só PT). Usa o `.venv` e o Chromium do `motor2`. A v4 e o `motor2` não são tocados |
| Node e npm | não instalados (a v4 não usa) |

## Regras que valem para a v5
- Nada de pedido final (a v4 termina sem convite; manter, salvo ordem do Cauê).
- Todo número e fato tem fonte aberta (Abrasel 73,49%, Abrasel 9 em 10, site da eStaff em 22/10/2026). Número novo só com fonte.
- Mostrar o estágio como é: TestFlight desde 20/10, meta App Store 13/11/2026. Confirmar antes de repetir.
- Nome de pessoa e telas do app só reais ou marcados como exemplo.
- Voz PT agora é ElevenLabs (a licença não-comercial do OmniVoice deixa de valer). Inferência: o plano Starter inclui uso comercial; **não conferi na página de preços**, confirmar antes de usar em anúncio.
- Aviso "Narração com voz sintética (IA)" fica no final e nos metadados do MP4.
- Fala de "eStaff" escreve-se "é-Staff" no texto da voz; na tela, "eStaff". Testar a pronúncia no ElevenLabs (o Scribe escreve "Frila" como "Freela"; o script já normaliza).
- A chave do ElevenLabs nunca entra em arquivo do workspace, commit, log ou resposta.

## Narrativa (estado em 26/10/2026)
- Proposta inicial: `NARRATIVA-v5.md`. Revisão do Codex (GPT-6-Astra high, terminal "Pauta"): `REVISAO-CODEX.md`.
- **Versão aprovada pelo Orquestrador: `NARRATIVA-v5-aprovada.md`** (é a fonte; ainda NÃO aplicada no `roteiro.json`).
- Arco: 3 dores seguidas (urgência, confiança, rotatividade) → virada → 3 soluções na mesma ordem em mockup → fecho em tempo e foco, sem preço nem pedido. 156 palavras, estimativa de 78 a 86 s.
- **Aguardando o Cauê** antes de gravar: (1) estágio TestFlight ainda vale? (2) o que o histórico mostra para profissional novo? (3) assinatura "Turno combinado, regra clara" fica?
- **Design:** `DESIGN.md` documenta o design da v4 (tokens, tipografia, componentes, movimento, som, ritmo, regras, mapa v4→v5 e observações para o critique). É a fonte única; mudança de design começa nele. Nenhuma mudança de design aplicada ainda.
- **Próxima etapa: critique de design do vídeo** (a abrir). Só depois dela se aplica o roteiro, se regrava a voz e se mexe no `filme.html`.

## O que preciso do Cauê para começar
1. **Direção da narrativa:** o que muda em relação à v4 (ordem, ênfase, cenas a cortar, cenas novas, tom).
2. **Duração-alvo** e **onde o vídeo vai passar** (banca, investidor, rede social). Define ritmo e licença.
3. **Pontos fechados vs. abertos:** textos e números da v4 que posso manter sem perguntar.

## Como rodar a v5 (de dentro de `v5-pt/`)
```sh
# 1. editar roteiro.json (fala = o que a voz diz; legenda = o que aparece na tela)
cd vozes
python3 eleven.py gerar [cena ...]      # só as cenas mudadas, ou todas
python3 eleven.py conferir [cena ...]   # Scribe: aponta frase cortada ou diferente
SEED=3 python3 eleven.py gerar c13      # outra tomada, se o Scribe apontar
cd ../motor
PY=../../motor2/.venv/bin/python
$PY tempos2.py          # régua de tempo e música
$PY fotos.py pt cenas   # quadros para conferir (cache/fotos/pt/)
$PY render.py pt        # imagem, ~4 min
$PY audio2.py pt        # som
bash mux.sh pt          # → ../pt/frila-pitch-pt.mp4
$PY legendas2.py        # → ../pt/frila-pitch-pt.srt
```
O texto da v4 (copiado em `roteiro.json`) já foi narrado com a Fernanda como teste de ambiente: 20 frases, régua de 74,8 s, 17 de 20 conferidas. O `tempos-pt.json` e as frases de `vozes/frases/pt/` são desse teste e serão refeitos com a narrativa nova.

## Achados do teste de voz (frases a ouvir/regravar quando o texto fechar)
- `c08-mapa-1` "O aviso chega **a até** quinze quilômetros": o Scribe ouviu "na de".
- `c10-concorrente-1` "é-Staff": ouvido como "estef". Pode precisar de outra grafia de pronúncia.
- `c13-estagio-1` "com meta de App Store": ouvido "com **o** meta" (o mesmo risco que a v4 teve com "meta").
- O Scribe é pista; **o ouvido do Cauê decide**.

## Pontos da v4 já levantados para decidir (opcional)
- Rotatividade: tela diz 73,49%, fala diz "passa de 70%".
- Pontos do slide de 7 em 10 usam lógica oposta à dos 9 em 10.
- Cartão do Bruno T. (18 de 20 turnos, 10 de 12 chamariam de novo) aparece como dado real; marcar como exemplo?
- O check-out aparece na tela do 200 m, mas a fala só cita o check-in.
- O vídeo abre sem logo e só mostra a marca no fim.

## Registro
- 26/10/2026: ambiente preparado, v4 preservada em `../v4-final-26-10/`, aguardando a pilotagem.
- 26/10/2026: Whisper CLI e OmniVoice trocados por ElevenLabs (voz) e Scribe (conferência). `eleven.py` testado ponta a ponta (gerar + conferir, 2 frases, 2/2 ok). Frases de teste apagadas.
- 26/10/2026: voz Fernanda confirmada pelo Cauê. Motor copiado para `v5-pt/motor/` (só PT) e testado: tempos, quadros e voz OK. Aguardando a mudança de narrativa.
- 26/10/2026: narrativa revisada pelo Codex e aprovada com ajustes (`NARRATIVA-v5-aprovada.md`). Nada aplicado em `roteiro.json`, `filme.html` ou voz. Próximo: critique de design.
- 26/10/2026: `DESIGN.md` criado (breakdown do design da v4, 18 seções). Sem mudança de design aplicada.
- 26/10/2026: diretrizes do Cauê: foco no mockup com parallax + zoom-in (D1), ducking cuidadoso (D2), trilhas separadas (D3), sem cortes de fala (D4). Áudio: Astra (terminal Pauta) planeja em `PLANO-AUDIO.md`, sem código até eu aprovar. Duas edições já feitas na cópia da v5: `audio2.py` (guarda de import) e `tempos2.py` (aparar mais gentil), não validadas.
- 26/10/2026: proposta de módulo investidor em `NARRATIVA-v5-investidor.md` (teaser no meio + dado, meta do piloto e estratégia de prospecção antes do fecho; versões curta e investidor). Aguarda decisões do Cauê (seção 8 do arquivo) e, se ele quiser, crítica do Astra. Nada aplicado.
- 26/10/2026: decisões do Cauê sobre o módulo investidor: uma versão só (~100 s), contato discreto frila.org@gmail.com (só na tela), sem eStaff no DF, sem âncoras nomeadas. **Fonte da narrativa agora: `NARRATIVA-v5-100s.md`** (14 momentos, 199 palavras, janelas somam ~97,5 s). `NARRATIVA-v5-aprovada.md` e `NARRATIVA-v5-investidor.md` ficam como histórico. Nada aplicado.
