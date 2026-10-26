# Plano de áudio — Frila v5, PT-BR

**Estado atual (26/10/2026): v5 de 108 s reprovada. Base: v4 de 76,7 s, nota 8/10 do Fabrício. Roteiro novo de ~80 s pendente; nenhuma geração real autorizada. PLAYBOOK A1–A7 e §I abaixo substituem as orientações históricas de geração/edição por frase em D1–D3. As seções anteriores permanecem como histórico da T4.**

Prioridade: preservar a frase inteira, manter a voz inteligível e permitir ajustes independentes de voz, música e efeitos. A narrativa de referência é `docs/historico/NARRATIVA-v5-aprovada.md`; este plano não altera texto, imagem, voz escolhida ou trilha.

Convenções: **Código** = comportamento lido nos arquivos autorizados; **Medido aqui** = leitura/medição local desta missão; **Informado** = medição fornecida pelo Orquestrador, não repetida aqui; **Hipótese** = causa a investigar; **Proposta** = parâmetro ou critério ainda sem validação auditiva. Os valores de processamento e aceite propostos não são resultados já alcançados.

## A. Diagnóstico e evidências

### A1. O que foi conferido

| Evidência | Resultado | Origem e limite |
|---|---|---|
| Formato entregue da v4 | H.264; áudio AAC, 48 kHz, estéreo; início dos dois streams em 0 s | **Medido aqui:** `ffprobe` no MP4 autorizado. Não prova alinhamento de cada palavra. |
| Durações da v4 | Imagem: 76,733333 s; áudio: 76,726292 s; régua: 76,7263 s | **Medido aqui:** MP4 e `docs/v4/tempos-pt.json` da cópia entregue. A diferença final de aproximadamente 7 ms não explica, por si, problemas em palavras no meio do vídeo. |
| Loudness do MP4 da v4 | −16,14 LUFS integrado; −1,96 dBTP; LRA 2,80 LU | **Medido aqui:** primeira análise `loudnorm`, saída descartada em `null`. Foram usados os campos `input_*`, que descrevem o arquivo entregue; `output_*` não é uma nova entrega. Próximo do informado: −16,0 LUFS / −2,0 dBTP. |
| Régua e eventos da v4 | 15 cenas, 20 frases, 69 eventos; pausas entre arquivos na mesma cena: 0,209–0,345 s; entre cenas: 0,549–2,419 s | **Medido aqui:** JSONs autorizados. São intervalos entre `fim` e `ini`, não silêncio acústico medido entre fonemas. |
| “Cadastro” na v4 | Frase começa em 43,527 s; `grave` em 43,2415 s: antecedência de 285,5 ms | **Medido aqui:** JSONs. A função `grave()` lida no motor da v5 dura 0,7 s; usando essa duração, a sobreposição prevista com a frase é 414,5 ms. Essa conta não mede a intensidade residual do efeito no MP4. |
| Limiter atual | `limit=0.74`, equivalente a aproximadamente −2,615 dBFS de amplitude; attack 1 ms, release 60 ms; sem `latency=true` | **Código e cálculo local:** não equivale diretamente ao teto anunciado de −1,5 dBTP. A ajuda local do FFmpeg confirma `latency=false` por padrão. Atraso efetivo da cadeia ainda não medido. |
| Segmentação da narrativa aprovada | 26 frases nas dez cenas: 2, 1, 3, 3, 2, 3, 3, 3, 4 e 2 | **Medido aqui:** aplicação da expressão de segmentação atual ao texto aprovado. As vinte frases antigas são material de diagnóstico, não a lista final da v5. |

Medições locais somente de leitura: `ffprobe`; FFmpeg com `loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json`, saída `-f null -`; ajuda local de `alimiter`; Python isolado para ler os JSONs e contar frases. Não houve chamada à API, leitura de credenciais, importação dos motores, geração de áudio, escuta executada nesta missão ou gravação intermediária.

### A2. Separar três classes de problema

| Camada | Evidência / diagnóstico | Como provar ou refutar na implementação |
|---|---|---|
| **Geração** | **Informado:** brutos da v5 com 10–100 ms antes e 255–375 ms depois; c04-1 e c08-1 terminam com energia de −52/−53 dBFS. **Hipótese:** final truncado na origem. Energia na borda também pode ser respiração, ruído ou cauda; não prova palavra incompleta. | Ouvir o bruto isolado e conferir texto e palavras de borda. Comparar outra tomada da mesma frase, sem mudar o texto. Se o bruto já perdeu o fonema, nenhum padding ou mixagem o recupera. Não regravar apenas porque o ASR divergiu uma vez. |
| **Corte — `aparar`** | **Informado como demonstrado:** a política antiga, −45 dBFS / 30 ms / 70 ms, retirou 40–60 ms de início fraco em 12/20 frases; “Turno” virou “termo” após o corte, embora o bruto estivesse correto. Não repetido nesta missão. **Código:** o detector usa média de valor absoluto em janela de 5 ms, não RMS; as grandezas não devem ser confundidas. | Comparar, no mesmo sample rate e sem música, bruto → intervalo escolhido → arquivo preparado, compensando apenas ganho conhecido e padding. Registrar amostras removidas e trecho afetado pelo fade. Scribe e ouvido nas três versões. A perda deve aparecer pela primeira vez no processamento, com o bruto preservado. |
| **Mixagem — mascaramento** | **Informado:** “Cadastro” correto no bruto e reconhecido como “Castro” no MP4. **Código:** efeitos não recebem ducking. **Medido aqui:** evento grave temporalmente próximo. **Hipótese principal:** início mascarado pelo efeito e/ou pela música. Isso é diferente de apagar amostras da voz. | Comparação A/B do mesmo trecho: voz; voz+música; voz+efeitos; soma; master; AAC decodificado. Congelar ganho da voz e ganho mestre entre variantes, para o normalizador não compensar a retirada de uma camada. O estágio em que se perde inteligibilidade localiza a causa. |
| **Mixagem — processamento final** | **Código:** soma, redução global de pico, `loudnorm` em duas passagens, resample a 192 kHz, limiter 0,74 e retorno a 48 kHz. **Hipóteses:** redução de transientes, mudança de loudness ou atraso adicional. Não há evidência de que o limiter tenha apagado “Ca”. | A/B com e sem cada estágio, no mesmo nível percebido; medir alinhamento e envelope de redução. Conferir novamente o AAC final. Registrar o modo efetivo de normalização da segunda passagem; `linear=true` solicitado não basta para provar processamento linear. |
| **Régua / alinhamento** | **Informado:** “hoje” de c05 e “não” de c07-2 aparecem tarde no Scribe; correlação por envelope inconclusiva. **Código:** `voz()` coloca o vetor inteiro em `ini`; não corta em `fim`. `soma()` só limita pelo início/fim do buffer total. | Conferir o áudio preparado realmente usado, seu hash, número de amostras e posição. Comparar alinhamento por amostras entre versões equivalentes antes do master; depois investigar atraso do master/codec. ASR no mix não é régua exata. Não corrigir `fim` para caber na transcrição sem essa prova. |

**Conclusão diagnóstica:** o defeito de corte na preparação da v5 é evidência fornecida e deve ser tratado como regressão conhecida. A divergência na entrega da v4 aponta para a cadeia posterior ao bruto, mas não prova sozinha corte físico nem identifica qual componente é culpado. O mascaramento pelo `grave` é a primeira hipótese a testar.

### A3. Achados específicos do código

