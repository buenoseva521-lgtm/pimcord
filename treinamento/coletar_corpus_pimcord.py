"""Coleta exemplos reais da árvore Pimcord para um corpus local.

O coletor não cria respostas sintéticas. Ele extrai continuções de arquivos Python
válidos e blocos Python completos presentes na documentação. O texto instrucional
é derivado do contexto real do arquivo e deve ser revisado antes do treinamento.
"""
from __future__ import annotations

import argparse
import ast
import json
import re
from pathlib import Path

BLOCO_PYTHON = re.compile(r"```python\s*\n(.*?)```", re.IGNORECASE | re.DOTALL)


def categoria(caminho: Path) -> str:
    nome = str(caminho).casefold()
    for termo, resultado in (
        ("gateway", "gateway"), ("view", "views"), ("permiss", "permissoes"),
        ("tarefa", "tarefas"), ("banco", "banco"), ("voz", "voz"),
        ("segur", "seguranca"), ("http", "rest"), ("discord", "discord"),
    ):
        if termo in nome:
            return resultado
    return "pimcord" if "pimcord" in nome else "python"


def exemplo(codigo: str, instrucao: str, fonte: str, *, tipo: str = "instrucao_codigo") -> dict[str, object] | None:
    codigo = codigo.strip()
    if len(codigo) < 20:
        return None
    try:
        ast.parse(codigo)
    except SyntaxError:
        return None
    return {
        "linguagem": "python",
        "tipo": tipo,
        "instrucao": instrucao.strip(),
        "contexto": f"Fonte real do projeto Pimcord: {fonte}",
        "resposta": codigo,
        "categoria": categoria(Path(fonte)),
        "nivel": "avancado" if len(codigo) > 1200 else "intermediario",
        "objetivo": "Aprender a estrutura real usada pelo projeto Pimcord.",
        "criterios": ["compila com Python", "não contém segredo literal", "preserva APIs reais do projeto"],
        "arquivos": [fonte],
        "testes": [],
        "dependencias": [],
        "tags": ["codigo-real", "pimcord", tipo],
        "fonte": f"Pimcord-MIT-local/{fonte}",
        "licenca": "MIT",
    }


def coletar(raiz: Path, destino: Path) -> int:
    destino.parent.mkdir(parents=True, exist_ok=True)
    aceitos: list[dict[str, object]] = []
    for caminho in sorted(raiz.rglob("*.py")):
        if any(parte in {".git", "__pycache__", ".pytest_cache", "build", "dist"} for parte in caminho.parts):
            continue
        texto = caminho.read_text(encoding="utf-8", errors="ignore")
        linhas = texto.splitlines()
        if len(linhas) >= 8:
            corte = min(256, len(linhas))
            codigo = "\n".join(linhas[:corte])
            item = exemplo(codigo, f"Continue e explique a implementação real de {caminho.name} da Pimcord.", str(caminho.relative_to(raiz)), tipo="continuacao_codigo")
            if item:
                aceitos.append(item)
    for caminho in sorted(raiz.rglob("*.md")):
        if any(parte in {".git", "build", "dist"} for parte in caminho.parts):
            continue
        texto = caminho.read_text(encoding="utf-8", errors="ignore")
        for bloco in BLOCO_PYTHON.findall(texto):
            item = exemplo(bloco, f"Implemente o exemplo Python documentado em {caminho.name} usando a API real da Pimcord.", str(caminho.relative_to(raiz)))
            if item:
                aceitos.append(item)
    with destino.open("w", encoding="utf-8") as saida:
        for item in aceitos:
            saida.write(json.dumps(item, ensure_ascii=False, sort_keys=True) + "\n")
    return len(aceitos)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raiz", type=Path, default=Path("."))
    parser.add_argument("--destino", type=Path, default=Path("dados/brutos/pimcord_local.jsonl"))
    args = parser.parse_args()
    total = coletar(args.raiz.resolve(), args.destino)
    print(f"[PimcordIA] {total} exemplos reais coletados em {args.destino}")


if __name__ == "__main__":
    main()
