import pytest
import pimcord
from pimcord import Bot, Simulador, diagnosticar



@pytest.mark.asyncio
async def test_simulador_inicia_sem_rede_e_emite_mensagem():
    bot = Bot()
    recebido = []

    @bot.comando("eco")
    async def eco(ctx, texto: str):
        recebido.append(texto)

    simulador = Simulador(bot)
    await simulador.iniciar()
    await simulador.mensagem("!eco teste")
    assert recebido == ["teste"]
    assert simulador.conectado
    assert bot.user.nome == "Pimcord Simulado"


def test_diagnostico_portugues_sem_expor_token():
    bot = Bot()
    relatorio = diagnosticar(bot)
    dados = relatorio.para_dict()
    assert "token" in {item["nome"] for item in dados["verificacoes"]}
    assert all("token" not in str(item) or "SEU" not in str(item) for item in dados["verificacoes"])


@pytest.mark.asyncio
async def test_simulador_emite_evento_portugues():
    bot = Bot()
    eventos = []

    @bot.evento("mensagem")
    async def mensagem(evento):
        eventos.append(evento)

    simulador = bot.criar_simulador()
    await simulador.emitir("MESSAGE_CREATE", {"id": "1", "content": "oi", "author": {"id": "2", "username": "A"}})
    assert len(eventos) == 1


def test_bot_agendar_registra_tarefa_resiliente():
    bot = Bot()

    @bot.agendar("limpeza", 60)
    async def limpeza():
        return None

    assert "limpeza" in bot.agendador.tarefas
    assert bot.agendador.tarefas["limpeza"].intervalo == 60


@pytest.mark.asyncio
async def test_autocomplete_portugues_responde_escolhas():
    class ClienteFalso:
        def __init__(self):
            self.requisicoes = []

        async def requisitar(self, metodo, rota, **kwargs):
            self.requisicoes.append((metodo, rota, kwargs))
            return kwargs.get("json")

    cliente = ClienteFalso()
    bot = Bot()
    bot.http = cliente

    async def sugerir_cidades(interacao):
        return ["São Paulo", {"name": "Rio", "value": "rio"}]

    @bot.comando_slash("cidade")
    @pimcord.autocomplete(sugerir_cidades)
    async def cidade(interacao):
        return None

    await bot.receber_interacao({"id": "1", "token": "t", "type": 4, "data": {"name": "cidade"}})
    assert cliente.requisicoes[0][0:2] == ("POST", "/interactions/1/t/callback")
    assert cliente.requisicoes[0][2]["json"]["type"] == 8
    assert cliente.requisicoes[0][2]["json"]["data"]["choices"][0]["value"] == "São Paulo"
