# Referências arquivadas (fora do git)

Mídia e insumos de calibração ficam em `/Users/fabriciotosta/dev/video-frila/referencias/` (nunca versionados; ver `.gitignore`).

| Pasta | Conteúdo | Uso |
|---|---|---|
| `v4-nota-8/` | `frila-pitch-pt-v4.mp4` (76,7 s), cópia do arquivo avaliado com **nota 8/10** pelo Fabrício | base de qualidade visual (PLAYBOOK D1) |
| `v5-reprovada/` | `frila-pitch-pt.mp4` (108,2 s, SHA-256 `3470ff03…`), `.srt`, `tempos-pt.json`, `eventos-pt.json`, `filme-v5.html` (de `2fdcb21`), `feat-tempos-v5.bundle` | **só calibração** das ferramentas (analisar_video, analisar_emendas); **não** é base de produção |

O branch local `feat/tempos-v5` (commit `2fdcb21`, nunca enviado ao GitHub) foi preservado; o `.bundle` é a cópia de segurança. Para recriar o worktree: `git worktree add ../fvp-tempos feat/tempos-v5`.