- `ducking()` detecta atividade a −45 dBFS em blocos de 10 ms **antes** de `main()` ajustar a voz para −20 dB RMS. Portanto, o corte novo a −60 dBFS não resolveu a detecção do ducking: uma consoante preservada pode continuar fora do detector.
- A antecipação de quinze blocos, retenção de 25 e média móvel centrada de quarenta blocos não representam uma envoltória com ataque/retenção/retorno explicitamente separados. **Inferência:** “começa 150 ms antes” não garante atenuação completa no primeiro fonema; a suavização distribui a transição nos dois sentidos.
- `sfx = efeitos(...) * 10**((-24+3)/20) / .1` é um fator de escala, **não uma normalização de cada efeito a −21 dB RMS**. RMS, pico, duração, peso e sobreposição dos sons variam. A hipótese de competição com a voz é plausível; a diferença real precisa ser medida por evento.
- A referência da música usa `mus[~falando]`. Trocar a voz pode mudar a máscara e alterar o nível de toda a música, mesmo sem mudança de trilha. A voz também recebe ganho global: trocar uma frase pode alterar as demais. Ambas as dependências prejudicam a edição independente.
- Há um gerador aleatório global com seed 7. Alterar eventos anteriores pode mudar o ruído sintetizado dos seguintes. Para cache estável, é preciso áudio do evento imutável ou seed individual estável, sem depender da ordem de execução.
- `aparar()` usa `vivo[0]`/`vivo[-1]` sem tratar atividade vazia. Seus fades atingem as bordas do arquivo escolhido mesmo quando faltou silêncio original. O fade-out de 40 ms pode reduzir um fonema final; o fade-in de 8 ms pode tocar o início já próximo da borda.
- `tempos2.py` termina com `main()` incondicional. Importá-lo agora produziria arquivos. A segmentação da geração usa `fala`, mas a régua enumera `legenda`: diferenças de pontuação podem associar a legenda ao WAV errado. O plano exige um manifesto único de frases.
- `secoes()`, `NO_COMPASSO`, entradas e mínimos ainda usam IDs e estrutura da v4. A v5 tem dez cenas e outra virada. Não reutilizar a régua antiga por posição ou substituir somente o texto.

### A4. Decisão proposta sobre as duas edições já feitas

| Edição | Decisão proposta | Motivo |
|---|---|---|
| Guarda `if __name__ == "__main__"` em `audio2.py` | **Manter.** | Permite análise/importação sem executar o mix. Acrescentar guarda equivalente em `tempos2.py` durante a implementação. |
| `aparar`: −60 dBFS, 60/120 ms, fades 8/40 ms | **Ajustar; não voltar a −45 dBFS. Não declarar a edição validada.** | Preservar bruto deve ser o padrão inicial. Manter −60 dBFS como referência conservadora de diagnóstico, não como prova de ausência de fala. Substituir fades obrigatórios por fades opcionais apenas em silêncio confirmado; propor proteção de 80/160 ms quando houver corte aprovado. Ver política D. |

## B. Arquitetura de trilhas e atualização incremental

### B1. Arquivos previstos — estado da infraestrutura T4 em §H

Todos os caminhos abaixo pertencem à v5. Fontes brutas preservadas; derivados descartáveis, identificados por hash. Um manifesto aponta para as versões aprovadas. O fato de um derivado existir não o torna aprovado.

| Artefato | Formato proposto | Conteúdo / localização |
|---|---|---|
| Tomada bruta por frase | WAV PCM 16 bits, 24 kHz, mono | Manter o formato confirmado em `eleven.py`. Novas tomadas versionadas em `vozes/tomadas/pt/<id-frase>/<hash>.wav`; não sobrescrever os brutos de diagnóstico existentes. |
| Frase preparada | WAV IEEE float 32 bits, 48 kHz, mono | `motor/cache/audio/pt/frases/`; resample único, padding/corte aprovados, ganho conhecido. Guardar offsets e transformação, sem música ou efeitos. |
| Voz por cena | WAV float 32 bits, 48 kHz, mono, opcional | Cache reutilizável das frases da cena. Origem local e deslocamento na régua explícitos no manifesto. Não obrigatório para a entrega. |
| `voz.wav` | WAV float 32 bits, 48 kHz, mono | Stem alinhado a t=0, com duração total N. Voz preparada, sem limiter de master. |
| `musica-base.wav` | WAV float 32 bits, 48 kHz, estéreo | Trilha remontada, emendas e fade musical final; ganho de referência estável, **sem ducking**. Medir a referência sobre a própria música, excluindo silêncio, sem depender da voz. |
| `musica-duck.wav` | WAV float 32 bits, 48 kHz, estéreo | Derivado de música-base × automação. Salvar ambos; assim mudar ducking não exige remontar/decodificar a música. |
| Efeito por evento | WAV float 32 bits, 48 kHz, mono no desenho atual | `motor/cache/audio/pt/eventos/`; áudio sintetizado e seed identificados. Hora de entrada, peso e ajuste de ganho são metadados independentes. |
| `efeitos-base.wav` | WAV float 32 bits, 48 kHz, estéreo | Eventos posicionados e ganhos aprovados, sem ducking de voz. Fonte mono duplicada ao centro, conforme o mix atual; não criar espacialização nova. |
| `efeitos-duck.wav` | WAV float 32 bits, 48 kHz, estéreo | Derivado com proteção de fala; o ajuste individual acontece antes da soma, e o controle do conjunto acontece no bus. |
| `premix.wav` / `master.wav` | Premix float 32 bits; master PCM 24 bits; ambos 48 kHz estéreo | Premix = voz central + música-duck + efeitos-duck. Master recebe apenas processamento final aprovado. |
| MP4 de entrega | Vídeo copiado; AAC 256 kbit/s, 48 kHz estéreo | Mesmo formato de áudio previsto em DESIGN §2. Remux sem recodificar a imagem quando a régua visual estiver válida. |
| Manifestos e automações | JSON; envoltórias em cache numérico | `motor/mixagem.json`, `motor/cache/audio/pt/manifesto.json` e relatórios de QA futuros. Sem credenciais. |

Stems de sessão ficam em `motor/cache/audio/pt/stems/`, com versões por dependências. Os cinco stems completos compartilham t=0, sample rate e **exatamente N amostras**. Voz mono entra igualmente em L/R, sem aplicar implicitamente outra lei de pan. Float permite processamento intermediário sem clipar o arquivo; não autoriza clipping no master.

**Regra de soma:** usar somente `voz + musica-duck + efeitos-duck`. Nunca somar base e versão ducked juntas. A soma deve reproduzir o premix antes do master; não se promete reproduzir o master pela soma de stems, porque normalização dinâmica/limiter podem ser não lineares. Guardar a receita do master e seus ganhos.

Cada frase deve ter ID estável, texto de fala, legenda associada, hash do bruto, tomada, configurações públicas de geração, contexto usado, cortes em amostras, padding, ganho, limites acústicos confirmados e intervalos de colocação. Separar `arquivo_ini/fim`, `fala_ini/fim`, `leg_ini/fim` e limites de cena. Arredondar para apresentação só na exportação; cálculo de áudio em amostras inteiras.

### B2. O que invalida o quê

| Mudança | Refazer | Reutilizar / condição |
|---|---|---|
| Trocar uma frase | Tomada selecionada → preparação e QA da frase → voz da cena/bus → envoltórias afetadas → premix/master/AAC | Música-base e eventos sintetizados. Se o contexto textual de frases vizinhas fizer parte da requisição, essas dependências também devem ser revistas; não prometer independência absoluta nesse caso. |
| Baixar um efeito | Ganho daquele evento → bus de efeitos → premix/master/AAC | Voz, música, régua, imagem e amostra sintetizada do evento. Não ressintetizar os demais efeitos. |
| Alterar ducking | Envoltórias → stems ducked → premix/master/AAC | Tomadas, preparação, música-base, efeitos-base e imagem. |
| Mudar alvo LUFS/TP | Master → AAC → QA final | Premix e todos os stems. Reanalisar o master completo; o ganho de loudness é global. |
| Frase nova cabe no intervalo aprovado, sem mudar texto visível | Reposicionar apenas dentro do intervalo permitido e repetir QA de sincronismo | Imagem pode ser reutilizada se início da legenda e momentos visuais continuarem corretos. Não esticar/acelerar fala para fazê-la caber. |
| Mudar duração de cena, legenda queimada, texto ou evento visual | Régua/legendas/eventos, derivados afetados e imagem | Remux sozinho não resolve. Primeiro aprovar voz e tempos; renderizar a imagem depois. |

O cache usa conteúdo e parâmetros, não apenas data do arquivo. Ganhos por frase são fixados após aprovação, para a troca de uma tomada não renormalizar silenciosamente as outras. A seed local de cada efeito não depende de sua posição na lista. Manter apenas o seed de geração de voz não garante tomada idêntica no serviço: o WAV aprovado é a referência reproduzível.

### B3. Esboço de `mixagem.json`

Exemplo de **estrutura proposta**, não configuração já lida ou aplicada. Overrides por cena/evento substituem a chave correspondente; não somam atenuações duas vezes. Os IDs de cena abaixo representam a numeração aprovada e deverão ser ligados aos IDs definitivos do roteiro.

