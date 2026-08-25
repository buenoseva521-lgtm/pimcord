import pytest
import pimcord
from pimcord.interacoes.modelos import Interacao


class ClienteInteracao:
    def __init__(self):
        self.chamadas = []

    async def requisitar(self, metodo, rota, *, json=None, **opcoes):
        self.chamadas.append((metodo, rota, json, opcoes))
        return {"ok": True}


async def test_intents_all_e_todos_ativam_o_conjunto_atual():
    assert pimcord.Intents.all() == pimcord.Intents.todos()
    assert pimcord.Intents.all().membros is True
    assert pimcord.Intents.all().conteudo_mensagens is True


async def test_evento_sem_parenteses_mapeia_ao_ligar():
    bot = pimcord.Bot()

    @bot.evento
    async def ao_ligar():
        return "ok"

    assert "pronto" in bot.eventos
    assert await bot.disparar("pronto") == ["ok"]


async def test_followup_ephemeral_edicao_e_exclusao():
    cliente = ClienteInteracao()
    interacao = pimcord.Interacao({"id": "1", "token": "tok", "application_id": "app", "type": 2, "data": {}}, cliente)
    await interacao.followup("privado", ephemeral=True)
    await interacao.editar_resposta("atualizado")
    await interacao.apagar_resposta()
    assert cliente.chamadas[0][2]["flags"] == 64
    assert cliente.chamadas[1][0:2] == ("PATCH", "/webhooks/app/tok/messages/@original")
    assert cliente.chamadas[2][0:2] == ("DELETE", "/webhooks/app/tok/messages/@original")


async def test_comando_hibrido_compartilha_callback_e_contexto():
    bot = pimcord.Bot()
    chamadas = []

    @bot.hibrido("perfil", descricao="Mostra o perfil")
    async def perfil(ctx):
        chamadas.append((type(ctx).__name__, ctx.interacao is not None))
        return "ok"

    assert bot.obter_comando("perfil").callback is perfil
    assert bot.comandos_slash["perfil"].hibrido is True
    assert bot.diagnostico()["comandos_hibridos"] == 1

    bot.http = ClienteInteracao()
    await bot.receber_interacao({
        "id": "2",
        "token": "tok",
        "application_id": "app",
        "type": 2,
        "data": {"name": "perfil", "options": []},
        "member": {"user": {"id": "42"}},
    })

    assert chamadas == [("Contexto", True)]


async def test_interacao_expoe_opcoes_view_e_adiamento():
    cliente = ClienteInteracao()
    view = pimcord.View()
    view.adicionar_item(pimcord.Botao("Confirmar", custom_id="confirmar"))
    interacao = pimcord.Interacao({
        "id": "3",
        "token": "tok",
        "application_id": "app",
        "type": 2,
        "data": {"name": "limpar", "options": [{"name": "quantidade", "value": 5}]},
        "member": {"user": {"id": "42"}},
    }, cliente)

    assert interacao.opcoes == {"quantidade": 5}
    await interacao.adiar(ephemeral=True)
    await interacao.responder("Pronto", view=view)
    assert cliente.chamadas[0][2]["type"] == 5
    assert cliente.chamadas[0][2]["data"]["flags"] == 64
    assert cliente.chamadas[1][2]["data"]["components"][0]["components"][0]["custom_id"] == "confirmar"


async def test_opcoes_slash_tipadas_e_schema_de_sincronizacao():
    bot = pimcord.Bot()
    bot.configuracao.application_id = "app"
    bot.http = ClienteInteracao()

    @bot.comando_slash(
        "buscar",
        descricao="Busca um item",
        opcoes=[pimcord.OpcaoSlash("limite", descricao="Quantidade", tipo=int, obrigatoria=True)],
    )
    async def buscar(interacao, limite: int):
        assert isinstance(limite, int)
        return limite

    await bot.sincronizar_comandos()
    payload = bot.http.chamadas[0][2][0]
    assert payload["options"][0]["type"] == 4
    assert payload["options"][0]["required"] is True

    recebido = []
    async def callback_teste(interacao, limite: int):
        recebido.append(limite)
    bot.comandos_slash["buscar"].callback = callback_teste
    await bot.receber_interacao({
        "id": "4",
        "token": "tok",
        "application_id": "app",
        "type": 2,
        "data": {"name": "buscar", "options": [{"name": "limite", "value": 7}]},
    })
    assert recebido == [7]


