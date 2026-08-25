from __future__ import annotations

import ast
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "pimcord"


def assinatura(node: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
    try:
        argumentos = ast.unparse(node.args)
        retorno = f" -> {ast.unparse(node.returns)}" if node.returns else ""
        return f"{node.name}({argumentos}){retorno}"
    except Exception:
        return f"{node.name}(...)"


def documentar(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    relativo = path.relative_to(ROOT.parent).with_suffix("")
    linhas = [f"## `{relativo}`", ""]
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            linhas.append(f"### Classe `{node.name}`")
            linhas.append("")
            docstring = ast.get_docstring(node)
            if docstring:
                linhas.append(docstring.strip())
                linhas.append("")
            for child in node.body:
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)) and not child.name.startswith("_"):
                    linhas.append(f"- `{node.name}.{assinatura(child)}`")
            linhas.append("")
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and not node.name.startswith("_"):
            linhas.append(f"### Função `{assinatura(node)}`")
            linhas.append("")
    return linhas


def gerar(destino: Path) -> None:
    linhas = [
        "# Referência da API Pimcord",
        "",
        "> Arquivo gerado offline a partir das assinaturas públicas do código-fonte. Não é necessário importar o pacote nem acessar a rede.",
        "",
    ]
    for path in sorted(ROOT.rglob("*.py")):
        linhas.extend(documentar(path))
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text("\n".join(linhas).rstrip() + "\n", encoding="utf-8")


if __name__ == "__main__":
    saida = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("docs/API.md")
    gerar(saida)
    print(saida)
