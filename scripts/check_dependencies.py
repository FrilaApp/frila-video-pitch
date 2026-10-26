#!/usr/bin/env python3
"""
scripts/check_dependencies.py
Verifica se todos os imports de bibliotecas de terceiros no código Python
estão formalmente declarados no requirements.txt.
Previne deriva de ambiente entre worktrees e repositório raiz.
"""
import ast
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Mapeamento de nomes de import para nomes canônicos no requirements.txt
KNOWN_MAPPINGS = {
    "cv2": "opencv-python-headless",
    "PIL": "pillow",
    "playwright": "playwright",
    "numpy": "numpy",
}

# Pastas locais consideradas módulos do próprio projeto
LOCAL_MODULES = {"motor", "scripts", "vozes", "tests"}

def get_stdlib():
    if hasattr(sys, "stdlib_module_names"):
        return sys.stdlib_module_names
    # Fallback básico para versões anteriores
    return {
        "os", "sys", "json", "pathlib", "subprocess", "time", "re", "math",
        "typing", "hashlib", "shutil", "glob", "dataclasses", "unittest",
        "ast", "traceback", "inspect", "wave", "struct", "io", "contextlib",
        "itertools", "collections", "datetime"
    }

def get_declared_requirements():
    req_file = ROOT / "requirements.txt"
    if not req_file.exists():
        return set()
    declared = set()
    with open(req_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            pkg = line.split("==")[0].split(">=")[0].split("<=")[0].split("~=")[0].strip().lower()
            declared.add(pkg)
    return declared

def extract_imports(filepath):
    imports = set()
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read(), filename=str(filepath))
    except Exception as e:
        print(f"[AVISO] Falha ao parsear {filepath}: {e}", file=sys.stderr)
        return imports

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                top = alias.name.split(".")[0]
                imports.add(top)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                top = node.module.split(".")[0]
                imports.add(top)
    return imports

def main():
    stdlib = get_stdlib()
    declared = get_declared_requirements()
    
    # Adiciona versões alternativas conhecidas
    if "opencv-python-headless" in declared:
        declared.add("opencv-python")

    errors = []
    scanned_files = 0

    scan_dirs = ["motor", "scripts", "vozes"]
    for dir_name in scan_dirs:
        dir_path = ROOT / dir_name
        if not dir_path.exists():
            continue
        for py_file in dir_path.rglob("*.py"):
            # Ignora caches
            if "__pycache__" in py_file.parts or ".venv" in py_file.parts or "qa-venv" in py_file.parts:
                continue
            scanned_files += 1
            imports = extract_imports(py_file)
            for imp in imports:
                if imp in stdlib or imp in LOCAL_MODULES:
                    continue
                # Se for relativo ao projeto (ex: motor.algo ou módulo irmão em motor/, vozes/, scripts/)
                if (ROOT / imp).exists() or (ROOT / f"{imp}.py").exists():
                    continue
                is_internal = False
                for sub in ["motor", "vozes", "scripts"]:
                    if (ROOT / sub / f"{imp}.py").exists() or (ROOT / sub / imp).exists():
                        is_internal = True
                        break
                if is_internal:
                    continue

                pkg_name = KNOWN_MAPPINGS.get(imp, imp).lower()
                if pkg_name not in declared:
                    rel_path = py_file.relative_to(ROOT)
                    errors.append((str(rel_path), imp, pkg_name))

    print(f"Verificados {scanned_files} arquivos Python contra requirements.txt...")
    if errors:
        print("\n❌ ERRO DE DEPENDÊNCIA NÃO DECLARADA ENCONTRADO:")
        for file_path, imp, pkg in errors:
            print(f"  • {file_path}: usa '{imp}', mas '{pkg}' não está no requirements.txt!")
        print("\nAdicione o pacote ao requirements.txt e reinstale no .venv antes de submeter PR.")
        sys.exit(1)

    print("✅ Todas as dependências externas estão formalmente declaradas no requirements.txt.")

if __name__ == "__main__":
    main()
