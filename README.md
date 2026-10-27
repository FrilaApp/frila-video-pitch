# Frila · vídeo-pitch v5 (PT-BR)

Narrativa, design, plano de áudio e motor de produção do vídeo-pitch do Frila: HTML calculado quadro a quadro (60 fps) + FFmpeg, com voz sintética em PT-BR.

> **Quem vai continuar: comece pelo [`HANDOFF.md`](HANDOFF.md).** Ele tem o estado, o que falta, o plano de trabalho, o aceite e as armadilhas.

## Documentos

| Arquivo | O que é |
|---|---|
| [`HANDOFF.md`](HANDOFF.md) | Estado, pendências, plano de trabalho e definição de pronto |
| [`roteiro.json`](roteiro.json) | Texto enxuto aprovado: 13 cenas, sem v08, alvo ~80 s |
| [`DESIGN.md`](DESIGN.md) | Design do vídeo: tokens, componentes, movimento, som, ritmo e regras |
| [`PLANO-AUDIO.md`](PLANO-AUDIO.md) | Plano de engenharia sonora: trilhas separadas, ducking, cortes de fala, QA |
| [`vozes/selecao-blocos-pt.json`](vozes/selecao-blocos-pt.json) | Quatro tomadas aprovadas de ouvido, hashes e exceção A8 de C seed 1 |
| [`AGENTS.md`](AGENTS.md) | Regras do repositório |
| `docs/v4/`, `docs/historico/` | Referências da v4 e histórico de decisões |

## Começo rápido

```sh
scripts/setup.sh      # venv, numpy, playwright e Chromium
scripts/trilha.sh     # baixa a trilha (não está no repositório) e confere o arquivo
export ELEVENLABS_API_KEY=...   # ou ~/.config/elevenlabs/chave
scripts/pipeline.sh   # lista as etapas: voz, conferir, tempos, quadros, imagem, audio, mux, tudo
```

Requisitos: macOS (Apple Silicon testado), FFmpeg, Python 3.12 ou 3.14.

As quatro vozes já estão aprovadas; não regenerar. Com as tomadas imutáveis
no disco, `.venv/bin/python motor/tempos2.py` gera a régua oficial de
**78,693604 s** em `motor/tempos-pt.json` e as janelas locais em
`motor/cache/blocos-regua/{A,B,C,D}.json`. `--bloco A` exporta somente A.
Os arquivos gerados ficam ignorados; seleção e gerador são versionados.
Render, mix e aprovação audiovisual continuam pendentes.

## O que não está aqui (de propósito)

- **Trilha musical, áudios, vídeos e caches** (`.mp3`, `.wav`, `.mp4`, `motor/cache/`): a trilha é "Talent in the Air" (Diego Nava, Mixkit) e a licença não permite redistribuir o arquivo; o resto é pesado e gerado.
- **Chaves e credenciais.** Nunca no repositório.

## Aviso

A narração é **voz sintética (IA)** e o vídeo traz esse aviso. Os números do roteiro vêm de fontes citadas na narrativa; as metas do piloto são **hipóteses a calibrar**, não resultados. Fontes: Abrasel, site da eStaff (como a empresa declara) e pesquisa interna do Frila.

Contato: frila.org@gmail.com
