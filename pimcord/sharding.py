"""Supervisor resiliente de shards do Pimcord.

A API pública é em português e permanece assíncrona. O supervisor não presume
um serviço externo: a coordenação pode ser local ou implementada por um
adaptador de transporte injetado pelo aplicativo.
"""
from __future__ import annotations

import asyncio
import json
import os
import tempfile
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Awaitable, Callable

from .coordenacao import Lease, TransporteCoordenação


@dataclass(slots=True)
class ShardInfo:
    id: int
    total: int
    conectado: bool = False
    latencia: float | None = None
    estado: str = "parado"
    reinicios: int = 0
    ultimo_erro: str | None = None
    ultima_mudanca: float = field(default_factory=time.monotonic)
    tarefa: asyncio.Task[Any] | None = field(default=None, repr=False)

    def pertence(self, servidor_id: int | str) -> bool:
        return (int(servidor_id) >> 22) % self.total == self.id

    def marcar(self, estado: str, *, latencia: float | None = None, erro: Exception | None = None) -> None:
        self.estado = estado
        self.conectado = estado == "conectado"
        if latencia is not None:
            self.latencia = latencia
        if erro is not None:
            self.ultimo_erro = f"{type(erro).__name__}: {erro}"
        self.ultima_mudanca = time.monotonic()


