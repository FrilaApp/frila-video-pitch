# Regras para agentes e pessoas que mexem neste repositório

- **Português do Brasil** em commits, PRs, comentários e documentos, com acentos.
- **Nunca** imprima, registre ou faça commit de chave de API (a do ElevenLabs fica em `ELEVENLABS_API_KEY` ou `~/.config/elevenlabs/chave`).
- **Todo número ou fato tem fonte aberta** e vai marcado: dado (com fonte), inferência (conta nossa) ou hipótese `[H]`. Não invente número, fonte ou função do app. Meta do piloto é meta, não resultado.
- **Design e som começam nos documentos**: mudança de design entra primeiro no `DESIGN.md`; mudança de áudio segue o `PLANO-AUDIO.md`. Só depois vai para o `motor/`.
- **O ouvido do Fabrício decide.** Conferência automática (Scribe) é pista, não aprovação.
- **O fluxo de produção é o `PLAYBOOK.md`** (blocos, papéis, regras de áudio A1–A7 e de motion D1–D5). Leia antes de qualquer tarefa de voz, mix, cena ou render.
- **Nenhuma frase falada cruza uma emenda de áudio** (PLAYBOOK A1): cortar uma frase e continuá-la depois é defeito bloqueante. Toda emenda é analisada, em ±2 s.
- **A v4 é o piso de qualidade visual** (PLAYBOOK D1). Revisão de motion é feita em vídeo, nunca só em quadro parado.
- **Trabalho sai por PR** para `main`; não faça push direto nem `--force`.
- Não commitar áudio, vídeo, trilha musical nem `motor/cache/` (ver `.gitignore`).