```json
{
  "versao": 1,
  "idioma": "pt",
  "sessao": {"sample_rate": 48000, "interno": "float32", "regua_travada": false},
  "voz": {
    "rms_ativo_alvo_dbfs": -20,
    "tolerancia_db": 2,
    "ajuste_automatico_max_db": 6,
    "ganho_bus_db": 0,
    "aparar": false,
    "diagnostico_pontas_dbfs": -60,
    "protecao_inicio_ms": 80,
    "protecao_fim_ms": 160,
    "fade_em_fala": false
  },
  "musica": {
    "rms_referencia_dbfs": -24,
    "referencia_independe_da_voz": true,
    "ganho_bus_db": 0,
    "duck": {
      "profundidade_db": 14,
      "inicio_rampa_antes_ms": 200,
      "atenuacao_completa_antes_ms": 50,
      "segura_ms": 250,
      "volta_ms": 450,
      "extra_nas_bordas_db": 3,
      "maximo_db": 22
    }
  },
  "efeitos": {
    "ajuste_sobre_referencia_legada_db": -6,
    "duck_db": 10,
    "duck_nas_bordas_db": 16,
    "inicio_rampa_antes_ms": 200,
    "atenuacao_completa_antes_ms": 50,
    "segura_ms": 200,
    "volta_ms": 250,
    "por_tipo": {"grave": {"ajuste_sobre_referencia_legada_db": -9}}
  },
  "protecao": {
    "inicio_frase_ms": 200,
    "fim_frase_ms": 150,
    "mesclar_pausas_ate_ms": 600,
    "margem_voz_musica_min_db": 12,
    "margem_voz_efeitos_min_db": 15,
    "margem_voz_fundo_min_db": 10,
    "fundo_nas_bordas_abaixo_ref_voz_db": 18,
    "pico_efeito_nas_bordas_abaixo_ref_voz_db": 6
  },
  "master": {
    "integrado_lufs": -16,
    "true_peak_pcm_alvo_dbtp": -2,
    "true_peak_aac_max_dbtp": -1.5,
    "lra_parametro_lu": 11,
    "limitador_extra": false
  },
  "cenas": {
    "09": {"musica_ganho_adicional_db": -2},
    "10": {"musica_ganho_adicional_db": -2}
  },
  "eventos": {},
  "qa": {"lufs_tolerancia_lu": 0.5, "janela_ms": 100, "passo_ms": 10}
}
```

Os ajustes de efeitos referem-se à escala legada calculada com a referência fixa original, não à música atual depois do ducking. Assim, baixar música não baixa automaticamente os efeitos. O valor `duck_nas_bordas_db=16` é a profundidade total nas bordas, não mais dezesseis sobre dez. O acréscimo de música nas bordas leva o ducking nominal a 17 dB; o teto de 22 dB limita a correção automática. Falhar no teto pede revisão, não liberação silenciosa.

## C. Ducking e proteção da voz

### C1. Projeto proposto

**A voz aprovada comanda a automação; o texto e a régua protegem suas bordas.** Usar os intervalos acústicos confirmados da preparação, acrescidos de margem, para garantir cobertura integral. O detector de energia pode refinar esses intervalos, mas não pode abrir a música dentro de uma palavra só porque a consoante é fraca. Se a borda estiver incerta, proteger conservadoramente o arquivo inteiro até revisão.

| Controle | Valor inicial proposto | Justificativa e comportamento |
|---|---|---|
| Voz | Referência −20 dB RMS ativo; tolerância ±2 dB por frase | Preserva a referência existente. Ajuste estático limitado inicialmente a ±6 dB; fora disso, revisar tomada/ganho. Não comprimir tudo para forçar igualdade nem amplificar respirações separadamente. |
| Música sem voz | Referência −24 dB RMS sobre a própria trilha | Manter o desenho atual como ponto de partida, sem a dependência da máscara de voz. Não é garantia de nível local em cada compasso. |
| Música sob voz | Ducking inicial de 14 dB; mais 3 dB nas bordas | **Conta nominal:** −24 −14 = −38 dB RMS, dezoito abaixo da referência de voz. A margem real depende do trecho musical e deve ser medida. Aumentar até 22 dB se necessário; se não bastar, revisar o trecho/ganho. |
| Antecipação | Rampa de 150 ms: começa 200 ms antes e termina 50 ms antes do primeiro som protegido | Garantir o patamar antes do fonema inicial. Curva suave de ganho em dB, sem degraus. Não detectar primeiro para só depois reagir. |
| Fim da frase | Segurar música 250 ms após o fim acústico protegido; retornar em 450 ms | Protege caudas e evita recuperação brusca. Os números são proposta, não equivalentes exatos à média móvel atual. |
| Pausas próximas | Manter patamar em pausas de até 600 ms; combinar envelopes pela maior atenuação | Não subir e descer entre frases de uma mesma ideia. Se duas rampas se sobrepuserem, prevalece a mais protetora. |
| Efeitos sob fala | Ajuste base −6 dB sobre a escala legada; ducking de 10 dB, chegando a 16 dB nas bordas | Separar identidade do som de sua competição com a voz. Ajustes são ponto de partida; picos e margem do conjunto decidem. |
| Retorno dos efeitos | Retenção 200 ms, retorno 250 ms | Evitar que a cauda de um sino volte de repente no fim de uma palavra. Um transiente sobre a fala deve nascer atenuado. |
| Fecho e assinatura | Música adicional −2 dB nas cenas 9–10; manter fade final musical | Proposta de calma coerente com o fecho aprovado. Não inventar nova trilha ou efeito. O fade total não pode alcançar “clara”. |

A automação é contínua no tempo absoluto do vídeo. Corte de cena não zera o ducking. Se a fala atravessar uma transição autorizada, mantém-se a proteção até o fim real. Não reiniciar os envelopes no começo de cada stem de cena.

### C2. Cortes escuros e `grave`

- Preservar a sincronização do ataque com o evento visual. Não deslocar o efeito arbitrariamente para fugir da palavra nem atrasar a fala sem atualizar a régua aprovada.
- Começar com ajuste do `grave` em −9 dB sobre a escala legada, substituindo o ajuste geral de −6. Aplicar também a envoltória de fala à sua cauda. A duração atual de 700 ms não significa 700 ms de intensidade constante.
- Se o ataque cair na janela protegida, abaixar o evento inteiro ou silenciá-lo naquele corte. Prioridade para a palavra. Encurtar/reprojetar o timbre fica como alternativa posterior, submetida à escuta, não como primeiro remédio.
- No caso de referência da v4, o ataque antecede a voz em 285,5 ms: o teste prioritário é reduzir a cauda já em andamento antes de “Ca”, além de comparar a versão sem `grave`.
- Na v5, o contraste escuro pertence à cena 3 aprovada; não copiar cegamente os tempos/IDs de c09 e c12 da v4. Eventos definitivos virão da imagem aprovada.

### C3. Como medir margem por frase

Medir nos stems **depois dos ganhos e ducking, antes do master**. Usar as mesmas janelas temporais em todas as trilhas, nunca comparar RMS da voz numa janela e música em outra. Para estéreo, usar energia média dos dois canais; voz central usa a mesma convenção. Além disso, conferir a redução para mono.

1. Construir uma máscara de fala confirmada que exclua padding/silêncio e preserve sons fracos. Guardar os limites e a regra usada. Não usar novamente −45 dBFS como verdade sobre presença de fala.
2. Em cada frase, calcular `ΔVM = RMS_dB(voz) − RMS_dB(música-duck)` e a margem para o fundo real `música-duck + efeitos-duck`. Para efeitos, medir também apenas janelas em que voz e efeito coexistem; não diluir um impacto curto com vários segundos de silêncio.
3. **Aceite proposto por frase:** ΔVM ≥12 dB; voz sobre efeitos ≥15 dB nas janelas de coexistência; voz sobre o fundo somado ≥10 dB. Sem efeito, registrar “não se aplica”, não inventar uma margem infinita.
4. Medir janelas de 100 ms, passo de 10 ms, para localizar a pior passagem. Nas janelas em que a voz estiver até 20 dB abaixo de sua referência ativa, aplicar também mínimo local de 10 dB sobre o fundo. Janelas de voz ainda mais fraca não recebem aprovação por essa regra: entram na lista de bordas/trechos a ouvir, com proteção conservadora.
5. Nos primeiros 200 ms e últimos 150 ms de cada frase: fundo RMS no máximo `referência ativa da frase −18 dB`; pico do efeito no máximo `referência ativa da frase −6 dB`, medido em dBFS. Se a referência da voz for −20, os tetos iniciais serão −38 dB RMS e −26 dBFS, respectivamente. São limites de projeto, não medidas da v4.

