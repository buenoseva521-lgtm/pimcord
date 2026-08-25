import json

import pytest

import pimcord


class _Mensagem:
    def __init__(self, content):
        self.content = content


class _Escolha:
    def __init__(self, content):
        self.message = _Mensagem(content)


class _Resposta:
    def __init__(self, content):
        self.choices = [_Escolha(content)]


class _Completions:
    def __init__(self, content):
        self.content = content
        self.calls = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        return _Resposta(self.content)


class _Cliente:
    def __init__(self, content):
        self.chat = type("Chat", (), {"completions": _Completions(content)})()


def plano():
    return {
        "prefixo": "!",
        "intents": "basicos",
        "comandos": [{"nome": "ola", "resposta": "Olá!", "aliases": ["oi"]}],
    }


def test_gerador_usa_json_estrito_e_nao_recebe_token():
    cliente = _Cliente(json.dumps(plano()))
    gerador = pimcord.GeradorPlanoIA(cliente)
    resultado = gerador.gerar_plano("Faça um bot de saudação")
    assert resultado == plano()
    chamada = cliente.chat.completions.calls[0]
    assert chamada["response_format"]["json_schema"]["strict"] is True
    assert "token" not in chamada["messages"][1]["content"].casefold()


def test_gerador_rejeita_campo_extra():
    dado = plano()
    dado["executar_python"] = "rm -rf /"
    with pytest.raises(pimcord.ErroGeradorIA):
        pimcord.validar_plano(dado)


def test_bot_pronto_com_gerador_constroi_comando_hibrido():
    cliente = _Cliente(json.dumps(plano()))
    gerador = pimcord.GeradorPlanoIA(cliente)
    bot = pimcord.bot_pronto("bot de saudação", gerador=gerador, iniciar=False)
    assert bot.comando_prefixo == "!"
    assert bot.obter_comando("ola") is not None
    assert "ola" in bot.comandos_slash
    assert "oi" in bot.comandos


def test_fallback_local_continua_funcionando():
    bot = pimcord.bot_pronto("""
    Prefixo: ?
    Comando: ola
    Resposta: Oi local!
    """, iniciar=False)
    assert bot.comando_prefixo == "?"
    assert bot.obter_comando("ola") is not None


def test_bot_pronto_prompt_livre_sem_checkpoint_falha_explicitamente():
    with pytest.raises(pimcord.ErroGeradorIA, match="checkpoint neural"):
        pimcord.bot_pronto("crie um bot de economia completo", iniciar=False)


@pytest.mark.asyncio
async def test_rodar_com_token_explicito_nao_solicita_terminal(monkeypatch):
    import importlib

    modulo_bot = importlib.import_module("pimcord.bot")
    bot = pimcord.Bot()
    recebido = []

    async def executar(token=None):
        recebido.append(token)

    def falhar_se_solicitar(_):
        raise AssertionError("não deveria solicitar token quando ele foi informado")

    monkeypatch.setattr(modulo_bot, "getpass", falhar_se_solicitar)
    monkeypatch.setattr(bot, "executar", executar)

    tarefa = bot.rodar("MEU_TOKEN_REAL_AQUI")
    await tarefa

    assert recebido == ["MEU_TOKEN_REAL_AQUI"]


@pytest.mark.asyncio
async def test_rodar_normaliza_token_antes_do_gateway(monkeypatch):
    bot = pimcord.Bot()
    recebido = []

    async def executar(token=None):
        recebido.append(token)

    monkeypatch.setattr(bot, "executar", executar)
    tarefa = bot.rodar(" toke" + chr(10) + "\t n ")
    await tarefa

    assert recebido == ["token"]


@pytest.mark.asyncio
async def test_iniciar_nao_aninha_asyncio_run(monkeypatch):
    bot = pimcord.Bot()
    executado = []

    async def executar(token=None):
        executado.append(token)

    monkeypatch.setattr(bot, "executar", executar)
    tarefa = bot.iniciar("token-de-teste")
    await tarefa

    assert executado == ["token-de-teste"]


@pytest.mark.asyncio
async def test_rodar_vazio_solicita_token(monkeypatch):
    import importlib

    modulo_bot = importlib.import_module("pimcord.bot")
    bot = pimcord.Bot()
    recebido = []

    async def executar(token=None):
        recebido.append(token)

    monkeypatch.setattr(modulo_bot, "getpass", lambda _: "token-do-terminal")
    monkeypatch.setattr(bot, "executar", executar)

    tarefa = bot.rodar("")
    await tarefa

    assert recebido == ["token-do-terminal"]


@pytest.mark.asyncio
async def test_bot_pronto_rodar_reutiliza_token_armazenado(monkeypatch):
    bot = pimcord.bot_pronto(
        "prefixo: !\ncomando: saudacao\nresposta: Oi",
        iniciar=False,
        token="token-armazenado",
    )
    recebido = []

    async def executar(token=None):
        recebido.append(token)

    monkeypatch.setattr(bot, "executar", executar)
    tarefa = bot.rodar()
    await tarefa

    assert recebido == ["token-armazenado"]


def test_pimcordia_propria_analisa_projeto_completo():
    ia = pimcord.PimcordIA()
    analise = ia.analisar("crie um bot profissional completo de economia, moderação e tickets")

    assert analise["completo"] is True
    assert {"economia", "moderacao", "tickets"}.issubset(analise["dominios"])
    assert analise["comandos_hibridos"] is True
    assert "saldo" in analise["comandos_catalogados"]
    assert "banir" in analise["comandos_catalogados"]
