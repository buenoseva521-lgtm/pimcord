"""Webhooks Discord para o Pimcord."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import aiohttp

from .nucleo import Embed


@dataclass(slots=True)
class Webhook:
    url: str
    nome: str | None = None
    avatar_url: str | None = None
    timeout: float = 30.0

    async def enviar(self, conteudo: str = "", *, nome: str | None = None, avatar_url: str | None = None, embed: Embed | None = None, embeds: list[Embed] | None = None, esperar: bool = False, permitido_mencionar: dict[str, Any] | None = None) -> Any:
        corpo: dict[str, Any] = {"content": conteudo}
        if nome or self.nome: corpo["username"] = nome or self.nome
        if avatar_url or self.avatar_url: corpo["avatar_url"] = avatar_url or self.avatar_url
        if embed: corpo["embeds"] = [embed.para_dict()]
        if embeds: corpo["embeds"] = [item.para_dict() for item in embeds]
        if permitido_mencionar is not None: corpo["allowed_mentions"] = permitido_mencionar
        separador = "&" if "?" in self.url else "?"
        destino = self.url + (f"{separador}wait=true" if esperar else "")
        async with aiohttp.ClientSession() as sessao:
            async with sessao.post(destino, json=corpo, timeout=self.timeout) as resposta:
                if resposta.status >= 400:
                    raise RuntimeError(f"Webhook HTTP {resposta.status}: {(await resposta.text())[:500]}")
                if resposta.status == 204: return None
                return await resposta.json(content_type=None)

    async def editar_mensagem(self, mensagem_id: str, *, conteudo: str | None = None, embed: Embed | None = None) -> Any:
        corpo: dict[str, Any] = {}
        if conteudo is not None: corpo["content"] = conteudo
        if embed is not None: corpo["embeds"] = [embed.para_dict()]
        async with aiohttp.ClientSession() as sessao:
            async with sessao.patch(f"{self.url}/messages/{mensagem_id}", json=corpo, timeout=self.timeout) as resposta:
                if resposta.status >= 400: raise RuntimeError(f"Webhook HTTP {resposta.status}: {(await resposta.text())[:500]}")
                return await resposta.json(content_type=None)

    async def apagar_mensagem(self, mensagem_id: str) -> None:
        async with aiohttp.ClientSession() as sessao:
            async with sessao.delete(f"{self.url}/messages/{mensagem_id}", timeout=self.timeout) as resposta:
                if resposta.status >= 400: raise RuntimeError(f"Webhook HTTP {resposta.status}: {(await resposta.text())[:500]}")


__all__ = ["Webhook"]