Os tetos de borda usam a referência da frase e não garantem SNR de cada consoante fraca. Listar todas as colisões nessa região, mesmo as que passaram nos números. Reduzir efeitos antes de elevar voz, para não usar loudness como substituto de inteligibilidade. A/B e ouvido continuam obrigatórios.

## D. Frases inteiras: geração, preparação e continuidade

### D1. Geração

- **Baseline v5 (aprovado pelo Fabrício em 26/10/2026, A/B "C"):** Fernanda, `eleven_multilingual_v2`, estabilidade 0,35, similaridade 0,75, estilo 0,35, velocidade 1,0, seed 1, com `previous_text` (as 2 falas anteriores do roteiro) e `next_text` (a fala seguinte). No A/B, frases isoladas com estabilidade 0,5 e estilo 0 soaram robóticas; o modelo `eleven_v3` sem contexto foi preterido. Gravar no manifesto o texto exato, configurações efetivamente usadas, tomada e hash. Nenhuma credencial entra em manifesto ou relatório.
- Manter uma frase por arquivo como unidade de edição. Na implementação, permitir selecionar **uma frase**, pois o filtro atual seleciona cena e pode regravar todas as frases dela. Preservar tomadas aprovadas e suas alternativas.
- O corpo de geração envia `text`, `model_id`, `language_code`, `voice_settings`, `seed`, `previous_text` e `next_text`. O contexto vai em campos próprios, nunca dentro de `text` (risco de narrá-lo de novo), e fica gravado na tomada (`contexto`). Mudou o texto vizinho, regerar as frases afetadas. Contexto não é garantia de continuidade de prosódia: a escuta sequencial continua obrigatória.
- Duas tentativas com o mesmo defeito: registrar e levar ao Orquestrador, sem loop de regeneração e consumo indefinido. Não alterar a narrativa para satisfazer o ASR.

### D2. Preparação e `aparar`

**Padrão inicial: não remover amostras do bruto.** Fazer o resample para 48 kHz uma única vez, preservar uma referência antes de qualquer corte e registrar cada transformação. Padding protege montagem; não restaura fonema ausente.

Depois da primeira validação, permitir corte conservador apenas de silêncio confirmado, por frase:

1. Avaliar pontas em janelas RMS de 10 ms e também no envelope de 5 ms equivalente ao atual. Registrar a diferença entre as métricas. −60 dBFS é referência conservadora proposta, não detector infalível de fonemas.
2. Não remover nada quando houver dúvida, atividade vazia, valor não finito ou borda suspeita. Atividade vazia deve retornar diagnóstico explícito e impedir aprovação; nunca indexar vetor vazio, descartar a frase ou aceitar silêncio como fala correta.
3. Preservar pelo menos 80 ms antes do primeiro som confirmado e 160 ms após o último, quando esse silêncio existir. Se faltar espaço, adicionar apenas o padding necessário, sem apagar o início/fim original. Se a borda do bruto contiver voz, marcar para revisão da geração, mesmo após adicionar padding.
4. Fades obrigatórios de 8/40 ms: desabilitar. Se houver necessidade demonstrada de evitar clique, usar rampa proposta de 3–5 ms **somente dentro de silêncio/padding confirmado**, sem tocar respiração ou fonema. O padrão pode permanecer sem fade.
5. Guardar corte inicial/final em amostras, duração original/preparada, padding e qualquer intervalo modificado por fade. A região de fala aprovada deve conservar as amostras da referência reamostrada, compensado apenas o ganho estático conhecido. Tolerância numérica proposta de `1e-6` nessa comparação em float32; comparar no mesmo sample rate e alinhamento.
6. Qualquer trecho removido com janela de energia acima de −60 dBFS bloqueia o corte automático. Abaixo disso também não há garantia de ausência de fala: aprovação depende das demais verificações e, em dúvida, conserva-se o bruto.

### D3. Pausas e grade

**Código:** `ini = sobe(ini + duração_do_arquivo + 0,10, P/2)`. Com P/2 = 245,9175 ms, o arredondamento pode adicionar quase outro meio tempo além dos 100 ms. O intervalo percebido inclui também silêncio final do arquivo anterior e inicial do próximo. Aumentar folgas sem rever isso pode tornar a locução ainda mais espaçada.

**Proposta:** falas seguem a respiração e a pontuação; cortes de cena e viradas musicais podem seguir a grade. Retirar a quantização obrigatória de cada frase, mantendo a grade como opção de direção, não como requisito técnico.

Pontos de partida, medidos entre último e primeiro som de fala confirmado:

- Continuação de ideia na mesma cena: 180–300 ms; referência inicial 250 ms.
- Punch, pergunta ou fechamento de raciocínio: 350–500 ms, por decisão editorial.
- Entre cenas: 400–700 ms; pausas maiores somente com justificativa visual/semântica. Não preencher automaticamente 2,4 s porque a grade exige.

Sobrepor somente padding/silêncio confirmado quando necessário para atingir esses intervalos, nunca fonemas ou respirações. A soma dos arquivos deve preservar suas partes úteis; o alinhamento não pode depender só do tamanho total do WAV. Se os limites não estiverem confiáveis, manter montagem conservadora e pedir escuta, em vez de forçar o intervalo.

Travar a régua final após aprovar voz e pausas. Manter o fim musical em compasso quando couber na duração aprovada; não acelerar fala para alcançar um compasso. Mudança que altere cena ou legenda queimada passa a exigir nova imagem.

### D4. Teste automático de “frase inteira”

Um único `ok` por igualdade de texto é insuficiente. O código atual solicita timestamps de palavra ao Scribe, mas salva apenas comparação normalizada e sobra final; essa sobra é diferença para o timestamp estimado, não silêncio acústico medido.

**Proposta de relatório por frase e estágio:** `geração → preparação → bus de voz → premix → master → AAC decodificado`. Comparar primeiro o estágio novo com o anterior aprovado, para localizar onde a divergência começou. Chamadas ao Scribe são futuras, após aprovação, com cache por hash do áudio e parâmetros; esta missão não chamou o serviço.

| Verificação | Limiar inicial / ação proposta |
|---|---|
| Arquivo válido | Duração positiva, áudio finito e atividade presente. Falha bloqueia montagem. Sequência de três amostras junto ao teto digital (módulo ≥0,999) gera alerta de clipping a investigar. |
| Texto Scribe | Alinhar palavras esperadas e reconhecidas; exigir zero omissões/substituições/inserções **não resolvidas**. Toda divergência nas primeiras/últimas duas palavras é prioritária. Preservar resposta e tempos palavra a palavra. |
| Normalização textual | Permitir apenas equivalências explícitas e revisáveis: algarismos/extenso e aliases já aceitos. Nunca normalizar “Castro” para “Cadastro”, “termo” para “Turno” ou apagar “não”. Conferir números, nomes e negações mesmo quando o texto normalizado passa. |
| Energia na borda do bruto | RMS no primeiro/último bloco de 10 ms acima de −55 dBFS gera alerta, não diagnóstico automático de corte. Início/fim estimado pelo ASR a menos de 30 ms da borda também gera alerta. Os casos informados de −52/−53 dBFS entram nessa fila. |
| Padding preparado | Proteção proposta de 80/160 ms em relação aos limites confirmados. Padding não encerra alerta de bruto suspeito. |
| Fidelidade da preparação | Nenhuma região de fala excluída ou atingida por fade; comparação de amostras dentro da tolerância indicada. Sem limite confirmado, conservar o bruto. |
| Fidelidade da montagem | Duração do trecho inserido igual à do preparado; zero amostras úteis cortadas por `soma`; não sobrepor atividade vocal de frases distintas. Recalcular `fim` a partir da colocação real. |
| Tempos do reconhecimento | Palavra fora do intervalo preparado por mais de 50 ms gera inspeção de alinhamento; não mover a régua automaticamente. Timestamp não mede com precisão a borda física do fonema. |
| Diferença bruto/processado/mix | Se bruto passa e preparado diverge, inspecionar corte/fade; se voz isolada passa e mix diverge, inspecionar margem/efeitos/master. Um erro de Scribe continua hipótese até escuta. |

Transcrição de trechos do mix deve incluir contexto de aproximadamente 250 ms dos dois lados, registrando o offset absoluto. Palavras vizinhas não contam como inserção da frase-alvo; precisam ser alinhadas ao seu próprio intervalo. Não cortar o trecho de conferência exatamente na borda que está sendo investigada.

