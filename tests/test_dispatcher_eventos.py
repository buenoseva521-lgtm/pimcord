import pytest

from pimcord import Bot


@pytest.mark.asyncio
async def test_evento_pronto_sem_argumento_aceita_modelo():
    bot = Bot()
    recebido = []

    @bot.evento("pronto")
    async def pronto():
        recebido.append(True)

    await bot.disparar("pronto", object())

    assert recebido == [True]


@pytest.mark.asyncio
async def test_excecao_de_evento_nao_interrompe_outros_handlers():
    bot = Bot()
    recebido = []

    @bot.evento("pronto")
    async def falho():
        raise RuntimeError("erro de teste")

    @bot.evento("pronto")
    async def saudavel():
        recebido.append(True)

    await bot.disparar("pronto", object())

    assert recebido == [True]
    assert falho is not saudavel


@pytest.mark.asyncio
async def test_message_create_processa_comando_e_responde_no_canal():
    class HTTPFalso:
        def __init__(self):
            self.enviadas = []

        async def enviar_mensagem(self, canal_id, conteudo, **kwargs):
            self.enviadas.append((canal_id, conteudo, kwargs))
            return {"id": "resposta-1", "channel_id": canal_id, "content": conteudo}

    bot = Bot()
    bot.http = HTTPFalso()

    @bot.comando_hibrido("ping")
    async def ping(ctx):
        await ctx.responder("pong")

    await bot.receber_mensagem({
        "id": "mensagem-1",
        "channel_id": "canal-1",
        "guild_id": "servidor-1",
        "content": "!ping",
        "author": {"id": "usuario-1", "username": "Pessoa", "bot": False},
    })

    assert bot.http.enviadas == [("canal-1", "pong", {"embed": None, "embeds": None, "view": None, "arquivos": None})]
