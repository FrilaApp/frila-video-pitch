# Plano de áudio — Frila v5, PT-BR

**Estado atual (26/10/2026): as quatro vozes estão aprovadas de ouvido pelo Fabrício. Seleção: A `b92c749b…`, B `43bbc466…`, C seed 1 `5e4184f8…` (pausa A8 de 0,600 s aceita como exceção de ouvido, mantendo a vírgula) e D `4acfe322…`. C seed 2 foi descartada, sem apagar ou modificar a tomada. Nenhuma regeneração autorizada. §L documenta a régua oficial T5; §§A–K preservam o histórico.**

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
MP4 v4 (`~/Downloads/frila-pitch-pt.mp4`) e v5 reprovada (`/Users/fabriciotosta/dev/video-frila/referencias/v5-reprovada/frila-pitch-pt.mp4`).
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

## J. Tarefa 2 — Ana Dias, A8 determinístico e piloto real do Bloco A

### J1. Decisão antes do código

**Informado e autorizado pelo Fabrício/Maestro em 26/10/2026:** opção C,
Ana Dias (`MZxV5lN3cv7hi1376O0m`), `eleven_multilingual_v2`, estabilidade
0,55, similaridade 0,75, estilo 0,10, velocidade 1,0, seed 1, contexto vizinho.
Direção A9: português do Brasil neutro, formal, editorial/jornalístico, sem
sotaque regional. Voz/parâmetros não são substituídos para satisfazer o ASR.
`use_speaker_boost: true` é preservado do cliente existente e registrado.

Os PRs #6, #7 e #8 entraram em main; por orientação posterior do Maestro,
esta tarefa continua em `feat/bloco-a`, criado de main `7b6abd2`, no worktree
`fvp-audio-blocos`. Isso substitui a entrega no branch antigo. O rebase sobre
`docs/voz-editorial` foi feito antes desse aviso; nenhuma alteração nova foi
transportada manualmente. Roteiro/PLAYBOOK integrados são a fonte vigente.

**Medido aqui:** Bloco A aprovado tem 299 caracteres no texto enviado,
incluindo espaços/pontuação, quatro cenas e seis frases. O contexto seguinte
é o Bloco B inteiro, em `next_text`; `previous_text` é vazio. Nenhum contexto
é inserido na fala. Não editar o texto para aproximá-lo de “330 caracteres”.
Chave: ler `~/.config/elevenlabs/chave` sem imprimi-la. Uma única requisição
TTS para A; uma conferência Scribe do bruto inteiro. Nenhuma geração B/C/D,
nem repetição automática de TTS. Gravar consumo/contagem de caracteres,
receita, hashes e resultado; preservar a tomada mesmo se falhar o Scribe/A8.

### J2. A8: limite, alinhamento e decisão

- Dois-pontos em `fala` bloqueiam antes de gerar; dois-pontos em `legenda`
  continuam permitidos. O detector também relata essa violação ao auditar
  texto/áudio já existentes.
- Usar as frases do **texto de origem**, separadas por `. ? !`; não inferir
  fronteiras pela pontuação do Scribe, que em v04 substituiu dois-pontos por
  ponto. Alinhar palavras normalizadas (mesmas equivalências do cliente) às
  frases e conservar timestamps Scribe. Divergência/ambiguidade entra como
  pendência, nunca recebe aprovação silenciosa.
- Interpretação explícita do “~0,5 s”: **0,500 s inclusivo**. O caso obrigatório
  de 62,090208 s mede exatamente 0,500 s no cache; comparar com tolerância
  numérica de 1 ns, sem alterar os tempos. Pausas entre frases não são A8.
- A8 recebe texto de `--falas JSON` (roteiro, manifesto de frases ou metadata
  da tomada); emite todas as pausas classificadas, violações de texto/pausa,
  palavras e WAV ±2 s para cada pausa reprovada, mesmo se `emendas: []`.
- Conforme PLAYBOOK §5b, suspeitas cegas sem calibração **informam**; A8 e
  frase atravessando emenda declarada **bloqueiam**. Distinguir `bloqueado`,
  pendências e escuta; nenhum campo libera aprovação artística do Fabrício.

### J3. Sequência de validação e geração

Documentar → testes vermelhos (baseline Ana Dias; dois-pontos antes da rede;
fronteira de frase do texto sobre pontuação ASR; pausa 0,500 s inclusive;
pausa entre frases permitida; falha sem emenda física) → implementar →
testes verdes → calibrar A8 com v5/Scribe e fala original, procurando os quatro
tempos 54,0 / 62,1 / 77,8 / 79,5 s → gerar A uma vez → guardar Scribe, palavras
e pausas → executar auditoria no bruto com manifesto sem emendas internas →
registrar medidas e limites aqui → commit local sem push → `maestri ask`.

A ausência de vídeo novo do Bloco A e de acesso perceptivo não será tratada
como escuta executada. A8 passado é resultado objetivo; A9 editorial e a
naturalidade exigem a escuta do Fabrício. Não aprovar som por gate técnico.

### J4. Resultados medidos — geração real e calibração

**Calibração A8 na v5 reprovada, com fala original do manifesto e Scribe em
cache:** recuperou **4/4 casos obrigatórios** dentro de ±120 ms dos tempos
informados. Não é resultado da detecção cega. Há um quinto caso:

| Centro (s) | Pausa Scribe (s) | Palavras ao redor | Resultado |
|---:|---:|---|---|
| 21,804458 | 0,560 | “fica.” [21,244–21,524] → “Nos” [22,084–22,224] | A8; texto original tem dois-pontos, não ponto |
| 54,020833 | 0,620 | “pública:” [53,331–53,711] → “quantas” [54,331–54,751] | A8; caso obrigatório |
| 62,090208 | 0,500 | “avaliam:” [61,340–61,840] → “chamaria” [62,340–62,760] | A8; limite inclusivo, caso obrigatório |
| 77,751833 | 0,920 | “piloto:” [76,832–77,292] → “oito” [78,212–78,412] | A8; caso obrigatório |
| 79,541833 | 0,860 | “semanas,” [78,512–79,112] → “50” [79,972–80,212] | A8; caso obrigatório |

Mais quatro violações textuais de dois-pontos (v04/v08/v09/v11). O alinhamento
global da v5 é incompleto, como já registrado no Scribe; os cinco intervalos
acima estão alinhados às respectivas frases de origem. Palavra de duração
zero permanece como pendência. A v5 retorna bloqueio objetivo e código 2.
Os trechos e palavras estão em `motor/cache/emendas/a8-v5/`.
**Informado pelo Fabrício no PLAYBOOK A8:** a escuta confirmou que as pausas
internas após dois-pontos causaram a percepção dos “3 a 5 cortes”. Essa decisão
substitui a hipótese histórica de §§I4–I5; não é diagnóstico de corte físico.

**Bloco A real:** uma requisição TTS, uma Scribe, sem regeneração; parâmetros
exatos de J1, seed 1, contexto do B (somente contexto). WAV PCM mono, 24 kHz,
16 bits, **549.477 amostras / 22,894875 s**. Nenhuma amostra aparada, nenhum
silêncio/fade inserido; nenhuma geração B/C/D. Fonte:

`vozes/tomadas/blocos/pt/A/b92c749be0314efea49558e467da3eb8/bruto.wav`

SHA-256: `056f3ac2572220ed2b10160548dc276f4ff668fe7b84584519d5257f7e65b596`.
`bruto.json` contém receita e hash da resposta `scribe.json`; os três arquivos
permanecem na tomada, sem alteração após geração. Inventário de hashes em
`motor/cache/bloco-a/hashes-tomada.json`.

Scribe: **46 entradas de palavra**, timestamps válidos; texto confere após as
equivalências já existentes (19h/dezenove horas, 10/dez, 1/um, 70%/setenta por
cento). Não houve substituição para esconder divergência. Alinhamento A8
completo nas seis frases; **zero dois-pontos, zero pausas internas ≥0,500 s**.
Todas as 40 pausas internas foram registradas. Maiores:

| Intervalo (s) | Pausa (s) | Palavras |
|---|---:|---|
| 5,000 → 5,480 | 0,480 | Abrasel → nove |
| 8,820 → 9,300 | 0,480 | restaurantes → acham |
| 18,500 → 18,900 | 0,400 | restaurantes → a |
| 0,360 → 0,740 | 0,380 | Hoje → 19h |

| Frase | Início → fim Scribe (s) |
|---|---|
| v01-gancho-1 | 0,060 → 1,740 |
| v01-gancho-2 | 2,120 → 3,300 |
| v02-dor1-1 | 3,860 → 10,660 |
| v03-dor2-1 | 11,320 → 14,840 |
| v03-dor2-2 | 15,500 → 16,680 |
| v04-dor3-1 | 17,200 → 22,260 |

As cinco pausas **entre frases** são 0,380 / 0,560 / 0,660 / 0,660 / 0,520 s;
não são falha A8. Timestamps Scribe são pista temporal, não medição exata de
fonema/silêncio. Folgas estimadas na tomada: 60 ms antes da primeira palavra
e 634,875 ms depois da última; não foram criadas por edição.

Manifesto do bruto declara **zero emendas internas**: toda a fala vem de uma
tomada TTS contínua. Auditoria com manifesto: `bloqueado: false`, A8
`sem_falha`, `apto_para_escuta: true`, `aprovado: false`, escuta pendente.
Varredura cega adicional produziu **26 pistas informativas**, incluindo nove
valas dentro de palavras; nenhuma é prova de corte, nem bloqueia o bruto
contínuo sob §5b. Não removi pausas/sílabas para satisfazer a heurística.

**Consumo medido no serviço:** 299 caracteres enviados em `text`. O histórico
TTS `fKYWQFm3rODJ2NwrcphW` informa `character_count_change_from: 19775` e
`character_count_change_to: 19895`: **débito de 120 no contador da chamada**.
O contador global posterior passou a 19902 (variação 127); não atribuí os sete
restantes sem evidência específica. A consulta imediatamente após geração
ainda mostrava 19775; foi conferida de novo e confrontada com o histórico da
voz/texto exatos. Não inferir custo pelo tamanho do contexto ou por tarifa.
Registros: `motor/cache/bloco-a/producao.json` e `consumo.json`, sem chave.

### J5. Reprodução e handoff

```sh
# Auditorias offline; não repetir a geração real desta autorização.
.venv/bin/python -m unittest motor.test_emendas vozes.test_blocos
.venv/bin/python -m unittest discover -s tests
.venv/bin/python motor/analisar_emendas.py \
  vozes/tomadas/blocos/pt/A/b92c749be0314efea49558e467da3eb8/bruto.wav \
  --scribe vozes/tomadas/blocos/pt/A/b92c749be0314efea49558e467da3eb8/bruto.json \
  --manifesto motor/cache/bloco-a/manifesto.json \
  --falas motor/cache/bloco-a/manifesto.json --saida motor/cache/bloco-a/auditoria
```