O aceite automático produz `apto para escuta`, `divergência` ou `inconclusivo`. Se o ouvido do Cauê confirmar que uma divergência é erro do ASR, registrar a exceção com frase/estágio/motivo. Nunca trocar a fala correta só para obter transcrição idêntica.

## E. Verificação final e critérios de aceite

Os limites de aceite foram aprovados conforme HANDOFF.md; não são resultados medidos da voz v5. O ensaio sintético está em §H.

| Item | Critério |
|---|---|
| Integridade das falas | Todas as frases previstas no manifesto presentes; nenhuma perda de amostra útil, fonema ou palavra confirmada; zero divergências de texto/tempo sem resolução documentada. |
| Voz isolada | Referência RMS ativo −20 ±2 dB por frase, salvo ajuste justificado e aprovado; sem estalos ou saltos perceptíveis entre tomadas. |
| Margens | ΔVM ≥12 dB por frase; voz/efeitos ≥15 dB na coexistência; voz/fundo ≥10 dB; varredura local e proteção das bordas conforme C3. Nenhuma colisão crítica pendente. |
| Colisões de efeitos | Listagem de evento, tipo, horário, pico, duração de sobreposição, margem e palavras afetadas. Zero ataque/cauda que mascare palavra na escuta; tetos de borda respeitados ou efeito retirado. |
| Loudness final | AAC decodificado entre −16,5 e −15,5 LUFS integrado. Medir novamente depois de qualquer limiter ou codificação; não aceitar apenas a meta passada a `loudnorm`. |
| Pico real | Master PCM com alvo inicial ≤−2,0 dBTP; AAC final ≤−1,5 dBTP. Se o codec ultrapassar, reduzir o teto do master e reencodar apenas o áudio. |
| Processamento final | Preferir uma normalização final em duas passagens. Desabilitar o limiter fixo 0,74 após A/B, salvo necessidade demonstrada. Se mantido um limiter adicional: teto explicitado, compensação de latência habilitada, nova medição e revisão de redução acima de 1 dB. Não afirmar que ele preserva LUFS. |
| LRA | Registrar; não forçar a entrega a 11 LU nem à medida da v4. O `LRA=11` é parâmetro do filtro, não um resultado obrigatório. Ouvido decide se há bombeamento ou excesso de compressão. |
| Alinhamento | Stems com N amostras e origem comum; deriva acumulada zero na sessão. Após master/codec, investigar deslocamento >10 ms em relação à referência alinhada, compensar atraso conhecido e repetir conferência visual. |
| Final do vídeo | Nenhuma amostra útil além do intervalo de entrega; “clara” e sua cauda preservadas. Não usar `-shortest` para esconder incompatibilidade de duração. Fade final somente depois da última fala protegida. |
| Entrega | Áudio AAC 48 kHz estéreo, idioma `por`, aviso de voz sintética mantido; vídeo sem recodificação quando a imagem for reutilizada. |

**Escuta obrigatória pelo Cauê:** voz isolada, mix normal, volume baixo em alto-falante de celular/notebook, fones e redução a mono. Ouvir o vídeo inteiro uma vez sem ler legenda, depois conferir pontualmente as bordas. Não foi executado nesta missão.

Focos de escuta da narrativa aprovada: entrada de “Hoje”; início de “Cadastro não é turno” após o trecho de dados; “Em bares e restaurantes”; passagem dos dados para “Mapeamos”; “quinze quilômetros”; “check-in”; a pergunta “Chamaria de novo?”; cadência das quatro frases do fecho; “Frila. Turno combinado, regra clara”. São prioridades de teste, não alterações de texto.

Usar “Cadastro”, “hoje”, “não” e “Turno combinado” dos testes antigos como casos de regressão quando os arquivos correspondentes estiverem disponíveis na implementação. Não confundir esses IDs antigos com a numeração das dez cenas novas.

## F. Implementação proposta, em ordem

P/M/G indicam esforço relativo, não horas garantidas. O estado de implementação da T4 está em §H; os passos 4 e 8–10 continuam futuros.

| Ordem | Arquivo / alteração futura | Esforço | Validação sem renderizar imagem |
|---|---|---|---|
| 1 | Registrar baseline e criar `motor/mixagem.json` e manifesto de áudio; documentar a mudança aprovada em DESIGN §12 | M | Esquema, hashes, caminhos isolados e inventário; nenhuma geração/API necessária. |
| 2 | `motor/tempos2.py`: guarda de main; separar leitura/preparação de gravação; modo preservar bruto; cortes/padding auditáveis, sem fades sobre fala | M | Comparação de amostras e casos de borda; silêncio/arquivo vazio; nenhuma imagem. |
| 3 | `vozes/eleven.py`: seleção por frase, tomadas imutáveis, manifesto compartilhado de fala/legenda, persistência de timestamps e QA por estágio | M | Parte estrutural e respostas gravadas podem ser verificadas offline. Geração/Scribe reais dependem de aprovação e serviço; contexto só após documentação confirmada. |
| 4 | Aprovar tomadas, continuidade e pausas; adaptar `motor/tempos2.py` à narrativa de dez cenas e remover IDs/quantização de frase herdados | G | Voz montada isolada, régua, duração e rascunho de legendas; sem render de imagem. Falas congeladas antes de produzir o vídeo definitivo. |
| 5 | `motor/audio2.py`: exportar/cachear stems, separar ganhos, referência musical independente, seeds/cache por evento, automação música+efeitos | G | Null test da soma dos stems contra premix, margem por frase, determinismo do cache e A/B de colisões; sem imagem nova se eventos/tempos estiverem disponíveis. |
| 6 | Novo `motor/conferir_audio.py` proposto: energia, integridade, margem, colisões, alinhamento, relatório de aprovação e medições FFmpeg | M | Medir brutos/derivados/MP4 existente sem render. ASR usa cache; chamadas novas só quando aprovadas. |
| 7 | `motor/audio2.py`: master em duas passagens, relatório de loudness/pico, revisar limiter e medir latência | M | Master e AAC de teste; nenhuma renderização de imagem. |
| 8 | `motor/mux.sh`: modo de trocar somente áudio, copiar stream de vídeo, preservar metadados e verificar duração; `legendas2.py` só se a régua exigir | P/M | Remux e inspeção de sincronismo. Esses arquivos não foram lidos nesta missão; confirmar a implementação real antes de editá-los. |
| 9 | Gerar uma vez a imagem com a régua v5 aprovada e seus eventos definitivos; repetir apenas mix/QA/remux nos ajustes sonoros | M | O render inicial continua necessário para a nova narrativa. Depois, ganhos e ducking não dependem de outro render. |
| 10 | Escuta final do Cauê; exportar master, stems, configuração e relatório da versão aprovada | P | Conferência do MP4 final e pacote de áudio; sem regenerar voz ou imagem se nada mudou. |

**Independência do render:** hoje os eventos são registrados pelo render, conforme DESIGN §12 e `audio2.py`. Depois de congelados `tempos-pt.json` e `eventos-pt.json`, uma mudança de ganho/ducking usa esses arquivos e os stems já existentes. Não executar `render.py` por conveniência em todo ajuste de áudio.

Para a v5 ainda sem imagem final, pode-se validar voz, música e critérios de mix antes do render. A sincronização dos efeitos permanece provisória até haver eventos aprovados. Um exportador de eventos sem codificar quadros seria melhoria possível, mas sua viabilidade depende da leitura futura de `render.py`/`filme.html`; não é capacidade confirmada nem requisito para os ajustes de volume.

**Meta de fluxo:** ajustes locais de ganho/ducking/master em segundos ou poucos minutos, seguidos de remux, sem o render de aproximadamente quatro minutos citado no briefing. Não é benchmark já alcançado. A medição local de loudness da v4 terminou normalmente, mas não mede geração de stems, master completo nem remux. APIs e regeneração de voz não entram nessa promessa de tempo.

Mesmo com cache, master/loudness devem ser reavaliados no programa completo. Evitar refazer música-base ou sintetizar efeitos estáticos economiza trabalho; não sacrificar QA global para tentar atualizar somente alguns segundos do arquivo final.

## G. Riscos, preservação e decisões

### Não mudar

- `docs/v4/` e `motor2/`: somente referências de leitura; não editar, reprocessar por cima, apagar ou substituir entregas.
- Nenhum texto da narrativa aprovada, fato, função do app, identidade da voz Fernanda, música escolhida ou evento visual muda por decisão deste plano.
- Nenhuma chave, configuração de credenciais ou autorização de API é lida ou registrada. Na missão original de planejamento, somente este documento foi criado.
- Não adicionar compressor, equalizador, de-esser ou nova trilha por hábito. Primeiro preservar a voz e corrigir níveis/colisões; qualquer tratamento adicional exige defeito identificado e A/B.
- Não mascarar falha com aceleração da voz, deslocamento silencioso de legenda ou corte do final para caber na duração da imagem.

