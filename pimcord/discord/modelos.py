from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Awaitable, Callable
import inspect

from ..nucleo import Embed


@dataclass(slots=True)
class Usuario:
    id: str
    nome: str
    bot: bool = False
    global_name: str | None = None
    avatar: str | None = None

    @classmethod
    def de_dict(cls, dados: dict[str, Any]) -> "Usuario":
        return cls(
            str(dados.get("id", "")),
            dados.get("username", ""),
            bool(dados.get("bot", False)),
            dados.get("global_name"),
            dados.get("avatar"),
        )

    @property
    def mencao(self) -> str:
        return f"<@{self.id}>"


@dataclass(slots=True)
class Cargo:
    id: str
    nome: str
    cor: int = 0
    posicao: int = 0
    gerenciado: bool = False

    @classmethod
    def de_dict(cls, dados: dict[str, Any]) -> "Cargo":
        return cls(str(dados.get("id", "")), dados.get("name", ""), int(dados.get("color", 0)), int(dados.get("position", 0)), bool(dados.get("managed", False)))


@dataclass(slots=True)
class Anexo:
    id: str
    nome: str
    url: str
    proxy_url: str | None = None
    tamanho: int = 0
    tipo: str | None = None

    @classmethod
    def de_dict(cls, dados: dict[str, Any]) -> "Anexo":
        return cls(str(dados.get("id", "")), dados.get("filename", ""), dados.get("url", ""), dados.get("proxy_url"), int(dados.get("size", 0)), dados.get("content_type"))


@dataclass(slots=True)
class Canal:
    id: str
    cliente: Any
    nome: str | None = None
    tipo: int | None = None
    servidor_id: str | None = None

    async def enviar(self, conteudo: str = "", *, embed: Embed | None = None, embeds: list[Embed] | None = None, view: Any = None, arquivos: list[Any] | None = None) -> dict[str, Any]:
        return await self.cliente.enviar_mensagem(
            self.id,
            conteudo,
            embed=embed.para_dict() if embed else None,
            embeds=[item.para_dict() for item in embeds] if embeds else None,
            view=view,
            arquivos=arquivos,
        )

    async def buscar(self) -> dict[str, Any]:
        return await self.cliente.requisitar("GET", f"/channels/{self.id}")

    async def editar(self, **campos: Any) -> dict[str, Any]:
        return await self.cliente.requisitar("PATCH", f"/channels/{self.id}", json=campos)

    async def excluir(self) -> dict[str, Any]:
        return await self.cliente.requisitar("DELETE", f"/channels/{self.id}")

    async def definir_permissoes(self, sobrescrita: Any, *, motivo: str | None = None) -> Any:
        """Substitui a regra de um cargo ou usuário neste canal."""
        dados = sobrescrita.para_dict() if hasattr(sobrescrita, "para_dict") else dict(sobrescrita)
        corpo = {"allow": dados.get("allow", "0"), "deny": dados.get("deny", "0"), "type": dados.get("type", 0)}
        if motivo is not None: corpo["reason"] = motivo
        return await self.cliente.requisitar("PUT", f"/channels/{self.id}/permissions/{dados['id']}", json=corpo)

    async def remover_permissoes(self, alvo_id: str, *, motivo: str | None = None) -> Any:
        rota = f"/channels/{self.id}/permissions/{alvo_id}"
        return await self.cliente.requisitar("DELETE", rota, json={"reason": motivo} if motivo else None)

    async def historico(self, *, limite: int = 50, antes_de: str | None = None, depois_de: str | None = None, em_torno_de: str | None = None) -> list["Mensagem"]:
        """Busca até 100 mensagens recentes deste canal."""
        dados = await self.cliente.buscar_mensagens(self.id, limite=limite, antes_de=antes_de, depois_de=depois_de, em_torno_de=em_torno_de)
        return [Mensagem.de_gateway(item, self.cliente) for item in dados]

    async def purge(self, *, limite: int = 100, check: Callable[["Mensagem"], bool | Awaitable[bool]] | None = None, antes_de: str | None = None, depois_de: str | None = None) -> list["Mensagem"]:
        """Apaga mensagens filtradas, usando exclusão em lote quando possível."""
        if not 1 <= limite <= 100:
            raise ValueError("purge aceita entre 1 e 100 mensagens por chamada.")
        mensagens = await self.historico(limite=limite, antes_de=antes_de, depois_de=depois_de)
        selecionadas: list[Mensagem] = []
        for mensagem in mensagens:
            aceita = True if check is None else check(mensagem)
            if inspect.isawaitable(aceita):
                aceita = await aceita
            if aceita:
                selecionadas.append(mensagem)
        await self.cliente.apagar_mensagens(self.id, [item.id for item in selecionadas])
        return selecionadas

    async def apagar_mensagens(self, **opcoes: Any) -> list["Mensagem"]:
        """Nome explícito em português para `purge`."""
        return await self.purge(**opcoes)


