# Regras para agentes e pessoas que mexem neste repositório

- **Português do Brasil** em commits, PRs, comentários e documentos, com acentos.
- **Nunca** imprima, registre ou faça commit de chave de API (a do ElevenLabs fica em `ELEVENLABS_API_KEY` ou `~/.config/elevenlabs/chave`).
- **Todo número ou fato tem fonte aberta** e vai marcado: dado (com fonte), inferência (conta nossa) ou hipótese `[H]`. Não invente número, fonte ou função do app. Meta do piloto é meta, não resultado.
- **Design e som começam nos documentos**: mudança de design entra primeiro no `DESIGN.md`; mudança de áudio segue o `PLANO-AUDIO.md`. Só depois vai para o `motor/`.
- **O ouvido do Cauê decide.** Conferência automática (Scribe) é pista, não aprovação.
- **Trabalho sai por PR** para `main`; não faça push direto nem `--force`.
- Não commitar áudio, vídeo, trilha musical nem `motor/cache/` (ver `.gitignore`).
