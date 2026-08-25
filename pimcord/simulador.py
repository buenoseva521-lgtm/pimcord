"""Simulador offline do Pimcord para desenvolvimento e testes sem rede."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .gateway.eventos import EVENTOS_PORTUGUES, modelar_evento


@dataclass(slots=True)
class RegistroSimulado:
    evento: str
    dados: dict[str, Any]
    modelo: Any = None


@dataclass
class Simulador:
    """Ambiente local para exercitar um Bot sem conectar ao Discord."""

    bot: Any
    registros: list[RegistroSimulado] = field(default_factory=list)
    respostas: list[dict[str, Any]] = field(default_factory=list)
    conectado: bool = False

    async def iniciar(self, usuario: dict[str, Any] | None = None, servidores: list[dict[str, Any]] | None = None) -> None:
        self.conectado = True
        dados = {"user": usuario or {"id": "simulado", "username": "Pimcord Simulado", "bot": True}, "guilds": servidores or []}
        self.bot._aplicar_ready(dados)
        self.bot._definir_estado_conexao("pronto")
        await self.bot.disparar("pronto", dados)

    async def emitir(self, evento: str, dados: dict[str, Any] | None = None) -> Any:
        """Emite um evento oficial ou português no dispatcher local."""
        nome = evento.removeprefix("on_")
        oficial = next((chave for chave, alias in EVENTOS_PORTUGUES.items() if alias == nome), nome.upper())
        payload = dados or {}
        if oficial == "MESSAGE_CREATE":
            self.registros.append(RegistroSimulado(oficial, payload))
            return await self.bot.receber_mensagem(payload)
        modelo = modelar_evento(oficial, payload, getattr(self.bot, "http", None))
        self.registros.append(RegistroSimulado(oficial, payload, modelo))
        resultado = []
        if nome in self.bot.eventos:
            resultado.extend(await self.bot.disparar(nome, modelo))
        alias = EVENTOS_PORTUGUES.get(oficial)
        if alias and alias != nome and alias in self.bot.eventos:
            resultado.extend(await self.bot.disparar(alias, modelo))
        if oficial.lower() in self.bot.eventos:
            resultado.extend(await self.bot.disparar(oficial.lower(), payload))
        return resultado

    async def mensagem(self, conteudo: str, *, autor: dict[str, Any] | None = None, canal_id: str = "canal-simulado") -> Any:
        """Envia uma mensagem sintética pelo fluxo de comandos do Bot."""
        autor = autor or {"id": "usuario-simulado", "username": "Usuário", "bot": False}
        payload = {"id": str(len(self.registros) + 1), "channel_id": canal_id, "content": conteudo, "author": autor}
        self.registros.append(RegistroSimulado("MESSAGE_CREATE", payload))
        return await self.bot.receber_mensagem(payload)

    async def interacao(self, dados: dict[str, Any]) -> Any:
        """Envia uma interação sintética, incluindo comandos e componentes."""
        self.registros.append(RegistroSimulado("INTERACTION_CREATE", dados))
        return await self.bot.receber_interacao(dados)

    def registrar_resposta(self, dados: dict[str, Any]) -> dict[str, Any]:
        self.respostas.append(dados)
        return dados

    async def parar(self) -> None:
        self.conectado = False
        self.bot._definir_estado_conexao("desconectado")


__all__ = ["RegistroSimulado", "Simulador"]
