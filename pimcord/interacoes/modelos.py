from __future__ import annotations
from typing import Any, Iterable
from ..nucleo import Embed, ErroDeConfiguracao

class Interacao:
    def __init__(self, dados: dict[str, Any], cliente: Any):
        self.id = str(dados["id"]); self.token = dados["token"]; self.dados = dados; self.cliente = cliente
        self.application_id = str(dados.get("application_id", ""))
        data = dados.get("data", {})
        self.tipo = int(dados.get("type", 0))
        self.custom_id = data.get("custom_id")
        self.valores = list(data.get("values", []))
        self.nome_comando = str(data.get("name", ""))
        self.opcoes_brutas = list(data.get("options", []) or [])
        self.grupo_subcomando: str | None = None
        self.subcomando: str | None = None
        self.opcoes: dict[str, Any] = {}
        self._ler_opcoes_aninhadas(self.opcoes_brutas)
        self.dados_brutos = dados
        self.permissoes_aplicacao = dados.get("app_permissions")
        self.entitlements: list[dict[str, Any]] = list(dados.get("entitlements", []) or [])
        self.proprietarios_autorizadores: dict[str, str] = dict(dados.get("authorizing_integration_owners", {}) or {})
        self.contexto_interacao = dados.get("context")
        self.limite_anexos: int | None = dados.get("attachment_size_limit")
        self.canal_resolvido: dict[str, Any] | None = None
        self.canal_id: str | None = str(dados.get("channel_id")) if dados.get("channel_id") is not None else None
        self.servidor_id: str | None = str(dados.get("guild_id")) if dados.get("guild_id") is not None else None
        resolvidos = data.get("resolved", {}) or {}
        canais_resolvidos = resolvidos.get("channels", {}) if isinstance(resolvidos, dict) else {}
        if isinstance(canais_resolvidos, dict):
            canal = next(iter(canais_resolvidos.values()), None)
            if isinstance(canal, dict):
                self.canal_resolvido = canal
                if self.canal_id is None and canal.get("id") is not None:
                    self.canal_id = str(canal["id"])
                if self.servidor_id is None and canal.get("guild_id") is not None:
                    self.servidor_id = str(canal["guild_id"])
                if self.permissoes_aplicacao is None:
                    self.permissoes_aplicacao = canal.get("app_permissions")
        membro = dados.get("member", {}) or {}
        self.membro = membro
        usuario = membro.get("user", {}) or dados.get("user", {}) or {}
        self.usuario_id = str(usuario.get("id", ""))

    @property
    def canal(self) -> Any:
        """Retorna o canal resolvido como modelo Canal quando o Discord o fornece."""
        if not self.canal_id:
            return None
        from ..discord.modelos import Canal
        dados = self.canal_resolvido or {}
        return Canal(
            id=str(self.canal_id),
            cliente=self.cliente,
            nome=dados.get("name"),
            tipo=dados.get("type"),
            servidor_id=self.servidor_id or dados.get("guild_id"),
        )

    @property
    def entitlements_modelados(self) -> list[Any]:
        """Entitlements da interação convertidos no modelo público quando possível."""
        from ..discord.recursos import Entitlement
        return [Entitlement.de_dict(item) for item in self.entitlements if isinstance(item, dict)]

    @property
    def authorizing_integration_owners(self) -> dict[str, str]:
        """Alias oficial para integrações que autorizaram a interação."""
        return self.proprietarios_autorizadores

    @property
    def attachment_size_limit(self) -> int | None:
        """Alias oficial do limite de anexos informado pelo Discord."""
        return self.limite_anexos

    @property
    def app_permissions(self) -> str | None:
        """Permissões efetivas da aplicação no canal resolvido, quando fornecidas pelo Discord."""
        return self.permissoes_aplicacao

    def _ler_opcoes_aninhadas(self, opcoes: list[dict[str, Any]], *, grupo: str | None = None) -> None:
        for opcao in opcoes:
            if not isinstance(opcao, dict) or "name" not in opcao:
                continue
            tipo = int(opcao.get("type", 0) or 0)
            nome = str(opcao["name"])
            if tipo == 2:
                self.grupo_subcomando = nome
                self._ler_opcoes_aninhadas(list(opcao.get("options", []) or []), grupo=nome)
            elif tipo == 1:
                self.subcomando = nome
                self._ler_opcoes_aninhadas(list(opcao.get("options", []) or []), grupo=grupo)
            elif "value" in opcao:
                self.opcoes[nome] = opcao["value"]

    async def responder(self, conteudo: str = "", *, embed: Embed | None = None, view: Any = None, ephemeral: bool = False, arquivos: Iterable[Any] | None = None, campos_multipart: dict[str, Any] | None = None) -> Any:
        corpo: dict[str, Any] = {"type": 4, "data": {"content": conteudo}}
        if embed: corpo["data"]["embeds"] = [embed.para_dict()]
        if view is not None: corpo["data"]["components"] = view.para_componentes()
        if ephemeral: corpo["data"]["flags"] = 64
        opcoes: dict[str, Any] = {"json": corpo}
        if arquivos is not None:
            opcoes["arquivos"] = arquivos
        if campos_multipart is not None:
            opcoes["campos_multipart"] = campos_multipart
        return await self.cliente.requisitar("POST", f"/interactions/{self.id}/{self.token}/callback", **opcoes)

    async def responder_autocomplete(self, escolhas: list[dict[str, Any]] | list[str]) -> Any:
        """Responde a uma interação de autocomplete com sugestões normalizadas."""
        normalizadas = [{"name": str(item), "value": str(item)} if not isinstance(item, dict) else item for item in escolhas[:25]]
        corpo = {"type": 8, "data": {"choices": normalizadas}}
        return await self.cliente.requisitar("POST", f"/interactions/{self.id}/{self.token}/callback", json=corpo)

    async def adiar(self, *, ephemeral: bool = False) -> Any:
        """Adia a resposta inicial para ganhar tempo de processamento."""
        corpo: dict[str, Any] = {"type": 5, "data": {}}
        if ephemeral: corpo["data"]["flags"] = 64
        return await self.cliente.requisitar("POST", f"/interactions/{self.id}/{self.token}/callback", json=corpo)

    def _rota_webhook(self) -> str:
        if not self.application_id:
            raise ErroDeConfiguracao("application_id é necessário para usar follow-ups de uma interação.")
        return f"/webhooks/{self.application_id}/{self.token}"

    async def followup(self, conteudo: str = "", *, embed: Embed | None = None, view: Any = None, ephemeral: bool = False, arquivos: Iterable[Any] | None = None, campos_multipart: dict[str, Any] | None = None) -> Any:
        corpo: dict[str, Any] = {"content": conteudo}
        if embed: corpo["embeds"] = [embed.para_dict()]
        if view is not None: corpo["components"] = view.para_componentes()
        if ephemeral: corpo["flags"] = 64
        opcoes: dict[str, Any] = {"json": corpo}
        if arquivos is not None:
            opcoes["arquivos"] = arquivos
        if campos_multipart is not None:
            opcoes["campos_multipart"] = campos_multipart
        return await self.cliente.requisitar("POST", self._rota_webhook(), **opcoes)

    async def obter_followup(self, mensagem_id: str) -> Any:
        """Obtém um follow-up pelo ID, sem confundi-lo com a resposta original."""
        return await self.cliente.requisitar("GET", f"{self._rota_webhook()}/messages/{mensagem_id}")

    async def apagar_followup(self, mensagem_id: str) -> Any:
        return await self.cliente.requisitar("DELETE", f"{self._rota_webhook()}/messages/{mensagem_id}")

    async def editar_followup(self, mensagem_id: str, conteudo: str | None = None, *, embed: Embed | None = None, view: Any = None) -> Any:
        corpo: dict[str, Any] = {}
        if conteudo is not None: corpo["content"] = conteudo
        if embed is not None: corpo["embeds"] = [embed.para_dict()]
        if view is not None: corpo["components"] = view.para_componentes()
        return await self.cliente.requisitar("PATCH", f"{self._rota_webhook()}/messages/{mensagem_id}", json=corpo)

    async def apagar_resposta(self) -> Any:
        return await self.cliente.requisitar("DELETE", f"{self._rota_webhook()}/messages/@original")

    async def editar_resposta(self, conteudo: str | None = None, *, embed: Embed | None = None, view: Any = None) -> Any:
        corpo: dict[str, Any] = {}
        if conteudo is not None: corpo["content"] = conteudo
        if embed is not None: corpo["embeds"] = [embed.para_dict()]
        if view is not None: corpo["components"] = view.para_componentes()
        return await self.cliente.requisitar("PATCH", f"{self._rota_webhook()}/messages/@original", json=corpo)
