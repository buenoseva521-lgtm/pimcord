"""Tarefas, filas e agendamento resiliente do Pimcord."""
from __future__ import annotations

import asyncio
import inspect
import logging
import random
from dataclasses import dataclass
from typing import Any, Awaitable, Callable, Generic, TypeVar

T = TypeVar("T")


@dataclass(slots=True)
class PoliticaRetentativa:
    tentativas: int = 3
    atraso_inicial: float = 1.0
    fator: float = 2.0
    atraso_maximo: float = 60.0
    jitter: float = 0.1

    def atraso(self, tentativa: int) -> float:
        base = min(self.atraso_inicial * (self.fator ** max(0, tentativa - 1)), self.atraso_maximo)
        return max(0.0, base + random.uniform(-self.jitter, self.jitter) * base)


class TarefaAgendada:
    def __init__(self, funcao: Callable[[], Any], intervalo: float, *, nome: str | None = None, politica: PoliticaRetentativa | None = None):
        self.funcao = funcao
        self.intervalo = float(intervalo)
        self.nome = nome or getattr(funcao, "__name__", "tarefa")
        self.politica = politica or PoliticaRetentativa()
        self.tarefa: asyncio.Task[Any] | None = None
        self.ultima_excecao: Exception | None = None
        self.execucoes = 0
        self.falhas = 0
        self.logger = logging.getLogger("pimcord.tarefas")

    @property
    def ativa(self) -> bool:
        return self.tarefa is not None and not self.tarefa.done()

    def iniciar(self) -> "TarefaAgendada":
        if self.ativa:
            return self
        self.tarefa = asyncio.create_task(self._executar(), name=f"pimcord:{self.nome}")
        return self

    async def _chamar(self) -> Any:
        resultado = self.funcao()
        return await resultado if inspect.isawaitable(resultado) else resultado

    async def _executar(self) -> None:
        while True:
            sucesso = False
            for tentativa in range(1, self.politica.tentativas + 1):
                try:
                    await self._chamar()
                    self.execucoes += 1
                    self.ultima_excecao = None
                    sucesso = True
                    break
                except asyncio.CancelledError:
                    raise
                except Exception as erro:
                    self.falhas += 1
                    self.ultima_excecao = erro
                    self.logger.exception("Falha na tarefa %s (tentativa %s/%s)", self.nome, tentativa, self.politica.tentativas)
                    if tentativa < self.politica.tentativas:
                        await asyncio.sleep(self.politica.atraso(tentativa))
            await asyncio.sleep(self.intervalo if sucesso else self.politica.atraso(self.politica.tentativas))

    async def parar(self) -> None:
        if self.tarefa:
            self.tarefa.cancel()
            try:
                await self.tarefa
            except asyncio.CancelledError:
                pass
            self.tarefa = None


class Agendador:
    def __init__(self):
        self.tarefas: dict[str, TarefaAgendada] = {}

    def registrar(self, nome: str, funcao: Callable[[], Any], intervalo: float, *, politica: PoliticaRetentativa | None = None) -> TarefaAgendada:
        if nome in self.tarefas:
            raise ValueError(f"Já existe uma tarefa chamada '{nome}'")
        tarefa = TarefaAgendada(funcao, intervalo, nome=nome, politica=politica)
        self.tarefas[nome] = tarefa
        return tarefa

    def iniciar_todas(self) -> None:
        for tarefa in self.tarefas.values():
            tarefa.iniciar()

    async def parar_todas(self) -> None:
        await asyncio.gather(*(tarefa.parar() for tarefa in self.tarefas.values()))


class FilaAssincrona(Generic[T]):
    """Fila limitada com produtores, consumidores e encerramento explícito."""
    _SENTINELA = object()

    def __init__(self, limite: int = 100):
        self._fila: asyncio.Queue[Any] = asyncio.Queue(maxsize=limite)
        self.limite = limite
        self.processados = 0
        self.erros = 0
        self.encerrada = False

    async def colocar(self, item: T) -> None:
        if self.encerrada:
            raise RuntimeError("A fila já foi encerrada")
        await self._fila.put(item)

    async def consumir(self, funcao: Callable[[T], Any], *, consumidores: int = 1) -> list[asyncio.Task[Any]]:
        async def trabalhador() -> None:
            while True:
                item = await self._fila.get()
                try:
                    if item is self._SENTINELA:
                        return
                    resultado = funcao(item)
                    if inspect.isawaitable(resultado):
                        await resultado
                    self.processados += 1
                except asyncio.CancelledError:
                    raise
                except Exception:
                    self.erros += 1
                    logging.getLogger("pimcord.fila").exception("Erro ao processar item da fila")
                finally:
                    self._fila.task_done()
        return [asyncio.create_task(trabalhador(), name=f"pimcord:fila:{i}") for i in range(max(1, consumidores))]

    async def encerrar(self, consumidores: int = 1) -> None:
        self.encerrada = True
        for _ in range(max(1, consumidores)):
            await self._fila.put(self._SENTINELA)


__all__ = ["PoliticaRetentativa", "TarefaAgendada", "Agendador", "FilaAssincrona"]
