"""Prepara exemplos licenciados para o treinamento da PimcordIA.

O formato de entrada aceita código puro ou exemplos instrucionais. O script não
cria conhecimento artificial: quando uma instrução não existe, o exemplo é
marcado como ``continuacao_codigo`` para não ser confundido com uma resposta de
especialista.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import random
import re
from collections import Counter
from pathlib import Path
from typing import Any

SEGREDO = re.compile(
    r"(?i)(?:token|api[_-]?key|secret|password|senha|authorization)\s*="
    r"\s*[\"'][^\"']+[\"']"
)
LICENCAS_PERMITIDAS = {
    "MIT", "BSD-2-Clause", "BSD-3-Clause", "Apache-2.0", "CC-BY-4.0", "CC0-1.0"
}
CAMPOS_INSTRUCAO = ("instrucao", "instrução", "prompt", "pedido", "pergunta")
CAMPOS_RESPOSTA = ("resposta", "answer", "saida", "saída", "completion")
PLACEHOLDER = re.compile(r"(?i)(?:comando foi executado com sucesso|recurso .* preparado|resposta genérica|implementação pendente)")
CATEGORIAS = {"python", "pimcord", "discord", "rest", "gateway", "views", "permissoes", "tarefas", "banco", "voz", "seguranca", "arquitetura"}
NIVEIS = {"iniciante", "intermediario", "avancado", "especialista"}


def _lista_strings(valor: Any) -> list[str]:
    if not isinstance(valor, list):
        return []
    return [str(item).strip() for item in valor[:100] if str(item).strip()]


def _primeiro_texto(exemplo: dict[str, Any], campos: tuple[str, ...]) -> str:
    for campo in campos:
        valor = exemplo.get(campo)
        if isinstance(valor, str) and valor.strip():
            return valor.strip()
    return ""


def normalizar(exemplo: dict[str, Any]) -> dict[str, Any] | None:
    if not isinstance(exemplo, dict):
        return None
    codigo = exemplo.get("codigo") or _primeiro_texto(exemplo, CAMPOS_RESPOSTA)
    linguagem = str(exemplo.get("linguagem", "python")).casefold()
    fonte = str(exemplo.get("fonte", "desconhecida"))
    licenca = str(exemplo.get("licenca", "")).strip()
    if not isinstance(codigo, str) or linguagem != "python" or licenca not in LICENCAS_PERMITIDAS:
        return None
    codigo = codigo.strip()
    if len(codigo) < 20 or len(codigo) > 200_000 or SEGREDO.search(codigo) or PLACEHOLDER.search(codigo):
        return None
    try:
        ast.parse(codigo)
    except (SyntaxError, ValueError):
        return None
    instrucao = _primeiro_texto(exemplo, CAMPOS_INSTRUCAO)
    contexto = exemplo.get("contexto", "")
    if not isinstance(contexto, str):
        contexto = json.dumps(contexto, ensure_ascii=False, sort_keys=True)
    arquivos = _lista_strings(exemplo.get("arquivos", []))
    testes = _lista_strings(exemplo.get("testes", []))
    dependencias = _lista_strings(exemplo.get("dependencias", []))
    tags = _lista_strings(exemplo.get("tags", []))
    categoria = str(exemplo.get("categoria", "pimcord" if "pimcord" in codigo.casefold() else "python")).casefold().strip()
    if categoria not in CATEGORIAS:
        categoria = "python"
    nivel = str(exemplo.get("nivel", "intermediario")).casefold().strip()
    if nivel not in NIVEIS:
        nivel = "intermediario"
    objetivo = str(exemplo.get("objetivo", "")).strip()
    criterios = _lista_strings(exemplo.get("criterios", []))
    tipo = "instrucao_codigo" if instrucao else "continuacao_codigo"
    return {
        "linguagem": "python",
        "tipo": tipo,
        "instrucao": instrucao,
        "contexto": contexto.strip(),
        "resposta": codigo,
        "codigo": codigo,
        "arquivos": arquivos,
        "testes": testes,
        "dependencias": dependencias,
        "tags": tags,
        "categoria": categoria,
        "nivel": nivel,
        "objetivo": objetivo,
        "criterios": criterios,
        "fonte": fonte,
        "licenca": licenca,
    }


def _chave(exemplo: dict[str, Any]) -> str:
    material = "\n".join((exemplo["instrucao"], exemplo["contexto"], exemplo["resposta"]))
    return hashlib.sha256(material.encode("utf-8")).hexdigest()


def _grupo(exemplo: dict[str, Any]) -> str:
    """Agrupa por fonte para impedir que um mesmo projeto vaze para validação."""
    return hashlib.sha256(exemplo["fonte"].encode("utf-8")).hexdigest()[:16]


def preparar(origem: Path, destino: Path, *, seed: int = 42, validacao: float = 0.1, teste: float = 0.1) -> int:
    if not 0 <= validacao < 1 or not 0 <= teste < 1 or validacao + teste >= 1:
        raise ValueError("As proporções de validação e teste devem somar menos que 1.")
    destino.parent.mkdir(parents=True, exist_ok=True)
    aceitos: list[dict[str, Any]] = []
    vistos: set[str] = set()
    rejeitados = Counter()
    for arquivo in sorted(origem.glob("*.jsonl")):
        for numero, linha in enumerate(arquivo.read_text(encoding="utf-8").splitlines(), 1):
            try:
                bruto = json.loads(linha)
            except json.JSONDecodeError:
                rejeitados["json_invalido"] += 1
                continue
            exemplo = normalizar(bruto)
            if exemplo is None:
                rejeitados["contrato_ou_seguranca"] += 1
                continue
            chave = _chave(exemplo)
            if chave in vistos:
                rejeitados["duplicado"] += 1
                continue
            vistos.add(chave)
            exemplo["id"] = chave
            exemplo["arquivo_origem"] = str(arquivo)
            exemplo["linha_origem"] = numero
            aceitos.append(exemplo)
    grupos: dict[str, list[dict[str, Any]]] = {}
    for exemplo in aceitos:
        grupos.setdefault(_grupo(exemplo), []).append(exemplo)
    chaves_grupo = list(grupos)
    random.Random(seed).shuffle(chaves_grupo)
    total = len(aceitos)
    alvo_teste = round(total * teste)
    alvo_validacao = round(total * validacao)
    grupos_teste: set[str] = set()
    grupos_validacao: set[str] = set()
    contagem_teste = contagem_validacao = 0
    fallback_por_exemplo = len(grupos) < 3 and total >= 3
    if fallback_por_exemplo:
        ordem = list(range(total))
        random.Random(seed).shuffle(ordem)
        indices_teste = set(ordem[:alvo_teste])
        indices_validacao = set(ordem[alvo_teste:alvo_teste + alvo_validacao])
    else:
        for grupo in chaves_grupo:
            tamanho = len(grupos[grupo])
            if contagem_teste < alvo_teste:
                grupos_teste.add(grupo)
                contagem_teste += tamanho
            elif contagem_validacao < alvo_validacao:
                grupos_validacao.add(grupo)
                contagem_validacao += tamanho
    destino.parent.mkdir(parents=True, exist_ok=True)
    contagem_split = Counter()
    with destino.open("w", encoding="utf-8") as saida:
        for indice, exemplo in enumerate(aceitos):
            grupo = _grupo(exemplo)
            if fallback_por_exemplo:
                exemplo["split"] = "teste" if indice in indices_teste else "validacao" if indice in indices_validacao else "treino"
            else:
                exemplo["split"] = "teste" if grupo in grupos_teste else "validacao" if grupo in grupos_validacao else "treino"
            contagem_split[exemplo["split"]] += 1
            saida.write(json.dumps(exemplo, ensure_ascii=False, sort_keys=True) + "\n")
    manifesto = {
        "seed": seed,
        "origem": str(origem),
        "destino": str(destino),
        "exemplos": total,
        "splits": dict(contagem_split),
        "tipos": dict(Counter(item["tipo"] for item in aceitos)),
        "categorias": dict(Counter(item["categoria"] for item in aceitos)),
        "niveis": dict(Counter(item["nivel"] for item in aceitos)),
        "fontes": len(grupos),
        "split_por_exemplo_fallback": fallback_por_exemplo,
        "rejeitados": dict(rejeitados),
    }
    destino.with_suffix(".manifesto.json").write_text(
        json.dumps(manifesto, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return total


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--origem", type=Path, default=Path("dados/brutos"))
    parser.add_argument("--destino", type=Path, default=Path("dados/limpos.jsonl"))
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--validacao", type=float, default=0.1)
    parser.add_argument("--teste", type=float, default=0.1)
    args = parser.parse_args()
    total = preparar(args.origem, args.destino, seed=args.seed, validacao=args.validacao, teste=args.teste)
    print(f"[PimcordIA] {total} exemplos preparados em {args.destino}")


if __name__ == "__main__":
    main()
