# Frila · vídeo-pitch v5 (PT-BR)

Documentação e código de produção do vídeo-pitch do Frila: narrativa, design, plano de áudio e o motor que gera o vídeo quadro a quadro (HTML calculado por `seek(t)`, 60 fps, voz sintética).

> Trabalho em andamento. O vídeo **ainda não foi renderizado** na v5; aqui está o que já foi decidido e preparado.

## O que há aqui

| Arquivo | O que é |
|---|---|
| `NARRATIVA-v5-100s.md` | Roteiro atual (14 momentos, ~100 s): três dores, soluções em mockup, dado, meta do piloto, estratégia e fecho |
| `NARRATIVA-v5-aprovada.md`, `NARRATIVA-v5.md`, `REVISAO-CODEX.md` | Histórico: proposta inicial, versão aprovada e a revisão de narrativa |
| `DESIGN.md` | Design do vídeo: tokens, tipografia, componentes, movimento, som, ritmo e regras |
| `PLANO-AUDIO.md` | Plano de engenharia sonora: trilhas separadas, ducking, política contra cortes de fala, critérios de aceite |
| `BRIEFING.md` | Estado, decisões e comandos da v5 |
| `roteiro.json` | Falas e legendas por cena (ainda é o texto da v4) |
| `motor/` | Motor de imagem e som (Python + Chromium headless + FFmpeg) |
| `vozes/eleven.py` | Geração da voz e conferência por transcrição (ElevenLabs) |

## O que não está aqui (de propósito)

- **Trilha musical, áudios e vídeos** (`.mp3`, `.wav`, `.mp4`): a música é "Talent in the Air" (Diego Nava, Mixkit) e sua licença não permite redistribuir o arquivo; os demais são pesados e gerados.
- **Fontes e logo** da marca (`../../assets/`): o `motor/filme.html` os carrega de lá. Sem eles o motor não renderiza.
- **Chaves e credenciais**: a chave do ElevenLabs fica em `~/.config/elevenlabs/chave` ou em `ELEVENLABS_API_KEY`, nunca no repositório.

## Aviso

A narração é feita por **voz sintética (IA)** e o vídeo traz esse aviso. Os números do roteiro vêm de fontes citadas na própria narrativa; as metas do piloto são **hipóteses a calibrar**, não resultados.

Contato: frila.org@gmail.com
