"""Coordenação de workers e leases do Pimcord.

O transporte é pequeno, assíncrono e injetável: a implementação local serve
para testes e processos únicos; aplicações distribuídas podem adaptar Redis,
SQLite compartilhado ou outro transporte sem contaminar o núcleo.
"""
from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass
from typing import Any, Protocol


@dataclass(slots=True, frozen=True)
class Lease:
    chave: str
    trabalhador: str
    época: int
    expira_em: float

    @property
    def válida(self) -> bool:
        return self.expira_em > time.monotonic()


class TransporteCoordenação(Protocol):
    async def adquirir(self, chave: str, trabalhador: str, *, duração: float = 30.0) -> Lease | None: ...
    async def renovar(self, lease: Lease, *, duração: float = 30.0) -> Lease | None: ...
    async def liberar(self, lease: Lease) -> bool: ...
    async def publicar(self, chave: str, estado: dict[str, Any]) -> None: ...
    async def estados(self) -> dict[str, dict[str, Any]]: ...


class CoordenaçãoLocal:
    """Coordenador determinístico para modo offline e um único processo."""

    def __init__(self) -> None:
        self._leases: dict[str, Lease] = {}
        self._épocas: dict[str, int] = {}
        self._estados: dict[str, dict[str, Any]] = {}
        self._trava = asyncio.Lock()

    async def adquirir(self, chave: str, trabalhador: str, *, duração: float = 30.0) -> Lease | None:
        if duração <= 0:
            raise ValueError("duração do lease deve ser positiva")
        agora = time.monotonic()
        async with self._trava:
            atual = self._leases.get(chave)
            if atual and atual.válida and atual.trabalhador != trabalhador:
                return None
            época = self._épocas.get(chave, 0) + 1
            self._épocas[chave] = época
            lease = Lease(chave, trabalhador, época, agora + duração)
            self._leases[chave] = lease
            return lease

    async def renovar(self, lease: Lease, *, duração: float = 30.0) -> Lease | None:
        if duração <= 0:
            raise ValueError("duração do lease deve ser positiva")
        async with self._trava:
            atual = self._leases.get(lease.chave)
            if not atual or atual.época != lease.época or atual.trabalhador != lease.trabalhador or not atual.válida:
                return None
            renovada = Lease(lease.chave, lease.trabalhador, lease.época, time.monotonic() + duração)
            self._leases[lease.chave] = renovada
            return renovada

    async def liberar(self, lease: Lease) -> bool:
        async with self._trava:
            atual = self._leases.get(lease.chave)
            if not atual or atual.época != lease.época or atual.trabalhador != lease.trabalhador:
                return False
            self._leases.pop(lease.chave, None)
            return True

    async def publicar(self, chave: str, estado: dict[str, Any]) -> None:
        async with self._trava:
            self._estados[chave] = dict(estado)

    async def estados(self) -> dict[str, dict[str, Any]]:
        async with self._trava:
            return {chave: dict(estado) for chave, estado in self._estados.items()}

    async def expurgar(self) -> int:
        agora = time.monotonic()
        async with self._trava:
            expirados = [chave for chave, lease in self._leases.items() if lease.expira_em <= agora]
            for chave in expirados:
                self._leases.pop(chave, None)
            return len(expirados)


__all__ = ["Lease", "TransporteCoordenação", "CoordenaçãoLocal"]
