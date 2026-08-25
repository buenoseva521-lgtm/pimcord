from __future__ import annotations

import ast
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = Path('/tmp/discord-openapi.json')
CLIENTE = ROOT / 'pimcord' / 'http' / 'cliente.py'
OUT = ROOT / 'docs' / 'AUDITORIA_OPENAPI_LOCAL.md'

METODOS = {'get', 'post', 'put', 'patch', 'delete', 'head', 'options', 'trace'}

def rotas_ast(node: ast.AST, ambiente: dict[str, set[str]] | None = None) -> set[str]:
    ambiente = ambiente or {}
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return {node.value}
    if isinstance(node, ast.JoinedStr):
        resultados = {''}
        for valor in node.values:
            if isinstance(valor, ast.Constant) and isinstance(valor.value, str):
                partes = {valor.value}
            elif isinstance(valor, ast.FormattedValue):
                partes = {'{param}'}
                if isinstance(valor.value, ast.Name) and valor.value.id in ambiente:
                    partes |= ambiente[valor.value.id]
            else:
                return set()
            resultados = {prefixo + parte for prefixo in resultados for parte in partes}
        return resultados
    if isinstance(node, ast.IfExp):
        return rotas_ast(node.body, ambiente) | rotas_ast(node.orelse, ambiente)
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        esquerdas = rotas_ast(node.left, ambiente)
        direitas = rotas_ast(node.right, ambiente)
        return {esquerda + direita for esquerda in esquerdas for direita in direitas}
    return set()


def rotas_locais() -> set[tuple[str, str]]:
    tree = ast.parse(CLIENTE.read_text(encoding='utf-8'))
    encontradas: set[tuple[str, str]] = set()
    for funcao in (node for node in ast.walk(tree) if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))):
        ambiente: dict[str, set[str]] = {}
        argumentos = list(funcao.args.args) + list(funcao.args.kwonlyargs)
        padrao_inicial = len(argumentos) - len(funcao.args.defaults)
        for argumento, padrao in zip(argumentos[padrao_inicial:], funcao.args.defaults):
            valores = rotas_ast(padrao, ambiente)
            if valores:
                ambiente[argumento.arg] = valores
        for argumento, padrao in zip(funcao.args.kwonlyargs, funcao.args.kw_defaults):
            if padrao is not None:
                valores = rotas_ast(padrao, ambiente)
                if valores:
                    ambiente[argumento.arg] = valores
        for node in ast.walk(funcao):
            if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
                valores = rotas_ast(node.value, ambiente)
                if valores:
                    ambiente[node.targets[0].id] = valores
            if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == 'requisitar'):
                continue
            if len(node.args) < 2 or not isinstance(node.args[0], ast.Constant):
                continue
            metodo = node.args[0].value
            rotas = rotas_ast(node.args[1], ambiente) if not isinstance(node.args[1], ast.Name) else ambiente.get(node.args[1].id, set())
            if isinstance(metodo, str) and metodo.lower() in METODOS:
                encontradas.update((metodo.upper(), normalizar_rota(rota)) for rota in rotas)
    return encontradas

def normalizar_rota(rota: str) -> str:
    return re.sub(r'\{[^}]+\}', '{param}', rota)


def operacoes_oficiais() -> set[tuple[str, str]]:
    dados = json.loads(SPEC.read_text(encoding='utf-8'))
    return {(m.upper(), normalizar_rota(p)) for p, item in dados.get('paths', {}).items() for m in item if m.lower() in METODOS}

def main() -> None:
    oficiais = operacoes_oficiais()
    locais = rotas_locais()
    rotas_oficiais = {p for _, p in oficiais}
    rotas_locais_set = {p for _, p in locais}
    texto = [
        '# Auditoria estática OpenAPI do Pimcord', '',
        '> Comparação conservadora. Rotas construídas por composição, aliases e operações fora do escopo podem exigir revisão manual; ausência nesta lista não prova ausência no pacote.', '',
        f'- Operações oficiais no OpenAPI v10: **{len(oficiais)}**',
        f'- Chamadas literais identificáveis em `ClienteHTTP`: **{len(locais)}**',
        f'- Caminhos oficiais: **{len(rotas_oficiais)}**',
        f'- Caminhos locais identificáveis: **{len(rotas_locais_set)}**', '',
        '## Operações oficiais sem correspondência literal', '',
    ]
    for metodo, rota in sorted(oficiais - locais):
        texto.append(f'- `{metodo} {rota}`')
    texto += ['', '## Rotas locais identificáveis', '']
    for metodo, rota in sorted(locais):
        texto.append(f'- `{metodo} {rota}`')
    OUT.write_text('\n'.join(texto) + '\n', encoding='utf-8')
    print(f'oficiais={len(oficiais)} locais={len(locais)} sem_correspondencia={len(oficiais - locais)}')

if __name__ == '__main__':
    main()
