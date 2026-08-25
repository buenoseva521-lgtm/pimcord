"""Extensões carregáveis com ciclo de vida e dependências em português."""
from __future__ import annotations

import importlib
import inspect
import logging
from types import ModuleType
from typing import Any


class Extensao:
    async def iniciar(self, bot: Any) -> None:
        return None

    async def parar(self, bot: Any) -> None:
        return None


class GerenciadorDeExtensoes:
    def __init__(self, bot: Any):
        self.bot = bot
        self.carregadas: dict[str, ModuleType | Extensao] = {}
        self.dependencias: dict[str, tuple[str, ...]] = {}
        self.saude: dict[str, str] = {}
        self.logger = logging.getLogger("pimcord.extensoes")

    async def carregar(self, caminho: str, *, dependencias: tuple[str, ...] = ()) -> ModuleType | Extensao:
        for dependencia in dependencias:
            if dependencia not in self.carregadas:
                await self.carregar(dependencia)
        modulo = importlib.import_module(caminho)
        configurar = getattr(modulo, "configurar", None) or getattr(modulo, "setup", None)
        if configurar is None:
            raise ImportError(f"A extensão '{caminho}' não possui configurar(bot).")
        resultado = configurar(self.bot)
        if inspect.isawaitable(resultado):
            await resultado
        self.carregadas[caminho] = modulo
        self.dependencias[caminho] = tuple(dependencias)
        self.saude[caminho] = "ativa"
        return modulo

    async def descarregar(self, caminho: str) -> None:
        dependentes = [nome for nome, deps in self.dependencias.items() if caminho in deps]
        if dependentes:
            raise RuntimeError(f"Não é possível descarregar '{caminho}'; dependentes ativos: {dependentes}")
        modulo = self.carregadas.pop(caminho, None)
        if modulo is None:
            return
        desconfigurar = getattr(modulo, "desconfigurar", None) or getattr(modulo, "teardown", None)
        if desconfigurar:
            resultado = desconfigurar(self.bot)
            if inspect.isawaitable(resultado):
                await resultado
        self.dependencias.pop(caminho, None)
        self.saude[caminho] = "descarregada"

    async def recarregar(self, caminho: str) -> ModuleType | Extensao:
        dependencias = self.dependencias.get(caminho, ())
        await self.descarregar(caminho)
        modulo = importlib.reload(importlib.import_module(caminho))
        configurar = getattr(modulo, "configurar", None) or getattr(modulo, "setup", None)
        if configurar is None:
            raise ImportError(f"A extensão '{caminho}' não possui configurar(bot).")
        resultado = configurar(self.bot)
        if inspect.isawaitable(resultado):
            await resultado
        self.carregadas[caminho] = modulo
        self.dependencias[caminho] = dependencias
        self.saude[caminho] = "ativa"
        return modulo

    async def carregar_lote(self, extensoes: dict[str, tuple[str, ...]]) -> list[ModuleType | Extensao]:
        novas: list[str] = []
        try:
            resultado = []
            for caminho, dependencias in extensoes.items():
                if caminho not in self.carregadas:
                    resultado.append(await self.carregar(caminho, dependencias=dependencias))
                    novas.append(caminho)
            return resultado
        except Exception:
            for caminho in reversed(novas):
                await self.descarregar(caminho)
            raise

    def diagnostico(self) -> dict[str, str]:
        return dict(self.saude)


__all__ = ["Extensao", "GerenciadorDeExtensoes"]