@dataclass(slots=True)
class GerenciadorDeShards:
    total: int
    iniciar_shard: Callable[[ShardInfo], Awaitable[Any]] | None = None
    shards: dict[int, ShardInfo] = field(default_factory=dict)
    max_reinicios: int | None = None
    atraso_inicial: float = 1.0
    atraso_maximo: float = 60.0
    _parando: bool = field(default=False, init=False, repr=False)
    coordenador: TransporteCoordenação | None = None
    trabalhador: str = "pimcord-local"
    duração_lease: float = 30.0
    caminho_checkpoint: str | Path | None = None

    def __post_init__(self) -> None:
        if self.total < 1:
            raise ValueError("total de shards deve ser maior que zero")
        if self.atraso_inicial <= 0 or self.atraso_maximo < self.atraso_inicial:
            raise ValueError("atrasos de reinício inválidos")
        if self.duração_lease <= 0:
            raise ValueError("duração do lease deve ser positiva")
        self.shards = {i: ShardInfo(i, self.total) for i in range(self.total)}
        self._carregar_checkpoint()

    def _carregar_checkpoint(self) -> None:
        if self.caminho_checkpoint is None:
            return
        caminho = Path(self.caminho_checkpoint)
        try:
            dados = json.loads(caminho.read_text(encoding="utf-8"))
        except (FileNotFoundError, OSError, ValueError, TypeError):
            return
        if dados.get("total") != self.total:
            return
        for chave, estado in (dados.get("shards") or {}).items():
            try:
                shard = self.shards[int(chave)]
            except (KeyError, TypeError, ValueError):
                continue
            shard.reinicios = max(0, int(estado.get("reinicios", 0)))
            shard.latencia = estado.get("latencia")
            shard.ultimo_erro = estado.get("ultimo_erro")
            retomavel = bool(estado.get("conectado")) or estado.get("estado") in {"conectado", "encerrado"}
            shard.estado = "retomando" if retomavel else "parado"
            shard.conectado = False

    def _salvar_checkpoint(self) -> None:
        if self.caminho_checkpoint is None:
            return
        caminho = Path(self.caminho_checkpoint)
        caminho.parent.mkdir(parents=True, exist_ok=True)
        dados = {"total": self.total, "trabalhador": self.trabalhador, "shards": self.estado()}
        fd, temporario = tempfile.mkstemp(prefix=f".{caminho.name}.", dir=str(caminho.parent))
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as arquivo:
                json.dump(dados, arquivo, ensure_ascii=False, sort_keys=True)
                arquivo.flush()
                os.fsync(arquivo.fileno())
            os.replace(temporario, caminho)
        finally:
            try:
                os.unlink(temporario)
            except FileNotFoundError:
                pass

    def shard_de_servidor(self, servidor_id: int | str) -> ShardInfo:
        return self.shards[(int(servidor_id) >> 22) % self.total]

    @property
    def saudavel(self) -> bool:
        return bool(self.shards) and all(shard.conectado for shard in self.shards.values())

    def estado(self) -> dict[int, dict[str, Any]]:
        return {
            shard.id: {
                "estado": shard.estado,
                "conectado": shard.conectado,
                "latencia": shard.latencia,
                "reinicios": shard.reinicios,
                "ultimo_erro": shard.ultimo_erro,
            }
            for shard in self.shards.values()
        }

    async def _publicar_estado(self, shard: ShardInfo) -> None:
        self._salvar_checkpoint()
        if self.coordenador is not None:
            await self.coordenador.publicar(f"shard:{shard.id}", self.estado()[shard.id])

    async def _supervisionar(self, shard: ShardInfo) -> None:
        atraso = self.atraso_inicial
        while not self._parando and (self.max_reinicios is None or shard.reinicios <= self.max_reinicios):
            lease: Lease | None = None
            if self.coordenador is not None:
                lease = await self.coordenador.adquirir(
                    f"shard:{shard.id}", self.trabalhador, duração=self.duração_lease
                )
                if lease is None:
                    shard.marcar("aguardando_lease")
                    await self._publicar_estado(shard)
                    await asyncio.sleep(min(self.duração_lease / 3, self.atraso_maximo))
                    continue
            shard.marcar("conectando")
            await self._publicar_estado(shard)
            try:
                if self.iniciar_shard is None:
                    shard.marcar("conectado")
                    await self._publicar_estado(shard)
                    return
                resultado = await self.iniciar_shard(shard)
                if isinstance(resultado, (int, float)):
                    shard.marcar("conectado", latencia=float(resultado))
                else:
                    shard.marcar("conectado")
                await self._publicar_estado(shard)
                return
            except asyncio.CancelledError:
                shard.marcar("encerrado")
                await self._publicar_estado(shard)
                raise
            except Exception as erro:
                shard.reinicios += 1
                shard.marcar("reconectando", erro=erro)
                if self._parando or (self.max_reinicios is not None and shard.reinicios > self.max_reinicios):
                    shard.marcar("falhou", erro=erro)
                    await self._publicar_estado(shard)
                    return
                await self._publicar_estado(shard)
                await asyncio.sleep(atraso)
                atraso = min(atraso * 2, self.atraso_maximo)
            finally:
                if lease is not None and self.coordenador is not None:
                    await self.coordenador.liberar(lease)

    async def iniciar(self) -> None:
        self._parando = False
        for shard in self.shards.values():
            if shard.tarefa and not shard.tarefa.done():
                continue
            shard.tarefa = asyncio.create_task(self._supervisionar(shard), name=f"pimcord-shard-{shard.id}")

    async def aguardar_saude(self, tempo_limite: float | None = None) -> bool:
        inicio = time.monotonic()
        while not self.saudavel:
            if tempo_limite is not None and time.monotonic() - inicio >= tempo_limite:
                return False
            if self._parando:
                return False
            await asyncio.sleep(0.05)
        return True

    async def reiniciar(self, shard_id: int) -> None:
        shard = self.shards[shard_id]
        if shard.tarefa and not shard.tarefa.done():
            shard.tarefa.cancel()
            await asyncio.gather(shard.tarefa, return_exceptions=True)
        shard.tarefa = asyncio.create_task(self._supervisionar(shard), name=f"pimcord-shard-{shard.id}")

    async def parar(self) -> None:
        self._parando = True
        tarefas = [shard.tarefa for shard in self.shards.values() if shard.tarefa and not shard.tarefa.done()]
        for tarefa in tarefas:
            tarefa.cancel()
        if tarefas:
            await asyncio.gather(*tarefas, return_exceptions=True)
        for shard in self.shards.values():
            shard.marcar("encerrado")
            await self._publicar_estado(shard)


__all__ = ["ShardInfo", "GerenciadorDeShards"]