### Riscos que permanecem

| Risco | Contenção |
|---|---|
| ASR confundir pronúncia correta ou timestamp | Evidência por estágio, comparação auditiva e exceção documentada; sem aprovação automática por texto apenas. |
| Limiares absolutos perderem consoante fraca | Preservar bruto por padrão, proteção de bordas, corte auditável e análise de amostras; −60 dBFS não vira garantia. |
| Padding aumentar pausas artificialmente | Separar duração do arquivo e limites acústicos; planejar pausas pela fala, sem quantizar cada frase. |
| Ducking profundo soar artificial ou apagar efeitos úteis | Mesclar pausas, ajustar curvas, A/B na cena inteira e ouvir em baixo volume. Ganho estético não supera palavra inteligível. |
| Margem média esconder transiente | Janelas curtas, medição de pico e coexistência por evento; lista de bordas obrigatória. |
| Master/AAC desfazer equilíbrio ou introduzir atraso | Medir novamente a entrega, conferir PTS/alinhamento e não confiar só em stems ou parâmetros pedidos ao filtro. |
| Troca de frase invalidar imagem | Régua travada e verificação explícita de duração, texto visível e sincronismo; se invalidar, render correto uma vez. |
| Contexto de API não suportado / custo de regeneração | Documentação a confirmar; cache por tomada; selecionar apenas dependências afetadas, sem chamadas nesta fase. |
| Cache reaproveitar eventos ou voz antigos | Hashes de fonte/receita/régua, IDs estáveis, detecção de divergência e aprovação associada à versão exata. |

### Decisões que dependem do Cauê / Orquestrador

1. **Aprovar a voz como prioridade do mix**, incluindo reduzir ou retirar um `grave` quando competir com a primeira palavra. Sugestão: aprovar essa regra; escolher a intensidade final ouvindo A/B.
2. **Aprovar a retirada da grade obrigatória entre frases**, mantendo grade para música e cortes quando útil. Sugestão: usar pausas naturais e fechar a régua antes da imagem.
3. **Aprovar preservar brutos e desabilitar fades obrigatórios**, com corte conservador opcional após verificação. Sugestão: manter a guarda de `audio2.py`, ajustar `aparar` como descrito e não retornar à política de −45 dBFS.
4. **Confirmar o contexto de exibição e a sensação de trilha desejada.** Os alvos −16 LUFS e os parâmetros deste plano são ponto de partida para a entrega atual; o ouvido do Cauê decide presença de música, efeitos e respiros.
5. **Autorizar em etapa futura a confirmação documental e o uso de contexto no ElevenLabs**, se suportado, e a geração/Scribe necessários para a narrativa aprovada. Sem essa confirmação, o plano funciona com tomadas separadas e revisão de continuidade.

As pendências editoriais de estágio, histórico e assinatura continuam com o Orquestrador; fechar o texto antes de produzir as tomadas finais. O planejamento original não autorizava implementação. A autorização posterior da T4 consta no estado e em §H; voz, geração, render e escuta final continuam pendentes.


## H. Execução T4 — decisões e desvios registrados antes do código (26/10/2026)

A solicitação do maestro autoriza a infraestrutura no branch `feat/audio-infra`,
sem push/PR. O baseline é o commit `6f6792b`; as evidências da v4 em A são
históricas e não foram repetidas com voz v5 (ainda inexistente).

1. **Régua preservada:** não alterar IDs, `ENTRADA`, `NO_COMPASSO`, `DURACAO_MIN`,
   `secoes()` nem quantização. O manifesto compartilhado valida fala/legenda por
   posição; ganhos/preparação ganham metadados em amostras. A T5 ligará as cenas
   finais, pausas e overrides de fecho. `cenas` inicia vazio, sem copiar os IDs
   obsoletos 09/10 do exemplo B3.
2. **Preservação padrão:** `preparar()` (em `motor/tempos2.py`; substituiu `aparar()`) conserva todas as amostras e não aplica
   fade. Padding e corte são explícitos; corte só com limites confirmados e
   aprovação, mantendo 80/160 ms quando disponíveis. Silêncio, vazio e NaN
   bloqueiam preparação. Limites desconhecidos protegem o arquivo inteiro e
   produzem estado inconclusivo para escuta, nunca aprovação textual.
3. **Infra local:** utilitários de áudio em `motor/audio_util.py` e manifesto
   compartilhado em `vozes/manifesto.py`; nenhum acesso a credencial. Tomadas
   imutáveis por hash, seleção de frase e cache Scribe com resposta completa
   ficam prontos para uso futuro, sem enviar requisições nesta tarefa.
4. **Cache incremental:** WAVs float por hash de conteúdo/receita; stems com N
   amostras e automações salvas. Hash da música/evento independe da voz; ruído
   tem seed local por identidade do evento. Alterar ducking reutiliza bases.
   Voz usa ganho fixo por frase (override público), sem renormalização global.
5. **Proteção conservadora:** música/efeitos recebem rampas em tempo absoluto,
   com intervalos próximos mesclados. Overrides substituem a referência geral.
   O `grave` mantém o ataque visual; a cauda recebe ducking. Evento com ataque
   dentro da borda protegida é silenciado (decisão conservadora autorizada em
   C2). QA mede coexistência, janelas locais e bordas; falha bloqueia master.
6. **Master:** duas passagens `loudnorm`, sem limiter adicional e sem fade no
   bus de voz. Master PCM com alvo −2 dBTP, encode AAC de verificação 256 kbit/s,
   medição do AAC decodificado; teto PCM reduzido em tentativas limitadas se
   necessário. Falhar em LUFS/TP impede aceitar a entrega. Registrar modo real,
   receita, N amostras e alinhamento por correlação (limite 10 ms).
7. **Limite do teste offline:** régua sintética mínima e eventos incluem a
   antecedência de 285,5 ms do `grave` e ataque dentro da borda. Não se declara
   palavra inteligível sem voz real: prova-se margem/atenuação física e ausência
   de perda de amostras. O relatório por estágio deixa Scribe/escuta pendentes;
   QA de MP4 final é comando separado após mux (passo 8 fora de T4).

### Sequência de implementação e reprodução

- [x] Testes de preservação/manifesto; implementar preparação e seleção offline.
- [x] Testes de stems/ducking/cache; implementar sessão e exportações.
- [x] Testes de QA/master; implementar relatório por estágio e régua sintética.
- [x] Rodar `.venv/bin/python -m unittest discover -s tests -v` e
  `.venv/bin/python scripts/testar_audio.py`; registrar medidas, atualizar HANDOFF
  e commitar apenas fontes/docs no branch. Nenhum áudio entra no git.

### Ajustes do ensaio antes da revisão final

- **Medido no ensaio:** converter mono para estéreo com `-ac 2` aplicava ganho
  0,707 por canal. A leitura passou a duplicar a voz explicitamente, sem lei de
  pan implícita (B1); teste de soma reproduziu a falha e passou após a correção.
- **Medição de coexistência:** usar apenas as amostras em que há efeito dentro
  de cada janela de 100 ms, evitando diluição de um clique curto por silêncio.
  A varredura usa janelas completas (ou a frase inteira quando menor que 100 ms),
  incluindo uma janela ancorada no fim; não troca o tamanho para 10 ms na cauda.
- **Medido no teste sintético:** clique no meio da fala ficou com mínimo local
  de 12,20 dB de margem, abaixo de 15. O ensaio terá override desse evento em
  −10 dB sobre referência legada (4 dB abaixo do baseline −6). A configuração
  de produção mantém o baseline proposto e bloqueia se não passar no QA.
- **Desvio conservador:** nesta T4 a profundidade musical é configurável até o
  teto de 22 dB, com bloqueio por QA; não há correção automática que aumente o
  ducking para satisfazer o medidor. Isso deixa qualquer mudança de intensidade
  explícita em `mixagem.json`, sujeita a A/B. Efeitos sintetizados permanecem no
  cache; silenciamento de ataque é decisão da montagem dependente da voz.


### Operação da infraestrutura T4

Da raiz do repositório (links locais do ambiente já montados):

```sh
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python scripts/testar_audio.py
.venv/bin/python motor/conferir_audio.py motor/cache/teste-audio/sessao \
  --final motor/cache/teste-audio/sessao/verificacao.m4a --trechos
```