@dataclass(slots=True)
class Servidor:
    id: str
    nome: str
    cliente: Any = None
    dono_id: str | None = None
    icone: str | None = None
    cargos: list[Cargo] = field(default_factory=list)

    @classmethod
    def de_dict(cls, dados: dict[str, Any], cliente: Any = None) -> "Servidor":
        return cls(str(dados.get("id", "")), dados.get("name", ""), cliente, str(dados["owner_id"]) if dados.get("owner_id") else None, dados.get("icon"), [Cargo.de_dict(c) for c in dados.get("roles", [])])

    async def buscar_canal(self, canal_id: str) -> Canal:
        dados = await self.cliente.requisitar("GET", f"/channels/{canal_id}")
        return Canal(str(dados.get("id", canal_id)), self.cliente, dados.get("name"), dados.get("type"), self.id)

    async def buscar_canais(self) -> list[Canal]:
        dados = await self.cliente.requisitar("GET", f"/guilds/{self.id}/channels")
        return [Canal(str(item.get("id", "")), self.cliente, item.get("name"), item.get("type"), self.id) for item in dados]

    async def criar_categoria(self, nome: str, *, sobrescritas: list[Any] | None = None, motivo: str | None = None) -> Canal:
        return await self.criar_canal(nome, tipo="categoria", sobrescritas=sobrescritas, motivo=motivo)

    async def criar_canal(self, nome: str, *, tipo: int | str = "texto", categoria_id: str | None = None, topico: str | None = None, nsfw: bool = False, sobrescritas: list[Any] | None = None, motivo: str | None = None) -> Canal:
        tipos = {"texto": 0, "voz": 2, "categoria": 4, "anuncios": 5, "anúncios": 5, "stage": 13, "forum": 15, "fórum": 15}
        tipo_numero = tipos.get(tipo.lower(), 0) if isinstance(tipo, str) else int(tipo)
        corpo: dict[str, Any] = {"name": nome, "type": tipo_numero, "nsfw": nsfw}
        if categoria_id is not None: corpo["parent_id"] = str(categoria_id)
        if topico is not None: corpo["topic"] = topico
        if motivo is not None: corpo["reason"] = motivo
        if sobrescritas is not None:
            corpo["permission_overwrites"] = [item.para_dict() if hasattr(item, "para_dict") else item for item in sobrescritas]
        dados = await self.cliente.requisitar("POST", f"/guilds/{self.id}/channels", json=corpo)
        return Canal(str(dados.get("id", "")), self.cliente, dados.get("name"), dados.get("type"), self.id)


@dataclass(slots=True)
class Membro:
    usuario: Usuario
    servidor_id: str
    apelido: str | None = None
    cargos: list[str] = field(default_factory=list)
    ingresso: datetime | None = None

    @property
    def id(self) -> str:
        return self.usuario.id

    @property
    def nome(self) -> str:
        return self.apelido or self.usuario.nome

    @classmethod
    def de_dict(cls, dados: dict[str, Any], servidor_id: str) -> "Membro":
        ingresso = dados.get("joined_at")
        return cls(Usuario.de_dict(dados.get("user", {})), servidor_id, dados.get("nick"), [str(x) for x in dados.get("roles", [])], datetime.fromisoformat(ingresso.replace("Z", "+00:00")) if ingresso else None)


@dataclass(slots=True)
class Mensagem:
    id: str
    canal: Canal
    conteudo: str
    autor: Usuario
    bruto: dict[str, Any]
    anexos: list[Anexo] = field(default_factory=list)
    servidor_id: str | None = None

    @classmethod
    def de_gateway(cls, dados: dict[str, Any], cliente: Any) -> "Mensagem":
        canal = Canal(str(dados.get("channel_id", "")), cliente, servidor_id=str(dados["guild_id"]) if dados.get("guild_id") else None)
        return cls(str(dados.get("id", "")), canal, dados.get("content", ""), Usuario.de_dict(dados.get("author", {})), dados, [Anexo.de_dict(a) for a in dados.get("attachments", [])], str(dados["guild_id"]) if dados.get("guild_id") else None)

    @property
    def mencao_autor(self) -> str:
        return self.autor.mencao

    async def responder(self, conteudo: str = "", *, embed: Embed | None = None, embeds: list[Embed] | None = None, view: Any = None) -> dict[str, Any]:
        return await self.canal.enviar(conteudo, embed=embed, embeds=embeds, view=view)

    async def editar(self, conteudo: str | None = None, **campos: Any) -> dict[str, Any]:
        if conteudo is not None: campos["content"] = conteudo
        return await self.canal.cliente.requisitar("PATCH", f"/channels/{self.canal.id}/messages/{self.id}", json=campos)

    async def excluir(self) -> dict[str, Any]:
        return await self.canal.cliente.requisitar("DELETE", f"/channels/{self.canal.id}/messages/{self.id}")

    async def apagar(self) -> dict[str, Any]:
        return await self.excluir()

    async def delete(self) -> dict[str, Any]:
        """Alias em inglês para facilitar a migração de exemplos existentes."""
        return await self.excluir()

    async def deletar(self) -> dict[str, Any]:
        """Alias em português para exclusão da mensagem."""
        return await self.excluir()


__all__ = ["Usuario", "Membro", "Cargo", "Anexo", "Canal", "Servidor", "Mensagem"]