27 testes de áudio/blocos e 13 regressões existentes passaram (40 no total).
Cobrem A8 no limite, frase definida pelo roteiro, quatro referências reais,
ausência/divergência de Scribe, A8 sem emenda física, suspeita cega informativa,
baseline Ana Dias e dois-pontos antes da rede. Normalização foi compartilhada
em `vozes/manifesto.py`, sem duplicá-la nem importar o cliente de API no detector.
Saída 2 agora significa **bloqueio objetivo**; saída 0 pode conter pistas e
pendências. Ler `a8.estado`, `apto_para_escuta` e o resumo; somente o Fabrício
aprova. `aprovado` global permanece falso até essa decisão.

Pacote local ignorado pelo Git: `motor/cache/bloco-a/RELATORIO.md` (WAV, 46
palavras, todas as pausas e pistas com trechos ±2 s), `manifesto.json`,
`auditoria/emendas.json`, `varredura-cega/emendas.json`, consumo e hashes.
Os 100 trechos exportados nesta conferência (26 do A e 74 da v5, incluindo
cinco A8) foram comparados amostra por amostra aos originais decodificados;
hashes íntegros e três arquivos da tomada A sem alteração, registrados em
`motor/cache/bloco-a/verificacao-exportacao.json`.
Nenhum vídeo do bloco foi entregue para revisão audiovisual nesta tarefa;
escuta perceptiva e avaliação editorial/A9 continuam pendentes do Fabrício.

## K. Blocos B/C/D e auditoria local das fronteiras — plano antes da execução

**Autorizado pelo Fabrício/Maestro:** A aprovado, PR #10 integrado. Branch
`feat/blocos-bcd`, criado de main e atualizado sobre `61a8407` (inclui PR #9,
que só altera a dependência OpenCV). Nenhuma nova geração de A. Hashes dos
três arquivos da tomada aprovada de A conferidos antes de começar.

Gerar B, C e D sequencialmente, **uma requisição TTS e uma Scribe por bloco**,
sem loop/repetição automática. Conferir texto, tempos e A8 imediatamente após
cada bloco; se divergir o Scribe, houver timestamp inválido ou falha/pendência
A8, parar antes do próximo bloco e avisar o Maestro. Não regenerar sem nova
autorização. Tomadas/receitas/respostas preservadas inclusive se houver falha.

Mesma baseline de A: Ana Dias `MZxV5lN3cv7hi1376O0m`,
`eleven_multilingual_v2`, estabilidade 0,55, similaridade 0,75, estilo 0,10,
velocidade 1,0, seed 1, speaker boost true. Chave lida do arquivo autorizado,
sem exposição. Contextos em campos separados: B leva A/C; C leva B/D; D leva
C/next vazio. Texto integral do roteiro, sem reescrita. **Medido antes da
geração:** B 273, C 279, D 118 caracteres; total previsto 670 caracteres em
`text`. Consumo efetivo será conferido no histórico do serviço, não estimado
como equivalente ao tamanho do texto.

### K1. Auditoria por bloco

Guardar WAV, metadata, Scribe bruto, todas as palavras e pausas. Rodar
`motor/analisar_emendas.py` com Scribe vinculado por hash, fala de origem e
manifesto local da tomada sem emendas internas. A8 mantém o limite inclusivo
0,500 s de §J. Não usar pistas cegas como reprovação sem calibração (§5b).
No handoff, informar ausência de escuta perceptiva e não aprovar artisticamente
B/C/D por gate técnico.

### K2. Fronteiras locais, sem régua nem mixagem

**Confirmado pelo Maestro nesta tarefa:** não existem clipes ou manifesto de
cortes aprovados para o texto enxuto de 13 cenas. Os clipes antigos não servem.
A coincidência estrutural vem do roteiro: A termina em v04; B, v09; C, v12;
D, v14. Auditar A→B (v04/v05), B→C (v09/v10), C→D (v12/v13), sem imagem.
Sincronismo com corte de cena fica **PENDENTE** até haver imagem e T5.

Para cada par, medir cauda do bruto anterior e início do seguinte: tempos das
palavras extremas, energia em janelas curtas, ruído e salto na junção. Extrair
somente trecho local da cauda/início para escuta, com origem/hash/offsets;
não cortar, preencher, sobrescrever ou reposicionar nenhuma tomada original.
Uma prévia local de emenda não é régua oficial nem mixagem do filme.

Relatar separadamente: folga temporal estimada pelo Scribe; energia medida nas
bordas; pausa mínima planejada entre blocos de **500 ms**; e eventual folga
adicional necessária para montar uma emenda com proteção ±120 ms, respeitando
também A5 (0,2–1,2 s). Nenhuma montagem global ou ajuste musical nesta tarefa.
Frase completa e tomada única são conferidas pelo texto/proveniência; ausência
de palavra em Scribe não basta para afirmar silêncio acústico. Se a junção
direta não cumprir A2/A5, registrar a falha e a necessidade de desenho da pausa
na futura montagem, sem modificar os brutos nem afrouxar limiares.

### K3. Entrega e critérios

`motor/cache/blocos-bcd/RELATORIO.md`, JSONs por bloco/fronteira, palavras,
pausas, hashes e trechos locais; WAVs nas tomadas imutáveis de B/C/D. Registrar
contagem por requisição e consumo retornado pelo serviço. Commit local no
branch novo, sem áudio/vídeo/cache, sem push. Encerrar com `maestri ask
"Claude Code"` contendo resultados, limites e caminhos. Se a execução parar,
o relatório identifica o bloco que falhou e os que não foram gerados.


### K4. Decisão posterior do Maestro — D independente e uma alternativa de C

Autorizado nesta sessão após medir C/seed 1: gerar D uma vez, baseline original,
com `previous_text` igual ao texto inteiro de C, independentemente da pausa de C.
Depois, uma única regeneração de C com **seed 2**, mesmas palavras/pontuação,
voz e parâmetros, contextos B/D. Preservar seed 1 imutável. Comparar pausas e
A8 nas duas tomadas; se seed 2 passar, selecioná-la para as prévias locais.
Se também apresentar pausa interna ≥0,500 s, parar sem terceira tomada e
entregar ambas com trechos ±2 s para decisão do Fabrício. Uma eventual troca
da vírgula de “semanas, cinquenta” é apenas proposta para o Fabrício, sem
alteração do roteiro ou nova chamada autorizada nesta tarefa.

