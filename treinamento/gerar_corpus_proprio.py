"""Gera exemplos de corpus a partir do próprio código licenciado do Pimcord.

Os exemplos são sementes de continuação e análise estrutural. Eles não substituem
um corpus instrucional amplo e ficam marcados com a fonte para auditoria.
"""
from __future__ import annotations

import argparse
import ast
import json
from pathlib import Path


def _resumo(arvore: ast.AST) -> str:
    nomes: list[str] = []
    for no in ast.walk(arvore):
        if isinstance(no, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            nomes.append(no.name)
    return ", ".join(nomes[:30]) or "módulo sem símbolos públicos detectáveis"


def gerar(raiz: Path, destino: Path) -> int:
    destino.parent.mkdir(parents=True, exist_ok=True)
    total = 0
    with destino.open("w", encoding="utf-8") as saida:
        for arquivo in sorted((raiz / "pimcord").rglob("*.py")):
            if arquivo.name == "__init__.py":
                continue
            codigo = arquivo.read_text(encoding="utf-8")
            try:
                arvore = ast.parse(codigo, filename=str(arquivo))
            except SyntaxError:
                continue
            relativo = arquivo.relative_to(raiz).as_posix()
            exemplo = {
                "instrucao": f"Explique a arquitetura e os contratos do módulo Pimcord {relativo}.",
                "contexto": f"Módulo próprio do Pimcord; símbolos encontrados: {_resumo(arvore)}.",
                "codigo": codigo,
                "linguagem": "python",
                "fonte": "Pimcord — código próprio",
                "licenca": "MIT",
                "arquivos": [relativo],
                "testes": [],
            }
            saida.write(json.dumps(exemplo, ensure_ascii=False) + "\n")
            total += 1
    return total


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raiz", type=Path, default=Path("."))
    parser.add_argument("--destino", type=Path, default=Path("treinamento/dados/brutos/pimcord_proprio.jsonl"))
    args = parser.parse_args()
    print(f"[PimcordIA] {gerar(args.raiz.resolve(), args.destino)} módulos exportados para {args.destino}")


if __name__ == "__main__":
    main()