O ensaio cria régua, fontes sintéticas, stems, relatório por frase/estágio,
`master.json`, AAC e trechos A/B **somente** em `motor/cache/teste-audio/`.
Os A/B usam ganho adicional zero, contexto de 250 ms e offset registrado;
comparações com master/AAC incluem o processamento global conhecido, sem
renormalizar cada variante. `resultado.json` traz as medidas resumidas.

Depois de T3/T5 e do render com eventos aprovados:

```sh
scripts/pipeline.sh audio
.venv/bin/python motor/conferir_audio.py motor/cache/audio/pt --trechos
# Após o mux da T10: medir o arquivo realmente entregue, não só o AAC de teste.
.venv/bin/python motor/conferir_audio.py motor/cache/audio/pt \
  --final pt/frila-pitch-pt.mp4 --trechos
```

`audio2.py` também aceita `--regua`, `--eventos`, `--config`, `--trilha`,
`--voz-dir` e `--saida` para sessões isoladas. Sem `--saida`, copia o master
validado para `motor/cache/mix-pt.wav`, preservando a interface com `mux.sh`.
Falha técnica produz saída diferente de zero. `inconclusivo` com limites
acústicos pendentes permite prévia conservadora, sem aprovar texto/escuta.

A sessão guarda stems float32 a 48 kHz, origem zero e N amostras, hashes de
fontes/receitas, parâmetros/seed por evento e configuração pública. Somar
**somente** voz + música-duck + efeitos-duck. A voz mono é duplicada em L/R
sem perda de 3 dB. O cache por receita tem versão explícita no motor: alteração
de síntese deve aumentar essa versão para invalidar objetos antigos.

Overrides em `voz.frases.<id>`: `ganho_db` fixa ganho independente por tomada;
`limites_amostras: [início, fim_exclusivo]` usa amostras a 48 kHz da referência
reamostrada; `limites_confirmados: true` permite separar fala de padding.
`aparar: true` requer também `corte_aprovado: true`. Limites não confirmados
são ignorados para proteção: preserva-se o arquivo inteiro. A T5 deve recalcular
a régua após qualquer alteração de preparação/padding. Não há fades de fala.
Overrides de efeito usam `eventos.<id>.ajuste_sobre_referencia_legada_db`;
sem ID explícito no render, o manifesto identifica o evento por hash de tipo/t.

**Medido no ensaio de 12 s (não é voz v5):**

| Verificação | Resultado |
|---|---|
| Stems / null test | 576.000 amostras por stem; erro máximo 0,0 |
| Bruto reamostrado → preparado → bus | Erro máximo 0,0 nas comparações compensadas pelo ganho registrado |
| Voz / música por frase | 17,57 / 17,94 / 18,56 dB |
| Voz / efeitos, pior janela em coexistência | 25,12 dB (grave), não se aplica (silenciado), 16,20 dB (clique com override) |
| Voz / fundo, pior janela local | 14,60 / 14,84 / 15,82 dB |
| Fundo nas bordas | Máximo −39,37 dBFS (teto aproximado −38 dBFS); todas passaram |
| `grave` 285,5 ms antes | Cauda coincide por 414,5 ms; pico residual −39,48 dBFS; margem no intervalo 29,30 dB |
| `grave` com ataque na borda | Silenciado integralmente, sem deslocar o evento |
| AAC final de teste | −16,44 LUFS; −5,48 dBTP; LRA 14,60 LU; 48 kHz estéreo AAC 256 kbit/s |
| Master / AAC alinhados | 0 amostras de atraso medidas por correlação do trecho inicial; master com N amostras |
| Codec | Stream com 12,000 s, origem 0; 576.512 amostras decodificadas incluem 512 de padding AAC; não há corte do PCM |
| Normalização | Duas passagens; modo efetivo `dynamic`; sem limiter extra |

Correlação usa até os primeiros 8 s e busca ±50 ms; não é prova de sincronismo
visual nem de ausência de deriva no vídeo inteiro. Esses itens e o ASR por
frase/estágio continuam pendentes da voz e da imagem aprovadas. Não houve
chamada a ElevenLabs; teste de timestamps usa resposta simulada em diretório
temporário. As 13 regressões cobrem também silêncio/NaN/vazio, consoante fraca,
corte auditável, evento independente de ordem, cache sem ressíntese, adulteração
de stem e atraso artificial de 25 ms. O Cauê ainda precisa ouvir a voz e o mix.

Ambiente medido nesta execução: Python 3.13.11 (venv compartilhado) e FFmpeg
8.1.1. Isso registra o ambiente efetivo do ensaio, sem alterar os requisitos
ou instalar dependências no checkout principal.

## I. Áudio por bloco e auditoria de emendas — desenho antes do código

Escopo autorizado pelo Maestro: `motor/analisar_emendas.py` e
`vozes/eleven.py gerar-bloco A|B|C|D`; calibração somente de leitura sobre os
MP4 v4 (`~/Downloads/frila-pitch-pt.mp4`) e v5 (`../fvp-tempos/pt/frila-pitch-pt.mp4`).
Sem API nesta missão, sem editar `roteiro.json`, cenas ou música. Testes do
serviço usam mock. Brutos e trechos ficam ignorados pelo Git.

### I1. Método e limites de evidência

1. Decodificar o áudio a 48 kHz; detectar candidatos sem consultar a régua de
   montagem: pausas entre palavras do Scribe, quedas curtas de energia dentro
   de palavra, saltos de nível/espectro e descontinuidades locais. No estéreo,
   a diferença L−R é uma pista do fundo quando a voz está centralizada; não é
   isolamento perfeito. Sons musicais/percussivos também produzem candidatos.
2. Aceitar `--scribe` local: resposta `words` com tempos absolutos e hash do
   arquivo, ou relatório do pipeline com palavras relativas a trechos e
   `ini_amostra`. Validar hash do arquivo e de cada trecho antes de converter
   offsets; nunca chamar o serviço. Ausência de Scribe bloqueia aprovação,
   mas não impede detecção acústica. Pontuação ausente no ASR não prova frase
   partida. Hash comprova proveniência, não exatidão dos timestamps.
3. Aceitar `--manifesto`: `emendas` com `tempo`, `frases` com `id`, `ini`,
   `fim`, `tomada`, e `cortes_cena` absolutos. A1 se prova quando a mesma frase
   tem segmentos em tomadas diferentes ou uma troca de tomada cai dentro
   de seu intervalo. Emendas declaradas são todas analisadas, mesmo sem
   sinal acústico. No modo sem manifesto, nunca afirmar proveniência de
   tomada a partir só do sinal misturado.
4. A2/A5: janela protegida ±120 ms, pausa entre palavras 0,2–1,2 s,
   diferença de fundo >3 dB, clique/descontinuidade e palavra atravessando o
   corte bloqueiam. Entre blocos: pausa ≥500 ms e coincidência com corte de
   cena. Falta de evidência suficiente também bloqueia liberação automática;
   não transformar ausência de detecção em aprovação.
5. Cada candidato gera WAV ±2 s, com offset e hash, palavras vizinhas,
   medidas, motivos, decisão técnica e confiança heurística (não probabilidade).
   `emendas.json` e `resumo.txt` ordenam a fila de escuta por confiança.
   Pausa uniforme curta (0,21–0,29 s) é pista de remendo, não prova isolada.
   Registrar separadamente pausa Scribe, pausa acústica e intervalo entre
   arquivos da régua; não ajustar os números para fazê-los coincidir.

### I2. Geração contínua, futura e protegida

Contrato futuro no roteiro: `audio_blocos_aprovados: true` e `blocos` em ordem,
cada um com `id` A/B/C/D e `cenas` (IDs existentes). Cada cena pertence a um
único bloco; texto vem integralmente de `pt.fala`. Antes da aprovação/metadata,
`gerar-bloco` falha antes de ler chave ou chamar a rede. Sem preencher esse
contrato no roteiro atual. Uma requisição TTS por bloco, todas as frases no
mesmo `text`, `previous_text`/`next_text` dos blocos adjacentes. Sem corte,
fade, padding ou alinhamento interno à música. Scribe recebe o WAV inteiro;
resposta, palavras e pausas naturais são preservadas com hashes. Cada execução
grava diretório exclusivo em `vozes/tomadas/blocos/pt/<bloco>/<uuid>/`, inclusive
se falhar o Scribe; nunca altera tomada anterior. Nenhuma aprovação automática
de texto, escuta ou produção. Defeito de frase pede nova tomada do bloco.

