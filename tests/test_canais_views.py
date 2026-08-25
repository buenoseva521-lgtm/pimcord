import pimcord


class ClienteFalso:
    def __init__(self):
        self.chamadas = []

    async def requisitar(self, metodo, rota, *, json=None):
        self.chamadas.append((metodo, rota, json))
        return {"id": "99", "name": json.get("name", "canal"), "type": json.get("type", 0)}


async def test_servidor_cria_canal_com_sobrescrita():
    cliente = ClienteFalso()
    servidor = pimcord.Servidor("1", "Teste", cliente)
    regra = pimcord.SobrescritaPermissao.cargo(
        "2",
        permitir=pimcord.Permissoes.ver_canal | pimcord.Permissoes.enviar_mensagens,
    )
    canal = await servidor.criar_canal("privado", sobrescritas=[regra])
    assert canal.id == "99"
    corpo = cliente.chamadas[0][2]
    assert corpo["type"] == 0
    assert corpo["permission_overwrites"][0]["allow"] == "3072"


async def test_view_e_persistente_e_rota_componentes():
    view = pimcord.View()
    acionado = []

    @view.botao("confirmar", texto="Confirmar")
    async def confirmar(interacao):
        acionado.append(interacao.custom_id)

    assert view.persistente is True
    bot = pimcord.Bot()
    bot.adicionar_view(view)
    await bot.receber_interacao({"id": "i", "token": "t", "type": 3, "data": {"custom_id": "confirmar"}})
    assert acionado == ["confirmar"]


async def test_view_upload_tipo_19_rota_callback():
    view = pimcord.View()
    acionado = []

    @view.upload("anexar", tipos_arquivo=["image/png"])
    async def anexar(interacao):
        acionado.append(interacao.custom_id)

    bot = pimcord.Bot()
    bot.adicionar_view(view)
    await bot.receber_interacao({"id": "i", "token": "t", "type": 19, "data": {"custom_id": "anexar", "resolved": {"attachments": {"a": {"id": "a"}}}}})
    assert acionado == ["anexar"]


async def test_canal_altera_permissoes():
    cliente = ClienteFalso()
    canal = pimcord.Canal("9", cliente, "privado", 0, "1")
    regra = pimcord.SobrescritaPermissao.usuario("7", negar=pimcord.Permissoes.enviar_mensagens)
    await canal.definir_permissoes(regra)
    assert cliente.chamadas[0][0:2] == ("PUT", "/channels/9/permissions/7")
    assert cliente.chamadas[0][2]["deny"] == str(2048)


class ClienteModeracao:
    def __init__(self):
        self.chamadas = []
        self.dados = [
            {"id": "10", "channel_id": "9", "content": "apagar", "author": {"id": "2", "username": "ana"}},
            {"id": "11", "channel_id": "9", "content": "manter", "author": {"id": "3", "username": "bia"}},
        ]

    async def buscar_mensagens(self, canal_id, **kwargs):
        self.chamadas.append(("GET", canal_id, kwargs))
        return self.dados

    async def apagar_mensagens(self, canal_id, ids):
        self.chamadas.append(("PURGE", canal_id, ids))

    async def requisitar(self, metodo, rota, *, json=None):
        self.chamadas.append((metodo, rota, json))
        return None


async def test_mensagem_delete_e_alias_do_excluir():
    cliente = ClienteModeracao()
    mensagem = pimcord.Mensagem.de_gateway({"id": "10", "channel_id": "9", "content": "x", "author": {"id": "2", "username": "ana"}}, cliente)
    await mensagem.delete()
    assert cliente.chamadas[-1][0:2] == ("DELETE", "/channels/9/messages/10")


async def test_purge_filtra_e_apaga_apenas_as_mensagens_selecionadas():
    cliente = ClienteModeracao()
    canal = pimcord.Canal("9", cliente, "geral", 0, "1")
    removidas = await canal.purge(check=lambda mensagem: mensagem.conteudo == "apagar")
    assert [mensagem.id for mensagem in removidas] == ["10"]
    assert cliente.chamadas[-1] == ("PURGE", "9", ["10"])


async def test_mensagem_deletar_e_alias_em_portugues():
    cliente = ClienteModeracao()
    mensagem = pimcord.Mensagem.de_gateway({"id": "12", "channel_id": "9", "content": "x", "author": {"id": "2", "username": "ana"}}, cliente)
    await mensagem.deletar()
    assert cliente.chamadas[-1][0:2] == ("DELETE", "/channels/9/messages/12")
