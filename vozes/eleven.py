"""v5 (PT): voz e conferência pelo ElevenLabs, no lugar do OmniVoice e do Whisper CLI.

  python3 eleven.py gerar [cena ...]     gera frases/pt/<cena>-<n>.wav (24 kHz, mono) a partir de ../../roteiro.json
  python3 eleven.py conferir [cena ...]  transcreve cada frase no Scribe e confere se saiu inteira → conferencia.json
  python3 eleven.py vozes                lista as vozes PT-BR da conta
  python3 eleven.py saldo                caracteres usados no mês

Chave: lida de ELEVENLABS_API_KEY ou de ~/.config/elevenlabs/chave. Nunca é impressa nem gravada aqui.
Ajustes por variável de ambiente: VOZ (padrão: Fernanda), MODELO, VEL (0.7 a 1.2), ESTAB, SIM, ESTILO, SEED
(SEED muda a tomada: frase que o Scribe aponta como diferente se regrava com `SEED=3 python3 eleven.py gerar <cena>` até passar).
Uma frase por arquivo, como na v4: a legenda fica presa ao início de cada frase.
"""
import json, os, re, subprocess, sys, unicodedata, urllib.request, urllib.error, wave
from pathlib import Path

AQUI = Path(__file__).resolve().parent
ROTEIRO = AQUI.parent / "roteiro.json"
SAIDA = AQUI / "frases/pt"
API = "https://api.elevenlabs.io"
VOZ = os.environ.get("VOZ", "7iqXtOF3wl3pomwXFY7G")  # Fernanda (aprovada pelo Cauê em 26/10/2026)
MODELO = os.environ.get("MODELO", "eleven_multilingual_v2")
CONFIG = {
    "stability": float(os.environ.get("ESTAB", 0.5)),
    "similarity_boost": float(os.environ.get("SIM", 0.75)),
    "style": float(os.environ.get("ESTILO", 0.0)),
    "use_speaker_boost": True,
    "speed": float(os.environ.get("VEL", 1.0)),
}


def chave():
    k = os.environ.get("ELEVENLABS_API_KEY")
    if not k:
        p = Path.home() / ".config/elevenlabs/chave"
        k = p.read_text().strip() if p.exists() else ""
    if not k:
        sys.exit("sem chave: defina ELEVENLABS_API_KEY ou grave em ~/.config/elevenlabs/chave")
    return k


def chamar(caminho, corpo=None, multipart=None):
    req = urllib.request.Request(API + caminho, headers={"xi-api-key": chave()})
    if corpo is not None:
        req.data = json.dumps(corpo).encode()
        req.add_header("Content-Type", "application/json")
    if multipart is not None:
        req.data, tipo = multipart
        req.add_header("Content-Type", tipo)
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return r.read()
    except urllib.error.HTTPError as e:
        sys.exit(f"ElevenLabs {e.code} em {caminho}: {e.read().decode()[:300]}")


def frases(texto):
    return [f for f in re.split(r"(?<=[.?!])\s+", texto.strip()) if f]


