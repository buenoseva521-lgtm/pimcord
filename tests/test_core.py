import pytest
import pimcord

@pytest.mark.asyncio
async def test_comando_e_alias():
    bot = pimcord.Bot(prefixo="!")
    recebido = []
    @bot.comando("ola", aliases=["oi"])
    async def ola(ctx, nome="mundo"):
        recebido.append(nome)
    await bot.processar_comando("!oi Ana")
    assert recebido == ["Ana"]

@pytest.mark.asyncio
async def test_evento():
    bot = pimcord.Bot(); estado = []
    @bot.evento("pronto")
    async def pronto(): estado.append(True)
    await bot.disparar("pronto")
    assert estado == [True]

def test_embed_e_permissoes():
    e = pimcord.Embed(titulo="Teste").adicionar_campo("A", "B")
    assert e.para_dict()["fields"][0]["name"] == "A"
    assert pimcord.Permissoes.administrador | pimcord.Permissoes.enviar_mensagens

def test_banco():
    db = pimcord.BancoSQLite().conectar()
    db.executar("CREATE TABLE itens (nome TEXT)")
    db.executar("INSERT INTO itens VALUES (?)", ["x"]); db.commit()
    assert db.buscar("SELECT nome FROM itens")[0]["nome"] == "x"
    db.fechar()


@pytest.mark.asyncio
async def test_argumentos_tipados():
    bot = pimcord.Bot(prefixo="!")

    @bot.comando("somar")
    async def somar(ctx, primeiro: int, segundo: int):
        return primeiro + segundo

    assert await bot.processar_comando("!somar 2 3") == 5


@pytest.mark.asyncio
async def test_cooldown_e_check():
    bot = pimcord.Bot(prefixo="!")

    @pimcord.verificar(lambda ctx: True)
    @pimcord.limitar(1, 60)
    @bot.comando("limitado")
    async def limitado(ctx):
        return "ok"

    assert await bot.processar_comando("!limitado") == "ok"
    with pytest.raises(pimcord.ComandoInvalido):
        await bot.processar_comando("!limitado")


def test_modelos_e_componentes_publicos():
    usuario = pimcord.Usuario.de_dict({"id": "1", "username": "ana"})
    assert usuario.mencao == "<@1>"
    view = pimcord.View()
    select = pimcord.Select("menu").adicionar_opcao("Sim", "sim")
    view.adicionar_item(select)
    modal = pimcord.Modal("Dados", "dados").adicionar_entrada(pimcord.EntradaModal("nome", "Nome"))
    assert view.para_componentes()[0]["components"][0]["type"] == 3
    assert modal.para_dict()["custom_id"] == "dados"


def test_shard_calcula_servidor():
    gerenciador = pimcord.GerenciadorDeShards(4)
    assert gerenciador.shard_de_servidor(str(123 << 22)).id == 123 % 4


def test_upload_arquivos_serializa_file_types_e_view_persistente():
    upload = pimcord.UploadArquivos("anexo", minimo=1, maximo=3, tipos_arquivo=["image/png", "application/pdf"])
    view = pimcord.View().adicionar_item(upload)
    componente = view.para_componentes()[0]["components"][0]
    assert componente == {
        "type": 19,
        "custom_id": "anexo",
        "min_values": 1,
        "max_values": 3,
        "required": True,
        "file_types": ["image/png", "application/pdf"],
    }
    assert view.persistente is True


def test_upload_arquivos_rejeita_limites_invalidos():
    with pytest.raises(ValueError, match="minimo/maximo"):
        pimcord.UploadArquivos("anexo", minimo=4, maximo=2)


def test_view_upload_decorator_registra_callback():
    view = pimcord.View()

    @view.upload("documento", tipos_arquivo=["application/pdf"], maximo=2)
    async def receber_upload(interacao):
        return interacao

    assert view.uploads[0].callback is receber_upload
    assert view.para_componentes()[0]["components"][0]["file_types"] == ["application/pdf"]