class ViewPersistenteDeTeste(pimcord.View):
    def __init__(self):
        super().__init__()
        self.adicionar_item(pimcord.Botao("Confirmar", custom_id="teste_confirmar"))


async def test_view_importavel_e_persistida_automaticamente(tmp_path):
    bot = pimcord.Bot()
    bot.arquivo_views_persistentes = tmp_path / "views.json"
    view = ViewPersistenteDeTeste()
    bot.registrar_view(view)
    assert view.persistente is True
    assert bot.arquivo_views_persistentes.exists()
    outro = pimcord.Bot()
    outro.arquivo_views_persistentes = bot.arquivo_views_persistentes
    outro._carregar_views_persistentes()
    assert any(type(item).__name__ == "ViewPersistenteDeTeste" for item in outro.views)


async def test_grupo_slash_serializa_e_executa_subcomando():
    bot = pimcord.Bot()
    recebido = []

    @bot.grupo("admin", descricao="Administração")
    async def admin(ctx):
        pass

    @admin.subcomando("banir", descricao="Bane uma pessoa")
    async def banir(ctx, usuario: str):
        recebido.append((ctx.interacao.subcomando, usuario))

    assert admin.para_dict()["type"] == 1
    assert admin.para_dict()["options"][0]["type"] == 1

    await bot.receber_interacao({
        "id": "1", "token": "t", "type": 2,
        "data": {"name": "admin", "options": [{"type": 1, "name": "banir", "options": [{"type": 3, "name": "usuario", "value": "42"}]}]},
        "member": {"user": {"id": "7"}},
    })
    assert recebido == [("banir", "42")]


async def test_subgrupo_slash_usa_tipo_oficial_aninhado():
    bot = pimcord.Bot()

    @bot.grupo("configurar")
    async def configurar(ctx):
        pass

    @configurar.subgrupo("servidor", descricao="Configura servidor")
    async def servidor(ctx):
        pass

    @servidor.subcomando("nomear", descricao="Altera o nome")
    async def nomear(ctx, nome: str):
        return nome

    schema = configurar.para_dict()
    assert schema["type"] == 1
    assert schema["options"][0]["type"] == 2
    assert schema["options"][0]["options"][0]["type"] == 1

@pytest.mark.asyncio
async def test_interacao_gerencia_followup_por_id():
    cliente = ClienteInteracao()
    interacao = Interacao({"id": "int", "token": "tok", "application_id": "app"}, cliente)
    await interacao.obter_followup("msg")
    await interacao.editar_followup("msg", "novo")
    await interacao.apagar_followup("msg")
    assert [c[0:2] for c in cliente.chamadas[-3:]] == [
        ("GET", "/webhooks/app/tok/messages/msg"),
        ("PATCH", "/webhooks/app/tok/messages/msg"),
        ("DELETE", "/webhooks/app/tok/messages/msg"),
    ]

@pytest.mark.asyncio
async def test_interacao_responder_e_followup_aceitam_anexo():
    cliente = ClienteInteracao()
    interacao = Interacao({"id": "int", "token": "tok", "application_id": "app"}, cliente)
    arquivo = [("files[0]", "x.txt", b"dados")]
    await interacao.responder("com arquivo", arquivos=arquivo)
    await interacao.followup("com arquivo", arquivos=arquivo)
    assert cliente.chamadas[-2][3]["arquivos"] == arquivo
    assert cliente.chamadas[-1][3]["arquivos"] == arquivo