def pcm_para_wav(pcm, destino):
    with wave.open(str(destino), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(24000); w.writeframes(pcm)


def cenas_do_roteiro(filtro):
    cenas = json.loads(ROTEIRO.read_text())["cenas"]
    return [c for c in cenas if not filtro or c["id"] in filtro or c["id"].split("-")[0] in filtro]


def gerar(filtro):
    if not VOZ:
        sys.exit("defina VOZ=<id da voz> (use: python3 eleven.py vozes)")  # só se alguém esvaziar o padrão
    SAIDA.mkdir(parents=True, exist_ok=True)
    for c in cenas_do_roteiro(filtro):
        for k, f in enumerate(frases(c["pt"]["fala"]), 1):
            pcm = chamar(f"/v1/text-to-speech/{VOZ}?output_format=pcm_24000",
                         {"text": f, "model_id": MODELO, "language_code": "pt", "voice_settings": CONFIG,
                          **({"seed": int(os.environ["SEED"])} if "SEED" in os.environ else {})})
            destino = SAIDA / f"{c['id']}-{k}.wav"
            pcm_para_wav(pcm, destino)
            print(f"{c['id']}-{k}  {len(pcm) / 48000:.2f}s  {f[:60]}")


def multipart(campos, arquivo):
    import uuid
    b = uuid.uuid4().hex
    corpo = b""
    for n, v in campos.items():
        corpo += f'--{b}\r\nContent-Disposition: form-data; name="{n}"\r\n\r\n{v}\r\n'.encode()
    corpo += (f'--{b}\r\nContent-Disposition: form-data; name="file"; filename="{arquivo.name}"\r\n'
              f"Content-Type: audio/wav\r\n\r\n").encode() + arquivo.read_bytes() + f"\r\n--{b}--\r\n".encode()
    return corpo, f"multipart/form-data; boundary={b}"


UNID = "zero um dois três quatro cinco seis sete oito nove dez onze doze treze quatorze quinze dezesseis dezessete dezoito dezenove".split()
DEZ = "_ _ vinte trinta quarenta cinquenta sessenta setenta oitenta noventa".split()
CENT = "_ cento duzentos trezentos quatrocentos quinhentos seiscentos setecentos oitocentos novecentos".split()


def extenso(n):
    """0 a 999.999, só para comparar o que o Scribe escreve em algarismos com o texto da fala."""
    if n >= 1000:
        m, r = divmod(n, 1000)
        return ("mil" if m == 1 else extenso(m) + " mil") + (" e " + extenso(r) if r and (r < 100 or r % 100 == 0) else " " + extenso(r) if r else "")
    if n == 100:
        return "cem"
    if n >= 100:
        c, r = divmod(n, 100)
        return CENT[c] + (" e " + extenso(r) if r else "")
    if n >= 20:
        d, u = divmod(n, 10)
        return DEZ[d] + (" e " + UNID[u] if u else "")
    return UNID[n]


def normal(t):
    """Põe fala e transcrição na mesma forma: sem acento, números por extenso, 'Freela'=Frila, 'pra'=para."""
    t = re.sub(r"(\d+)\s*%", lambda m: m.group(1) + " por cento", t.lower())
    t = re.sub(r"\d+", lambda m: extenso(int(m.group())), t)
    t = t.replace("km", "quilômetros").replace(" m ", " metros ")
    t = unicodedata.normalize("NFD", t)
    t = "".join(ch for ch in t if unicodedata.category(ch) != "Mn")
    t = t.replace("freela", "frila").replace("e-staff", "estaff").replace("da staff", "da estaff")
    return [("para" if w == "pra" else w) for w in re.findall(r"[a-z0-9]+", t)]


def conferir(filtro):
    rel = {}
    for c in cenas_do_roteiro(filtro):
        for k, f in enumerate(frases(c["pt"]["fala"]), 1):
            wav = SAIDA / f"{c['id']}-{k}.wav"
            if not wav.exists():
                rel[wav.stem] = {"ok": False, "motivo": "arquivo não existe"}; continue
            d = json.loads(chamar("/v1/speech-to-text", multipart=multipart(
                {"model_id": "scribe_v2", "language_code": "por", "timestamps_granularity": "word"}, wav)))
            esperado, ouvido = normal(f), normal(d["text"])
            dur = wave.open(str(wav)).getnframes() / 24000
            palavras = [w for w in d["words"] if w["type"] == "word"]
            sobra = dur - palavras[-1]["end"] if palavras else dur
            ok = esperado == ouvido
            rel[wav.stem] = {"ok": ok, "esperado": " ".join(esperado), "ouvido": " ".join(ouvido),
                             "duracao": round(dur, 2), "silencio_no_fim": round(sobra, 2)}
            print(("ok     " if ok else "DIFERE ") + wav.stem + ("" if ok else f"  esperado: {' '.join(esperado)} | ouvido: {' '.join(ouvido)}"))
    (AQUI / "conferencia.json").write_text(json.dumps(rel, ensure_ascii=False, indent=1))
    falhas = [n for n, v in rel.items() if not v["ok"]]
    print(f"\n{len(rel) - len(falhas)}/{len(rel)} frases conferidas; relatório em conferencia.json")
    if falhas:
        print("a regravar:", " ".join(falhas))


def listar_vozes():
    d = json.loads(chamar("/v2/voices?page_size=100"))
    for v in d["voices"]:
        l = v.get("labels", {})
        if l.get("language") == "pt" or "pt" in [x.get("language") for x in v.get("verified_languages") or []][:1]:
            print(v["voice_id"], "|", v["name"], "|", l.get("accent", ""), l.get("gender", ""), l.get("descriptive", ""))


def saldo():
    d = json.loads(chamar("/v1/user/subscription"))
    print(f"plano {d['tier']}: {d['character_count']} de {d['character_limit']} caracteres usados")


if __name__ == "__main__":
    cmd, *resto = sys.argv[1:] or ["saldo"]
    if cmd in ("gerar", "conferir"):
        {"gerar": gerar, "conferir": conferir}[cmd](resto)
    elif cmd in ("vozes", "saldo"):
        {"vozes": listar_vozes, "saldo": saldo}[cmd]()
    else:
        sys.exit(__doc__)
