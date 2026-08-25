"""Catálogo runtime da API Pimcord para a PimcordIA Neural.

O catálogo é derivado da instalação atual, limitado a símbolos públicos e
serializável. Ele não executa funções nem importa módulos opcionais de rede.
"""
from __future__ import annotations

import importlib
import inspect
from types import ModuleType
from typing import Any, Iterable

MODULOS_PUBLICOS = (
    "pimcord",
    "pimcord.comandos",
    "pimcord.discord.modelos",
    "pimcord.discord.recursos",
    "pimcord.interacoes.modelos",
    "pimcord.permissoes",
    "pimcord.economia",
    "pimcord.tarefas",
    "pimcord.extensoes",
)


def _assinatura(valor: Any) -> str | None:
    try:
        return str(inspect.signature(valor))
    except (TypeError, ValueError):
        return None


def _entrada(nome: str, valor: Any) -> dict[str, Any]:
    item: dict[str, Any] = {
        "nome": nome,
        "tipo": "classe" if inspect.isclass(valor) else "funcao" if callable(valor) else "objeto",
        "doc": (inspect.getdoc(valor) or "").splitlines()[0][:400] if inspect.getdoc(valor) else "",
        "assinatura": _assinatura(valor),
    }
    if inspect.isclass(valor):
        metodos: dict[str, str | None] = {}
        for atributo in dir(valor):
            if atributo.startswith("_"):
                continue
            membro = getattr(valor, atributo, None)
            if callable(membro):
                metodos[atributo] = _assinatura(membro)
        item["metodos"] = dict(sorted(metodos.items())[:200])
    return item


def catalogar(modulos: Iterable[str] = MODULOS_PUBLICOS) -> dict[str, Any]:
    resultado: dict[str, Any] = {"modulos": {}, "versao": None}
    for nome_modulo in modulos:
        try:
            modulo: ModuleType = importlib.import_module(nome_modulo)
        except Exception:
            continue
        simbolos: dict[str, Any] = {}
        for nome, valor in sorted(vars(modulo).items()):
            modulo_do_simbolo = getattr(valor, "__module__", nome_modulo)
            pertence_ao_pacote = modulo_do_simbolo == nome_modulo or modulo_do_simbolo.startswith("pimcord.")
            if nome.startswith("_") or not pertence_ao_pacote:
                continue
            simbolos[nome] = _entrada(nome, valor)
        resultado["modulos"][nome_modulo] = simbolos
        if nome_modulo == "pimcord":
            resultado["versao"] = getattr(modulo, "__version__", None)
    return resultado


def resumo_catalogo(catalogo: dict[str, Any] | None = None) -> str:
    catalogo = catalogo or catalogar()
    linhas = [f"Versão Pimcord: {catalogo.get('versao') or 'desconhecida'}"]
    for modulo, simbolos in catalogo.get("modulos", {}).items():
        for nome, item in simbolos.items():
            assinatura = item.get("assinatura") or ""
            metodos = ", ".join(item.get("metodos", {}))
            linhas.append(f"{modulo}.{nome}{assinatura}" + (f"; métodos: {metodos}" if metodos else ""))
    return "\n".join(linhas)