A decisão substitui apenas a parada antes de D e autoriza exatamente uma
nova chamada TTS/Scribe de C; não libera outras regenerações. Alertas cegos
continuam Nível 2, para escuta. O gate de Nível 1 é `./scripts/verificar.sh`
no próprio worktree, rebaseado em main `30da07c` (PR #11); scripts canônicos
não serão duplicados no commit de áudio. `.venv` permanece compartilhado.

### K5. Retomada da auditoria — sem novas gerações

Após reinício, os arquivos existentes já contêm Scribe e auditoria de B, C/1,
C/2 e D. C/2 também falha na A8 (0,620 s em “semanas, cinquenta” e 0,520 s
em “Depois, bares”); nenhuma tomada de C fica selecionada para produção.
Reexecutar as auditorias offline e preservar as duas alternativas. Não chamar
TTS ou Scribe novamente. Consultas GET ao histórico/consumo servem apenas
para fechar a contabilidade das quatro chamadas TTS já feitas.

As prévias de fronteira serão a concatenação direta, sem ganho/fade/padding,
dos últimos e primeiros 2,5 s dos brutos, em arquivos locais independentes.
Auditar A→B e ambas as alternativas B→C e C→D, com um único ponto de junção
por prévia, manifesto com as frases completas e offsets de cada origem.
Essa prévia permite localizar defeitos da junção direta, sem fingir que uma
pausa planejada já foi aprovada. Medir e reportar a pausa entre palavras,
proteção ±120 ms, energia/ruído/salto e eventual folga adicional necessária;
nenhum corte de cena será inventado para satisfazer o detector. Sincronismo
visual e musical, escuta perceptiva e avaliação A9 permanecem pendentes.
O relatório incluirá todas as palavras/pausas e os trechos de todas as falhas
A8, além das pistas cegas (Nível 2), declarando os limites da calibração.

### K6. Resultados da retomada — C bloqueado, sem seleção

**Medido aqui, offline:** Scribe, texto normalizado, hashes das respostas e
timestamps conferidos novamente nas cinco tomadas. Reexecutadas auditoria
com manifesto e varredura cega por `motor/analisar_emendas.py`. Nenhuma chamada
TTS/Scribe nesta retomada; somente dois GETs de histórico/consumo. Sem Computer,
GUI, régua global, mixagem, música, master ou render.

| Tomada | Duração (s) | Palavras Scribe | Maior pausa interna (s) | A8 | Pistas cegas |
|---|---:|---:|---:|---|---:|
| A, seed 1, `b92c749b…` | 22,894875 | 46 | 0,480 | sem falha; aprovado pelo Fabrício conforme briefing | 26 |
| B, seed 1, `43bbc466…` | 19,922708 | 46 | 0,420 | sem falha | 22 |
| C, seed 1, `5e4184f8…` | 19,551208 | 40 | 0,600 | falha | 22 |
| C, seed 2, `1eb568e0…` | 20,433542 | 40 | 0,620 | duas falhas | 26 |
| D, seed 1, `4acfe322…` | 8,962917 | 19 | 0,320 | sem falha | 9 |

O manifesto de cada bruto declara zero emendas internas; cada frase pertence
a uma tomada contínua. Não houve corte, fade, ganho ou silêncio inserido nos
brutos. Os 15 arquivos (cinco WAVs, cinco metadados, cinco respostas Scribe)
permanecem idênticos antes/depois; snapshots anteriores de A e C/1 também
conferidos. **116 trechos** exportados comparados amostra por amostra às
origens decodificadas, erro máximo 0,0. As cinco prévias de fronteira também
reproduzem exatamente os segmentos decodificados, sem alterar os originais.

#### C — entregar as duas tomadas para escuta, sem terceira tentativa

| Tomada | Palavra anterior (s) | Palavra seguinte (s) | Pausa (s) | Centro (s) | Trecho ±2 s (s) |
|---|---|---|---:|---:|---|
| Seed 1 | semanas, [6,320–6,860] | 50 [7,460–7,660] | 0,600 | 7,160 | 5,160–9,160 |
| Seed 2 | semanas, [6,840–7,360] | 50 [7,980–8,180] | 0,620 | 7,670 | 5,670–9,670 |
| Seed 2 | Depois, [15,580–16,100] | bares [16,620–16,980] | 0,520 | 16,360 | 14,360–18,360 |

Trechos, a partir de `motor/cache/blocos-bcd/`:

- `C/auditoria/a8/001-7.160s.wav`;
- `C-seed2/auditoria/a8/001-7.670s.wav`;
- `C-seed2/auditoria/a8/002-16.360s.wav`.

**Proposta, sem execução:** vale submeter ao Fabrício um teste retirando só a
vírgula de “semanas, cinquenta”, mesmas palavras. O intervalo repetiu a falha
nas duas seeds; a relação com pontuação é hipótese, não causa comprovada nem
garantia de solução. Seed 2 tem ainda a pausa independente em “Depois, bares”.
Não trocar por ponto apenas para reclassificar a falha. Nenhum texto foi
alterado; nova tentativa seria do bloco inteiro, mediante nova autorização.

#### Fronteiras — prévias diretas, sem liberação para montagem

Todas têm duração local de 5 s e **uma junção em 2,500000 s**; analisador
exporta 0,500–4,500 s (±2 s). Origem anterior: últimos 2,5 s; seguinte:
primeiros 2,5 s. Os limites externos são recortes de contexto para escuta,
não cortes internos de frase na montagem. Os manifestos conservam os
intervalos das frases completas e não inventam cortes de cena.

Pausa planejada mínima: **500 ms**, teto A5 de 1,2 s. A pausa direta abaixo é
estimativa entre palavras Scribe, não silêncio acústico. A folga adicional
é só limite inferior temporal para futuro desenho, não receita aplicada.

| Fronteira | Fim da origem anterior (s) | Cauda / início Scribe (ms) | Pausa direta (ms) | Folga adicional mínima (ms) | Δ fundo estimado (dB) |
|---|---:|---|---:|---:|---:|
| A→B | 22,894875 | 634,875 / 120 | 754,875 | 0 | 7,34 |
| B→C/1 | 19,922708 | 582,708 / 100 | 682,708 | 20 | 36,21 |
| C/1→D | 19,551208 | 531,208 / 60 | 591,208 | 60 | 36,28 |
| B→C/2 | 19,922708 | 582,708 / 80 | 662,708 | 40 | 40,95 |
| C/2→D | 20,433542 | 433,542 / 60 | 493,542 | 60 | 29,64 |

Cada par está em `motor/cache/blocos-bcd/fronteiras/<anterior>--<seguinte>/`,
com `previa-direta.wav`, `manifesto.json`, `scribe-local.json`, `resultado.json`
e `auditoria/` (emendas, palavras e trecho ±2 s). Os tempos do Scribe local
foram deslocados das respostas originais; nenhuma nova transcrição.

As cinco prévias retornam bloqueio no detector de emendas declaradas, sem
liberação para montagem. B→C e C→D têm palavra dentro de ±120 ms segundo
o Scribe. C/2→D também falha no mínimo de 500 ms. A→B fica no limite de
+120 ms pelo Scribe, mas tem energia na borda. Nenhum manifesto indica frase
dividida, e não houve clique sinalizado no ponto; ausência de alerta não
prova integridade perceptiva da palavra na origem. Diferença de fundo e
energia são pistas de Nível 2: o método mono/mid inclui voz/respiração, não
isola ruído, e algumas janelas alcançam a primeira palavra. Limiares mantidos.

**Sincronismo visual e musical PENDENTE:** não há imagem do texto enxuto nem
cortes aprovados; o detector registra “sem corte de cena correspondente”.
Nenhuma fronteira foi marcada como aprovada. Faltam escuta perceptiva e revisão
contra vídeo, não executáveis neste runtime; aprovação continua com Fabrício.

#### Contabilidade e calibração

Histórico do serviço: B **273** caracteres em `text` / débito declarado **109**;
C/1 **279 / 112**; D **118 / 47**; C/2 **279 / 112**. Totais desta etapa:
**949 caracteres enviados e 380 de soma dos deltas TTS declarados**. A, de
etapa anterior, permanece 299 / 120. Registros em `historico-final.json`.
Contador global: **19.902 → 20.303**, variação **401**; residual de **21** sem
atribuição comprovada. Os snapshots de D e C/2 se sobrepõem; os deltas por
item não são extrato exclusivo conciliado nem custo monetário. C/1 e C/2
identificados no histórico pela ordem informada e instantes, pois o texto é
idêntico e os campos consultados não trazem seed. Não atribuir o residual
automaticamente ao Scribe.

Releitura das calibrações existentes com hashes das fontes/Scribe reconferidos:
A8 recupera **4/4** referências v5 em ±120 ms (54,020833 / 62,090208 /
77,751833 / 79,541833 s). Na v4, detector cego alcança **1/4** centros da régua
em ±120 ms; é proximidade, não recall auditiva validada. As demais heurísticas
não têm recall validada e somente informam (§5b). Não houve nova escuta.

#### Artefatos e reprodução

- Relatório completo local: `motor/cache/blocos-bcd/RELATORIO.md` — cinco WAVs,
  todas as 191 palavras Scribe e 186 pausas, falhas A8, 105 pistas cegas,
  fronteiras com palavras/offsets, consumo e limites de evidência.
- Resultados por tomada: `{A,B,C,C-seed2,D}/resultado-final.json` e
  `auditoria/emendas.json`; integridade em `verificacao-final.json`;
  calibração em `calibracao-conferida.json`, sob o mesmo cache.
- WAVs imutáveis: `vozes/tomadas/blocos/pt/<bloco>/<uuid>/bruto.wav`, com
  `bruto.json` e `scribe.json` ao lado; UUIDs completos no relatório.
- Auxiliar local offline: `.venv/bin/python
  motor/cache/blocos-bcd/retomar_auditoria.py`; fica no cache ignorado e não
  integra o código de produção. Usa o analisador versionado, sem API.
- Gate canônico: `./scripts/verificar.sh`, no `.venv` compartilhado pelo
  `scripts/worktree.sh`: **passou, código 0**, com AST/dependências, linters
  de roteiro/cópia, ausência de binários/chaves e **56 testes** (13 + 16 + 27).
  Log local: `motor/cache/blocos-bcd/verificar-final.log`. `git diff --check`
  também passou. Isso valida a infraestrutura, não aprova o som de C nem
  libera as fronteiras.

## L. T5 — seleção aprovada e régua oficial (plano antes do código)

**Decisão do Fabrício, recebida em 26/10/2026:** A `b92c749be0314efea49558e467da3eb8`,
B `43bbc4666c484358834e92131dad38ce`, C **seed 1**
`5e4184f8bc7840f39acd9e74169417c1` e D
`4acfe322e133423faa154465d85fc3cf` aprovados de ouvido. Em C, a pausa de
**0,600 s**, entre “semanas,” [6,320–6,860] e “cinquenta”/Scribe “50”
[7,460–7,660], foi **aceita como exceção de ouvido pelo Fabrício nessa data**.
O resultado medido da A8 continua falha; registra-se a aceitação separada,
vinculada ao hash da tomada e ao intervalo, sem aumentar o limite de 0,500 s.
Vírgula e palavras permanecem. C seed 2 é descartada para seleção, imutável.
Essa decisão substitui o estado histórico de bloqueio em §K6.

### L1. Contrato e sequência

1. Gravar a seleção em `vozes/selecao-blocos-pt.json`, versionada, com UUID,
   hashes de WAV/metadata/Scribe, aprovador/data e exceção específica de C.
   Nunca mudar `bruto.json` nem `scribe.json` para inserir aprovação retroativa.
2. Testes de cortes na metade da pausa, preservação de tempos relativos,
   detecção de texto/hash/seleção divergentes e exceção A8 restrita ao caso
   autorizado; implementar gerador offline em `vozes/regua_blocos.py`.
3. Escrever **A primeiro** em `motor/cache/blocos-regua/A.json`, validar e
   rodar `./scripts/verificar.sh` antes de avisar o Diretor via Maestri.
4. Completar B/C/D e `motor/tempos-pt.json` pelo caminho normal
   `motor/tempos2.py`, sem gerar arquivos por frase. `falas` continua sendo
   a lista de legendas/frases do motor; `audio_blocos` descreve quatro WAVs
   inteiros com posições independentes. Não cortar voz para criar legendas.
5. Mapear música: tensão A (v01–v04), groove B/C (v05–v07, v09–v12), calma D
   (v13–v14), ganho −2 dB no fecho. Não gerar música nem mix. Adaptar somente
   a leitura de eventos vocais do motor para usar os quatro blocos quando
   presentes, preservando o contrato legado das réguas sem `audio_blocos`.
6. Conferir limites, palavras, compassos, duração alvo 78–90 s, integridade
   de todas as tomadas e `janela_s`; reportar cenas apertadas ao Diretor e
   Maestro. Testes e gate final; commit local, sem push/PR; handoff.

### L2. Relógios, cortes e pausas

Os JSONs locais usam **tempo zero no início visual do bloco**, e informam
`voz_ini` (deslocamento do início do WAV), `ini_global`, duração do bloco,
cenas com início/fim locais e palavras com tempo local e tempo de origem.
O áudio bruto continua inteiro e pode ter cauda não verbal além do corte
visual; esse corte nunca implica cortar o WAV. Margens de transição de imagem
ficam a cargo do Diretor, sem alterar a régua nem duplicar a voz.

Dentro do bloco, a fronteira de cena é exatamente a média entre o fim Scribe
da última palavra da cena anterior e o início da primeira da seguinte.
Nenhuma frase é quantizada, recortada, reposicionada ou preenchida. A pausa
interna aceita de C não recebe corte de cena. Posições vocais são calculadas
em amostras a 48 kHz; tempos Scribe relativos são preservados.

Grade existente medida da trilha: `P = 0,491835 s`, `bar = 1,967340 s`
(~122 BPM; mantém a referência do motor, sem substituí-la por 1,967 arredondado).
Somente cortes **entre blocos** e fim do vídeo são alinhados ao compasso.
Escolher recuo inicial e posições dos WAVs de modo a manter ≥500 ms entre
última/primeira palavras dos blocos, proteção temporal ±120 ms nos cortes e
sem sobreposição dos WAVs completos. Folgas musicais não são inseridas dentro
da tomada. Cauda final termina em fim de compasso e será informada como tempo
para a animação da assinatura, sem presumir quadro congelado aprovado.

`janela_s` é planejamento histórico da versão de ~100 s, conforme o próprio
roteiro; registrar todas as janelas menores como pendências de design, sem
esticar a voz nem alterar esses valores. Revisão audiovisual e emendas da
montagem efetiva continuam pendentes até haver imagem/mix.

### L3. Resultado calculado da T5

Régua oficial: **78,693604167 s / 40 compassos**. Grade mantida do motor:
P 0,491835 s e compasso 1,967340 s (~122 BPM); limites globais quantizados
à amostra de 48 kHz, desvio máximo medido 9,167 µs. Nenhuma frase recebeu
quantização ou alteração interna.

Recuo do WAV A: **2,459166667 s** (cinco tempos, quantizados à amostra).
Recuos locais de B/C/D: **0,080 / 0,340 / 0,240 s**. A combinação mantém
os cortes de bloco na grade, pausas Scribe de 0,5–1,2 s e os WAVs completos
sem sobreposição. Cauda após o WAV D: **4,568458333 s**, para o fecho animado
da assinatura, terminando no compasso 40; não é autorização de quadro parado.

| Bloco | Início global (s) | Fim global (s) | Duração visual (s) | Duração do WAV (s) |
|---|---:|---:|---:|---:|
| A | 0.000000000 | 25.575416667 | 25.575416667 | 22.894875000 |
| B | 25.575416667 | 45.248812500 | 19.673395833 | 19.922708333 |
| C | 45.248812500 | 64.922229167 | 19.673416667 | 19.551208333 |
| D | 64.922229167 | 78.693604167 | 13.771375000 | 8.962916667 |

As caudas dos WAVs inteiros B e C ultrapassam seus limites **visuais** em
0,329312500 e 0,217791667 s, respectivamente, depois da última palavra
Scribe. Nenhum WAV é cortado nessa passagem. As futuras emendas de áudio
precisam ser auditadas no contexto da montagem e coincidir com os cortes de
cena conforme A2/A5; a régua não aprova uma emenda acústica nem autoriza cortar
respiração/fonema. Não houve mixagem ou montagem de stem nesta tarefa.

#### Cortes por cena e planejamento histórico

| Cena | Início global (s) | Fim global (s) | Duração (s) | janela_s | Déficit (s) |
|---|---:|---:|---:|---:|---:|
| v01-gancho | 0.000000000 | 6.039166667 | 6.039166667 | 4.000 | 0.000000000 |
| v02-dor1 | 6.039166667 | 13.449166667 | 7.410000000 | 6.000 | 0.000000000 |
| v03-dor2 | 13.449166667 | 19.399166667 | 5.950000000 | 9.000 | 3.050000000 |
| v04-dor3 | 19.399166667 | 25.575416667 | 6.176250000 | 7.500 | 1.323750000 |
| v05-virada | 25.575416667 | 29.895416667 | 4.320000000 | 6.000 | 1.680000000 |
| v06-solucao1 | 29.895416667 | 35.515416667 | 5.620000000 | 6.500 | 0.880000000 |
| v07-solucao2 | 35.515416667 | 41.225416667 | 5.710000000 | 7.000 | 1.290000000 |
| v09-solucao3 | 41.225416667 | 45.248812500 | 4.023395833 | 7.500 | 3.476604167 |
| v10-dado | 45.248812500 | 50.148812500 | 4.900000000 | 7.500 | 2.600000000 |
| v11-meta | 50.148812500 | 57.318812500 | 7.170000000 | 7.500 | 0.330000000 |
| v12-estrategia | 57.318812500 | 64.922229167 | 7.603416667 | 9.000 | 1.396583333 |
| v13-fecho | 64.922229167 | 70.732229167 | 5.810000000 | 8.000 | 2.190000000 |
| v14-assinatura | 70.732229167 | 78.693604167 | 7.961375000 | 6.000 | 0.000000000 |

Dez cenas menores que o planejamento: **v03, v04, v05, v06, v07, v09,
v10, v11, v12 e v13**. São pendências explícitas de coreografia, sem voz
esticada. A informação foi disponibilizada nas janelas ao Diretor; aprovação
visual segue por bloco. `janela_s` não foi tratado como duração já medida.

A foi exportado primeiro. Seus cortes no relógio **do WAV** são 3,580 /
10,990 / 16,940 s; no relógio **visual local**, 6,039166667 / 13,449166667 /
19,399166667 s. O segundo corte provisório de 11,000 s foi corrigido para
10,990 s pelo Scribe: fim de “contratar” em 10,660, início de “Uma” em 11,320.
O JSON já continha a medição correta; a correção de 10 ms do aviso textual foi
enviada ao Diretor via Maestri, sem mudar o arquivo. Gate antes da entrega A:
60 testes passaram (17 + 16 + 27), log `verificar-A.log` no cache da régua.

#### Fronteiras planejadas e música

| Fronteira | Corte global (s) | Compasso | Última palavra fim (s) | Primeira palavra início (s) | Pausa Scribe (s) | Intervalo entre WAVs (s) |
|---|---:|---:|---:|---:|---:|---:|
| A→B | 25.575416667 | 13 | 24.719166667 | 25.775416667 | 1.056250000 | 0.301375000 |
| B→C | 45.248812500 | 23 | 44.995416667 | 45.688812500 | 0.693395833 | 0.010687500 |
| C→D | 64.922229167 | 33 | 64.608812500 | 65.222229167 | 0.613416667 | 0.022208333 |

Proteção temporal Scribe ≥120 ms em todas as fronteiras planejadas. Pausa
entre palavras não equivale a silêncio acústico; escuta de montagem pendente.
A exceção interna de C continua dentro de v11, sem receber corte de cena.

Receita musical global de quarenta compassos, sem gerar trilha: tensão em
A/0–13; groove contínuo B+C/13–33 (nenhuma quebra de v08); calma D/33–40.
`musica[]` conserva `v`/`src` do motor e documenta seção/ganho; ganho efetivo
planejado de −2 dB em v13/v14 consta em `motor/mixagem.json`. O clima musical
é planejamento a conferir no mix futuro, não resultado ouvido nesta tarefa.

#### Artefatos e validação

- `vozes/selecao-blocos-pt.json`: seleção versionada, aprovação e exceção por
  hash; nenhum metadado original foi alterado.
- `.venv/bin/python motor/tempos2.py`: gera `motor/tempos-pt.json` (13 cenas,
  22 janelas de legenda, quatro eventos de voz) e `motor/cache/blocos-regua/`.
  `--bloco A` gera somente a janela A; nunca chama API.
- `{A,B,C,D}.json`: relógios local/global, deslocamento do WAV, palavras,
  tempos de origem, cenas e déficits. `RELATORIO.md` e `verificacao.json`
  no mesmo cache. JSONs de régua continuam gerados/ignorados pelo Git.
- `motor/audio2.py` passa a ler `audio_blocos` quando existir, para inserir
  quatro tomadas inteiras uma vez cada, sem tratar legendas como arquivos
  de áudio. Checa o hash declarado; régua legada conserva o comportamento.
  Validado com fontes sintéticas temporárias; nenhuma mixagem real executada.
- Integridade: quinze arquivos das cinco tomadas, incluindo C seed 2
  descartada, reconferidos contra o inventário anterior e intactos. Todas as
  151 palavras Scribe selecionadas mantêm tempos relativos; cortes internos
  no meio da pausa; cenas contíguas; 22 legendas contidas nas respectivas cenas.
- Gate final: `./scripts/verificar.sh` **passou, código 0, com 61 testes**
  (18 + 16 + 27), AST/dependências, roteiro/cópia e ausência de binários/chaves.
  `git diff --check` também passou. Log: `motor/cache/blocos-regua/verificar-final.log`.
  Aprovação audiovisual e de montagem pendentes; commit local sem push/PR.

## M. Tarefa 4 — prévia de voz e música (plano antes do código)

**Autorizado pelo Fabrício/Maestro:** produzir somente voz + música, usando
as quatro tomadas já selecionadas e a régua T5 de 78,693604 s. Sem efeitos,
vídeo, nova geração de voz ou alteração de tomada/régua. Branch
`feat/mix-voz-musica`, criado de main após o PR #18. Efeitos terão configuração
preservada, mas bus desligado e sem leitura de `eventos-pt.json`.

### M1. Análise e proposta de montagem

Primeiro medir a trilha original com FFmpeg/NumPy, sem nova dependência:
SHA-256, duração, energia RMS/pico/crest por compasso da grade existente
(P 0,491835 s, compasso 1,967340 s, origem musical 1,014 s), bandas espectrais
e energia/transientes ao redor das fronteiras. A identificação de clima por
energia é hipótese para orientar a escuta, não aprovação musical.

A montagem será **uma trilha global**, sem reiniciar nos blocos. Priorizar
intervalos contíguos longos, sem loops curtos; qualquer salto/repetição só em
fim de compasso e em pausa entre palavras da régua. Propor a lista exata de
compassos de origem antes de implementar a montagem. Medir os dois lados e
o salto em cada ponto; crossfade musical curto somente na música, no
compasso, sem coincidir com palavra. Final deve usar cauda musical natural
e encerrar no compasso 40. Se um corte musical não tiver pausa de fala,
escolher outro corte/trecho, sem mover a voz.

### M2. Voz, ducking e master

A voz é exatamente a referência decodificada/reamostrada a 48 kHz, sem ganho,
fade, corte ou normalização por tomada; quatro WAVs inteiros nas amostras da
régua. Registrar o padrão bit a bit em float32 (24→48 kHz exige reamostragem;
não confundir com identidade dos bytes dos WAVs 24 kHz). Stems separados de
voz, música-base e música-duck; premix é sua soma, com bus de efeitos zero.

Ducking baseado nas frases/palavras Scribe, não na duração inteira dos WAVs;
proteger sons fracos e bordas, mesclar pausas curtas para não bombear. Rampas
suaves e release musical, recuperação em pausas com espaço suficiente. Medir
≥12 dB de voz/música em fala ativa e bordas; registrar mínimo/mediana por
frase, limiares, envelope e intervalos. Não aumentar voz nem afrouxar limiar
para passar. A referência legada −20 dB RMS deixa de ser um alvo que altere
a voz nesta prévia: medir o nível aprovado e baixar música conforme preciso.

Master em duas passagens `loudnorm`, sem limiter extra. Registrar modo
linear/dinâmico efetivo e alinhamento; medir −16 LUFS ±0,5 e ≤−1,5 dBTP no
AAC final a 256 kbit/s, 48 kHz estéreo. A identidade da voz é verificada no
stem/premix antes do processamento global e da codificação com perdas.

### M3. Conferência, testes e entrega

Testes primeiro para voz com ganho zero apesar da referência de RMS, efeitos
desligados sem síntese/leitura de eventos, montagem musical contígua sem
emendas a cada compasso e margens por frase em fala ativa. Null test da soma
dos stems; comparação bit a bit das quatro inserções e integridade dos brutos.

Conferir cache Scribe pelo hash do AAC final. Se não houver resposta válida,
**uma única chamada** no mix final, com contexto de 250 ms ao redor da fala
(cabeça/cauda do filme já dão essa margem); guardar resposta inteira e custo
em duração/minutos. Nenhuma repetição automática de API. A5/A8 nas três
fronteiras com manifesto, palavras do mix e trechos ±2 s; confrontar com as
fontes para distinguir timestamp/ASR, mascaramento e edição. Exceção A8 de
C fica explícita e vinculada à tomada aprovada, sem mudar o limiar.

Entregar `motor/cache/mix-voz-musica.m4a`, sessão/stems/relatório local,
lista de trechos para escuta do Fabrício, configuração e código/testes.
Ausência de acesso perceptivo não será declarada como escuta feita.
`./scripts/verificar.sh` antes de commit/handoff; commit local sem push/PR.

### M4. Medição da trilha e montagem proposta antes da implementação

**Medido aqui:** a trilha tem **114,113750 s**, não ~2,5 min. SHA-256
`29a93bdd8ff4ebfe1eff786eb788c0bcc8c82db2338690c5bceebb7aff8eb1e5`,
igual ao de `scripts/trilha.sh`. Há 57 compassos completos após a origem
1,014 s, mais 0,961375 s residual. RMS estéreo por compasso:
intro 0–6 em −14,52 a −14,99 dBFS; groove 8–23 em −12,97 a −15,27;
quebra 24–30 em −17,45 a −19,31; groove 32–47 em −12,61 a −14,41;
outro 48–55 em −17,44 a −20,43; cauda 56 em −41,19. O grave ocupa
aproximadamente 0,74–0,82 da energia do primeiro groove, 0,68–0,71 do segundo,
e 0,08–0,12 do outro. Dados completos por compasso, bandas e bordas em
`motor/cache/mix-voz-musica/analise-musica.json`. “Intro/groove/outro” são
hipóteses estruturais apoiadas na energia/bandas, ainda sem escuta perceptiva.

**Proposta escolhida para a prévia — índices a partir de zero, fim exclusivo:**

| Compassos do vídeo | Compassos da fonte | Papel e razão |
|---|---|---|
| 0–13 | 0–13 | A: intro/tensão, com abertura progressiva nos últimos cinco compassos |
| 13–29 | 32–48 | Groove mais cheio, 16 compassos contíguos atravessando B→C sem emenda em 23 |
| 29–33 | 20–24 | Quatro compassos de groove/fill para completar C; não usados antes nesta montagem |
| 33–40 | 50–57 | Outro leve/cauda original para D, −2 dB; final natural, sem loop de assinatura |

Quarenta compassos de origem **únicos**, sem repetição de trecho. Três saltos
musicais, nos compassos de saída **13 / 29 / 33**, tempos **25,575420 /
57,052860 / 64,922220 s**; nenhum reinício no corte B→C. Cada salto tem
crossfade musical de **40 ms**, centrado na fronteira de compasso (±20 ms),
sem mudar duração/grade. As folgas Scribe antes/depois desses centros são,
respectivamente, **856/200, 84/616 e 313/300 ms**: nenhuma janela do crossfade
intersecta palavra conhecida. Reconfirmar com o Scribe do mix final.

As bordas da fonte em 13/32 e 48/20 têm ataque de compasso e **não são
silêncio** (RMS de ±5 ms: −8,72/−9,15 e −16,65/−9,33 dBFS). Não apresentar
isso como corte bruto já limpo: o crossfade suprime descontinuidade e a
atenuação musical durante a pausa da fala reduz a energia efetiva da emenda;
medir RMS/salto/transiente no stem montado e listar para escuta. A última
junção (24→50) tem bordas de −18,28/−18,33 dBFS em ±5 ms. Se a emenda não
for suficientemente suave, reportar a limitação, sem afrouxar regra ou chamar
outra geração. Ao fim da fonte 57 o residual de 0,961375 s mede −64,11 dBFS;
os últimos 80 ms do compasso 56 medem −59,33. Usar a cauda desse compasso e
um fechamento de **80 ms só na música**, sem fade no bus de voz.

### M5. Ajuste medido de nível antes do master

O ensaio inicial (música-base −28 dBFS e duck18/21 dB nas bordas)
conservou voz e null test, mas falhou em margens locais de fala ativa.
Não se alterou o limiar. Comparação em memória com duck fixo22 dB
(teto já previsto) mediu mínimo **5.974561 dB** por frase.
Para alvo conservador de12,5 dB, baixar uniformemente a música-base em
**6.525439 dB**, para **-34.525439 dBFS**, mantendo voz ganho0.
Ducking22 dB, sem reforço adicional nas bordas; hold200 ms, release984 ms
(~dois tempos), antecipação200 ms, patamar50 ms antes da fala.
Essa opção prioriza as consoantes fracas e pode deixar a música discreta;
isso é item de escuta, não aprovação automática do equilíbrio artístico.
Ensaio inicial preservado em `motor/cache/mix-voz-musica/qa-inicial.json`.

### M6. Prévia entregue — medições e limites

Arquivo local `motor/cache/mix-voz-musica.m4a`, AAC256 kbit/s,48 kHz estéreo,
SHA-256 `fa45326c61187afffb0b9e29618e54c062d273bb3c27ba95e363a8c7b308b82f`.
**Medido no AAC:** −16,03 LUFS, −1,99 dBTP, LRA3,10 LU; atraso0 amostras;
stream78,693 s, régua78,693604167 s. Decodificação tem243 amostras de padding
AAC além das3.777.293 do PCM, sem truncamento do stem. Master em duas
passagens, modo efetivo **dynamic**, uma tentativa e sem limiter adicional;
a dinâmica/limitação interna do loudnorm atua globalmente, não na voz isolada.

Stem de voz: quatro inserções bit a bit iguais à referência48 kHz dos brutos,
ganho0, sem cortes/fades/padding internos. Os15 arquivos das5 tomadas
permaneceram intactos. Null test voz + música-duck + efeitos-zero →premix:
**erro máximo0,0**. Efeitos-base/duck inteiramente zero, sem síntese e sem ler
`eventos-pt.json`. A identidade bit a bit é anterior ao master/AAC com perdas.

#### Margens e envelope

Referência musical final −34,525439 dBFS; duck22 dB (teto mantido), hold200 ms,
release984 ms, antecipação200 ms e patamar50 ms antes da fala. A voz não foi
normalizada ao alvo histórico−20: preservação explícita solicitada nesta tarefa.
As22 frases da régua orientam o duck, não os4 intervalos inteiros dos WAVs.
Janelas100 ms, passo10 ms, ativas quando voz≥referência da frase−20 dB,
critério já declarado no plano; janelas abaixo entram na escuta, sem fingir
que são silêncio. Mínimo VM ativo **12,50 dB**; mediana das medianas por frase
**37,68 dB**. Este equilíbrio é conservador/discreto, a ouvir. Não se afirma
que não bombeia: recuperação máxima nas pausas A/B, B/C e C/D foi17,55 /
7,46 /5,33 dB a partir do patamar22. Envelope e todas as janelas no cache.

| Frase | VM agregado (dB) | VM ativo mínimo (dB) | VM ativo mediana (dB) |
|---|---:|---:|---:|
| v01-gancho-1 | 40.98 | 24.15 | 43.43 |
| v01-gancho-2 | 39.35 | 13.77 | 40.65 |
| v02-dor1-1 | 39.09 | 16.48 | 39.70 |
| v03-dor2-1 | 39.80 | 17.10 | 40.87 |
| v03-dor2-2 | 38.85 | 24.23 | 39.09 |
| v04-dor3-1 | 37.09 | 18.04 | 37.10 |
| v05-virada-1 | 35.71 | 12.50 | 36.74 |
| v06-solucao1-1 | 37.65 | 30.47 | 37.43 |
| v06-solucao1-2 | 35.13 | 15.73 | 34.93 |
| v07-solucao2-1 | 35.16 | 19.90 | 36.29 |
| v07-solucao2-2 | 36.70 | 14.83 | 36.28 |
| v09-solucao3-1 | 37.61 | 21.57 | 37.63 |
| v10-dado-1 | 37.21 | 21.09 | 37.23 |
| v11-meta-1 | 37.13 | 15.19 | 37.30 |
| v12-estrategia-1 | 36.89 | 19.78 | 36.32 |
| v12-estrategia-2 | 37.63 | 19.37 | 37.74 |
| v12-estrategia-3 | 37.96 | 14.90 | 37.34 |
| v13-fecho-1 | 43.50 | 32.82 | 43.36 |
| v13-fecho-2 | 41.64 | 27.32 | 41.32 |
| v13-fecho-3 | 43.04 | 26.90 | 41.86 |
| v14-assinatura-1 | 41.13 | 37.28 | 42.34 |
| v14-assinatura-2 | 44.07 | 25.24 | 43.55 |

Montagem M4 preservada,40 compassos únicos, sem repetição exata. RMS do stem
música-duck em±20 ms nas emendas13/29/33: **−35,10 /−57,79 /−61,22 dBFS**.
O corte B→C/23, sem emenda musical, mede−50,76 dBFS. As bordas originais de
13/32 são fortes, não silêncio natural; crossfade/ganho produzem transição
mais baixa no mix. Conferência musical perceptiva pendente, sobretudo13.

#### Scribe, fronteiras e exceção

**Uma chamada Scribe v2** no AAC final:78,693604167 s / **1,311560 min**,
zero caracteres TTS enviados;151 palavras e964 caracteres transcritos,
incluindo tags de evento musical no texto bruto. Sem inferir preço ou
arredondamento de cobrança. O áudio inteiro já contém mais de250 ms antes e
depois da fala. Resposta completa e wrapper por hash preservados; não há
outra chamada nem retentativa. As151 palavras normalizadas conferem com o
roteiro; nenhuma omissão/substituição não resolvida no ASR. Isso não prova
inteligibilidade perceptiva de todas as palavras.

A8 no mix mede **0,620 s**, “semanas,” [51,920–52,440] →“50”
[53,060–53,260], centro52,750. A fonte C seed1 tem pausa0,600 s aceita pelo
Fabrício em26/10/2026; a identidade do stem prova a mesma tomada sem edição.
O analisador mantém a falha medida e o limiar0,500; a exceção da fonte está
registrada separadamente, sem fingir A8 sem falha. Nenhuma outra falha A8 ou
pendência de alinhamento textual no mix.

| Fronteira/emenda | Pausa Scribe do mix (s) | Achados brutos |
|---|---:|---|
| 25.575417 s | 1.020000 | diferença de fundo >3 dB (estimativa no mix); energia central em ±120 ms; mix não separa fala de música/efeitos |
| 45.248812 s | 0.680000 | energia central em ±120 ms; mix não separa fala de música/efeitos |
| 57.052860 s | 0.680000 | palavra/energia de fala na proteção ±120 ms (pista Scribe) |
| 64.922229 s | 0.481000 | pausa entre blocos menor que 500 ms; energia central em ±120 ms; mix não separa fala de música/efeitos |

**C→D não está liberada pela análise automática:** Federal. termina64,739 e
Menos começa65,220 no Scribe do mix, pausa **0,481 s**, abaixo de500 ms.
A régua baseada nos brutos estimava0,613416667 s; o novo fim de Federal.
foi~130 ms depois. Energia do stem:64,6–64,7 s em−36,01 dBFS e64,7–64,8 em
−60,80; depois há cauda/respiração. Não classificar automaticamente como
silêncio/fonema nem alterar a régua/voz para esconder o alerta. **Ouvir
Federal./Menos e decidir com Fabrício/Maestro.** A prévia está disponível
para essa escuta, sem declaração de aprovação de som ou liberação final.

A→B acusa diferença de fundo>3 dB, e as três fronteiras têm energia central;
o mix inclui música/caudas, sem prova automática de fala cortada. Em29,
a proteção genérica±120 ms alcança presentes., mas o crossfade musical
±20 ms não intersecta palavra no Scribe antigo ou novo. Nenhuma frase
comprovadamente dividida e nenhum clique sinalizado nas4 análises. Os
relatórios brutos continuam bloqueados; não se afrouxou limiar para passá-los.

Calibração declarada: A8 histórica4/4 referências v5; detector cego v4
aproxima1/4 centros da régua em±120 ms, o que não é recall auditiva validada.
Heurísticas de energia/fundo/transiente continuam Nível2, para escuta;
exceção de C e divergência temporal C/D ficam explícitas. Não houve acesso
perceptivo ao som neste runtime nem revisão contra vídeo nesta tarefa.

#### Artefatos e escuta

- Sessão `motor/cache/mix-voz-musica/sessao/`: voz, música-base, música-duck,
  efeitos-zero, premix, master, AAC, configuração/receitas, QA e envelope.
- Relatório `motor/cache/mix-voz-musica/RELATORIO.md`:57 compassos da fonte,
  montagem, margens, palavras do Scribe ao redor de cada emenda e limites.
- `auditoria-mix/`: A5/A8 brutos e trechos±2 s; `scribe-mix.json` vinculado ao
  hash final; `verificacao-mix.json`: identidade, null e energia por stem.
- Trechos AAC decodificado, sem normalização separada, em `escuta/`:
  abertura0–7; A/B23,575417–27,575417; B/C43,248812–47,248812;
  exceção C50,750–54,750; música29 em55,052860–59,052860;
  C/D62,922229–66,922229; assinatura69,500–78,693604.
- Ouvir o nível discreto da música, recuperação de até17,55 dB na pausa A/B,
  crossfades e transição para calma; conferir a pausa C/D e o final natural.
- Reprodução sem API: `.venv/bin/python motor/audio2.py pt --saida
  motor/cache/mix-voz-musica/sessao`; a prévia é cópia exata do
  `verificacao.m4a` dessa sessão. Scribe só é reutilizável se o hash conferir.
- Gate final: `./scripts/verificar.sh` **passou, código0,67 testes**
  (21 +19 +27), dependências, roteiro/cópia e ausência de binários/chaves.
  `git diff --check` passou; log em `motor/cache/mix-voz-musica/verificar-final.log`.
  Isso valida a infraestrutura, não libera C→D ou aprova o som.

## N. Tarefa 5 — experimento de voz, interpretação e mix (antes da execução)

**Autorizado pelo Fabrício/Maestro:** somente kit comparativo de três textos
(v05 pico4, v02 factual1, v13 calor4), sem regenerar os quatro blocos ou mudar
sua seleção/régua. Teto **3.000 caracteres TTS** incluindo tags e testes de
formato; lançar cada tentativa antes da requisição, nunca repetir
automaticamente. Medir também o débito retornado pelo serviço, sem equipará-lo
à contagem de texto/contexto. Starter informado com20.327/40.000; conferir a
conta. Listagens GET não sintetizam áudio. Brutos/resultados imutáveis no cache.

O mapa do PR#20 (`docs/mapa-narrativo:docs/MAPA-NARRATIVO.md`) foi **aprovado
pelo Fabrício na atualização recebida nesta tarefa**, embora a revisão do PR
ainda esteja em andamento. Seguir a curva e a tabela por cena, sem mudar
palavras, pontuação ou intensidades. Alterar intensidade só por pedido dele.

### N1. Hipóteses e fontes (consulta em 26/10/2026)

- PCM24 kHz impõe Nyquist12 kHz, mas não prova a causa de “rádio/telefone”.
  PCM não tem compressão com perdas; timbre/ruído do modelo ou da referência,
  interpretação e master global também podem influenciar. Medir o espectro
  real e comparar em volume equivalente; reamostrar não cria agudos ausentes.
- O mix anterior mediu mediana das medianas VM37,68 dB e duck22 dB:
  o diagnóstico de música sufocada é compatível com esses números. A margem
  foi imposta até em janelas100 ms de voz fraca; testar nova métrica apenas
  como emenda proposta ao A6, mantendo M1 intacto para comparação.
- Documentação oficial `Create speech`: MP3 192 kbit/s exige Creator+;
  PCM/WAV44,1 kHz exige Pro+. Testar a negação na conta e guardar HTTP/status,
  sem chave. MP3_44100_128 é a referência permitida ao Starter; consultar
  também PCM48/Opus48 e registrar o que a API efetivamente aceita.
  Fonte: https://elevenlabs.io/docs/api-reference/text-to-speech/convert
  e https://elevenlabs.io/docs/help-center/troubleshooting/what-audio-formats-do-you-support
- v3 suporta tags de áudio; v2 não oferece o mesmo mecanismo. v3 não suporta
  SSML break. Usar somente tags documentadas e sem efeitos/reações que mudem
  palavras; sua eficácia por voz precisa de escuta. Não supor que velocidade,
  contexto e estilo funcionam da mesma maneira nos dois modelos.
  Fonte: https://elevenlabs.io/docs/overview/capabilities/text-to-speech/best-practices
- Biblioteca compartilhada: filtros oficiais language/locale/use_cases e
  metadados de categoria/descrição; listar pt/pt-BR/publicidade/narração.
  Selecionar no máximo duas vozes, sem tarifa customizada, como candidatas,
  sem alegar qualidade de estúdio a partir do rótulo da biblioteca.
  Fonte: https://elevenlabs.io/docs/api-reference/voices/voice-library/get-shared

### N2. Kit de voz e direção

V1 reutiliza os trechos inteiros aprovados de v05/v02/v13, com margens só nas
pausas externas. V2 usa Ana/v2 no melhor formato comprovadamente permitido;
V3 trata offline a mesma V2. V4 compara Ana/v3 neutra e dirigida, com cadeia;
V5/V6 testam até duas vozes pt-BR de publicidade/narração, no melhor formato,
com cadeia. Manter versões neutras e dirigidas quando o modelo permitir:
v2 por parâmetros de requisição, sem fingir instrução semântica por frase;
v3 por tags documentadas. Contexto anterior/seguinte em campos separados,
com limitações do modelo identificadas. Mesmas palavras/pontuação aprovadas.

A geração de cada texto é uma tomada contínua, não uma nova seleção de
produção. Sem montagem de fala ou silêncio intra-frase. A8 por pontuação e
pausas acústicas como pista, sem confundir silêncio entre frases com falha.
Não gastar Scribe no kit sem necessidade/autorização adicional: fidelidade
lexical e A8 perceptiva ficam na lista de escuta; o envelope acústico pode
apontar pausas, mas não atribui palavra/frase com certeza.

Cadeia variante não destrutiva, a confirmar por ensaio: high-pass80 Hz,
de-esser suave, presença+1,5 dB em3,8 kHz/Q0,8, shelf de ar+1 dB em11 kHz
**só se energia real nessa banda for mensurável**, compressor leve1,6:1,
ataque15 ms/release120 ms, sem limiter e sem reverb por padrão (sala é opcional,
não necessária para “estúdio”). Equalizar volume dos ativos de comparação
por ganho constante medido, preservando fontes/derivados e sem fade sobre fala.
Não prometer transformar uma fonte informal em publicidade apenas com EQ.

### N3. Direção aprovada e tradução para futura geração por blocos

A direção segue o mapa aprovado pelo Fabrício nesta sessão. A: factual e estável,
sem picos repetidos; B: abrir em v05 e sustentar clareza nas features, com
pergunta genuína em v09; C: destacar “nenhum” e sustentar metas como metas;
D: calor e alívio em v13, assinatura firme em v14. v2 só permite parâmetros
por tomada: propor faixas estreitas de speed0,97–1,03, estabilidade0,45–0,65,
estilo0,10–0,25; essas faixas são hipóteses de teste, não controles exatos de
emoção/terminação. Não editar cada frase por áudio para simular direção.

Se v3 responder às tags, colocá-las antes da frase dentro de **uma tomada
contínua por bloco**, sem narrar a direção; não usar SSML não suportado,
reticências nem pausas inseridas para imitar respiração. Pedir contraste
calor/confiança/neutro, sem alterar palavras. Metas de pausa entre frases
0,4–0,7 s; entre blocos≥0,5 s; dentro da frase<0,5 s, salvo a exceção já
aceita do C atual. Os alvos do mapa não viram silêncio artificial nem régua
rígida. A interpretação v05/v02/v13 deste kit não aprova mudança dos blocos.

### N4. Mix offline M1/M2/M3 e emenda proposta ao A6

M1 é cópia do AAC e dos stems atuais, sem remixar ou rebaixar a referência.
M2 mantém a voz idêntica nas posições e a montagem musical, mas testa duck
raso6–10 dB com detector sidechain, ataque rápido/retorno musical e EQ na
música em1–4 kHz apenas sob fala. Medir separadamente música broadband,
música/voz na banda300 Hz–6 kHz e silêncio/pausas. Ganho da voz continua0.
M3 acrescenta a curva do mapa aprovado: abrir v05, recuar nos dados,
respirar v04→v05 e v12→v13, crescer nas features/fecho, sem degraus bruscos.

**Emenda proposta, não vigente:** comparar VM RMS na banda300 Hz–6 kHz,
alvo de12–18 dB por frase para a cama musical (faixa de ensaio sugerida no
briefing, não norma universal comprovada). Não forçar essa margem em todo
fonema fraco de100 ms, pois isso volta a sufocar a trilha. Manter também
mínimos/medianas locais como informação e testes de inteligibilidade/escuta.
Identificar que M2/M3 podem não satisfazer o gate broadband do A6 atual:
são alternativas autorizadas para escuta, não alteração silenciosa da regra.

Todos com−16 LUFS±0,5 e AAC≤−1,5 dBTP, stems/premix/null test e voz bit a bit
antes do master. Parte3 é **offline, sem API**: A5 acústica e tempos de palavra
projetados das vozes aprovadas são referências, não novo Scribe do mix nem
prova de ausência de mascaramento. Preservar os alertas C/D e a exceção C.
Se o arranjo continuar denso mesmo após recorte, reportar a limitação antes
de trocar trilha; nenhuma geração de música/licença nova presumida.

### N5. Entrega e governança

Copiar WAVs/M4As de escuta para `~/Downloads/frila-escuta-iteracao/`, com nomes
claros, README/RELATÓRIO curto e ordem de escuta. **Atualização do Fabrício:**
feedback livre, sem scorecard, notas, formulário ou checklist para preencher.
Cada ativo terá apenas caminho, SHA-256, duração, LUFS/TP e uma lista de
2–4 pontos objetivos de “o que ouvir”. O adendo anterior e seu template foram
cancelados e retirados. Sem criar `docs/orquestracao/SCORECARD-AUDIO.md`.
Testes, gate canônico antes de commit/handoff; commit local sem push/PR.


### N6. Formatos e modelos — testes reais da conta

Conta conferida: Starter,20.327/40.000, limite10 vozes. Em26/10/2026:
`pcm_44100` →HTTP403 `output_format_not_allowed`, exige Pro;
`mp3_44100_192` →HTTP403, exige Creator; `pcm_48000`,
`opus_48000_192` e `mp3_44100_128` →HTTP200. Cada probe usou “Frila.”,
6 caracteres;36 caracteres reservados incluindo negativas/modelo.
**V2 usará PCM48 kHz, sem perdas, aceito de fato neste endpoint/conta**;
não generalizar essa permissão para outros planos, formatos ou momentos.
Comparar conteúdo espectral real; taxa de saída não garante banda útil.
Registros e HTTPs em `motor/cache/voz-estudio-mix/tts-ledger.json`.

v3 com `previous_text/next_text` foi recusado: HTTP400 `unsupported_model`,
“Providing previous_text or next_text is not yet supported with the
'eleven_v3' model.” O kit v3 registrará os contextos pretendidos como
metadados, mas não os enviará para fingir suporte. Para futura produção,
isso é uma limitação frente ao A3 atual; não promover v3 nem regenerar blocos
sem decisão do Maestro/Fabrício. O GET/models desta conta informa v3 sem
style/speaker_boost; v2 com ambos. v3 usará estabilidade0,5, sem esses campos.
Fonte de API para campos/contexto e opção de clone:
https://elevenlabs.io/docs/api-reference/text-to-speech/convert .

Escolha de candidatas: Gabriel `WPgqgCVa3mD38JuyODU6` (professional,
pt-BR, advertisement, descrição declara estúdio) e Bianca
`9LwXyqQB0mUwtLRsS227` (high_quality, português brasileiro verificado em
v2, advertisement, perfil sofisticado). Tarifa de ambas1,0 no catálogo,
sem tarifa customizada. São rótulos do catálogo, não avaliação auditiva.
Não alterar seleção A/B/C/D; as duas inclusões na biblioteca, se necessárias,
servem só ao experimento autorizado.

Adicionar V1-controle com3 sínteses PCM24 nas mesmas condições de V2, além
de V1-atual extraída das tomadas aprovadas, para reduzir o confundimento de
contexto/formato. Teto previsto de todas as solicitações permanece<3.000.
V3 é derivado de V2 (zero caracteres), sem tratamento na voz dos mixes.

### N7. Validação do kit e interpretação efetivamente enviada

v2 neutra: estabilidade0,55, similaridade0,75, estilo0,10, speed1,0.
Direção (curva aprovada, sem mudar as intensidades): v05 pico4 usa
estabilidade0,45/estilo0,22/speed0,98; v02 factual1 usa0,65/0,05/1,0;
v13 calor4 usa0,50/0,18/0,97. São ajustes globais por texto do kit,
não uma alegação de controle semântico exato ou de terminação determinística.
Para produção por blocos, v2 não pode trocar esses parâmetros dentro da
tomada; essa limitação permanece, sem montagem de frases para contorná-la.

v3 neutra usa estabilidade0,5 sem tags; dirigida usa `[happy]` em v05 e
`[thoughtful]` / `[happy]` / `[thoughtful]` nas três frases de v13, para
contrastar menos/mais/conclusão. v02 factual reutiliza a neutra, sem tag
emotiva, evitando gasto e contraste artificial. Essas tags são exemplos
oficiais, sua correspondência ao mapa é hipótese de tradução a ouvir.
Fontes (26/10/2026):
https://elevenlabs.io/blog/v3-audiotags e
https://elevenlabs.io/docs/overview/capabilities/text-to-speech/best-practices .
Nenhuma reticência, SSML ou palavra nova foi inserida na fala do roteiro.

Para verificar **A8 e fidelidade lexical** das variantes novas, uma única
conferência Scribe do kit concatenado para análise, com offsets registrados,
é necessária porque não se pode atribuir palavras às pausas acústicas com
certeza nem supor que as tags não foram narradas. Não é Scribe dos mixes:
será feita antes da Parte3, que continua integralmente offline/sem API.
O custo de STT é reportado separadamente em minutos; não consome o teto de
texto TTS. Não haverá retentativa de TTS ou seleção silenciosa para esconder
falhas: cada variante permanece disponível com seus achados. Brutos originais
e a seleção A/B/C/D continuam imutáveis; essa chamada não autoriza novos blocos.

### N8. Resultados de voz e receita experimental de mix antes do render

TTS encerrado: **2.115 caracteres reservados** nas32 tentativas, incluindo
negativas; **2.097 caracteres em29 respostas de áudio**. Contador global
conferido após TTS: **20.327→21.158**, débito831 créditos do contador, que não
é sinônimo do comprimento textual. Nenhuma nova geração será feita nesta
iteração. As36 WAVs incluem as referências atuais e controles, neutras e
dirigidas. PCM48 trouxe energia real12–20 kHz: V2 v05−26,5 dB relativos à
energia total, contra−46,5 no controle PCM24, com duração idêntica4,133 s;
as outras duas frases de controle também têm durações iguais nos formatos.
Isso apoia uma diferença de banda; não prova, por si, melhor interpretação.

Cadeia de estúdio aplicada a V3/V4/V5/V6, sempre em derivado, sem reverb.
Volume comparativo mira−20 LUFS por ganho estático e pico≤−1,5 dBTP; onde
os transientes não permitem ambos sem limiter, aceitar alvo mais baixo e
registrar a diferença, em vez de esconder dinâmica com compressão extra.

Scribe do kit: **uma chamada**,215,615333 s /3,593589 min, com offsets e
fontes rastreadas. V1-controle v02 tem pausa0,540 s Abrasel/nove; V2/V3
neutras v02 têm0,520 s. As dirigidas v02 não tiveram esse alerta. Quatro
segmentos ficam inconclusivos lexicalmente no ASR do kit repetitivo:
V4 v05 dirigida, V4 v02 dirigida, V4 v13 dirigida e V5 v05 neutra.
A leitura se estende entre clipes e deixa palavras ausentes no segmento;
não concluir automaticamente que o TTS as omitiu. V4 v02 dirigida é **o mesmo
arquivo/hash** da neutra que conferiu, evidência concreta de limitação do ASR
nessa repetição. Manter os áudios e pedir atenção lexical no feedback livre,
sem retentativa de API ou aprovação cega. Não houve outra falha A8 detectada
nos segmentos alinhados. A Parte3 começa agora e não terá nenhuma API.

M2/M3: detector `sidechaincompress` de FFmpeg, threshold0,035, ratio4:1,
ataque10 ms, release320 ms; envelope limitado a **8 dB** e antecipado25 ms
somente na música. EQ peaking na música em2,2 kHz, Q0,65, −7 dB;
mistura seca/tratada acompanha a redução do sidechain e volta ao sinal
pleno na pausa. Não há processamento da voz. Medir banda300 Hz–6 kHz por
FFT apenas para análise, sem aplicar esse filtro ao áudio ouvido.

Calibrar um único ganho global da música para mediana de VM por frase na
banda em torno de15,5 dB; registrar todas as frases e os extremos, em vez
de forçar mínimos de fonemas fracos ao baixar a trilha inteira. Isso é o
ensaio autorizado da **emenda ainda não aprovada ao A6**, não o gate vigente.
M3 usa os mesmos8 dB/EQ e ganho de base de M2, somando curva musical suave:
v02/v10−2 dB, v11−1; v05/v13+2; features v06/v07/v09+1;
v12 abre0→+1; v14−2. Os valores são ganhos musicais de tradução da direção,
não alteração das intensidades aprovadas de locução. Respiração musical
nas pausas v04→v05 e v12→v13, sem mudar a duração de nenhuma fala.

### N9. Contabilidade e kit de voz consolidado

32 solicitações/probes reservadas;29 respostas de áudio. Texto conservador
de todas as tentativas **2.115/3.000**, texto de respostas geradas2.097;
as negativas somam18. Histórico conciliado:29 itens desta etapa, soma de
débitos **831**, contador20.327→21.158. Um item antigo de mesmo texto foi
excluído por ser anterior à etapa. O Scribe único do kit somou **66** no
contador; final **21.224/40.000**, variação total897. Créditos do contador
não são caracteres literais nem preço. Nenhuma API na Parte3.

| Variante | WAVs | Texto TTS reservado | O que muda |
|---|---:|---:|---|
| V1-atual | 3 | 0 | Ana/v2 PCM24, trechos contínuos já aprovados; referência ouvida anteriormente |
| V1-controle | 3 | 237 | Ana/v2 PCM24,3 controles novos com contexto/seed/settings de V2 |
| V2 | 6 | 474 | Ana/v2 PCM48 aceito, neutra e dirigida por parâmetros |
| V3 | 6 | 0 | As mesmas V2 com cadeia offline, sem sintetizar de novo |
| V4 | 6 | 420 | Ana/v3 PCM48 + cadeia; tags dirigidas; sem previous/next suportado |
| V5 | 6 | 474 | Gabriel pt-BR publicidade, v2 PCM48 + cadeia |
| V6 | 6 | 474 | Bianca pt-BR publicidade, v2 PCM48 + cadeia |
| probes | 0 | 36 | 5 formatos e1 contexto v3, incluindo negativas |

V4 factual dirigida reutiliza exatamente o WAV neutro; é a mesma direção
factual1, sem tag emotiva e sem novo gasto. Comparação em−20 LUFS por ganho
estático, com teto−1,5 dBTP: ativos variam de−20,93 a−19,99 LUFS quando o
teto impede igualar sem limiter; diferença explicitada por arquivo. Os
brutos de geração permanecem separados dos WAVs de escuta e não foram
aparados para eliminar pausas. Todos os27 registros de texto novo/alias
passaram na checagem de texto/pontuação após retirar apenas as tags, sem
dois-pontos. Isso verifica o pedido enviado, não a pronúncia final.

Leitura do kit/Scribe permanece pista:32 segmentos alinharam;4 ficaram
inconclusivos no ASR repetitivo. Entre os alinhados, V1-controle v02 alerta
0,540 s após Abrasel e V2/V3 v02 neutras0,520; as dirigidas v02 não alertam.
Esses áudios não estão aprovados para substituir a tomada atual de A.
Sem novas sínteses corretivas ou novo Scribe para forçar aprovação.

As36 WAVs têm hashes/LUFS/TP e pontos de escuta individuais em README do kit,
com feedback livre. A preparação do mix/empacotamento foi delegada ao
Compasso, por decisão expressa do Fabrício, em worktree/branch aux/audio-*,
sem API e sem editar nossas vozes. Antes da integração, o teste de sidechain
mostrou divergência de duração no gate completo; a investigação foi incluída
na subtarefa. Não liberar commit/handoff final com esse gate falhando.

### N10. Diagnóstico verificado e decisão técnica antes da escuta

1. O código atual de geração realmente pede PCM24 e os brutos aprovados são
   24 kHz. Nyquist12 kHz é a restrição, mas a conclusão “logo telefone/rádio”
   não está demonstrada: a banda vai além da telefonia estreita, PCM não é
   lossy, e ruído/timbre, interpretação e processamento global são causas
   distintas. A/B controlado aponta banda adicional real no PCM48, mantendo
   a mesma duração e texto; a preferência e a qualidade de publicidade são
   decisões de ouvido, não da extensão do arquivo.
2. No M1 a base−34,525439 e o duck22 dB estão confirmados. A voz não foi
   colocada artificialmente em−20 dBFS: `preservar_amostras=true`, ganho0,
   referências por frase medidas aproximadamente entre−16,44 e−20,06 dBFS.
   O−20 configurado é alvo legado, ignorado nesse modo. A mediana VM37,68 dB
   confirma a grande separação que tornou a cama discreta. O master de M1
   usa loudnorm dinâmico; comparar V1 bruto com M1 ajuda a separar geração
   e master. Os novos mixes usam as mesmas vozes, não as variantes do kit.
3. O mapa narrativo está aprovado e integrado em main ed63819; já atualizamos
   a base do branch. `vozes/direcao-estudio.json` fixa a curva/tabela e o hash
   do documento, parâmetros/tags do kit e a restrição de não promover nova
   voz/modelo sem escuta. v10 permanece intensidade3, pico moderado; não foi
   aumentado para4. A proposta de A6 por banda ainda NÃO está aprovada.
4. Nenhuma voz vencedora foi escolhida pelo agente. Prioridade de escuta:
   comparar V1-controle→V2 neutra (formato), V2→V3 (cadeia), V3 neutra→dirigida
   (parâmetros), V4 (tags/modelo) e V5/V6 (persona); conferir factual/v13 após
   escolher a abertura v05. A avaliação será em texto livre, sem formulário.

## O. Tarefa 6 — Vozes por Bloco e Alternância de Narradores (Decisão do Fabrício)

**Decisão do Fabrício em 26/10/2026:**
A partir da escuta do kit da Tarefa 5, o Fabrício aprovou de ouvido:
- `V5_v05_dirigida` (Gabriel pt-BR publicidade, `eleven_multilingual_v2`, PCM 48 kHz, dirigida);
- `V5_v13_neutra` (Gabriel);
- `V4_v13_dirigida` (Ana Dias, `eleven_v3`, PCM 48 kHz, dirigida).

E definiu a estratégia de **alternância de vozes por blocos inteiros** (nunca com trocas frequentes intra-bloco, garantindo que o ouvinte se adapte organicamente ao timbre):
- **Bloco A (Dores v01–v04):** **Ana Dias** (`eleven_v3`, PCM 48 kHz, dirigida). O Bloco A aprovado na v4/v5 (gerado em v2, 24 kHz) é regerado com a Ana v3 para harmonizar timbre, resolução espectral (48 kHz) e intenção. A imagem e as janelas de v01–v04 serão reajustadas pelo motion na sequência.
- **Bloco B (Soluções v05–v09):** **Gabriel pt-BR publicidade** (`eleven_multilingual_v2`, PCM 48 kHz, dirigida). A cena v05 abre o bloco com o **Pico 1** da virada narrativa (energia, calor, promessa do Frila).
- **Bloco C (Prova e Metas v10–v12):** **Ana Dias** (`eleven_v3`, PCM 48 kHz, dirigida). Abre com o **Pico 2** em v10 ("nenhum mostra comparecimento medido"), trazendo autoridade e dados.
- **Bloco D (Fecho e Assinatura v13–v14):** **Ana Dias** (`eleven_v3`, PCM 48 kHz, dirigida). Contém o **Pico 3** caloroso em v13 ("Deixa que o Frila cuida") e encerra com a assinatura firme e pausada em v14.

### O1. Parâmetros efetivos e formatos de áudio

Todas as sínteses utilizam **PCM 48 kHz linear mono** (`pcm_48000`, 16-bit little-endian, sample rate 48.000 Hz, 96.000 bytes/s), eliminando o teto de 12 kHz do antigo PCM 24 kHz.

| Bloco | Voz | Voice ID | Modelo | Formato | Settings de Voz | Tags de Áudio / Direção |
|---|---|---|---|---|---|---|
| **A** | Ana Dias | `MZxV5lN3cv7hi1376O0m` | `eleven_v3` | `pcm_48000` | `stability: 0.5` | v01–v02 factual/urgência; v03 `[thoughtful]` ceticismo; v04 gravidade |
| **B** | Gabriel | `WPgqgCVa3mD38JuyODU6` | `eleven_multilingual_v2` | `pcm_48000` | `stability: 0.45, similarity: 0.75, style: 0.22, speed: 0.98, speaker_boost: true` | Direcionamento por settings de voz; contexto vizinho ativo; Pico 1 em v05 |
| **C** | Ana Dias | `MZxV5lN3cv7hi1376O0m` | `eleven_v3` | `pcm_48000` | `stability: 0.5` | v10 Pico 2 (descoberta); v11 factual metas; v12 expansão |
| **D** | Ana Dias | `MZxV5lN3cv7hi1376O0m` | `eleven_v3` | `pcm_48000` | `stability: 0.5` | v13 `[thoughtful]` e `[happy]` Pico 3 caloroso; v14 assinatura calma |

### O2. Cadeia de masterização de estúdio não destrutiva

Conforme estabelecido na infraestrutura de estúdio, os brutos originais gerados pela API (`bruto.wav`) são **estritamente imutáveis** e preservados em disco. A cadeia de masterização é aplicada offline como **variante processada** (`voz.wav`):
1. **Filtro Passa-Altas (High-pass):** Butterworth 2ª ordem em 80 Hz para eliminação de rumble subsônico e ruídos de baixa frequência sem afetar a fundamental vocal.
2. **De-esser Suave Dinâmico:** Atenuação suave em sibilâncias acima de 6 kHz.
3. **Equalização de Presença e Ar:**
   - Ganho sutil de presença de +1,5 dB centrado em 3.800 Hz (Q = 0,8);
   - High-shelf de ar de +1,0 dB em 11 kHz aplicado apenas quando há energia real na banda (garantido pelo PCM 48 kHz).
4. **Compressão Óptica Leve:** Ratio suave 1,6:1, attack 15 ms, release 120 ms, controlando a dinâmica sem achatar os picos intencionais da locução.
5. **Sem limiter destrutivo e sem reverb artificial:** A voz permanece limpa, seca e natural.

### O3. Fronteiras entre blocos, cortes de cena e respiro musical

1. **Coincidência com corte de cena:** Toda emenda entre blocos (A→B, B→C, C→D) coincide **exatamente com um corte de cena visual**. Nenhuma frase falada cruza emenda (Regra A1).
2. **Pausa Inter-Blocos:** Pausa mínima entre a última palavra do bloco anterior e a primeira palavra do bloco seguinte de **≥ 500 ms** (alvo projetado na grade de **~700 ms**). Essa pausa é indispensável perceptivamente para que o cérebro do ouvinte processe a alternância de gênero/timbre entre Ana e Gabriel.
3. **Respiro da Trilha:** Nas transições de bloco A→B e C→D, a automação musical aplica elevação suave de +1,5 dB na cama musical (curva senoidal nas pausas), marcando o corte de bloco e evitando silêncio vazio.

### O4. Limitação técnica do eleven_v3 e mitigação da deriva de timbre

- **Limitação confirmada em §N:** O modelo `eleven_v3` retorna `HTTP 400 Bad Request` se os parâmetros `previous_text` ou `next_text` forem enviados.
- **Mitigação de Consistência:** A consistência tímbrica e estilística da Ana Dias nos blocos A, C e D é assegurada por:
  - Idêntico `voice_id` (`MZxV5lN3cv7hi1376O0m`);
  - Idêntico `seed` (`1`);
  - Idêntico `stability` (`0.5`);
  - Idêntica cadeia de masterização offline;
  - **Aferição Objetiva de Deriva:** Medição de espectro médio, frequência fundamental média ($F_0$) e centroide espectral comparativo entre os blocos A, C e D para detectar qualquer salto aberrante de pitch antes do envio ao Fabrício.

### O5. Orçamento, regras de gate e verificação

- **Teto da Tarefa 6 ajustado:** Máximo de 5.500 caracteres somando TTS e Scribe (saldo anterior: 21.224 / 40.000). Sendo:
  - Teto adicional de até **1.000 caracteres** reservado para o Kit de Pronúncia (§O6);
  - Teto restante de **4.500 caracteres** reservado para a síntese dos 4 blocos integrais.
- **Geração Atômica dos Blocos:** Exatamente 1 chamada TTS por bloco (4 chamadas no total) em tomada contínua (A3).
- **Sem Regeração Automática em Loop:** Se um bloco falhar em A8 ou no alinhamento do Scribe, a execução é interrompida para aviso ao Maestro; regeneração somente sob autorização expressa.
- **Condição Bloqueante:** NÃO sintetizar os 4 blocos definitivos antes da escuta e decisão soberana do Fabrício quanto às formas fonéticas candidatas do Kit de Pronúncia.
- **Verificação Obrigatória:** `./scripts/verificar.sh` executado e aprovado com 100% de sucesso antes de qualquer commit ou handoff.

### O6. Mecânica de pronúncia e fonética familiar (Diretriz do Fabrício)

Para assegurar locução em português do Brasil editorial, neutro e sem sotaques regionais ou leituras anglicizadas de marcas e números, adota-se a correção fonética prévia:
1. **Imutabilidade do Roteiro e Legendas:** `roteiro.json` e as legendas visuais são estritamente preservados com a ortografia padrão oficial. Nenhuma grafia de tela é alterada.
2. **Dicionário de Pronúncia (`vozes/pronuncia.json`):**
   - Mapeia cada termo de risco para sua substituição fonética:
     ```json
     {
       "termo": {
         "forma": "substituicao_fonetica",
         "voz": "ana" | "gabriel" | "ambas",
         "status": "candidata" | "aprovada" | "descartada",
         "nota": "motivo ou contexto"
       }
     }
     ```
   - Somente entradas com `status: "aprovada"` são elegíveis para substituição na síntese dos blocos oficiais.
3. **Mecânica de Aplicação:**
   - A substituição ocorre estritamente na string de envio para o TTS no momento da geração do áudio;
   - Substituição por palavra inteira (`\bpalavra\b`), preservando caixa alta/baixa do primeiro caractere;
   - As substituições aplicadas são registradas explicitamente no manifesto do bloco (`bruto.json`).
4. **Conferência Literal e Normalização no ASR:**
   - O normalizador (`vozes.manifesto.normal` e conferência Scribe) reconhece o mapeamento inverso das formas aprovadas, permitindo que transcrições fonéticas ou grafias alternativas (ex.: Scribe ouvindo `Freela` para `Frila` ou `Fríla`) casem com o texto oficial do roteiro sem falso positivo.
5. **Kit de Pronúncia de Escuta:**
   - Palavras das prioridades 1 e 2 geradas em frases-veículo curtas (original vs. candidata) para ambas as vozes (Ana v3 e Gabriel v2), tratadas com a cadeia de estúdio e disponibilizadas em `~/Downloads/frila-escuta-pronuncia/` para julgamento de ouvido do Fabrício.

### O7. Travas de segurança e execução controlada dos blocos (Ajuste PR #27)

Para evitar qualquer disparo acidental de chamadas de API, vazamento de quota e garantir aplicação rigorosa da pronúncia aprovada:
1. **Modo Dry-Run por Padrão:**
   - A invocação padrão do script (`python vozes/produzir_blocos_tarefa6.py`) opera estritamente em modo informativo/dry-run;
   - Extrai o texto dos blocos diretamente de `roteiro.json`, aplica `aplicar_pronuncia()`, calcula os caracteres previstos e exibe o resumo completo de execução sem ler chaves de API, sem tráfego de rede e sem debitar saldo;
   - Encerra com código de saída `0`.
2. **Execução com Teto Explícito Obrigatório:**
   - O modo real de síntese requer simultaneamente `--executar` e `--teto-caracteres <N>`;
   - A execução é rejeitada se `--executar` for fornecido sem `--teto-caracteres`, ou se o total de caracteres previstos exceder o teto estipulado.
3. **Bloqueio por Termos Candidatos Não Aprovados (Código 2):**
   - O script varre todo o texto dos blocos contra `vozes/pronuncia.json`. Se qualquer termo encontrado possuir status diferente de `"aprovada"` (por exemplo, status `"candidata"`), a execução é abortada imediatamente com código de saída `2` e mensagem explicativa de que formas ainda não aprovadas de ouvido pelo Fabrício bloqueiam a produção oficial;
   - Apenas quando todos os termos de risco estiverem aprovados (ou descartados explicitamente), a produção pode prosseguir.
4. **Fonte Canônica Dinâmica:**
   - Nenhum texto de bloco é gravado de forma estática no script; as falas são compostas a partir de `roteiro.json`, preservando imutabilidade da fonte e aplicando as substituições fonéticas no pipeline de geração.
5. **Auditoria de Saldo:**
   - A consulta e registro de saldo da API ElevenLabs ocorrem exclusivamente dentro do fluxo `--executar`.


