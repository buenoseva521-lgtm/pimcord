"""Auxiliares OAuth2 do Pimcord.

A construção de URLs e formulários é totalmente offline. O transporte HTTP é
injetável para que aplicações e testes escolham sua própria sessão aiohttp,
sem acoplar o núcleo a uma chamada de rede durante importação ou documentação.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Awaitable, Callable, Mapping
from urllib.parse import urlencode


URL_AUTORIZACAO = "https://discord.com/oauth2/authorize"
URL_TOKEN = "https://discord.com/api/oauth2/token"
URL_REVOGACAO = "https://discord.com/api/oauth2/token/revoke"


@dataclass(frozen=True, slots=True)
class TokenOAuth2:
    """Resposta normalizada do endpoint de token OAuth2."""

    acesso: str
    tipo: str
    expiracao: int
    escopos: str = ""
    renovacao: str | None = None
    bruto: Mapping[str, Any] | None = None

    @classmethod
    def de_dict(cls, dados: Mapping[str, Any]) -> "TokenOAuth2":
        return cls(
            acesso=str(dados.get("access_token", "")),
            tipo=str(dados.get("token_type", "Bearer")),
            expiracao=int(dados.get("expires_in", 0)),
            escopos=str(dados.get("scope", "")),
            renovacao=dados.get("refresh_token"),
            bruto=dict(dados),
        )


TransportadorOAuth = Callable[..., Awaitable[Mapping[str, Any] | None]]
TransportadorAnexoAtividade = Callable[[str, str, str, bytes, str], Awaitable[Mapping[str, Any]]]


class ClienteOAuth2:
    """Constrói URLs e executa os três fluxos OAuth2 suportados pelo Discord.

    O parâmetro ``transportador`` recebe ``(url, dados_formulario)`` e deve
    devolver o JSON decodificado. Assim, a parte determinística permanece
    utilizável em Pydroid/Termux e a rede fica sob controle da aplicação.
    """

    def __init__(self, id_cliente: str, segredo_cliente: str | None = None, *, transportador: TransportadorOAuth | None = None, transportador_anexo: TransportadorAnexoAtividade | None = None) -> None:
        if not id_cliente:
            raise ValueError("id_cliente é obrigatório")
        self.id_cliente = id_cliente
        self.segredo_cliente = segredo_cliente
        self.transportador = transportador
        self.transportador_anexo = transportador_anexo

    def url_autorizacao(self, *, redirecionamento: str, escopos: list[str] | tuple[str, ...], estado: str | None = None, resposta: str = "code", permissao: int | None = None, prompt: str | None = None, servidor_id: str | None = None, desabilitar_selecao_servidor: bool | None = None, tipo_integracao: int | None = None) -> str:
        if not redirecionamento:
            raise ValueError("redirecionamento é obrigatório")
        if not escopos:
            raise ValueError("informe ao menos um escopo OAuth2")
        dados: dict[str, Any] = {
            "client_id": self.id_cliente,
            "redirect_uri": redirecionamento,
            "response_type": resposta,
            "scope": " ".join(escopos),
        }
        if estado is not None:
            dados["state"] = estado
        if permissao is not None:
            dados["permissions"] = str(permissao)
        if prompt is not None:
            if prompt not in {"none", "consent"}:
                raise ValueError("prompt OAuth2 deve ser 'none' ou 'consent'")
            dados["prompt"] = prompt
        if servidor_id is not None:
            dados["guild_id"] = str(servidor_id)
        if desabilitar_selecao_servidor is not None:
            dados["disable_guild_select"] = "true" if desabilitar_selecao_servidor else "false"
        if tipo_integracao is not None:
            dados["integration_type"] = str(tipo_integracao)
        return f"{URL_AUTORIZACAO}?{urlencode(dados)}"

    def formulario_codigo(self, codigo: str, *, redirecionamento: str, segredo: str | None = None) -> dict[str, str]:
        if not codigo or not redirecionamento:
            raise ValueError("codigo e redirecionamento são obrigatórios")
        return self._credenciais({"grant_type": "authorization_code", "code": codigo, "redirect_uri": redirecionamento}, segredo)

    def formulario_renovacao(self, token_renovacao: str, *, escopo: str | None = None, segredo: str | None = None) -> dict[str, str]:
        if not token_renovacao:
            raise ValueError("token de renovação é obrigatório")
        dados = {"grant_type": "refresh_token", "refresh_token": token_renovacao}
        if escopo:
            dados["scope"] = escopo
        return self._credenciais(dados, segredo)

    @staticmethod
    def codificar_formulario(dados: Mapping[str, str]) -> str:
        """Serializa o corpo conforme ``application/x-www-form-urlencoded``."""
        return urlencode(dict(dados))

    async def trocar_codigo(self, codigo: str, *, redirecionamento: str, segredo: str | None = None) -> TokenOAuth2:
        return await self._token(self.formulario_codigo(codigo, redirecionamento=redirecionamento, segredo=segredo))

    async def renovar(self, token_renovacao: str, *, escopo: str | None = None, segredo: str | None = None) -> TokenOAuth2:
        return await self._token(self.formulario_renovacao(token_renovacao, escopo=escopo, segredo=segredo))

    async def criar_anexo_atividade(self, token: str, arquivo: bytes, *, nome_arquivo: str = "arquivo", tipo_mime: str = "application/octet-stream") -> Mapping[str, Any]:
        """Cria uma URL CDN efêmera para uma Activity usando bearer OAuth2.

        O transporte é injetável para manter o núcleo offline e deve receber
        `(url, token, nome_arquivo, arquivo, tipo_mime)`, equivalente a um
        upload multipart com o campo `file`.
        """
        if not token:
            raise ValueError("token bearer é obrigatório")
        if not arquivo:
            raise ValueError("arquivo não pode ser vazio")
        if not nome_arquivo:
            raise ValueError("nome_arquivo é obrigatório")
        if not tipo_mime or "/" not in tipo_mime:
            raise ValueError("tipo_mime deve ser um MIME válido")
        if self.transportador_anexo is None:
            raise RuntimeError("nenhum transportador de anexo de Activity foi configurado")
        resposta = await self.transportador_anexo(
            f"https://discord.com/api/applications/{self.id_cliente}/attachment",
            token,
            nome_arquivo,
            bytes(arquivo),
            tipo_mime,
        )
        if not isinstance(resposta, Mapping):
            raise TypeError("endpoint de anexo de Activity não devolveu um mapa")
        return resposta

    async def revogar(self, token: str, *, tipo: str = "access_token", segredo: str | None = None) -> None:
        if not token:
            raise ValueError("token é obrigatório")
        dados = self._credenciais({"token": token, "token_type_hint": tipo}, segredo)
        resposta = await self._transportar(URL_REVOGACAO, dados)
        if resposta is not None and not isinstance(resposta, Mapping):
            raise TypeError("a revogação OAuth2 deve retornar um mapa ou None")

    def _credenciais(self, dados: dict[str, str], segredo: str | None) -> dict[str, str]:
        segredo_final = segredo if segredo is not None else self.segredo_cliente
        if segredo_final:
            dados["client_id"] = self.id_cliente
            dados["client_secret"] = segredo_final
        return dados

    async def _token(self, dados: dict[str, str]) -> TokenOAuth2:
        resposta = await self._transportar(URL_TOKEN, dados)
        if not isinstance(resposta, Mapping):
            raise TypeError("endpoint OAuth2 não devolveu um mapa de token")
        token = TokenOAuth2.de_dict(resposta)
        if not token.acesso:
            raise ValueError("resposta OAuth2 sem access_token")
        return token

    async def _transportar(self, url: str, dados: dict[str, str]) -> Mapping[str, Any] | None:
        if self.transportador is None:
            raise RuntimeError("nenhum transportador OAuth2 foi configurado")
        return await self.transportador(url, dados)


__all__ = ["URL_AUTORIZACAO", "URL_TOKEN", "URL_REVOGACAO", "TokenOAuth2", "ClienteOAuth2", "TransportadorAnexoAtividade"]
