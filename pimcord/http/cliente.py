"""Cliente REST assíncrono e abrangente do Discord para o Pimcord."""
from __future__ import annotations

import asyncio
import json
import logging
from collections import defaultdict
from io import IOBase
from typing import Any, AsyncIterator, Iterable
from urllib.parse import urlencode

import aiohttp

from ..nucleo import ErroDaAPI, ErroDeConfiguracao, RateLimitado
from ..seguranca import FiltroSegredos


class ClienteHTTP:
    """Transporte REST com retries, buckets locais, JSON e multipart.

    Os métodos de recurso são apenas uma camada ergonômica sobre ``requisitar``;
    ``requisitar`` continua disponível para endpoints novos do Discord.
    """

    def __init__(self, token: str, *, versao: int = 10, timeout: float = 30.0):
        if not isinstance(token, str):
            raise ErroDeConfiguracao("O token do bot precisa ser texto.")
        token = "".join(
            caractere for caractere in token
            if not caractere.isspace() and 32 <= ord(caractere) != 127
        )
        if not token:
            raise ErroDeConfiguracao("Token vazio. Cole o token do bot novamente.")
        self.token = token
        self.versao = versao
        self.base_url = f"https://discord.com/api/v{versao}"
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self._sessao: aiohttp.ClientSession | None = None
        self._locks: defaultdict[str, asyncio.Lock] = defaultdict(asyncio.Lock)
        self._limites: dict[str, tuple[int, float]] = {}
        self.logger = logging.getLogger("pimcord.http")
        self.logger.addFilter(FiltroSegredos([token]))

    async def abrir(self) -> None:
        if self._sessao is None or self._sessao.closed:
            self._sessao = aiohttp.ClientSession(
                timeout=self.timeout,
                headers={
                    "Authorization": f"Bot {self.token}",
                    "User-Agent": "Pimcord/0.7.0 (+https://github.com/pimcord/pimcord)",
                },
            )

    async def fechar(self) -> None:
        if self._sessao and not self._sessao.closed:
            await self._sessao.close()

    async def requisitar(
        self,
        metodo: str,
        rota: str,
        *,
        json: Any = None,
        dados: Any = None,
        arquivos: Iterable[Any] | None = None,
        campos_multipart: dict[str, Any] | None = None,
        parametros: dict[str, Any] | None = None,
        motivo: str | None = None,
        cabecalhos: dict[str, str] | None = None,
        tentativas: int = 3,
        bruto: bool = False,
    ) -> Any:
        """Executa uma chamada; aceita JSON, dados e multipart sem rede em testes quando sessão é substituída."""
        if tentativas < 1:
            raise ValueError("tentativas deve ser pelo menos 1")
        if motivo is not None:
            if not isinstance(motivo, str):
                raise TypeError("motivo deve ser texto")
            if len(motivo) > 512:
                raise ValueError("motivo deve ter no máximo 512 caracteres")
        await self.abrir()
        assert self._sessao is not None
        rota_base = rota.split("?", 1)[0]
        chave = rota_base
        headers = dict(cabecalhos or {})
        if motivo is not None:
            headers["X-Audit-Log-Reason"] = motivo
        corpo = dados
        if arquivos is not None:
            formulario = aiohttp.FormData()
            if json is not None:
                formulario.add_field("payload_json", __import__("json").dumps(json, ensure_ascii=False))
            for campo, valor in (campos_multipart or {}).items():
                formulario.add_field(str(campo), str(valor))
            for indice, item in enumerate(arquivos):
                campo = f"files[{indice}]"
                nome = getattr(item, "nome", None) or getattr(item, "name", None) or f"arquivo_{indice}"
                conteudo = item
                if isinstance(item, tuple) and len(item) >= 3:
                    campo, nome, conteudo = item[0], item[1], item[2]
                elif isinstance(item, tuple) and len(item) >= 2:
                    nome, conteudo = item[0], item[1]
                if isinstance(conteudo, (bytes, bytearray)):
                    formulario.add_field(campo, conteudo, filename=str(nome))
                elif isinstance(conteudo, IOBase):
                    formulario.add_field(campo, conteudo, filename=str(nome))
                else:
                    formulario.add_field(campo, str(conteudo), filename=str(nome))
            corpo = formulario
            json = None
        url = self.base_url + rota
        for tentativa in range(tentativas):
            async with self._locks[chave]:
                async with self._sessao.request(metodo, url, json=json, data=corpo, params=parametros, headers=headers) as resposta:
                    restante = resposta.headers.get("X-RateLimit-Remaining")
                    reset = resposta.headers.get("X-RateLimit-Reset-After")
                    if restante is not None and reset is not None:
                        self._limites[chave] = (int(restante), float(reset))
                    if resposta.status == 429:
                        texto_rate_limit = await resposta.text()
                        try:
                            dados_erro = json_module_loads(texto_rate_limit) if texto_rate_limit else {}
                        except Exception:
                            dados_erro = {}
                        if not isinstance(dados_erro, dict):
                            dados_erro = {}
                        espera_bruta = dados_erro.get("retry_after", resposta.headers.get("Retry-After", resposta.headers.get("X-RateLimit-Reset-After", 1)))
                        try:
                            espera = float(espera_bruta)
                        except (TypeError, ValueError):
                            espera = 1.0
                        if tentativa + 1 == tentativas:
                            raise RateLimitado(f"Rate limitado; tente novamente em {espera}s", espera=espera, global_=bool(dados_erro.get("global", False)), rota=rota)
                        await asyncio.sleep(espera)
                        continue
                    if resposta.status in {500, 502, 503, 504} and tentativa + 1 < tentativas:
                        await asyncio.sleep(2 ** tentativa)
                        continue
                    if resposta.status >= 400:
                        texto = await resposta.text()
                        try:
                            erro = json_module_loads(texto)
                        except Exception:
                            erro = {"message": texto[:500]}
                        raise ErroDaAPI(f"Discord HTTP {resposta.status}: {erro.get('message', erro) if isinstance(erro, dict) else erro}", status=resposta.status, codigo=erro.get("code") if isinstance(erro, dict) else None, erros=erro.get("errors") if isinstance(erro, dict) else None, rota=rota, metodo=metodo)
                    if resposta.status == 204:
                        return None
                    if bruto:
                        return await resposta.read()
                    texto = await resposta.text()
                    if not texto:
                        return None
                    try:
                        return json_module_loads(texto)
                    except Exception:
                        return texto
        raise ErroDaAPI("Falha inesperada na requisição REST", rota=rota, metodo=metodo)

    async def endpoint(self, metodo: str, rota: str, **kwargs: Any) -> Any:
        """Alias explícito para permitir endpoints futuros sem alterar o cliente."""
        return await self.requisitar(metodo, rota, **kwargs)

    async def paginar(self, metodo: str, rota: str, *, limite: int = 100, campo: str | None = None, antes_de: str | None = None, depois_de: str | None = None, **kwargs: Any) -> AsyncIterator[Any]:
        """Percorre endpoints baseados em ``before`` ou ``after`` sem perder filtros entre páginas.

        A iteração encerra com segurança quando o endpoint devolve um cursor repetido,
        evitando consumo infinito diante de um servidor ou mock inconsistente.
        """
        restante = max(0, int(limite))
        if antes_de is not None and depois_de is not None:
            raise ValueError("use antes_de ou depois_de, não ambos")
        parametros_base = dict(kwargs.pop("parametros", {}) or {})
        cursor = antes_de if antes_de is not None else depois_de
        nome_cursor = "after" if depois_de is not None else "before"
        cursor_anterior: str | None = None
        while restante:
            quantidade = min(restante, 100)
            parametros = dict(parametros_base)
            parametros["limit"] = quantidade
            if cursor:
                parametros[nome_cursor] = cursor
            pagina = await self.requisitar(metodo, rota, parametros=parametros, **kwargs)
            itens = pagina.get(campo, []) if campo and isinstance(pagina, dict) else pagina
            if not isinstance(itens, (list, tuple)) or not itens:
                return
            cursor_pagina: str | None = None
            for item in itens:
                yield item
                restante -= 1
                if isinstance(item, dict) and item.get("id") is not None:
                    cursor_pagina = str(item["id"])
                if not restante:
                    return
            if cursor_pagina is None or cursor_pagina == cursor_anterior:
                return
            cursor_anterior = cursor_pagina
            cursor = cursor_pagina

    async def gateway(self) -> str:
        return (await self.requisitar("GET", "/gateway/bot"))["url"]

    # Mensagens e canais
    async def enviar_mensagem(self, canal_id: str, conteudo: str = "", *, embed: dict[str, Any] | None = None, embeds: list[dict[str, Any]] | None = None, view: Any = None, arquivos: Iterable[Any] | None = None, permitido_mencionar: dict[str, Any] | None = None, tts: bool = False, reply: str | None = None) -> dict[str, Any]:
        corpo: dict[str, Any] = {"content": conteudo, "tts": tts}
        if embed is not None: corpo["embeds"] = [embed]
        elif embeds is not None: corpo["embeds"] = embeds
        if view is not None and hasattr(view, "para_componentes"): corpo["components"] = view.para_componentes()
        if permitido_mencionar is not None: corpo["allowed_mentions"] = permitido_mencionar
        if reply is not None: corpo["message_reference"] = {"message_id": str(reply)}
        return await self.requisitar("POST", f"/channels/{canal_id}/messages", json=corpo, arquivos=arquivos)

    async def buscar_mensagem(self, canal_id: str, mensagem_id: str) -> dict[str, Any]: return await self.requisitar("GET", f"/channels/{canal_id}/messages/{mensagem_id}")
    async def editar_mensagem(self, canal_id: str, mensagem_id: str, **dados: Any) -> dict[str, Any]: return await self.requisitar("PATCH", f"/channels/{canal_id}/messages/{mensagem_id}", json=dados)
    async def apagar_mensagem(self, canal_id: str, mensagem_id: str, *, motivo: str | None = None) -> None: await self.requisitar("DELETE", f"/channels/{canal_id}/messages/{mensagem_id}", motivo=motivo)
    async def indicar_digitacao(self, canal_id: str) -> None: await self.requisitar("POST", f"/channels/{canal_id}/typing")
    async def publicar_mensagem(self, canal_id: str, mensagem_id: str) -> dict[str, Any]: return await self.requisitar("POST", f"/channels/{canal_id}/messages/{mensagem_id}/crosspost")
    async def encerrar_enquete(self, canal_id: str, mensagem_id: str) -> dict[str, Any]: return await self.requisitar("POST", f"/channels/{canal_id}/polls/{mensagem_id}/expire")
    async def listar_usuarios_reacao(self, canal_id: str, mensagem_id: str, emoji: str, *, limite: int = 25, depois_de: str | None = None) -> list[dict[str, Any]]:
        """Lista usuários que usaram um emoji em uma mensagem."""
        if not 1 <= limite <= 100:
            raise ValueError("limite de reações deve estar entre 1 e 100")
        parametros: dict[str, Any] = {"limit": limite}
        if depois_de is not None:
            parametros["after"] = str(depois_de)
        return await self.requisitar("GET", f"/channels/{canal_id}/messages/{mensagem_id}/reactions/{emoji}", parametros=parametros)
    async def adicionar_reacao(self, canal_id: str, mensagem_id: str, emoji: str, *, usuario_id: str = "@me") -> None: await self.requisitar("PUT", f"/channels/{canal_id}/messages/{mensagem_id}/reactions/{emoji}/{usuario_id}")
    async def remover_reacao(self, canal_id: str, mensagem_id: str, emoji: str, *, usuario_id: str = "@me") -> None: await self.requisitar("DELETE", f"/channels/{canal_id}/messages/{mensagem_id}/reactions/{emoji}/{usuario_id}")
    async def listar_reacoes(self, canal_id: str, mensagem_id: str, emoji: str, **parametros: Any) -> list[dict[str, Any]]: return await self.requisitar("GET", f"/channels/{canal_id}/messages/{mensagem_id}/reactions/{emoji}", parametros=parametros)
    async def limpar_reacoes(self, canal_id: str, mensagem_id: str, emoji: str | None = None) -> None: await self.requisitar("DELETE", f"/channels/{canal_id}/messages/{mensagem_id}/reactions" + (f"/{emoji}" if emoji else ""))
    async def adicionar_reacao_atual(self, canal_id: str, mensagem_id: str, emoji: str) -> None: await self.requisitar("PUT", f"/channels/{canal_id}/messages/{mensagem_id}/reactions/{emoji}/@me")
    async def remover_reacao_atual(self, canal_id: str, mensagem_id: str, emoji: str) -> None: await self.requisitar("DELETE", f"/channels/{canal_id}/messages/{mensagem_id}/reactions/{emoji}/@me")
    async def limpar_reacoes_emoji(self, canal_id: str, mensagem_id: str, emoji: str) -> None: await self.requisitar("DELETE", f"/channels/{canal_id}/messages/{mensagem_id}/reactions/{emoji}")
    async def limpar_todas_reacoes(self, canal_id: str, mensagem_id: str) -> None:
        """Remove todas as reações de uma mensagem."""
        await self.requisitar("DELETE", f"/channels/{canal_id}/messages/{mensagem_id}/reactions")
    async def buscar_mensagens(self, canal_id: str, *, limite: int = 50, antes_de: str | None = None, depois_de: str | None = None, em_torno_de: str | None = None) -> list[dict[str, Any]]:
        parametros: dict[str, Any] = {"limit": max(1, min(int(limite), 100))}
        if antes_de is not None: parametros["before"] = str(antes_de)
        if depois_de is not None: parametros["after"] = str(depois_de)
        if em_torno_de is not None: parametros["around"] = str(em_torno_de)
        return await self.requisitar("GET", f"/channels/{canal_id}/messages", parametros=parametros)
    async def apagar_mensagens(self, canal_id: str, mensagens: list[str], *, motivo: str | None = None) -> None:
        ids = [str(item) for item in mensagens]
        if not ids: return
        if len(ids) == 1: return await self.apagar_mensagem(canal_id, ids[0], motivo=motivo)
        if len(ids) > 100: raise ValueError("O Discord aceita no máximo 100 mensagens por exclusão em lote.")
        await self.requisitar("POST", f"/channels/{canal_id}/messages/bulk-delete", json={"messages": ids}, motivo=motivo)
    async def obter_canal(self, canal_id: str) -> dict[str, Any]: return await self.requisitar("GET", f"/channels/{canal_id}")
    async def listar_votantes_enquete(self, canal_id: str, mensagem_id: str, resposta_id: str, *, limite: int = 25, depois_de: str | None = None) -> list[dict[str, Any]]:
        """Lista usuários que votaram em uma resposta de enquete."""
        if not 1 <= limite <= 100:
            raise ValueError("limite de votantes deve estar entre 1 e 100")
        parametros: dict[str, Any] = {"limit": limite}
        if depois_de is not None:
            parametros["after"] = str(depois_de)
        return await self.requisitar("GET", f"/channels/{canal_id}/polls/{mensagem_id}/answers/{resposta_id}", parametros=parametros)
    async def editar_canal(self, canal_id: str, **dados: Any) -> dict[str, Any]: return await self.requisitar("PATCH", f"/channels/{canal_id}", json=dados)
    async def excluir_canal(self, canal_id: str, *, motivo: str | None = None) -> dict[str, Any]: return await self.requisitar("DELETE", f"/channels/{canal_id}", motivo=motivo)
    async def listar_canais_servidor(self, servidor_id: str) -> list[dict[str, Any]]: return await self.requisitar("GET", f"/guilds/{servidor_id}/channels")
    async def criar_canal(self, servidor_id: str, **dados: Any) -> dict[str, Any]: return await self.requisitar("POST", f"/guilds/{servidor_id}/channels", json=dados, motivo=dados.pop("motivo", None))
    async def mover_canais(self, servidor_id: str, canais: list[dict[str, Any]]) -> None: await self.requisitar("PATCH", f"/guilds/{servidor_id}/channels", json=canais)
    async def definir_permissoes(self, canal_id: str, alvo_id: str, **dados: Any) -> None: await self.requisitar("PUT", f"/channels/{canal_id}/permissions/{alvo_id}", json=dados, motivo=dados.pop("motivo", None))
    async def remover_permissoes(self, canal_id: str, alvo_id: str, *, motivo: str | None = None) -> None: await self.requisitar("DELETE", f"/channels/{canal_id}/permissions/{alvo_id}", motivo=motivo)
    async def listar_pins(self, canal_id: str) -> list[dict[str, Any]]: return await self.requisitar("GET", f"/channels/{canal_id}/pins")
    async def listar_mensagens_fixadas(self, canal_id: str) -> list[dict[str, Any]]: return await self.requisitar("GET", f"/channels/{canal_id}/messages/pins")
    async def fixar_mensagem_oficial(self, canal_id: str, mensagem_id: str, *, motivo: str | None = None) -> None: await self.requisitar("PUT", f"/channels/{canal_id}/messages/pins/{mensagem_id}", motivo=motivo)
    async def desafixar_mensagem_oficial(self, canal_id: str, mensagem_id: str, *, motivo: str | None = None) -> None: await self.requisitar("DELETE", f"/channels/{canal_id}/messages/pins/{mensagem_id}", motivo=motivo)
    async def fixar_mensagem(self, canal_id: str, mensagem_id: str, *, motivo: str | None = None) -> None: await self.requisitar("PUT", f"/channels/{canal_id}/pins/{mensagem_id}", motivo=motivo)
    async def desafixar_mensagem(self, canal_id: str, mensagem_id: str, *, motivo: str | None = None) -> None: await self.requisitar("DELETE", f"/channels/{canal_id}/pins/{mensagem_id}", motivo=motivo)
    async def adicionar_destinatario(self, canal_id: str, usuario_id: str, *, acesso: str | None = None) -> None:
        dados = {"access_token": acesso} if acesso is not None else None
        await self.requisitar("PUT", f"/channels/{canal_id}/recipients/{usuario_id}", json=dados)
    async def remover_destinatario(self, canal_id: str, usuario_id: str) -> None: await self.requisitar("DELETE", f"/channels/{canal_id}/recipients/{usuario_id}")
    async def criar_thread(self, canal_id: str, **dados: Any) -> dict[str, Any]: return await self.requisitar("POST", f"/channels/{canal_id}/threads", json=dados)
    async def criar_thread_mensagem(self, canal_id: str, mensagem_id: str, **dados: Any) -> dict[str, Any]: return await self.requisitar("POST", f"/channels/{canal_id}/messages/{mensagem_id}/threads", json=dados)
    async def listar_threads_ativas(self, servidor_id: str) -> dict[str, Any]: return await self.requisitar("GET", f"/guilds/{servidor_id}/threads/active")
    async def listar_threads_arquivadas(self, canal_id: str, *, publicas: bool = True, **parametros: Any) -> dict[str, Any]: return await self.requisitar("GET", f"/channels/{canal_id}/threads/archived/" + ("public" if publicas else "private"), parametros=parametros)
    async def listar_threads_privadas_do_usuario(self, canal_id: str, **parametros: Any) -> dict[str, Any]: return await self.requisitar("GET", f"/channels/{canal_id}/users/@me/threads/archived/private", parametros=parametros)
    async def buscar_threads(self, canal_id: str, **parametros: Any) -> dict[str, Any]: return await self.requisitar("GET", f"/channels/{canal_id}/threads/search", parametros=parametros)
    async def entrar_thread(self, thread_id: str, usuario_id: str = "@me") -> None: await self.requisitar("PUT", f"/channels/{thread_id}/thread-members/{usuario_id}")
    async def sair_thread(self, thread_id: str, usuario_id: str = "@me") -> None: await self.requisitar("DELETE", f"/channels/{thread_id}/thread-members/{usuario_id}")
    async def entrar_thread_como_eu(self, thread_id: str) -> None: await self.requisitar("PUT", f"/channels/{thread_id}/thread-members/@me")
    async def sair_thread_como_eu(self, thread_id: str) -> None: await self.requisitar("DELETE", f"/channels/{thread_id}/thread-members/@me")
    async def listar_membros_thread(self, thread_id: str, **parametros: Any) -> list[dict[str, Any]]: return await self.requisitar("GET", f"/channels/{thread_id}/thread-members", parametros=parametros)
    async def obter_membro_thread(self, thread_id: str, usuario_id: str) -> dict[str, Any]:
        """Obtém um membro específico de uma thread."""
        return await self.requisitar("GET", f"/channels/{thread_id}/thread-members/{usuario_id}")

    # Servidores, membros, cargos e moderação
    async def obter_servidor(self, servidor_id: str, *, contagem: bool = False) -> dict[str, Any]: return await self.requisitar("GET", f"/guilds/{servidor_id}", parametros={"with_counts": str(contagem).lower()})
    async def editar_servidor(self, servidor_id: str, **dados: Any) -> dict[str, Any]: return await self.requisitar("PATCH", f"/guilds/{servidor_id}", json=dados, motivo=dados.pop("motivo", None))
    async def excluir_servidor(self, servidor_id: str) -> None: await self.requisitar("DELETE", f"/guilds/{servidor_id}")
    async def buscar_mensagens_servidor(self, servidor_id: str, *, consulta: str | None = None, limite: int = 25, antes_de: str | None = None, depois_de: str | None = None) -> dict[str, Any]:
        """Busca mensagens no servidor usando os filtros oficiais disponíveis."""
        if not 1 <= limite <= 25:
            raise ValueError("limite de mensagens do servidor deve estar entre 1 e 25")
        parametros: dict[str, Any] = {"limit": limite}
        if consulta is not None:
            parametros["content"] = consulta
        if antes_de is not None:
            parametros["min_id"] = str(antes_de)
        if depois_de is not None:
            parametros["max_id"] = str(depois_de)
        return await self.requisitar("GET", f"/guilds/{servidor_id}/messages/search", parametros=parametros)
    async def listar_contagens_cargos(self, servidor_id: str) -> list[dict[str, Any]]:
        return await self.requisitar("GET", f"/guilds/{servidor_id}/roles/member-counts")
    async def obter_membro_usuario_atual(self, servidor_id: str) -> dict[str, Any]:
        return await self.requisitar("GET", f"/users/@me/guilds/{servidor_id}/member")
    async def buscar_membros(self, servidor_id: str, consulta: str, *, limite: int = 1) -> list[dict[str, Any]]:
        """Busca membros pelo nome ou apelido no servidor."""
        if not consulta or len(consulta) > 32:
            raise ValueError("consulta de membros deve ter entre 1 e 32 caracteres")
        if not 1 <= limite <= 1000:
            raise ValueError("limite de membros deve estar entre 1 e 1000")
        return await self.requisitar("GET", f"/guilds/{servidor_id}/members/search", parametros={"query": consulta, "limit": limite})
    async def listar_membros(self, servidor_id: str, *, limite: int = 1000, depois_de: str | None = None) -> list[dict[str, Any]]:
        if not 1 <= limite <= 1000:
            raise ValueError("limite de membros deve estar entre 1 e 1000")
        parametros = {"limit": limite}
        if depois_de:
            parametros["after"] = str(depois_de)
        return await self.requisitar("GET", f"/guilds/{servidor_id}/members", parametros=parametros)
    async def obter_membro(self, servidor_id: str, usuario_id: str) -> dict[str, Any]: return await self.requisitar("GET", f"/guilds/{servidor_id}/members/{usuario_id}")
    async def obter_membro_atual(self, servidor_id: str) -> dict[str, Any]:
        """Obtém a representação do usuário autenticado no servidor."""
        return await self.requisitar("GET", f"/guilds/{servidor_id}/members/@me")
    async def alterar_apelido_atual(self, servidor_id: str, apelido: str | None, *, motivo: str | None = None) -> dict[str, Any]:
        """Altera o apelido atual pela rota oficial dedicada (compatibilidade)."""
        return await self.requisitar("PATCH", f"/guilds/{servidor_id}/members/@me/nick", json={"nick": apelido}, motivo=motivo)
    async def editar_membro(self, servidor_id: str, usuario_id: str, **dados: Any) -> dict[str, Any]: return await self.requisitar("PATCH", f"/guilds/{servidor_id}/members/{usuario_id}", json=dados, motivo=dados.pop("motivo", None))
    async def editar_membro_atual(self, servidor_id: str, **dados: Any) -> dict[str, Any]:
        """Edita o membro do bot no servidor indicado (`/members/@me`)."""
        motivo = dados.pop("motivo", None)
        return await self.requisitar("PATCH", f"/guilds/{servidor_id}/members/@me", json=dados, motivo=motivo)
    async def expulsar_membro(self, servidor_id: str, usuario_id: str, *, motivo: str | None = None) -> None: await self.requisitar("DELETE", f"/guilds/{servidor_id}/members/{usuario_id}", motivo=motivo)
    async def banir_membro(self, servidor_id: str, usuario_id: str, *, dias_mensagens: int = 0, motivo: str | None = None) -> None: await self.requisitar("PUT", f"/guilds/{servidor_id}/bans/{usuario_id}", json={"delete_message_days": max(0, min(7, dias_mensagens))}, motivo=motivo)
    async def desbanir_membro(self, servidor_id: str, usuario_id: str, *, motivo: str | None = None) -> None: await self.requisitar("DELETE", f"/guilds/{servidor_id}/bans/{usuario_id}", motivo=motivo)
    async def obter_banimento(self, servidor_id: str, usuario_id: str) -> dict[str, Any]:
        """Obtém o banimento individual de um usuário no servidor."""
        return await self.requisitar("GET", f"/guilds/{servidor_id}/bans/{usuario_id}")
    async def listar_banimentos(self, servidor_id: str, *, limite: int = 1000, antes_de: str | None = None, depois_de: str | None = None) -> list[dict[str, Any]]:
        if not 1 <= limite <= 1000:
            raise ValueError("limite de banimentos deve estar entre 1 e 1000")
        if antes_de and depois_de:
            raise ValueError("antes_de e depois_de são mutuamente exclusivos")
        parametros = {"limit": limite}
        if antes_de:
            parametros["before"] = str(antes_de)
        elif depois_de:
            parametros["after"] = str(depois_de)
        return await self.requisitar("GET", f"/guilds/{servidor_id}/bans", parametros=parametros)
    async def listar_banimentos_modelados(self, servidor_id: str, *, limite: int = 1000, antes_de: str | None = None, depois_de: str | None = None) -> list[Any]:
        from ..discord.recursos import Banimento
        return [Banimento.de_dict(item) for item in await self.listar_banimentos(servidor_id, limite=limite, antes_de=antes_de, depois_de=depois_de)]
    async def listar_cargos(self, servidor_id: str) -> list[dict[str, Any]]: return await self.requisitar("GET", f"/guilds/{servidor_id}/roles")
    async def obter_cargo(self, servidor_id: str, cargo_id: str) -> dict[str, Any]:
        """Obtém um cargo específico, preservando a resposta oficial."""
        return await self.requisitar("GET", f"/guilds/{servidor_id}/roles/{cargo_id}")
    async def criar_cargo(self, servidor_id: str, **dados: Any) -> dict[str, Any]: return await self.requisitar("POST", f"/guilds/{servidor_id}/roles", json=dados, motivo=dados.pop("motivo", None))
    async def editar_cargo(self, servidor_id: str, cargo_id: str, **dados: Any) -> dict[str, Any]: return await self.requisitar("PATCH", f"/guilds/{servidor_id}/roles/{cargo_id}", json=dados, motivo=dados.pop("motivo", None))
    async def excluir_cargo(self, servidor_id: str, cargo_id: str, *, motivo: str | None = None) -> None: await self.requisitar("DELETE", f"/guilds/{servidor_id}/roles/{cargo_id}", motivo=motivo)
    async def mover_cargos(self, servidor_id: str, cargos: list[dict[str, Any]]) -> None: await self.requisitar("PATCH", f"/guilds/{servidor_id}/roles", json=cargos)
    async def adicionar_cargo(self, servidor_id: str, usuario_id: str, cargo_id: str, *, motivo: str | None = None) -> None: await self.requisitar("PUT", f"/guilds/{servidor_id}/members/{usuario_id}/roles/{cargo_id}", motivo=motivo)
    async def remover_cargo(self, servidor_id: str, usuario_id: str, cargo_id: str, *, motivo: str | None = None) -> None: await self.requisitar("DELETE", f"/guilds/{servidor_id}/members/{usuario_id}/roles/{cargo_id}", motivo=motivo)
    async def obter_auditoria(
        self,
        servidor_id: str,
        *,
        usuario_id: str | None = None,
        acao: int | None = None,
        antes_de: str | None = None,
        limite: int = 50,
        **parametros: Any,
    ) -> dict[str, Any]:
        """Obtém o registro de auditoria com filtros oficiais e validação offline."""
        if not 1 <= limite <= 100:
            raise ValueError("limite deve estar entre 1 e 100")
        consulta = dict(parametros)
        consulta["limit"] = limite
        if usuario_id is not None:
            consulta["user_id"] = str(usuario_id)
        if acao is not None:
            consulta["action_type"] = int(acao)
        if antes_de is not None:
            consulta["before"] = str(antes_de)
        return await self.requisitar("GET", f"/guilds/{servidor_id}/audit-logs", parametros=consulta)

    async def obter_auditoria_modelada(self, servidor_id: str, **parametros: Any) -> Any:
        from ..discord.recursos import RegistroAuditoria
        return RegistroAuditoria.de_dict(await self.obter_auditoria(servidor_id, **parametros))

    async def listar_registros_auditoria(self, servidor_id: str, **parametros: Any) -> list[Any]:
        """Atalho que retorna somente as entradas modeladas do registro."""
        registro = await self.obter_auditoria_modelada(servidor_id, **parametros)
        return registro.entradas

    async def listar_convites_canal(self, canal_id: str) -> list[dict[str, Any]]: return await self.requisitar("GET", f"/channels/{canal_id}/invites")
    async def listar_convites_servidor(self, servidor_id: str) -> list[dict[str, Any]]: return await self.requisitar("GET", f"/guilds/{servidor_id}/invites")
    async def criar_convite(self, canal_id: str, **dados: Any) -> dict[str, Any]: return await self.requisitar("POST", f"/channels/{canal_id}/invites", json=dados, motivo=dados.pop("motivo", None))
    async def obter_convite(self, codigo: str, *, contagem: bool = False, expiracao: bool = False) -> dict[str, Any]: return await self.requisitar("GET", f"/invites/{codigo}", parametros={"with_counts": contagem, "with_expiration": expiracao})
    async def excluir_convite(self, codigo: str, *, motivo: str | None = None) -> dict[str, Any]: return await self.requisitar("DELETE", f"/invites/{codigo}", motivo=motivo)
    async def obter_usuarios_alvo_convite(self, codigo: str) -> bytes: return await self.requisitar("GET", f"/invites/{codigo}/target-users", bruto=True)
    async def atualizar_usuarios_alvo_convite(self, codigo: str, arquivo: Any, *, nome_arquivo: str = "usuarios.csv") -> dict[str, Any]:
        """Substitui a lista CSV de usuários autorizados a aceitar um convite."""
        return await self.requisitar(
            "PUT",
            f"/invites/{codigo}/target-users",
            arquivos=[("target_users_file", nome_arquivo, arquivo)],
        )
    async def obter_status_usuarios_alvo_convite(self, codigo: str) -> dict[str, Any]:
        """Consulta o processamento assíncrono da lista CSV de usuários-alvo."""
        return await self.requisitar("GET", f"/invites/{codigo}/target-users/job-status")

    # Lobbies e superfícies de sessão especializadas
    async def atualizar_lobbies(self, **dados: Any) -> dict[str, Any]:
        """Atualiza a configuração global de Lobbies usando `PUT /lobbies`."""
        return await self.requisitar("PUT", "/lobbies", json=dados)

    async def criar_lobby(self, **dados: Any) -> dict[str, Any]:
        """Cria um Lobby com o corpo oficial fornecido pelo Discord."""
        return await self.requisitar("POST", "/lobbies", json=dados)

    async def obter_lobby(self, lobby_id: str) -> dict[str, Any]:
        return await self.requisitar("GET", f"/lobbies/{lobby_id}")

    async def excluir_lobby(self, lobby_id: str) -> None:
        await self.requisitar("DELETE", f"/lobbies/{lobby_id}")

    async def editar_lobby(self, lobby_id: str, **dados: Any) -> dict[str, Any]:
        return await self.requisitar("PATCH", f"/lobbies/{lobby_id}", json=dados)

    async def editar_vinculo_canal_lobby(self, lobby_id: str, **dados: Any) -> dict[str, Any]:
        return await self.requisitar("PATCH", f"/lobbies/{lobby_id}/channel-linking", json=dados)

    async def sair_lobby(self, lobby_id: str) -> None:
        await self.requisitar("DELETE", f"/lobbies/{lobby_id}/members/@me")

    async def convidar_eu_para_lobby(self, lobby_id: str) -> dict[str, Any]:
        return await self.requisitar("POST", f"/lobbies/{lobby_id}/members/@me/invites")

    async def adicionar_membros_lobby(self, lobby_id: str, membros: list[Any]) -> list[dict[str, Any]]:
        if not isinstance(membros, list):
            raise TypeError("membros deve ser uma lista")
        return await self.requisitar("POST", f"/lobbies/{lobby_id}/members/bulk", json=membros)

    async def adicionar_membro_lobby(self, lobby_id: str, usuario_id: str, **dados: Any) -> dict[str, Any]:
        return await self.requisitar("PUT", f"/lobbies/{lobby_id}/members/{usuario_id}", json=dados)

    async def remover_membro_lobby(self, lobby_id: str, usuario_id: str) -> None:
        await self.requisitar("DELETE", f"/lobbies/{lobby_id}/members/{usuario_id}")

    async def convidar_membro_lobby(self, lobby_id: str, usuario_id: str) -> dict[str, Any]:
        return await self.requisitar("POST", f"/lobbies/{lobby_id}/members/{usuario_id}/invites")

    async def listar_mensagens_lobby(self, lobby_id: str, *, limite: int | None = None) -> list[dict[str, Any]]:
        parametros = {} if limite is None else {"limit": limite}
        return await self.requisitar("GET", f"/lobbies/{lobby_id}/messages", parametros=parametros)

    async def enviar_mensagem_lobby(self, lobby_id: str, dados: Any) -> dict[str, Any]:
        return await self.requisitar("POST", f"/lobbies/{lobby_id}/messages", json=dados)

    async def definir_metadata_moderacao_mensagem_lobby(self, lobby_id: str, mensagem_id: str, dados: Any, *, formulario: bool = False) -> None:
        if formulario:
            await self.requisitar("PUT", f"/lobbies/{lobby_id}/messages/{mensagem_id}/moderation-metadata", arquivos=[], campos_multipart={str(k): v for k, v in (dados or {}).items()})
        else:
            await self.requisitar("PUT", f"/lobbies/{lobby_id}/messages/{mensagem_id}/moderation-metadata", json=dados)

    async def criar_anexo_aplicacao(self, aplicacao_id: str, arquivo: Any, *, nome_arquivo: str = "arquivo") -> dict[str, Any]:
        """Envia um anexo de aplicação pelo campo multipart oficial `file`."""
        if not aplicacao_id:
            raise ValueError("aplicacao_id não pode ser vazio")
        return await self.requisitar("POST", f"/applications/{aplicacao_id}/attachment", arquivos=[("file", nome_arquivo, arquivo)])

    async def desvincular_conta_provisoria(self, dados: dict[str, Any]) -> None:
        self._validar_dados_partner(dados, ("client_id", "external_auth_token", "external_auth_type"))
        await self.requisitar("POST", "/partner-sdk/provisional-accounts/unmerge", json=dados)

    async def desvincular_conta_provisoria_bot(self, external_user_id: str) -> None:
        if not external_user_id:
            raise ValueError("external_user_id não pode ser vazio")
        await self.requisitar("POST", "/partner-sdk/provisional-accounts/unmerge/bot", json={"external_user_id": external_user_id})

    async def obter_token_partner(self, dados: dict[str, Any]) -> dict[str, Any]:
        self._validar_dados_partner(dados, ("client_id", "external_auth_token", "external_auth_type"))
        return await self.requisitar("POST", "/partner-sdk/token", json=dados)

    async def obter_token_partner_bot(self, external_user_id: str, *, provisional_user_id: str | None = None, preferred_global_name: str | None = None) -> dict[str, Any]:
        if not external_user_id:
            raise ValueError("external_user_id não pode ser vazio")
        dados: dict[str, Any] = {"external_user_id": external_user_id}
        if provisional_user_id is not None:
            dados["provisional_user_id"] = provisional_user_id
        if preferred_global_name is not None:
            dados["preferred_global_name"] = preferred_global_name
        return await self.requisitar("POST", "/partner-sdk/token/bot", json=dados)

    async def definir_metadata_moderacao_dm_partner(self, usuario_id_1: str, usuario_id_2: str, mensagem_id: str, dados: dict[str, Any], *, formulario: bool = False) -> None:
        if not isinstance(dados, dict) or len(dados) > 5:
            raise ValueError("dados deve ser um dicionário com no máximo 5 campos")
        if any(not isinstance(chave, str) or not isinstance(valor, str) or len(valor) > 2000 for chave, valor in dados.items()):
            raise ValueError("metadata deve conter textos de no máximo 2000 caracteres")
        rota = f"/partner-sdk/dms/{usuario_id_1}/{usuario_id_2}/messages/{mensagem_id}/moderation-metadata"
        if formulario:
            await self.requisitar("PUT", rota, arquivos=[], campos_multipart=dados)
        else:
            await self.requisitar("PUT", rota, json=dados)

    async def executar_webhook_github(self, webhook_id: str, token: str, dados: dict[str, Any], *, esperar: bool = False, thread_id: str | None = None) -> Any:
        parametros = {"wait": esperar}
        if thread_id is not None:
            parametros["thread_id"] = thread_id
        return await self.requisitar("POST", f"/webhooks/{webhook_id}/{token}/github", json=dados, parametros=parametros)

    async def executar_webhook_slack(self, webhook_id: str, token: str, dados: dict[str, Any], *, esperar: bool = False, thread_id: str | None = None, formulario: bool = False) -> Any:
        parametros = {"wait": esperar}
        if thread_id is not None:
            parametros["thread_id"] = thread_id
        if formulario:
            return await self.requisitar("POST", f"/webhooks/{webhook_id}/{token}/slack", arquivos=[], campos_multipart=dados, parametros=parametros)
        return await self.requisitar("POST", f"/webhooks/{webhook_id}/{token}/slack", json=dados, parametros=parametros)

    @staticmethod
    def _validar_dados_partner(dados: dict[str, Any], obrigatorios: tuple[str, ...]) -> None:
        if not isinstance(dados, dict):
            raise TypeError("dados deve ser um dicionário")
        ausentes = [campo for campo in obrigatorios if not dados.get(campo)]
        if ausentes:
            raise ValueError(f"campos obrigatórios ausentes: {', '.join(ausentes)}")

    # Webhooks, emojis, stickers, eventos e integrações
    async def criar_webhook(self, canal_id: str, **dados: Any) -> dict[str, Any]: return await self.requisitar("POST", f"/channels/{canal_id}/webhooks", json=dados, motivo=dados.pop("motivo", None))
    async def listar_webhooks_canal(self, canal_id: str) -> list[dict[str, Any]]: return await self.requisitar("GET", f"/channels/{canal_id}/webhooks")
    async def listar_webhooks_servidor(self, servidor_id: str) -> list[dict[str, Any]]: return await self.requisitar("GET", f"/guilds/{servidor_id}/webhooks")
    async def obter_webhook(self, webhook_id: str) -> dict[str, Any]: return await self.requisitar("GET", f"/webhooks/{webhook_id}")
    async def obter_webhook_token(self, webhook_id: str, token: str) -> dict[str, Any]: return await self.requisitar("GET", f"/webhooks/{webhook_id}/{token}")
    async def editar_webhook(self, webhook_id: str, **dados: Any) -> dict[str, Any]: return await self.requisitar("PATCH", f"/webhooks/{webhook_id}", json=dados, motivo=dados.pop("motivo", None))
    async def editar_webhook_token(self, webhook_id: str, token: str, **dados: Any) -> dict[str, Any]: return await self.requisitar("PATCH", f"/webhooks/{webhook_id}/{token}", json=dados)
    async def excluir_webhook(self, webhook_id: str, *, motivo: str | None = None) -> None: await self.requisitar("DELETE", f"/webhooks/{webhook_id}", motivo=motivo)
    async def excluir_webhook_token(self, webhook_id: str, token: str) -> None: await self.requisitar("DELETE", f"/webhooks/{webhook_id}/{token}")
    async def executar_webhook(self, webhook_id: str, token: str, *, arquivos: Iterable[Any] | None = None, campos_multipart: dict[str, Any] | None = None, **dados: Any) -> Any:
        """Executa um webhook com validação local dos requisitos oficiais.

        Aceita `esperar`, `id_thread` e `nome_thread` como aliases portugueses,
        mantendo também `wait`, `thread_id` e `thread_name` para interoperabilidade.
        Pelo menos um conteúdo, embed, componente, arquivo ou enquete é obrigatório.
        """
        payload = dict(dados)
        esperar = bool(payload.pop("esperar", payload.pop("wait", False)))
        id_thread = payload.pop("id_thread", payload.pop("thread_id", None))
        nome_thread = payload.pop("nome_thread", payload.pop("thread_name", None))
        aliases = {"conteudo": "content", "componentes": "components", "arquivo": "file", "enquete": "poll"}
        for portugues, oficial in aliases.items():
            if portugues in payload and oficial not in payload:
                payload[oficial] = payload.pop(portugues)
        if not any(payload.get(chave) is not None for chave in ("content", "embeds", "components", "file", "poll")):
            raise ValueError("um webhook exige content, embeds, components, file ou poll")
        parametros: dict[str, str] = {"wait": str(esperar).lower()}
        if id_thread is not None:
            parametros["thread_id"] = str(id_thread)
        if nome_thread is not None:
            payload["thread_name"] = nome_thread
        return await self.requisitar("POST", f"/webhooks/{webhook_id}/{token}", json=payload, arquivos=arquivos, campos_multipart=campos_multipart, parametros=parametros)
    async def obter_mensagem_webhook_original(self, webhook_id: str, token: str) -> dict[str, Any]:
        return await self.requisitar("GET", f"/webhooks/{webhook_id}/{token}/messages/@original")
    async def editar_mensagem_webhook_original(self, webhook_id: str, token: str, **dados: Any) -> dict[str, Any]:
        return await self.requisitar("PATCH", f"/webhooks/{webhook_id}/{token}/messages/@original", json=dados)
    async def apagar_mensagem_webhook_original(self, webhook_id: str, token: str) -> None:
        await self.requisitar("DELETE", f"/webhooks/{webhook_id}/{token}/messages/@original")
    async def obter_mensagem_webhook(self, webhook_id: str, token: str, mensagem_id: str) -> dict[str, Any]:
        return await self.requisitar("GET", f"/webhooks/{webhook_id}/{token}/messages/{mensagem_id}")
    async def editar_mensagem_webhook(self, webhook_id: str, token: str, mensagem_id: str, **dados: Any) -> dict[str, Any]:
        return await self.requisitar("PATCH", f"/webhooks/{webhook_id}/{token}/messages/{mensagem_id}", json=dados)
    async def apagar_mensagem_webhook(self, webhook_id: str, token: str, mensagem_id: str) -> None:
        await self.requisitar("DELETE", f"/webhooks/{webhook_id}/{token}/messages/{mensagem_id}")
    async def listar_emojis(self, servidor_id: str) -> list[dict[str, Any]]: return await self.requisitar("GET", f"/guilds/{servidor_id}/emojis")
    async def obter_emoji(self, servidor_id: str, emoji_id: str) -> dict[str, Any]:
        """Obtém um emoji específico de um servidor."""
        return await self.requisitar("GET", f"/guilds/{servidor_id}/emojis/{emoji_id}")
    async def criar_emoji(self, servidor_id: str, **dados: Any) -> dict[str, Any]: return await self.requisitar("POST", f"/guilds/{servidor_id}/emojis", json=dados, motivo=dados.pop("motivo", None))
    async def editar_emoji(self, servidor_id: str, emoji_id: str, **dados: Any) -> dict[str, Any]: return await self.requisitar("PATCH", f"/guilds/{servidor_id}/emojis/{emoji_id}", json=dados, motivo=dados.pop("motivo", None))
    async def excluir_emoji(self, servidor_id: str, emoji_id: str, *, motivo: str | None = None) -> None: await self.requisitar("DELETE", f"/guilds/{servidor_id}/emojis/{emoji_id}", motivo=motivo)
    async def listar_stickers_servidor(self, servidor_id: str) -> list[dict[str, Any]]: return await self.requisitar("GET", f"/guilds/{servidor_id}/stickers")
    async def criar_sticker(self, servidor_id: str, *, nome: str, tags: str, arquivo: Any, nome_arquivo: str = "sticker.png", descricao: str | None = None, motivo: str | None = None) -> dict[str, Any]:
        if not nome.strip():
            raise ValueError("nome do sticker não pode ser vazio")
        if not tags.strip():
            raise ValueError("tags do sticker não podem ser vazias")
        campos = {"name": nome, "tags": tags}
        if descricao is not None:
            campos["description"] = descricao
        return await self.requisitar("POST", f"/guilds/{servidor_id}/stickers", arquivos=[("file", nome_arquivo, arquivo)], campos_multipart=campos, motivo=motivo)
    async def obter_sticker(self, sticker_id: str) -> dict[str, Any]: return await self.requisitar("GET", f"/stickers/{sticker_id}")
    async def obter_sticker_servidor(self, servidor_id: str, sticker_id: str) -> dict[str, Any]: return await self.requisitar("GET", f"/guilds/{servidor_id}/stickers/{sticker_id}")
    async def editar_sticker(self, servidor_id: str, sticker_id: str, **dados: Any) -> dict[str, Any]: return await self.requisitar("PATCH", f"/guilds/{servidor_id}/stickers/{sticker_id}", json=dados, motivo=dados.pop("motivo", None))
    async def excluir_sticker(self, servidor_id: str, sticker_id: str, *, motivo: str | None = None) -> None: await self.requisitar("DELETE", f"/guilds/{servidor_id}/stickers/{sticker_id}", motivo=motivo)

    async def listar_stickers_modelados(self, servidor_id: str) -> list[Any]:
        from ..discord.recursos import Adesivo
        return [Adesivo.de_dict(item) for item in await self.listar_stickers_servidor(servidor_id)]

    async def obter_sticker_modelado(self, sticker_id: str) -> Any:
        from ..discord.recursos import Adesivo
        return Adesivo.de_dict(await self.obter_sticker(sticker_id))

    async def criar_instancia_stage(self, servidor_id: str, **dados: Any) -> dict[str, Any]: return await self.requisitar("POST", f"/stage-instances", json=dados)
    async def obter_instancia_stage(self, canal_id: str) -> dict[str, Any]: return await self.requisitar("GET", f"/stage-instances/{canal_id}")
    async def obter_instancia_stage_modelada(self, canal_id: str) -> Any:
        from ..discord.recursos import InstanciaStage
        return InstanciaStage.de_dict(await self.obter_instancia_stage(canal_id))
    async def editar_instancia_stage(self, canal_id: str, **dados: Any) -> dict[str, Any]: return await self.requisitar("PATCH", f"/stage-instances/{canal_id}", json=dados)
    async def excluir_instancia_stage(self, canal_id: str) -> None: await self.requisitar("DELETE", f"/stage-instances/{canal_id}")
    async def listar_integracoes(self, servidor_id: str) -> list[dict[str, Any]]: return await self.requisitar("GET", f"/guilds/{servidor_id}/integrations")
    async def listar_integracoes_modeladas(self, servidor_id: str) -> list[Any]:
        from ..discord.recursos import Integracao
        return [Integracao.de_dict(item) for item in await self.listar_integracoes(servidor_id)]
    async def excluir_integracao(self, servidor_id: str, integracao_id: str, *, motivo: str | None = None) -> None:
        """Exclui uma integração pela rota oficial, sem o segmento obsoleto de tipo."""
        await self.requisitar("DELETE", f"/guilds/{servidor_id}/integrations/{integracao_id}", motivo=motivo)
    async def listar_regioes_voz(self) -> list[dict[str, Any]]: return await self.requisitar("GET", "/voice/regions")
    async def listar_regioes_servidor(self, servidor_id: str) -> list[dict[str, Any]]: return await self.requisitar("GET", f"/guilds/{servidor_id}/regions")
    async def listar_regioes_voz_modeladas(self) -> list[Any]:
        from ..discord.recursos import RegiaoVoz
        return [RegiaoVoz.de_dict(item) for item in await self.listar_regioes_voz()]
    async def obter_widget(self, servidor_id: str) -> dict[str, Any]: return await self.requisitar("GET", f"/guilds/{servidor_id}/widget.json")
    async def obter_configuracao_widget(self, servidor_id: str) -> dict[str, Any]: return await self.requisitar("GET", f"/guilds/{servidor_id}/widget")
    async def obter_widget_png(self, servidor_id: str) -> bytes: return await self.requisitar("GET", f"/guilds/{servidor_id}/widget.png", bruto=True)
    async def editar_configuracao_widget(self, servidor_id: str, **dados: Any) -> dict[str, Any]: return await self.requisitar("PATCH", f"/guilds/{servidor_id}/widget", json=dados)
    @staticmethod
    def _validar_dias_poda(dias: int) -> None:
        if not 1 <= dias <= 30:
            raise ValueError("dias de poda deve estar entre 1 e 30")

    async def contar_poda(self, servidor_id: str, *, dias: int = 7, incluir_cargos: bool = False) -> dict[str, Any]:
        self._validar_dias_poda(dias)
        return await self.requisitar("GET", f"/guilds/{servidor_id}/prune", parametros={"days": dias, "include_roles": incluir_cargos})
    async def podar_membros(self, servidor_id: str, *, dias: int = 7, calcular_contagem: bool = True, incluir_cargos: bool = False) -> dict[str, Any]:
        self._validar_dias_poda(dias)
        dados = {"days": dias, "compute_prune_count": calcular_contagem, "include_roles": incluir_cargos}
        return await self.requisitar("POST", f"/guilds/{servidor_id}/prune", json=dados)
    async def obter_preview_servidor(self, servidor_id: str) -> dict[str, Any]: return await self.requisitar("GET", f"/guilds/{servidor_id}/preview")
    async def listar_solicitacoes_entrada(self, servidor_id: str, *, status: str | None = None, limite: int = 100, antes_de: str | None = None, depois_de: str | None = None) -> list[dict[str, Any]]:
        """Lista solicitações de entrada do servidor com paginação oficial."""
        if not 1 <= limite <= 100:
            raise ValueError("limite deve estar entre 1 e 100")
        if antes_de and depois_de:
            raise ValueError("antes_de e depois_de são mutuamente exclusivos")
        parametros: dict[str, Any] = {"limit": limite}
        if status is not None:
            parametros["status"] = status
        if antes_de:
            parametros["before"] = antes_de
        elif depois_de:
            parametros["after"] = depois_de
        return await self.requisitar("GET", f"/guilds/{servidor_id}/requests", parametros=parametros)

    async def modificar_solicitacao_entrada(self, servidor_id: str, solicitacao_id: str, *, acao: str, motivo_rejeicao: str | None = None) -> dict[str, Any]:
        """Aprova ou rejeita uma solicitação de entrada."""
        if acao not in {"STARTED", "SUBMITTED", "REJECTED", "APPROVED"}:
            raise ValueError("acao deve ser STARTED, SUBMITTED, REJECTED ou APPROVED")
        if motivo_rejeicao is not None and len(motivo_rejeicao) > 160:
            raise ValueError("motivo_rejeicao deve ter no máximo 160 caracteres")
        dados: dict[str, Any] = {"action": acao}
        if motivo_rejeicao is not None:
            dados["rejection_reason"] = motivo_rejeicao
        return await self.requisitar("PATCH", f"/guilds/{servidor_id}/requests/{solicitacao_id}", json=dados)

    async def obter_url_personalizada(self, servidor_id: str) -> dict[str, Any]: return await self.requisitar("GET", f"/guilds/{servidor_id}/vanity-url")
    async def obter_estado_voz(self, servidor_id: str, usuario_id: str = "@me") -> dict[str, Any]: return await self.requisitar("GET", f"/guilds/{servidor_id}/voice-states/{usuario_id}")
    async def alterar_estado_voz(self, servidor_id: str, *, canal_id: str | None = None, suprimido: bool | None = None, pedido_fala_em: str | None = None) -> None:
        dados = {}
        if canal_id is not None: dados["channel_id"] = str(canal_id)
        if suprimido is not None: dados["suppress"] = bool(suprimido)
        if pedido_fala_em is not None: dados["request_to_speak_timestamp"] = pedido_fala_em
        await self.requisitar("PATCH", f"/guilds/{servidor_id}/voice-states/@me", json=dados)
    async def alterar_estado_voz_usuario(self, servidor_id: str, usuario_id: str, *, canal_id: str | None = None, suprimido: bool | None = None) -> None:
        dados = {}
        if canal_id is not None: dados["channel_id"] = str(canal_id)
        if suprimido is not None: dados["suppress"] = bool(suprimido)
        await self.requisitar("PATCH", f"/guilds/{servidor_id}/voice-states/{usuario_id}", json=dados)
    async def obter_tela_boas_vindas(self, servidor_id: str) -> dict[str, Any]: return await self.requisitar("GET", f"/guilds/{servidor_id}/welcome-screen")
    async def obter_boas_vindas_novos_membros(self, servidor_id: str) -> dict[str, Any]: return await self.requisitar("GET", f"/guilds/{servidor_id}/new-member-welcome")
    async def obter_onboarding(self, servidor_id: str) -> dict[str, Any]: return await self.requisitar("GET", f"/guilds/{servidor_id}/onboarding")
    async def editar_onboarding(self, servidor_id: str, **dados: Any) -> dict[str, Any]: return await self.requisitar("PUT", f"/guilds/{servidor_id}/onboarding", json=dados)
    async def editar_tela_boas_vindas(self, servidor_id: str, **dados: Any) -> dict[str, Any]: return await self.requisitar("PATCH", f"/guilds/{servidor_id}/welcome-screen", json=dados)
    async def modificar_acoes_incidente(self, servidor_id: str, **dados: Any) -> dict[str, Any]:
        """Atualiza as ações de incidente do servidor conforme a API oficial."""
        permitidos = {"invites_disabled_until", "dms_disabled_until"}
        desconhecidos = set(dados) - permitidos
        if desconhecidos:
            raise ValueError(f"Campos de incidente desconhecidos: {sorted(desconhecidos)}")
        if not dados:
            raise ValueError("Informe ao menos uma ação de incidente")
        for chave, valor in dados.items():
            if valor is not None and not isinstance(valor, str):
                raise TypeError(f"{chave} deve ser um timestamp ISO8601 ou None")
        return await self.requisitar("PUT", f"/guilds/{servidor_id}/incident-actions", json=dados)

    # Usuário, aplicações e comandos de aplicação
    async def obter_usuario(self, usuario_id: str = "@me") -> dict[str, Any]: return await self.requisitar("GET", f"/users/{usuario_id}")
    async def editar_usuario_atual(self, **dados: Any) -> dict[str, Any]:
        """Edita o usuário do bot autenticado, conforme o endpoint oficial `/users/@me`."""
        return await self.requisitar("PATCH", "/users/@me", json=dados)
    async def criar_dm(self, usuario_id: str) -> dict[str, Any]: return await self.requisitar("POST", "/users/@me/channels", json={"recipient_id": str(usuario_id)})
    async def listar_conexoes_usuario(self) -> list[dict[str, Any]]: return await self.requisitar("GET", "/users/@me/connections")
    async def listar_conexoes_usuario_modeladas(self) -> list[Any]:
        from ..discord.recursos import ConexaoUsuario
        return [ConexaoUsuario.de_dict(item) for item in await self.listar_conexoes_usuario()]
    async def remover_conexao_cargo_usuario(self, aplicacao_id: str = "@me") -> None:
        await self.requisitar("DELETE", f"/users/@me/applications/{aplicacao_id}/role-connection")
    async def obter_conexao_cargo_usuario(self, aplicacao_id: str = "@me") -> dict[str, Any]:
        return await self.requisitar("GET", f"/users/@me/applications/{aplicacao_id}/role-connection")
    async def obter_conexao_cargo_usuario_modelada(self, aplicacao_id: str = "@me") -> Any:
        from ..discord.recursos import ConexaoUsuario
        return ConexaoUsuario.de_dict(await self.obter_conexao_cargo_usuario(aplicacao_id))
    async def atualizar_conexao_cargo_usuario(self, dados: dict[str, Any], aplicacao_id: str = "@me") -> dict[str, Any]:
        return await self.requisitar("PUT", f"/users/@me/applications/{aplicacao_id}/role-connection", json=dados)
    async def atualizar_conexao_cargo_usuario_modelada(self, dados: dict[str, Any], aplicacao_id: str = "@me") -> Any:
        from ..discord.recursos import ConexaoUsuario
        return ConexaoUsuario.de_dict(await self.atualizar_conexao_cargo_usuario(dados, aplicacao_id))
    async def criar_dm_grupo(self, **dados: Any) -> dict[str, Any]: return await self.requisitar("POST", "/users/@me/channels", json=dados)
    async def obter_aplicacao(self, aplicacao_id: str = "@me") -> dict[str, Any]: return await self.requisitar("GET", f"/applications/{aplicacao_id}")
    async def editar_aplicacao(self, aplicacao_id: str, **dados: Any) -> dict[str, Any]: return await self.requisitar("PATCH", f"/applications/{aplicacao_id}", json=dados)
    async def obter_oauth2_atual(self) -> dict[str, Any]:
        """Obtém as informações do token OAuth2 atualmente autenticado."""
        return await self.requisitar("GET", "/oauth2/@me")
    async def obter_aplicacao_oauth2_atual(self) -> dict[str, Any]:
        """Obtém a aplicação associada ao token OAuth2 atual."""
        return await self.requisitar("GET", "/oauth2/applications/@me")
    async def obter_chaves_oauth2(self) -> dict[str, Any]:
        """Obtém as chaves públicas OAuth2 da aplicação autenticada."""
        return await self.requisitar("GET", "/oauth2/keys")
    async def obter_userinfo_oauth2(self) -> dict[str, Any]:
        """Obtém as claims OpenID Connect do token OAuth2 atual."""
        return await self.requisitar("GET", "/oauth2/userinfo")
    async def obter_metadados_conexoes_cargo(self, aplicacao_id: str = "@me") -> list[dict[str, Any]]: return await self.requisitar("GET", f"/applications/{aplicacao_id}/role-connections/metadata")
    async def obter_metadados_conexoes_cargo_modelados(self, aplicacao_id: str = "@me") -> list[Any]:
        from ..discord.recursos import MetadadoConexao
        return [MetadadoConexao.de_dict(item) for item in await self.obter_metadados_conexoes_cargo(aplicacao_id)]
    async def substituir_metadados_conexoes_cargo(self, metadados: list[dict[str, Any]], aplicacao_id: str = "@me") -> list[dict[str, Any]]: return await self.requisitar("PUT", f"/applications/{aplicacao_id}/role-connections/metadata", json=metadados)
    async def substituir_metadados_conexoes_cargo_modelados(self, metadados: list[dict[str, Any]], aplicacao_id: str = "@me") -> list[Any]:
        from ..discord.recursos import MetadadoConexao
        resposta = await self.substituir_metadados_conexoes_cargo(metadados, aplicacao_id)
        return [MetadadoConexao.de_dict(item) for item in resposta]
    async def executar_comando_aplicacao(self, aplicacao_id: str, token: str, **dados: Any) -> None: await self.requisitar("POST", f"/interactions/{aplicacao_id}/{token}/callback", json=dados)
    async def listar_emojis_aplicacao(self, aplicacao_id: str) -> dict[str, Any]:
        return await self.requisitar("GET", f"/applications/{aplicacao_id}/emojis")
    async def criar_emoji_aplicacao(self, aplicacao_id: str, *, nome: str, imagem: str) -> dict[str, Any]:
        if not nome.strip():
            raise ValueError("nome do emoji não pode ser vazio")
        if not imagem.strip():
            raise ValueError("imagem do emoji não pode ser vazia")
        return await self.requisitar("POST", f"/applications/{aplicacao_id}/emojis", json={"name": nome, "image": imagem})
    async def obter_emoji_aplicacao(self, aplicacao_id: str, emoji_id: str) -> dict[str, Any]:
        return await self.requisitar("GET", f"/applications/{aplicacao_id}/emojis/{emoji_id}")
    async def editar_emoji_aplicacao(self, aplicacao_id: str, emoji_id: str, *, nome: str) -> dict[str, Any]:
        if not nome.strip():
            raise ValueError("nome do emoji não pode ser vazio")
        return await self.requisitar("PATCH", f"/applications/{aplicacao_id}/emojis/{emoji_id}", json={"name": nome})
    async def excluir_emoji_aplicacao(self, aplicacao_id: str, emoji_id: str) -> None:
        await self.requisitar("DELETE", f"/applications/{aplicacao_id}/emojis/{emoji_id}")
    async def listar_entitlements(self, aplicacao_id: str, **parametros: Any) -> list[dict[str, Any]]: return await self.requisitar("GET", f"/applications/{aplicacao_id}/entitlements", parametros=parametros)

    async def listar_entitlements_modelados(self, aplicacao_id: str, **parametros: Any) -> list[Any]:
        from ..discord.recursos import Entitlement
        return [Entitlement.de_dict(item) for item in await self.listar_entitlements(aplicacao_id, **parametros)]
    async def obter_entitlement(self, aplicacao_id: str, entitlement_id: str) -> dict[str, Any]:
        return await self.requisitar("GET", f"/applications/{aplicacao_id}/entitlements/{entitlement_id}")
    async def obter_entitlement_modelado(self, aplicacao_id: str, entitlement_id: str) -> Any:
        from ..discord.recursos import Entitlement
        return Entitlement.de_dict(await self.obter_entitlement(aplicacao_id, entitlement_id))
    async def criar_entitlement_teste(self, aplicacao_id: str, *, sku_id: str, owner_id: str, tipo_dono: int) -> dict[str, Any]:
        dados = {"sku_id": str(sku_id), "owner_id": str(owner_id), "owner_type": int(tipo_dono)}
        return await self.requisitar("POST", f"/applications/{aplicacao_id}/entitlements", json=dados)
    async def criar_entitlement_teste_modelado(self, aplicacao_id: str, *, sku_id: str, owner_id: str, tipo_dono: int) -> Any:
        from ..discord.recursos import Entitlement
        return Entitlement.de_dict(await self.criar_entitlement_teste(aplicacao_id, sku_id=sku_id, owner_id=owner_id, tipo_dono=tipo_dono))
    async def excluir_entitlement_teste(self, aplicacao_id: str, entitlement_id: str) -> None:
        await self.requisitar("DELETE", f"/applications/{aplicacao_id}/entitlements/{entitlement_id}")
    async def consumir_entitlement(self, aplicacao_id: str, entitlement_id: str) -> None: await self.requisitar("POST", f"/applications/{aplicacao_id}/entitlements/{entitlement_id}/consume")
    async def listar_skus(self, aplicacao_id: str = "@me", **parametros: Any) -> list[dict[str, Any]]:
        """Lista os produtos/SKUs de uma aplicação, sem exigir estado remoto local."""
        return await self.requisitar("GET", f"/applications/{aplicacao_id}/skus", parametros=parametros)

    async def obter_sku(self, aplicacao_id: str, sku_id: str) -> dict[str, Any]:
        return await self.requisitar("GET", f"/applications/{aplicacao_id}/skus/{sku_id}")

    async def listar_assinaturas(self, aplicacao_id: str = "@me", **parametros: Any) -> list[dict[str, Any]]:
        """Lista assinaturas com filtros oficiais (user_id, sku_ids e status)."""
        return await self.requisitar("GET", f"/applications/{aplicacao_id}/subscriptions", parametros=parametros)

    async def obter_assinatura(self, aplicacao_id: str, assinatura_id: str) -> dict[str, Any]:
        return await self.requisitar("GET", f"/applications/{aplicacao_id}/subscriptions/{assinatura_id}")

    async def cancelar_assinatura(self, aplicacao_id: str, assinatura_id: str) -> None:
        await self.requisitar("DELETE", f"/applications/{aplicacao_id}/subscriptions/{assinatura_id}")

    async def listar_skus_modelados(self, aplicacao_id: str = "@me", **parametros: Any) -> list[Any]:
        from ..discord.recursos import SkuAplicacao
        return [SkuAplicacao.de_dict(item) for item in await self.listar_skus(aplicacao_id, **parametros)]

    async def obter_sku_modelado(self, aplicacao_id: str, sku_id: str) -> Any:
        from ..discord.recursos import SkuAplicacao
        return SkuAplicacao.de_dict(await self.obter_sku(aplicacao_id, sku_id))

    async def listar_assinaturas_modeladas(self, aplicacao_id: str = "@me", **parametros: Any) -> list[Any]:
        from ..discord.recursos import AssinaturaAplicacao
        return [AssinaturaAplicacao.de_dict(item) for item in await self.listar_assinaturas(aplicacao_id, **parametros)]

    async def listar_assinaturas_sku(self, sku_id: str, *, antes: str | None = None, depois: str | None = None, limite: int | None = None, usuario_id: str | None = None) -> list[dict[str, Any]]:
        """Lista assinaturas que contêm um SKU, com filtros oficiais de paginação e usuário."""
        parametros = {chave: valor for chave, valor in {"before": antes, "after": depois, "limit": limite, "user_id": usuario_id}.items() if valor is not None}
        return await self.requisitar("GET", f"/skus/{sku_id}/subscriptions", parametros=parametros)

    async def obter_assinatura_sku(self, sku_id: str, assinatura_id: str, *, usuario_id: str | None = None) -> dict[str, Any]:
        """Obtém uma assinatura específica vinculada a um SKU."""
        parametros = {"user_id": usuario_id} if usuario_id is not None else {}
        return await self.requisitar("GET", f"/skus/{sku_id}/subscriptions/{assinatura_id}", parametros=parametros)

    async def obter_assinatura_modelada(self, aplicacao_id: str, assinatura_id: str) -> Any:
        from ..discord.recursos import AssinaturaAplicacao
        return AssinaturaAplicacao.de_dict(await self.obter_assinatura(aplicacao_id, assinatura_id))

    async def obter_usuario_atual(self) -> dict[str, Any]:
        """Obtém o usuário autenticado em ``GET /users/@me``."""
        return await self.requisitar("GET", "/users/@me")

    async def obter_aplicacao_atual(self) -> dict[str, Any]:
        """Obtém a aplicação autenticada em ``GET /applications/@me``."""
        return await self.requisitar("GET", "/applications/@me")

    async def editar_aplicacao_atual(self, **dados: Any) -> dict[str, Any]:
        """Edita a aplicação atual; recusa edição vazia antes da rede."""
        if not dados:
            raise ValueError("a edição da aplicação exige ao menos um campo")
        return await self.requisitar("PATCH", "/applications/@me", json=dados)

    async def listar_comandos_aplicacao(self, aplicacao_id: str, *, servidor_id: str | None = None) -> list[dict[str, Any]]:
        rota = f"/applications/{aplicacao_id}/guilds/{servidor_id}/commands" if servidor_id else f"/applications/{aplicacao_id}/commands"
        return await self.requisitar("GET", rota)

    async def listar_comandos_servidor(self, aplicacao_id: str, servidor_id: str) -> list[dict[str, Any]]:
        return await self.listar_comandos_aplicacao(aplicacao_id, servidor_id=servidor_id)
    async def criar_comando_aplicacao(self, aplicacao_id: str, *, servidor_id: str | None = None, **dados: Any) -> dict[str, Any]:
        rota = f"/applications/{aplicacao_id}/guilds/{servidor_id}/commands" if servidor_id else f"/applications/{aplicacao_id}/commands"
        return await self.requisitar("POST", rota, json=dados)

    async def criar_comando_servidor(self, aplicacao_id: str, servidor_id: str, **dados: Any) -> dict[str, Any]: return await self.requisitar("POST", f"/applications/{aplicacao_id}/guilds/{servidor_id}/commands", json=dados)
    async def substituir_comandos(self, aplicacao_id: str, comandos: list[dict[str, Any]], *, servidor_id: str | None = None) -> list[dict[str, Any]]:
        rota = f"/applications/{aplicacao_id}/guilds/{servidor_id}/commands" if servidor_id else f"/applications/{aplicacao_id}/commands"
        return await self.requisitar("PUT", rota, json=comandos)
    async def obter_comando_aplicacao(self, aplicacao_id: str, comando_id: str, *, servidor_id: str | None = None) -> dict[str, Any]:
        rota = f"/applications/{aplicacao_id}/guilds/{servidor_id}/commands/{comando_id}" if servidor_id else f"/applications/{aplicacao_id}/commands/{comando_id}"
        return await self.requisitar("GET", rota)
    async def editar_comando_aplicacao(self, aplicacao_id: str, comando_id: str, **dados: Any) -> dict[str, Any]:
        return await self.requisitar("PATCH", f"/applications/{aplicacao_id}/commands/{comando_id}", json=dados)

    async def excluir_comando_aplicacao(self, aplicacao_id: str, comando_id: str) -> None:
        await self.requisitar("DELETE", f"/applications/{aplicacao_id}/commands/{comando_id}")

    async def editar_comando_servidor(self, aplicacao_id: str, servidor_id: str, comando_id: str, **dados: Any) -> dict[str, Any]: return await self.requisitar("PATCH", f"/applications/{aplicacao_id}/guilds/{servidor_id}/commands/{comando_id}", json=dados)
    async def excluir_comando_servidor(self, aplicacao_id: str, servidor_id: str, comando_id: str) -> None: await self.requisitar("DELETE", f"/applications/{aplicacao_id}/guilds/{servidor_id}/commands/{comando_id}")
    async def obter_permissoes_comandos_servidor(self, aplicacao_id: str, servidor_id: str) -> list[dict[str, Any]]:
        """Obtém as permissões de todos os comandos da aplicação no servidor."""
        return await self.requisitar("GET", f"/applications/{aplicacao_id}/guilds/{servidor_id}/commands/permissions")
    async def obter_permissoes_comando(self, aplicacao_id: str, servidor_id: str, comando_id: str) -> dict[str, Any]:
        rota = f"/applications/{aplicacao_id}/guilds/{servidor_id}/commands/{comando_id}/permissions"
        return await self.requisitar("GET", rota)
    async def substituir_permissoes_comando(self, aplicacao_id: str, servidor_id: str, comando_id: str, permissoes: list[dict[str, Any]]) -> dict[str, Any]:
        rota = f"/applications/{aplicacao_id}/guilds/{servidor_id}/commands/{comando_id}/permissions"
        return await self.requisitar("PUT", rota, json={"permissions": permissoes})
    async def listar_regras_automoderacao(self, servidor_id: str) -> list[dict[str, Any]]: return await self.requisitar("GET", f"/guilds/{servidor_id}/auto-moderation/rules")
    async def obter_regra_automoderacao(self, servidor_id: str, regra_id: str) -> dict[str, Any]: return await self.requisitar("GET", f"/guilds/{servidor_id}/auto-moderation/rules/{regra_id}")
    async def criar_regra_automoderacao(self, servidor_id: str, **dados: Any) -> dict[str, Any]: return await self.requisitar("POST", f"/guilds/{servidor_id}/auto-moderation/rules", json=dados, motivo=dados.pop("motivo", None))
    async def editar_regra_automoderacao(self, servidor_id: str, regra_id: str, **dados: Any) -> dict[str, Any]: return await self.requisitar("PATCH", f"/guilds/{servidor_id}/auto-moderation/rules/{regra_id}", json=dados, motivo=dados.pop("motivo", None))
    async def excluir_regra_automoderacao(self, servidor_id: str, regra_id: str, *, motivo: str | None = None) -> None: await self.requisitar("DELETE", f"/guilds/{servidor_id}/auto-moderation/rules/{regra_id}", motivo=motivo)
    async def listar_eventos_agendados(self, servidor_id: str, *, incluir_entidade: bool = False) -> list[dict[str, Any]]:
        parametros = {"with_user_count": "true"} if incluir_entidade else None
        return await self.requisitar("GET", f"/guilds/{servidor_id}/scheduled-events", parametros=parametros)
    async def obter_evento_agendado(self, servidor_id: str, evento_id: str, *, incluir_entidade: bool = False) -> dict[str, Any]:
        parametros = {"with_user_count": "true"} if incluir_entidade else None
        return await self.requisitar("GET", f"/guilds/{servidor_id}/scheduled-events/{evento_id}", parametros=parametros)
    async def criar_evento_agendado(self, servidor_id: str, **dados: Any) -> dict[str, Any]:
        return await self.requisitar("POST", f"/guilds/{servidor_id}/scheduled-events", json=dados, motivo=dados.pop("motivo", None))
    async def editar_evento_agendado(self, servidor_id: str, evento_id: str, **dados: Any) -> dict[str, Any]:
        return await self.requisitar("PATCH", f"/guilds/{servidor_id}/scheduled-events/{evento_id}", json=dados, motivo=dados.pop("motivo", None))
    async def excluir_evento_agendado(self, servidor_id: str, evento_id: str, *, motivo: str | None = None) -> None:
        await self.requisitar("DELETE", f"/guilds/{servidor_id}/scheduled-events/{evento_id}", motivo=motivo)
    async def listar_eventos_agendados_modelados(self, servidor_id: str, *, incluir_entidade: bool = False) -> list[Any]:
        from ..discord.recursos import EventoAgendado
        return [EventoAgendado.de_dict(item) for item in await self.listar_eventos_agendados(servidor_id, incluir_entidade=incluir_entidade)]
    async def obter_evento_agendado_modelado(self, servidor_id: str, evento_id: str, *, incluir_entidade: bool = False) -> Any:
        from ..discord.recursos import EventoAgendado
        return EventoAgendado.de_dict(await self.obter_evento_agendado(servidor_id, evento_id, incluir_entidade=incluir_entidade))
    async def listar_inscritos_evento(self, servidor_id: str, evento_id: str, *, limite: int = 100, antes_de: str | None = None, depois_de: str | None = None, incluir_membro: bool = False) -> list[dict[str, Any]]:
        if not 1 <= limite <= 100:
            raise ValueError("limite deve estar entre 1 e 100")
        if antes_de and depois_de:
            raise ValueError("antes_de e depois_de são mutuamente exclusivos")
        parametros: dict[str, Any] = {"limit": limite}
        if antes_de:
            parametros["before"] = antes_de
        if depois_de:
            parametros["after"] = depois_de
        if incluir_membro:
            parametros["with_member"] = "true"
        return await self.requisitar("GET", f"/guilds/{servidor_id}/scheduled-events/{evento_id}/users", parametros=parametros)
    async def listar_inscritos_excecao_evento(self, servidor_id: str, evento_id: str, excecao_id: str, *, limite: int = 100, antes_de: str | None = None, depois_de: str | None = None, incluir_membro: bool = False) -> list[dict[str, Any]]:
        """Lista inscritos de uma ocorrência/exceção de evento recorrente."""
        if not excecao_id:
            raise ValueError("excecao_id é obrigatório")
        if not 1 <= limite <= 100:
            raise ValueError("limite deve estar entre 1 e 100")
        if antes_de and depois_de:
            raise ValueError("antes_de e depois_de são mutuamente exclusivos")
        parametros: dict[str, Any] = {"limit": limite}
        if antes_de:
            parametros["before"] = antes_de
        if depois_de:
            parametros["after"] = depois_de
        if incluir_membro:
            parametros["with_member"] = "true"
        return await self.requisitar("GET", f"/guilds/{servidor_id}/scheduled-events/{evento_id}/{excecao_id}/users", parametros=parametros)

    async def criar_excecao_evento(self, servidor_id: str, evento_id: str, usuario_id: str | None = None, *, inicio_original: str | None = None, inicio: str | None = None, fim: str | None = None, cancelada: bool | None = None, **dados_legados: Any) -> dict[str, Any]:
        """Cria exceção pela rota oficial; aceita a assinatura antiga apenas como compatibilidade."""
        if usuario_id is not None:
            # Compatibilidade legada: a API oficial atual não usa usuário no POST.
            if not dados_legados:
                raise ValueError("dados da exceção legada são obrigatórios")
            return await self.requisitar("POST", f"/guilds/{servidor_id}/scheduled-events/{evento_id}/exceptions/{usuario_id}", json=dados_legados)
        if not inicio_original:
            raise ValueError("inicio_original é obrigatório")
        dados: dict[str, Any] = {"original_scheduled_start_time": inicio_original}
        if inicio is not None:
            dados["scheduled_start_time"] = inicio
        if fim is not None:
            dados["scheduled_end_time"] = fim
        if cancelada is not None:
            dados["is_canceled"] = bool(cancelada)
        return await self.requisitar("POST", f"/guilds/{servidor_id}/scheduled-events/{evento_id}/exceptions", json=dados)
    async def editar_excecao_evento(self, servidor_id: str, evento_id: str, usuario_id: str, **dados: Any) -> dict[str, Any]:
        """Edita a exceção de um usuário em um evento recorrente."""
        if not usuario_id or not dados:
            raise ValueError("usuario_id e ao menos um campo são obrigatórios")
        return await self.requisitar("PATCH", f"/guilds/{servidor_id}/scheduled-events/{evento_id}/exceptions/{usuario_id}", json=dados)
    async def excluir_excecao_evento(self, servidor_id: str, evento_id: str, usuario_id: str) -> None:
        """Exclui a exceção de um usuário em um evento recorrente."""
        if not usuario_id:
            raise ValueError("usuario_id é obrigatório")
        await self.requisitar("DELETE", f"/guilds/{servidor_id}/scheduled-events/{evento_id}/exceptions/{usuario_id}")
    async def listar_templates(self, servidor_id: str) -> list[dict[str, Any]]: return await self.requisitar("GET", f"/guilds/{servidor_id}/templates")
    async def obter_template(self, codigo: str) -> dict[str, Any]: return await self.requisitar("GET", f"/guilds/templates/{codigo}")
    async def criar_template(self, servidor_id: str, **dados: Any) -> dict[str, Any]: return await self.requisitar("POST", f"/guilds/{servidor_id}/templates", json=dados)
    async def editar_template(self, servidor_id: str, codigo: str, **dados: Any) -> dict[str, Any]: return await self.requisitar("PATCH", f"/guilds/{servidor_id}/templates/{codigo}", json=dados)
    async def excluir_template(self, servidor_id: str, codigo: str) -> None: await self.requisitar("DELETE", f"/guilds/{servidor_id}/templates/{codigo}")
    async def sincronizar_template(self, servidor_id: str, codigo: str) -> dict[str, Any]: return await self.requisitar("PUT", f"/guilds/{servidor_id}/templates/{codigo}")
    async def listar_sons_padrao(self) -> dict[str, Any]: return await self.requisitar("GET", "/soundboard-default-sounds")
    async def listar_sons_padrao_modelados(self) -> list[Any]:
        from ..discord.recursos import SomSoundboard
        payload = await self.listar_sons_padrao()
        itens = payload.get("items", payload.get("sounds", [])) if isinstance(payload, dict) else payload
        return [SomSoundboard.de_dict(item) for item in (itens or [])]
    async def listar_sons_servidor(self, servidor_id: str) -> list[dict[str, Any]]: return await self.requisitar("GET", f"/guilds/{servidor_id}/soundboard-sounds")
    async def listar_sons_servidor_modelados(self, servidor_id: str) -> list[Any]:
        from ..discord.recursos import SomSoundboard
        return [SomSoundboard.de_dict(item) for item in await self.listar_sons_servidor(servidor_id)]
    async def obter_som_servidor(self, servidor_id: str, som_id: str) -> dict[str, Any]: return await self.requisitar("GET", f"/guilds/{servidor_id}/soundboard-sounds/{som_id}")
    async def obter_som_servidor_modelado(self, servidor_id: str, som_id: str) -> Any:
        from ..discord.recursos import SomSoundboard
        return SomSoundboard.de_dict(await self.obter_som_servidor(servidor_id, som_id))
    async def enviar_som(self, canal_id: str, som_id: str, *, servidor_origem_id: str | None = None) -> None:
        dados = {"sound_id": str(som_id)}
        if servidor_origem_id is not None: dados["source_guild_id"] = str(servidor_origem_id)
        await self.requisitar("POST", f"/channels/{canal_id}/send-soundboard-sound", json=dados)
    async def criar_som_servidor(self, servidor_id: str, **dados: Any) -> dict[str, Any]: return await self.requisitar("POST", f"/guilds/{servidor_id}/soundboard-sounds", json=dados)
    async def editar_som_servidor(self, servidor_id: str, som_id: str, **dados: Any) -> dict[str, Any]: return await self.requisitar("PATCH", f"/guilds/{servidor_id}/soundboard-sounds/{som_id}", json=dados)
    async def excluir_som_servidor(self, servidor_id: str, som_id: str) -> None: await self.requisitar("DELETE", f"/guilds/{servidor_id}/soundboard-sounds/{som_id}")
    async def listar_servidores_usuario(self, *, limite: int = 100, antes_de: str | None = None, depois_de: str | None = None) -> list[dict[str, Any]]:
        if not 1 <= limite <= 200:
            raise ValueError("limite deve estar entre 1 e 200")
        if antes_de and depois_de:
            raise ValueError("antes_de e depois_de são mutuamente exclusivos")
        parametros = {"limit": limite}
        if antes_de:
            parametros["before"] = antes_de
        if depois_de:
            parametros["after"] = depois_de
        return await self.requisitar("GET", "/users/@me/guilds", parametros=parametros)
    async def sair_servidor(self, servidor_id: str) -> None: await self.requisitar("DELETE", f"/users/@me/guilds/{servidor_id}")
    async def adicionar_membro_oauth(self, servidor_id: str, usuario_id: str, token_acesso: str, *, dados: dict[str, Any] | None = None) -> dict[str, Any]: return await self.requisitar("PUT", f"/guilds/{servidor_id}/members/{usuario_id}", json={"access_token": token_acesso, **(dados or {})})
    async def obter_canais_voz(self, servidor_id: str) -> list[dict[str, Any]]: return [canal for canal in await self.listar_canais_servidor(servidor_id) if canal.get("type") in {2, 13}]
    async def gateway_publico(self) -> dict[str, Any]: return await self.requisitar("GET", "/gateway")
    async def listar_pacotes_sticker(self) -> list[dict[str, Any]]: return await self.requisitar("GET", "/sticker-packs")
    async def obter_pacote_sticker(self, pacote_id: str) -> dict[str, Any]: return await self.requisitar("GET", f"/sticker-packs/{pacote_id}")
    async def obter_instancia_atividade(self, aplicacao_id: str, instancia_id: str) -> dict[str, Any]: return await self.requisitar("GET", f"/applications/{aplicacao_id}/activity-instances/{instancia_id}")
    async def listar_entitlements_usuario(self, aplicacao_id: str, **parametros: Any) -> list[dict[str, Any]]: return await self.requisitar("GET", f"/users/@me/applications/{aplicacao_id}/entitlements", parametros=parametros)
    async def listar_contagens_inscritos_evento(self, servidor_id: str, evento_id: str, **parametros: Any) -> list[dict[str, Any]]: return await self.requisitar("GET", f"/guilds/{servidor_id}/scheduled-events/{evento_id}/users/counts", parametros=parametros)
    async def seguir_canal(self, canal_id: str, webhook_canal_id: str) -> dict[str, Any]: return await self.requisitar("POST", f"/channels/{canal_id}/followers", json={"webhook_channel_id": str(webhook_canal_id)})
    async def banir_membros_em_lote(self, servidor_id: str, usuarios: list[str], *, dias_mensagens: int = 0, motivo: str | None = None) -> dict[str, Any]:
        if not 1 <= len(usuarios) <= 200:
            raise ValueError("bulk-ban exige entre 1 e 200 usuários")
        if not 0 <= dias_mensagens <= 7:
            raise ValueError("dias_mensagens deve estar entre 0 e 7")
        return await self.requisitar("POST", f"/guilds/{servidor_id}/bulk-ban", json={"user_ids": [str(usuario) for usuario in usuarios], "delete_message_days": dias_mensagens}, motivo=motivo)
    async def alterar_status_voz(self, canal_id: str, *, status: str | None = None) -> None: await self.requisitar("PUT", f"/channels/{canal_id}/voice-status", json={"status": status})
def json_module_loads(texto: str) -> Any:

    return json.loads(texto)


__all__ = ["ClienteHTTP"]