### I3. Sequência e verificações

Documentar → testes vermelhos (frase dividida, palavra no corte, silêncio
natural, fundo >3 dB, clique, falta de Scribe, offsets/hash incorretos,
detecção sem manifesto; serviço mockado e tomadas imutáveis) → implementar →
testes verdes → calibrar v5/v4 sem manifesto → confrontar com régua e fontes
existentes como evidência independente → registrar tempos e limitações aqui →
commit local, sem push → `maestri ask "Claude Code"` com resultados e caminhos.
Sem acesso perceptivo ao áudio no runtime, não registrar escuta como feita;
entregar os trechos para escuta do Maestro/Fabrício. Calibração acústica não
substitui a revisão audiovisual de cada bloco quando houver voz aprovada.

### I4. Calibração realizada — resultado insuficiente para encerrar a validação

**Medido aqui, sem API, sem escuta perceptiva:** v5 decodificada com 108,224 s
(inclui padding do codec); v4 com 76,736 s. SHA-256 dos MP4:

- v5: `3470ff03f57aaf0fa55939dd10463df9e0125fc96f1310ad55af1cc77fcd5889`.
- v4: `6a32a3bbd4bd6ec3ae458b3886c5ac41cf7a612c7270b0ff09af1acb2f280565`.

O Scribe da v5 é `../fvp-tempos/motor/cache/audio/pt/scribe-aac-final.json`:
hash do MP4 e de todos os trechos conferidos, offsets `ini_amostra/48000`.
Uma palavra `1` tem duração zero em 15,236458 s; preservada, gera pendência,
não um intervalo inventado. Nenhum Scribe correspondente ao MP4 v4 foi
localizado; palavras da régua não foram apresentadas como reconhecimento.

Detecção cega (sem manifesto): **69 candidatos na v5 e 48 na v4**. São filas
de suspeitas, não contagens de emendas reais. Todas têm WAV ±2 s, hash,
offset, medidas e decisão; palavras Scribe ao redor somente onde disponíveis.
Todas permanecem bloqueadas para aprovação automática. Confiança é ordinal
de evidência acústica/temporal, não probabilidade de frase cortada.

| Prioridade v5 | Tempo (s) | Pista e limite |
|---|---:|---|
| Transiente, confiança 0,85 | 27,314000 | Clique/descontinuidade; pausa Scribe de 3,346 s. Sem palavra no ponto; não comprova A1. |
| Transiente, confiança 0,85 | 95,674750 | Clique entre “gente” e “Mais”; pausa Scribe 0,600 s. Não comprova A1. |
| Continuação, confiança 0,74 | 54,020833 | “pública:” [53,331–53,711] → “quantas” [54,331–54,751]; pausa 0,620 s dentro do mesmo segmento Scribe. |
| Continuação, confiança 0,74 | 62,090208 | “avaliam:” [61,340–61,840] → “chamaria” [62,340–62,760]; pausa 0,500 s. |
| Continuação, confiança 0,74 | 77,751833 | “piloto:” [76,832–77,292] → “oito” [78,212–78,412]; pausa 0,920 s. |
| Continuação, confiança 0,74 | 79,541833 | “semanas,” [78,512–79,112] → “50” [79,972–80,212]; pausa 0,860 s. |
| Faixa curta, confiança 0,60 | 8,710000; 60,400208; 72,929208 | Pausas Scribe 0,220; 0,280; 0,220 s. Pausa curta isolada não prova remendo. |
| Queda dentro de palavra, confiança 0,50 | 8,030; 13,025; 16,355; 25,480; 30,045; 32,855; 44,460; 64,500; 65,775; 77,150; 90,385 | Também pode ser oclusiva/sílaba natural ou erro de timestamp. Ouvir antes de diagnosticar corte. |

O confronto posterior com os 28 registros `frases` do manifesto existente da
v5 deu **zero frases comprovadamente divididas entre tomadas**. Isso não
refuta o Fabrício: os IDs do pipeline não são validação semântica independente.
As pausas prioritárias acima podem ser naturais; **os 3–5 casos relatados ainda
não foram confirmados**. O Maestro aprovou explicitamente entregar candidatos
ordenados e distingui-los de A1 comprovada; não forneceu marcações de escuta.

Na v4, confronto posterior com `docs/v4/tempos-pt.json`:

| Centro do trecho (s) | Fim anterior → início seguinte | Intervalo entre arquivos (s) | Cena |
|---:|---|---:|---|
| 24,487000 | 24,382 → 24,592 | 0,210 | c06-passos-a |
| 26,695500 | 26,586 → 26,805 | 0,219 | c06-passos-a |
| 32,356500 | 32,252 → 32,461 | 0,209 | c07-passos-b |
| 37,972500 | 37,828 → 38,117 | 0,289 | c08-mapa |
| 70,897500 | 70,725 → 71,070 | 0,345 | c16-logo — exceção do fecho |

São intervalos da régua, **não silêncio acústico medido entre fonemas**. O
0,209 s explica o arredondamento informado de 0,21 s. Os centros detectados
cegamente mais próximos dos quatro primeiros foram 24,315; 26,750; 32,105;
36,855 s: desvios −172; +54,5; −251,5; −1117,5 ms. Só **1/4** fica a ±120 ms;
esse confronto mede proximidade, não precisão/recall validada por ouvido.
Portanto, **a recuperação cega dos remendos da v4 não está validada**. Os cinco
trechos exatos da régua foram extraídos em uma saída separada, identificada
como referência assistida, sem fingir que o detector os descobriu sozinho.

Primeira varredura gerou 287/235 candidatos (v5/v4): confundiu muitas sílabas
e ataques musicais com emendas. Ajuste registrado: seleção de valas passou
de −37 para −55 dBFS, duração mínima 40 ms e contraste ≥25 dB; saltos
espectrais só em janelas com nível <−40 dBFS; pausas do Scribe foram mantidas.
Isso **restringe candidatos** e reduz confiança de valas fonéticas; não afrouxa
os gates A1–A5 (±120 ms; 3 dB; 0,2–1,2 s; ≥500 ms entre blocos). Um ensaio
descartável de cancelamento estéreo adaptativo não separou de modo confiável
o fundo da v4 e não foi incorporado. O mix final sozinho não identifica com
certeza a proveniência de uma tomada; faltam Scribe da v4 e rótulos auditivos.

### I5. Reprodução, artefatos e pendências

```sh
.venv/bin/python -m unittest motor.test_emendas vozes.test_blocos
.venv/bin/python -m unittest discover -s tests
.venv/bin/python motor/analisar_emendas.py ../fvp-tempos/pt/frila-pitch-pt.mp4 \
  --scribe ../fvp-tempos/motor/cache/audio/pt/scribe-aac-final.json \
  --saida motor/cache/emendas/v5
.venv/bin/python motor/analisar_emendas.py ~/Downloads/frila-pitch-pt.mp4 \
  --saida motor/cache/emendas/v4
```

Código de saída **2** nessas calibrações é esperado: bloqueio, sem aprovação.
Saídas locais ignoradas: `motor/cache/emendas/RELATORIO.md` (fila inteira com
links), `{v5,v4,v4-referencia}/emendas.json`, `resumo.txt` e `trechos/*.wav`;
`v4-referencia-manifesto.json`; `v5-confronto-proveniencia.json`.
O auxiliar local `motor/cache/emendas/reproduzir.py` repete as duas varreduras
e os confrontos, sem rede. Não é fonte de produção nem arquivo versionado.

Exportação conferida: os 122 WAVs (69 + 48 + 5) são idênticos, amostra por
amostra, às fatias dos MP4 decodificados; hashes dos trechos e dos originais
conferidos novamente (`verificacao-exportacao.json`). Nenhum corte/fade/ganho
foi aplicado aos trechos de auditoria.

Validação offline: 17 testes novos e 13 regressões existentes; nenhum serviço
real chamado. PCM do bloco preservado amostra por amostra, uma única requisição
TTS mockada por execução, contextos dos vizinhos, timestamps/pausas e segunda
tomada sem alterar a primeira. Roteiro pendente impede rede antes de ler chave.
Pendências: confirmar/refutar candidatos de v5 de ouvido; obter Scribe/rótulos
da v4 para calibrar recuperação cega; revisão audiovisual quando existir bloco
aprovado. Não há geração real, mix novo, render, aprovação de som ou aprovação
do roteiro nesta entrega.
