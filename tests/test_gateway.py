import pytest

from pimcord import Bot
from pimcord.gateway.cliente import Gateway


def gateway_de_teste():
    bot = Bot()
    return bot, Gateway(bot, "wss://gateway.test", "token", 0)


def test_close_code_4007_limpa_sessao_para_novo_identify():
    bot, gateway = gateway_de_teste()
    gateway.sessao_id = "sessao"
    gateway.sequencia = 12
    gateway.url_resume = "wss://resume.test"

    gateway._tratar_close_code(4007)

    assert gateway.sessao_id is None
    assert gateway.sequencia is None
    assert gateway.url_resume is None
    assert gateway._parar is False


def test_close_code_4004_interrompe_e_marca_autenticacao():
    bot, gateway = gateway_de_teste()

    gateway._tratar_close_code(4004)

    assert gateway._parar is True
    assert bot.estado_conexao == "erro_autenticacao"


def test_close_code_4014_interrompe_e_marca_intents():
    bot, gateway = gateway_de_teste()

    gateway._tratar_close_code(4014)

    assert gateway._parar is True
    assert bot.estado_conexao == "erro_intents"


def test_close_code_4011_marca_sharding_necessario():
    bot, gateway = gateway_de_teste()

    gateway._tratar_close_code(4011)

    assert gateway._parar is True
    assert bot.estado_conexao == "sharding_necessario"


def test_gateway_descompacta_fluxo_zlib_stream():
    import json
    import zlib

    bot, gateway = gateway_de_teste()
    compressor = zlib.compressobj(wbits=zlib.MAX_WBITS)
    pacote = compressor.compress(json.dumps({"op": 10, "d": {"heartbeat_interval": 41250}}).encode())
    pacote += compressor.flush(zlib.Z_SYNC_FLUSH)

    assert gateway._descompactar(pacote).startswith('{"op": 10')


def test_gateway_descompacta_varios_quadros_no_mesmo_fluxo():
    import json
    import zlib

    bot, gateway = gateway_de_teste()
    compressor = zlib.compressobj(wbits=zlib.MAX_WBITS)
    primeiro = compressor.compress(json.dumps({"op": 1, "d": None}).encode()) + compressor.flush(zlib.Z_SYNC_FLUSH)
    segundo = compressor.compress(json.dumps({"op": 11, "d": None}).encode()) + compressor.flush(zlib.Z_SYNC_FLUSH)

    assert [json.loads(item)["op"] for item in gateway._descompactar_varios(primeiro)] == [1]
    assert [json.loads(item)["op"] for item in gateway._descompactar_varios(segundo)] == [11]


def test_gateway_descompacta_quadro_fragmentado_em_dois_pacotes():
    import json
    import zlib

    bot, gateway = gateway_de_teste()
    compressor = zlib.compressobj(wbits=zlib.MAX_WBITS)
    pacote = compressor.compress(json.dumps({"op": 0, "t": "READY", "d": {}}).encode())
    pacote += compressor.flush(zlib.Z_SYNC_FLUSH)
    meio = max(1, len(pacote) // 2)

    assert gateway._descompactar_varios(pacote[:meio]) == []
    mensagens = gateway._descompactar_varios(pacote[meio:])
    assert json.loads(mensagens[0])["t"] == "READY"


def test_gateway_invalid_session_nao_resumivel_limpa_estado():
    import asyncio

    bot, gateway = gateway_de_teste()
    gateway.sessao_id = "sessao"
    gateway.sequencia = 8
    gateway.url_resume = "wss://resume.test"

    asyncio.run(gateway._processar(None, {"op": 9, "d": False}))

    assert gateway.sessao_id is None
    assert gateway.sequencia is None
    assert gateway.url_resume is None


def test_gateway_hello_escolhe_resume_quando_sessao_e_sequencia_existirem():
    import asyncio

    class WebSocketFalso:
        def __init__(self):
            self.pacotes = []

        async def send_json(self, pacote):
            self.pacotes.append(pacote)

    bot, gateway = gateway_de_teste()
    gateway.sessao_id = "sessao"
    gateway.sequencia = 8
    gateway.url_resume = "wss://resume.test"
    ws = WebSocketFalso()

    asyncio.run(gateway._hello(ws, {"heartbeat_interval": 60000}))

    assert ws.pacotes[-1]["op"] == 6
    assert ws.pacotes[-1]["d"]["seq"] == 8


def test_guild_delete_invalida_servidor_e_canais_associados():
    import asyncio

    bot, gateway = gateway_de_teste()
    bot._aplicar_servidor({"id": "guild-1", "name": "Teste", "channels": []})
    bot._aplicar_canal({"id": "channel-1", "name": "geral", "type": 0, "guild_id": "guild-1"})
    assert bot.obter_servidor("guild-1") is not None
    assert bot.obter_canal("channel-1") is not None

    asyncio.run(gateway._evento("GUILD_DELETE", {"id": "guild-1"}))

    assert bot.obter_servidor("guild-1") is None
    assert bot.obter_canal("channel-1") is None
    assert bot.cache.obter("servidor:guild-1") is None
    assert bot.cache.obter("canal:channel-1") is None


@pytest.mark.asyncio
async def test_close_code_anormal_gera_falha_para_acionar_backoff():
    class WebSocketFechado:
        close_code = 1006

        def __aiter__(self):
            return self

        async def __anext__(self):
            raise StopAsyncIteration

    bot, gateway = gateway_de_teste()

    with pytest.raises(ConnectionError, match="1006"):
        await gateway._loop_ws(WebSocketFechado())

    assert gateway._parar is False


@pytest.mark.asyncio
async def test_ready_dispara_pronto_uma_vez_define_application_id_e_sincroniza():
    class HTTPFalso:
        def __init__(self):
            self.chamadas = []

        async def requisitar(self, metodo, rota, **kwargs):
            self.chamadas.append((metodo, rota, kwargs))
            return []

    bot, gateway = gateway_de_teste()
    bot.http = HTTPFalso()
    pronto = []

    @bot.evento("pronto")
    async def quando_pronto(_dados):
        pronto.append(True)

    @bot.comando_hibrido("ping")
    async def ping(ctx):
        await ctx.responder("pong")

    await gateway._evento("READY", {"user": {"id": "app-1", "username": "mugi bot"}, "guilds": []})

    assert bot.application_id == "app-1"
    assert pronto == [True]
    assert bot.http.chamadas[0][0:2] == ("PUT", "/applications/app-1/commands")
