from __future__ import annotations

import ast
from pathlib import Path

arvore = ast.parse(Path("pimcord/http/cliente.py").read_text(encoding="utf-8"))
classe = next(no for no in arvore.body if isinstance(no, ast.ClassDef) and no.name == "ClienteHTTP")
nomes = [no.name for no in classe.body if isinstance(no, (ast.AsyncFunctionDef, ast.FunctionDef)) and not no.name.startswith("_")]
print(f"metodos_publicos_ast={len(nomes)} unicos={len(set(nomes))}")
