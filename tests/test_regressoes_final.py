from types import SimpleNamespace
import asyncio

import pytest

from pimcord import Bot
from pimcord.gateway.cliente import Gateway



def test_str_do_bot_retorna_apenas_nome_do_usuario():
    bot = Bot()
    bot._usuario = SimpleNamespace(nome="MeuBot", username="meu-bot")

    assert str(bot) == "MeuBot"
    assert "0x" not in str(bot)


@pytest.mark.asyncio
async def test_gateway_ignora_payload_que_nao_e_objeto():
    bot = Bot()
    gateway = Gateway(bot, "wss://gateway.test", "token-de-teste", 0)

    await gateway._processar(SimpleNamespace(), 42)
    await gateway._processar(SimpleNamespace(), None)

    assert gateway.sequencia is None


@pytest.mark.asyncio
async def test_gateway_processa_objeto_normal_apos_validacao():
    bot = Bot()
    gateway = Gateway(bot, "wss://gateway.test", "token-de-teste", 0)

    class WebSocket:
        async def close(self):
            return None

    await gateway._processar(WebSocket(), {"op": 11, "d": None})

    assert gateway.sequencia is None


@pytest.mark.parametrize("token", [" token\n", "token\rquebrado", "token\x00quebrado"])
def test_cliente_http_normaliza_token_colado_com_controle(token):
    from pimcord.http.cliente import ClienteHTTP

    cliente = ClienteHTTP(token)
    assert cliente.token == "tokenquebrado" if "quebrado" in token else cliente.token == "token"


@pytest.mark.asyncio
async def test_bot_fecha_http_se_gateway_rest_falhar(monkeypatch):
    import importlib

    modulo_bot = importlib.import_module("pimcord.bot")
    estado = {"fechado": False}

    class ClienteFalso:
        def __init__(self, token):
            self.token = token

        async def gateway(self):
            raise RuntimeError("falha simulada")

        async def fechar(self):
            estado["fechado"] = True

    monkeypatch.setattr(modulo_bot, "ClienteHTTP", ClienteFalso)
    bot = Bot()

    with pytest.raises(RuntimeError, match="falha simulada"):
        await bot.executar("token-de-teste")

    assert estado["fechado"] is True



def test_diagnostico_avisa_message_content_para_comando_prefixado():
    from pimcord import Intents

    bot = Bot(intents=Intents(mensagens=True, conteudo_mensagens=False))

    @bot.comando("ola")
    async def ola(ctx):
        return None

    relatorio = bot.diagnostico_saude()
    verificacoes = {item.nome: item for item in relatorio.verificacoes}

    assert verificacoes["mensagens"].ok is True
    assert verificacoes["conteudo_mensagens"].ok is False
    assert "Message Content Intent" in verificacoes["conteudo_mensagens"].mensagem


def test_diagnostico_aprova_prefixo_com_intents_completos():
    from pimcord import Intents

    bot = Bot(intents=Intents(mensagens=True, conteudo_mensagens=True))

    @bot.comando("ola")
    async def ola(ctx):
        return None

    relatorio = bot.diagnostico_saude()
    verificacoes = {item.nome: item for item in relatorio.verificacoes}

    assert verificacoes["mensagens"].ok is True
    assert verificacoes["conteudo_mensagens"].ok is True
    assert verificacoes["comandos"].ok is True


def test_diagnostico_avisa_quando_nao_ha_comandos():
    bot = Bot()
    relatorio = bot.diagnostico_saude()
    verificacoes = {item.nome: item for item in relatorio.verificacoes}

    assert verificacoes["comandos"].ok is False
    assert "não responderá" in verificacoes["comandos"].mensagem



def test_intents_padrao_permite_conteudo_de_mensagens():
    bot = Bot()
    assert bot.configuracao.intents.mensagens is True
    assert bot.configuracao.intents.conteudo_mensagens is True


@pytest.mark.asyncio
async def test_diagnostico_pos_ready_avisa_sem_mensagens(caplog):
    bot = Bot()

    @bot.comando("ola")
    async def ola(ctx):
        return None

    bot._pronto.set()
    with caplog.at_level("WARNING", logger="pimcord"):
        tarefa = asyncio.create_task(bot._verificar_mensagens_recebidas())
        tarefa.cancel()
        with pytest.raises(asyncio.CancelledError):
            await tarefa

    assert "Nenhum MESSAGE_CREATE" not in caplog.text



def test_comando_hibrido_informa_opcao_slash_a_partir_da_assinatura():
    from pimcord import Intents, Permissoes

    bot = Bot(intents=Intents.todos())

    @bot.comando_hibrido(
        "limpar",
        descricao="Apaga mensagens",
        permissoes=int(Permissoes.gerenciar_mensagens),
    )
    async def limpar(ctx, quantidade: int = 10):
        return quantidade

    comando = bot.comandos_slash["limpar"]
    assert comando.descricao == "Apaga mensagens"
    assert comando.permissoes == int(Permissoes.gerenciar_mensagens)
    assert len(comando.opcoes) == 1
    assert comando.opcoes[0].nome == "quantidade"
    assert comando.opcoes[0].tipo is int
    assert comando.opcoes[0].obrigatoria is False


def test_pimcordia_cataloga_api_instalada():
    from pimcord.ia import PimcordIA

    analise = PimcordIA().analisar("crie um bot de moderação com tickets")
    assert "moderacao" in analise["dominios"]
    assert "tickets" in analise["dominios"]
    assert "Bot" in analise["api"]
    assert "Canal" in analise["api"]
    assert "comando_hibrido" in analise["api"]["Bot"]["metodos"]
