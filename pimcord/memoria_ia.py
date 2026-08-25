"""Memória local consultável da PimcordIA.

A memória não é um modelo geral e não finge conhecer tudo. Ela organiza o
conhecimento disponível no ambiente: API pública do Pimcord, padrões da
biblioteca padrão do Python e regras de projeto verificáveis. O resultado é
usado como contexto antes da geração neural ou determinística.
"""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True, slots=True)
class TrechoConhecimento:
    titulo: str
    texto: str
    termos: tuple[str, ...]


_TOPICOS_PYTHON = (
    ("asyncio", "concorrência assíncrona, corrotinas, tarefas, cancelamento e asyncio.gather"),
    ("sqlite3", "persistência SQLite, conexão, transações, consultas parametrizadas e sqlite3.Row"),
    ("typing", "anotações, Protocol, TypeVar, Generic, Literal, TypedDict e tipos opcionais"),
    ("dataclasses", "modelos de dados imutáveis, slots, defaults e validação de estado"),
    ("pathlib", "caminhos portáveis, leitura, escrita e criação segura de diretórios"),
    ("logging", "logs estruturados, níveis, handlers e diagnóstico sem expor segredos"),
    ("ast", "parse, análise estática e validação de código Python sem execução"),
    ("json", "serialização, desserialização, schema e tratamento de JSON inválido"),
    ("re", "expressões regulares, grupos nomeados e normalização de texto"),
    ("datetime", "datas, fusos, timedelta e armazenamento consistente de horários"),
    ("contextlib", "gerenciadores de contexto síncronos e assíncronos"),
    ("collections", "defaultdict, Counter, deque e estruturas de dados"),
    ("enum", "enums para estados, permissões e valores controlados"),
    ("functools", "cache, wraps, partial e composição de funções"),
    ("inspect", "assinaturas, introspecção e identificação de corrotinas"),
    ("unittest", "fixtures, mocks, casos de teste e isolamento"),
)


def _normalizar(texto: str) -> str:
    return unicodedata.normalize("NFKD", texto.casefold()).encode("ascii", "ignore").decode()


def _palavras(texto: str) -> set[str]:
    return {item for item in re.findall(r"[a-z0-9_]{2,}", _normalizar(texto))}


def _trechos_python() -> tuple[TrechoConhecimento, ...]:
    return tuple(
        TrechoConhecimento(
            titulo=f"Python: {nome}",
            texto=f"{nome}: {descricao}. Prefira APIs documentadas, tratamento explícito de erros e testes isolados.",
            termos=(nome, *descricao.split()),
        )
        for nome, descricao in _TOPICOS_PYTHON
    )


def _trechos_pimcord() -> tuple[TrechoConhecimento, ...]:
    try:
        from .catalogo import catalogar
        modulos = catalogar().get("modulos", {}).get("pimcord", {})
    except Exception:
        modulos = {}
    saida: list[TrechoConhecimento] = []
    for nome, item in modulos.items():
        doc = str(item.get("doc", "")).strip()
        assinatura = str(item.get("assinatura", "")).strip()
        metodos = ", ".join(str(chave) for chave in item.get("metodos", {}))
        texto = f"{nome}{assinatura}. {doc} Métodos: {metodos}."
        saida.append(TrechoConhecimento(f"Pimcord: {nome}", texto, tuple(_palavras(texto))))
    return tuple(saida)


class MemoriaLocal:
    """Índice pequeno, determinístico e sem rede para recuperação de contexto."""

    def __init__(self, trechos: Iterable[TrechoConhecimento] | None = None) -> None:
        self.trechos = tuple(trechos) if trechos is not None else (*_trechos_python(), *_trechos_pimcord())

    def consultar(self, pedido: str, *, limite: int = 12) -> str:
        if not isinstance(pedido, str) or not pedido.strip():
            return ""
        consulta = _palavras(pedido)
        pontuados: list[tuple[int, TrechoConhecimento]] = []
        for trecho in self.trechos:
            termos = _palavras(" ".join(trecho.termos))
            pontos = len(consulta & termos)
            if pontos:
                pontuados.append((pontos, trecho))
        pontuados.sort(key=lambda item: (-item[0], item[1].titulo))
        selecionados = [trecho.texto for _, trecho in pontuados[:max(1, limite)]]
        return "\n".join(f"- {texto}" for texto in selecionados)


def contexto_local(pedido: str, *, limite: int = 12) -> str:
    """Retorna contexto de Python e Pimcord para anexar ao prompt."""
    return MemoriaLocal().consultar(pedido, limite=limite)


__all__ = ["TrechoConhecimento", "MemoriaLocal", "contexto_local"]
