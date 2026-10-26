#!/usr/bin/env python3
"""
scripts/lint_roteiro.py
Linter estrito para roteiro.json (Regra A8 e integridade de blocos).
Verifica:
1. Ausência de ':' em falas faladas (evita pausas artificiais e emendas audíveis na locução).
2. Paridade de frases entre fala e legenda (. ? !).
3. Consistência entre 'blocos' e 'cenas'.
4. Presença de campos obrigatórios (id, bloco, pt.fala, pt.legenda).
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def count_sentences(text):
    # Divide por pontuação final mantendo frases não vazias
    parts = re.split(r'[\.\?\!]+', text)
    return len([p.strip() for p in parts if p.strip()])

def main():
    roteiro_path = ROOT / "roteiro.json"
    if not roteiro_path.exists():
        print(f"❌ roteiro.json não encontrado em {roteiro_path}", file=sys.stderr)
        sys.exit(1)

    with open(roteiro_path, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except Exception as e:
            print(f"❌ Erro de JSON em roteiro.json: {e}", file=sys.stderr)
            sys.exit(1)

    cenas = data.get("cenas", [])
    blocos = data.get("blocos", [])

    if not cenas:
        print("❌ 'cenas' está vazio em roteiro.json!", file=sys.stderr)
        sys.exit(1)

    errors = []
    
    # 1. Checa blocos declarados
    cenas_em_blocos = set()
    for b in blocos:
        bid = b.get("id")
        for c in b.get("cenas", []):
            cenas_em_blocos.add(c)

    cenas_ids = set()
    for c in cenas:
        cid = c.get("id")
        if not cid:
            errors.append("Cena sem 'id' encontrado.")
            continue
        cenas_ids.add(cid)

        bloco = c.get("bloco")
        if not bloco:
            errors.append(f"Cena '{cid}': campo 'bloco' ausente.")

        pt = c.get("pt", {})
        fala = pt.get("fala", "")
        legenda = pt.get("legenda", "")

        if not fala:
            errors.append(f"Cena '{cid}': 'pt.fala' está vazio.")
        if not legenda:
            errors.append(f"Cena '{cid}': 'pt.legenda' está vazio.")

        # Regra A8: Dois-pontos proibido na locução falada
        if ":" in fala:
            errors.append(
                f"Cena '{cid}': ':' detectado em 'pt.fala'! Regra A8 proíbe dois-pontos na fala "
                f"(insere pausas de 0,5–0,9s gerando sensação de corte/remendo)."
            )

        # Checa número de frases entre fala e legenda
        nf = count_sentences(fala)
        nl = count_sentences(legenda)
        if nf != nl and nf > 0 and nl > 0:
            errors.append(
                f"Cena '{cid}': número de frases diverge entre fala ({nf}) e legenda ({nl})."
            )

    # Checa consistência entre lista de cenas e blocos
    diff_bloco = cenas_ids.symmetric_difference(cenas_em_blocos)
    if diff_bloco:
        errors.append(f"Divergência entre 'cenas' e 'blocos': cenas {diff_bloco} desalinhadas.")

    if errors:
        print(f"❌ Linter de roteiro encontrou {len(errors)} erro(s):")
        for err in errors:
            print(f"  • {err}")
        sys.exit(1)

    print(f"✅ roteiro.json validado com sucesso ({len(cenas)} cenas, {len(blocos)} blocos). Regra A8 cumprida.")

if __name__ == "__main__":
    main()
