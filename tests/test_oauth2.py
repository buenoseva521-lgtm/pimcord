import pytest

from pimcord.oauth2 import (
    ClienteOAuth2,
    URL_AUTORIZACAO,
    URL_REVOGACAO,
    URL_TOKEN,
)


@pytest.mark.asyncio
async def test_oauth2_constroi_url_e_troca_codigo_sem_rede():
    chamadas = []

    async def transporte(url, dados):
        chamadas.append((url, dados))
        return {"access_token": "abc", "token_type": "Bearer", "expires_in": 3600, "scope": "identify bot"}

    cliente = ClienteOAuth2("123", "segredo", transportador=transporte)
    url = cliente.url_autorizacao(redirecionamento="https://app.test/callback", escopos=["identify", "bot"], estado="xyz", permissao=8)
    assert url.startswith(URL_AUTORIZACAO + "?")
    assert "client_id=123" in url
    assert "scope=identify+bot" in url
    token = await cliente.trocar_codigo("codigo", redirecionamento="https://app.test/callback")
    assert token.acesso == "abc"
    assert chamadas == [
        (URL_TOKEN, {
            "grant_type": "authorization_code",
            "code": "codigo",
            "redirect_uri": "https://app.test/callback",
            "client_id": "123",
            "client_secret": "segredo",
        })
    ]


@pytest.mark.asyncio
async def test_oauth2_renova_e_revoga_com_formulario():
    chamadas = []

    async def transporte(url, dados):
        chamadas.append((url, dados))
        return {} if url == URL_REVOGACAO else {"access_token": "novo", "token_type": "Bearer", "expires_in": 60}

    cliente = ClienteOAuth2("123", transportador=transporte)
    token = await cliente.renovar("refresh", escopo="identify")
    await cliente.revogar(token.acesso)
    assert token.renovacao is None
    assert chamadas == [
        (URL_TOKEN, {"grant_type": "refresh_token", "refresh_token": "refresh", "scope": "identify"}),
        (URL_REVOGACAO, {"token": "novo", "token_type_hint": "access_token"}),
    ]


def test_oauth2_serializa_formulario_urlencoded():
    cliente = ClienteOAuth2("123", "segredo")
    corpo = cliente.codificar_formulario(cliente.formulario_codigo("código", redirecionamento="https://app.test/callback"))
    assert "grant_type=authorization_code" in corpo
    assert "redirect_uri=https%3A%2F%2Fapp.test%2Fcallback" in corpo
    assert "code=c%C3%B3digo" in corpo
    assert "client_secret=segredo" in corpo


def test_oauth2_exige_transportador_e_dados_obrigatorios():
    cliente = ClienteOAuth2("123")
    with pytest.raises(ValueError):
        cliente.url_autorizacao(redirecionamento="", escopos=["identify"])
    with pytest.raises(RuntimeError):
        import asyncio
        asyncio.run(cliente.trocar_codigo("codigo", redirecionamento="https://app.test/callback"))


def test_oauth2_url_inclui_parametros_de_instalacao_oficiais():
    cliente = ClienteOAuth2("123")
    url = cliente.url_autorizacao(
        redirecionamento="https://app.test/callback",
        escopos=["bot", "applications.commands"],
        prompt="consent",
        servidor_id="456",
        desabilitar_selecao_servidor=True,
        tipo_integracao=0,
    )
    assert "prompt=consent" in url
    assert "guild_id=456" in url
    assert "disable_guild_select=true" in url
    assert "integration_type=0" in url
    with pytest.raises(ValueError):
        cliente.url_autorizacao(redirecionamento="https://app.test/callback", escopos=["identify"], prompt="invalido")




@pytest.mark.asyncio
async def test_oauth2_cria_anexo_de_activity_com_bearer_e_multipart_injetavel():
    chamadas = []

    async def transportar_anexo(url, token, nome, arquivo, mime):
        chamadas.append((url, token, nome, arquivo, mime))
        return {"attachment": {"url": "https://cdn.discord.test/efemero.gif"}}

    cliente = ClienteOAuth2("123", transportador_anexo=transportar_anexo)
    resposta = await cliente.criar_anexo_atividade(
        "bearer-token", b"GIF89a", nome_arquivo="imagem.gif", tipo_mime="image/gif"
    )

    assert resposta["attachment"]["url"].startswith("https://cdn.discord.test/")
    assert chamadas == [
        (
            "https://discord.com/api/applications/123/attachment",
            "bearer-token",
            "imagem.gif",
            b"GIF89a",
            "image/gif",
        )
    ]

    with pytest.raises(ValueError):
        await cliente.criar_anexo_atividade("", b"x")
    with pytest.raises(ValueError):
        await cliente.criar_anexo_atividade("token", b"", nome_arquivo="x")
    with pytest.raises(ValueError):
        await cliente.criar_anexo_atividade("token", b"x", tipo_mime="imagem")
