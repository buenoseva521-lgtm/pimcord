import asyncio

from pimcord import Bot
from pimcord.gateway.cliente import Gateway


def test_estado_publico_e_ready():
    bot = Bot()
    assert bot.user is None
    assert bot.servidores == []
    assert bot.canais == []
    assert bot.latencia is None
    bot._aplicar_ready({
        "user": {"id": "42", "username": "Pimcord", "bot": True},
        "guilds": [{"id": "10", "name": "Teste", "owner_id": "42", "roles": []}],
    })
    assert bot.user is not None
    assert bot.user.nome == "Pimcord"
    assert bot.usuario.id == "42"
    assert bot.guilds[0].nome == "Teste"
    assert bot.is_ready


def test_cache_de_canais_e_diagnostico():
    bot = Bot()
    bot._aplicar_canal({"id": "99", "name": "geral", "type": 0, "guild_id": "10"})
    diagnostico = bot.diagnostico()
    assert bot.canais[0].nome == "geral"
    assert diagnostico["canais"] == 1
    assert diagnostico["servidores"] == 0
    assert diagnostico["estado_conexao"] == "desconectado"


def test_gateway_expoe_latencia_e_estado():
    bot = Bot()
    gateway = Gateway(bot, "wss://gateway.example", "token", 0)
    gateway._latencia = 0.123
    bot.gateway = gateway
    bot._definir_estado_conexao("pronto")
    assert bot.latencia == 0.123
    assert bot.latency == 0.123
    assert bot.conectado
    assert bot.ws is None


def test_aliases_de_lifecycle():
    bot = Bot()
    assert asyncio.iscoroutinefunction(bot.close)
    assert asyncio.iscoroutinefunction(bot.wait_until_ready)


def test_cache_lru_remove_o_item_menos_recente():
    from pimcord import Cache

    cache = Cache(limite=2)
    cache.definir("a", 1)
    cache.definir("b", 2)
    assert cache.obter("a") == 1
    cache.definir("c", 3)
    assert cache.obter("b") is None
    assert cache.obter("c") == 3
    assert cache.estatisticas()["evictados"] == 1


def test_cache_ttl_e_expurgo_manual():
    from pimcord import Cache

    cache = Cache()
    cache.definir("temporario", "valor", ttl=0)
    assert cache.obter("temporario") is None
    cache.definir("outro", "valor", ttl=60)
    assert cache.expurgar() == 0
    assert cache.estatisticas()["expirados"] == 1
