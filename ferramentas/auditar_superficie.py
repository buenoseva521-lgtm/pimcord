from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "pimcord"

for path in sorted(ROOT.rglob("*.py")):
    tree = ast.parse(path.read_text(encoding="utf-8"))
    print(f"\n## {path.relative_to(ROOT.parent)}")
    for node in tree.body:
        if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            kind = "classe" if isinstance(node, ast.ClassDef) else "função"
            decorators = [ast.unparse(d) for d in getattr(node, "decorator_list", [])]
            print(f"{kind}: {node.name} | decoradores={decorators}")
            if isinstance(node, ast.ClassDef):
                for child in node.body:
                    if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        calls = [ast.unparse(x) for x in ast.walk(child) if isinstance(x, ast.Call)]
                        has_pass = any(isinstance(x, ast.Pass) for x in ast.walk(child))
                        has_not_impl = any(isinstance(x, ast.Raise) and "NotImplementedError" in ast.unparse(x) for x in ast.walk(child))
                        markers = []
                        if has_pass:
                            markers.append("pass")
                        if has_not_impl:
                            markers.append("NotImplementedError")
                        print(f"  - {child.name} | async={isinstance(child, ast.AsyncFunctionDef)} | marcadores={markers} | chamadas={calls[:4]}")
