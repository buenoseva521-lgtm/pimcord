import pytest

from pimcord.http.cliente import ClienteHTTP


class ClienteFalso(ClienteHTTP):
    def __init__(self):
        super().__init__("token-de-teste")
        self.chamadas = []

    async def requisitar(self, metodo, rota, **kwargs):
        self.chamadas.append((metodo, rota, kwargs))
        if rota == "/guilds/10/stickers":
            return []
        if rota == "/stickers/20":
            return {"id": "20"}
        if rota == "/guilds/10/scheduled-events":
            return [{"id": "20", "name": "Reunião", "guild_id": "10"}]
        if rota == "/guilds/10/bans":
            return [{"user": {"id": "30", "username": "Banido"}, "reason": "teste"}]
        if rota == "/guilds/10/integrations":
            return [{"id": "40", "name": "Integração", "type": "twitch", "guild_id": "10", "enabled": True}]
        if rota == "/voice/regions":
            return [{"id": "brazil", "name": "Brazil", "vip": False, "optimal": True, "deprecated": False}]
        if rota == "/soundboard-default-sounds":
            return {"items": [{"sound_id": "51", "name": "Padrão", "volume": 1.0, "emoji_name": "?"}]}
        if rota == "/users/@me/connections":
            return [{"id": "github-1", "name": "conta", "type": "github", "verified": True, "friend_sync": True, "show_activity": False, "visibility": 1}]
        if rota == "/users/@me/applications/app/role-connection":
            return {"platform_name": "Pimcord", "platform_username": "usuario", "metadata": {"nivel": "3"}}
        if rota == "/applications/app/role-connections/metadata":
            return [{"type": 3, "name": "Nível", "description": "Nível do usuário", "key": "nivel", "value_type": 3}]
        if rota == "/applications/app/entitlements/ent-1":
            return {"id": "ent-1", "sku_id": "sku-1", "application_id": "app", "owner_id": "user-1", "owner_type": 2}
        if rota == "/applications/app/entitlements":
            return {"id": "ent-2", "sku_id": "sku-1", "application_id": "app", "owner_id": "user-1", "owner_type": 2}
        if rota == "/guilds/10/soundboard-sounds":
            return [{"sound_id": "50", "name": "Alerta", "volume": 0.8, "emoji_name": "!"}]
        if rota == "/guilds/10/soundboard-sounds/50":
            return {"sound_id": "50", "name": "Alerta", "volume": 0.8, "emoji_name": "!"}
        if rota == "/guilds/10/scheduled-events/20":
            return {"id": "20", "name": "Reunião", "guild_id": "10"}
        if rota == "/guilds/10/audit-logs":
            return {
                "audit_log_entries": [{
                    "id": "90", "action_type": 10, "target_type": 1,
                    "target_id": "30", "user_id": "40",
                    "changes": [{"key": "name", "old_value": "antes", "new_value": "depois"}],
                    "options": {"channel_id": "50", "count": "2"},
                }],
                "users": [{"id": "40", "username": "Moderador"}],
                "integrations": [],
            }
        return kwargs.get("json", {"rota": rota})


@pytest.mark.asyncio
async def test_conexoes_usuario_modeladas():
    cliente = ClienteFalso()
    conexoes = await cliente.listar_conexoes_usuario_modeladas()
    cargo = await cliente.obter_conexao_cargo_usuario_modelada("app")
    atualizada = await cliente.atualizar_conexao_cargo_usuario_modelada({"platform_name": "Pimcord"}, "app")
    from pimcord.discord.recursos import ConexaoUsuario
    assert isinstance(conexoes[0], ConexaoUsuario)
    assert conexoes[0].id == "github-1"
    assert conexoes[0].verificada is True
    assert isinstance(cargo, ConexaoUsuario)
    assert isinstance(atualizada, ConexaoUsuario)
    assert cargo.bruto["platform_name"] == "Pimcord"
    metadados = await cliente.obter_metadados_conexoes_cargo_modelados("app")
    substituidos = await cliente.substituir_metadados_conexoes_cargo_modelados([{"type": 3, "name": "Nível"}], "app")
    from pimcord.discord.recursos import MetadadoConexao
    assert isinstance(metadados[0], MetadadoConexao)
    assert isinstance(substituidos[0], MetadadoConexao)
    assert metadados[0].chave == "nivel"


@pytest.mark.asyncio
async def test_paginar_preserva_filtros_e_interrompe_cursor_repetido():
    cliente = ClienteFalso()
    paginas = [
        [{"id": "3"}, {"id": "2"}],
        [{"id": "2"}],
    ]

    async def requisitar_paginado(metodo, rota, **kwargs):
        cliente.chamadas.append((metodo, rota, kwargs))
        return paginas.pop(0)

    cliente.requisitar = requisitar_paginado
    itens = [item async for item in cliente.paginar("GET", "/rota", limite=10, parametros={"tipo": "x"})]
    assert [item["id"] for item in itens] == ["3", "2", "2"]
    assert cliente.chamadas[0][2]["parametros"] == {"tipo": "x", "limit": 10}
    assert cliente.chamadas[1][2]["parametros"] == {"tipo": "x", "limit": 8, "before": "2"}


@pytest.mark.asyncio
async def test_prune_rejeita_dias_fora_do_intervalo_oficial():
    cliente = ClienteFalso()
    with pytest.raises(ValueError):
        await cliente.contar_poda("10", dias=0)
    with pytest.raises(ValueError):
        await cliente.podar_membros("10", dias=31)
    assert cliente.chamadas == []


@pytest.mark.asyncio
async def test_auditoria_modelada_filtra_e_valida_limite():
    cliente = ClienteFalso()
    registro = await cliente.obter_auditoria_modelada("10", usuario_id="40", acao=10, antes_de="100", limite=25)
    entradas = await cliente.listar_registros_auditoria("10", limite=1)
    assert registro.entradas[0].usuario_id == "40"
    assert registro.entradas[0].alteracoes[0].depois == "depois"
    assert entradas[0].opcoes.canal_id == "50"
    chamada = cliente.chamadas[0]
    assert chamada[0:2] == ("GET", "/guilds/10/audit-logs")
    assert chamada[2]["parametros"] == {"limit": 25, "user_id": "40", "action_type": 10, "before": "100"}
    with pytest.raises(ValueError):
        await cliente.obter_auditoria("10", limite=101)


@pytest.mark.asyncio
async def test_skus_assinaturas_e_comandos_por_servidor():
    cliente = ClienteFalso()
    await cliente.listar_skus("app")
    await cliente.obter_sku("app", "sku")
    await cliente.listar_assinaturas("app", user_id="42", status="active")
    await cliente.obter_assinatura("app", "sub")
    await cliente.cancelar_assinatura("app", "sub")
    await cliente.criar_comando_aplicacao("app", servidor_id="guild", name="teste")
    sku = await cliente.obter_sku_modelado("app", "sku")
    assinatura = await cliente.obter_assinatura_modelada("app", "sub")
    assert sku.id is None and assinatura.id is None
    assert [(metodo, rota) for metodo, rota, _ in cliente.chamadas] == [
        ("GET", "/applications/app/skus"),
        ("GET", "/applications/app/skus/sku"),
        ("GET", "/applications/app/subscriptions"),
        ("GET", "/applications/app/subscriptions/sub"),
        ("DELETE", "/applications/app/subscriptions/sub"),
        ("POST", "/applications/app/guilds/guild/commands"),
        ("GET", "/applications/app/skus/sku"),
        ("GET", "/applications/app/subscriptions/sub"),
    ]


@pytest.mark.asyncio
async def test_endpoints_rest_avancados_em_portugues():
    cliente = ClienteFalso()
    await cliente.obter_configuracao_widget("10")
    await cliente.editar_configuracao_widget("10", enabled=True, channel_id="30")
    await cliente.contar_poda("10", dias=14, incluir_cargos=True)
    await cliente.podar_membros("10", dias=14, calcular_contagem=True, incluir_cargos=True)
    await cliente.obter_url_personalizada("10")
    await cliente.obter_estado_voz("10")
    await cliente.obter_estado_voz("10", "20")
    await cliente.alterar_estado_voz("10", canal_id="30", suprimido=True, pedido_fala_em="2026-08-17T00:00:00Z")
    await cliente.alterar_estado_voz_usuario("10", "20", suprimido=False)
    await cliente.obter_onboarding("10")
    await cliente.editar_onboarding("10", enabled=True)
    await cliente.listar_sons_padrao()
    await cliente.obter_som_servidor("10", "20")
    await cliente.enviar_som("30", "20")
    await cliente.enviar_som("30", "20", servidor_origem_id="10")
    await cliente.obter_webhook_token("30", "segredo")
    await cliente.editar_webhook_token("30", "segredo", name="novo")
    await cliente.excluir_webhook_token("30", "segredo")
    await cliente.obter_metadados_conexoes_cargo()
    await cliente.substituir_metadados_conexoes_cargo([{"type": 2, "name": "nivel"}])
    with pytest.raises(ValueError):
        await cliente.criar_sticker("10", nome="", tags="emoji", arquivo=b"x")
    with pytest.raises(ValueError):
        await cliente.criar_sticker("10", nome="sticker", tags="", arquivo=b"x")
    await cliente.criar_sticker("10", nome="sticker", tags="emoji", arquivo=b"png", nome_arquivo="x.png")
    await cliente.editar_sticker("10", "20", name="novo")
    await cliente.excluir_sticker("10", "20", motivo="limpeza")
    adesivos = await cliente.listar_stickers_modelados("10")
    adesivo = await cliente.obter_sticker_modelado("20")
    assert adesivos == [] and adesivo.id == "20"
    assert [(metodo, rota) for metodo, rota, _ in cliente.chamadas] == [
        ("GET", "/guilds/10/widget"),
        ("PATCH", "/guilds/10/widget"),
        ("GET", "/guilds/10/prune"),
        ("POST", "/guilds/10/prune"),
        ("GET", "/guilds/10/vanity-url"),
        ("GET", "/guilds/10/voice-states/@me"),
        ("GET", "/guilds/10/voice-states/20"),
        ("PATCH", "/guilds/10/voice-states/@me"),
        ("PATCH", "/guilds/10/voice-states/20"),
        ("GET", "/guilds/10/onboarding"),
        ("PUT", "/guilds/10/onboarding"),
        ("GET", "/soundboard-default-sounds"),
        ("GET", "/guilds/10/soundboard-sounds/20"),
        ("POST", "/channels/30/send-soundboard-sound"),
        ("POST", "/channels/30/send-soundboard-sound"),
        ("GET", "/webhooks/30/segredo"),
        ("PATCH", "/webhooks/30/segredo"),
        ("DELETE", "/webhooks/30/segredo"),
        ("GET", "/applications/@me/role-connections/metadata"),
        ("PUT", "/applications/@me/role-connections/metadata"),
        ("POST", "/guilds/10/stickers"),
        ("PATCH", "/guilds/10/stickers/20"),
        ("DELETE", "/guilds/10/stickers/20"),
        ("GET", "/guilds/10/stickers"),
        ("GET", "/stickers/20"),
    ]


@pytest.mark.asyncio
async def test_permissoes_de_comando_por_servidor():
    cliente = ClienteFalso()
    existentes = await cliente.obter_permissoes_comando("app", "guild", "cmd")
    atualizadas = await cliente.substituir_permissoes_comando(
        "app", "guild", "cmd", [{"id": "role", "type": 1, "permission": True}]
    )

    assert existentes["rota"] == "/applications/app/guilds/guild/commands/cmd/permissions"
    assert atualizadas["permissions"][0]["permission"] is True
    assert [(metodo, rota) for metodo, rota, _ in cliente.chamadas] == [
        ("GET", "/applications/app/guilds/guild/commands/cmd/permissions"),
        ("PUT", "/applications/app/guilds/guild/commands/cmd/permissions"),
    ]
    assert cliente.chamadas[1][2]["json"] == {
        "permissions": [{"id": "role", "type": 1, "permission": True}]
    }


@pytest.mark.asyncio
async def test_conexoes_do_usuario_e_conexao_de_cargo():
    cliente = ClienteFalso()
    await cliente.listar_conexoes_usuario()
    await cliente.obter_conexao_cargo_usuario("app")
    resposta = await cliente.atualizar_conexao_cargo_usuario(
        {"platform_name": "Pimcord", "platform_username": "usuario", "metadata": {"nivel": "10"}},
        "app",
    )

    assert resposta["platform_name"] == "Pimcord"
    assert [(metodo, rota) for metodo, rota, _ in cliente.chamadas] == [
        ("GET", "/users/@me/connections"),
        ("GET", "/users/@me/applications/app/role-connection"),
        ("PUT", "/users/@me/applications/app/role-connection"),
    ]
    assert cliente.chamadas[-1][2]["json"]["metadata"]["nivel"] == "10"


@pytest.mark.asyncio
async def test_paginar_suporta_after_e_rejeita_cursores_conflitantes():
    cliente = ClienteFalso()
    chamadas = []

    async def requisitar_after(metodo, rota, **kwargs):
        chamadas.append(kwargs["parametros"])
        return [{"id": "20"}]

    cliente.requisitar = requisitar_after
    itens = [item async for item in cliente.paginar("GET", "/rota", limite=1, depois_de="19")]
    assert [item["id"] for item in itens] == ["20"]
    assert chamadas == [{"limit": 1, "after": "19"}]

    with pytest.raises(ValueError, match="antes_de ou depois_de"):
        _ = [item async for item in cliente.paginar("GET", "/rota", limite=1, antes_de="1", depois_de="2")]


@pytest.mark.asyncio
async def test_servidores_usuario_suporta_after_e_valida_limites():
    cliente = ClienteFalso()
    await cliente.listar_servidores_usuario(limite=50, depois_de="20")
    assert cliente.chamadas[-1][0:2] == ("GET", "/users/@me/guilds")
    assert cliente.chamadas[-1][2]["parametros"] == {"limit": 50, "after": "20"}

    await cliente.listar_servidores_usuario(limite=200, antes_de="40")
    assert cliente.chamadas[-1][2]["parametros"] == {"limit": 200, "before": "40"}

    with pytest.raises(ValueError, match="entre 1 e 200"):
        await cliente.listar_servidores_usuario(limite=0)
    with pytest.raises(ValueError, match="mutuamente exclusivos"):
        await cliente.listar_servidores_usuario(antes_de="1", depois_de="2")

    assert len(cliente.chamadas) == 2


@pytest.mark.asyncio
async def test_eventos_agendados_e_inscritos():
    cliente = ClienteFalso()
    await cliente.listar_eventos_agendados("10", incluir_entidade=True)
    await cliente.obter_evento_agendado("10", "20")
    await cliente.criar_evento_agendado("10", name="Reunião", entity_type=3)
    await cliente.editar_evento_agendado("10", "20", status=2)
    await cliente.excluir_evento_agendado("10", "20")
    await cliente.listar_inscritos_evento("10", "20", limite=25, depois_de="7", incluir_membro=True)

    assert [(metodo, rota) for metodo, rota, _ in cliente.chamadas[-6:]] == [
        ("GET", "/guilds/10/scheduled-events"),
        ("GET", "/guilds/10/scheduled-events/20"),
        ("POST", "/guilds/10/scheduled-events"),
        ("PATCH", "/guilds/10/scheduled-events/20"),
        ("DELETE", "/guilds/10/scheduled-events/20"),
        ("GET", "/guilds/10/scheduled-events/20/users"),
    ]
    assert cliente.chamadas[-1][2]["parametros"] == {"limit": 25, "after": "7", "with_member": "true"}

    with pytest.raises(ValueError):
        await cliente.listar_inscritos_evento("10", "20", limite=101)
    with pytest.raises(ValueError):
        await cliente.listar_inscritos_evento("10", "20", antes_de="1", depois_de="2")


@pytest.mark.asyncio
async def test_eventos_agendados_modelados():
    cliente = ClienteFalso()
    eventos = await cliente.listar_eventos_agendados_modelados("10")
    evento = await cliente.obter_evento_agendado_modelado("10", "20")
    from pimcord.discord.recursos import EventoAgendado
    assert isinstance(eventos[0], EventoAgendado)
    assert isinstance(evento, EventoAgendado)


@pytest.mark.asyncio
async def test_listar_membros_valida_limite_e_cursor():
    cliente = ClienteFalso()
    await cliente.listar_membros("10", limite=250, depois_de="99")
    chamada = cliente.chamadas[-1]
    assert chamada[1] == "/guilds/10/members"
    assert chamada[2]["parametros"] == {"limit": 250, "after": "99"}
    with pytest.raises(ValueError):
        await cliente.listar_membros("10", limite=0)
    with pytest.raises(ValueError):
        await cliente.listar_membros("10", limite=1001)


@pytest.mark.asyncio
async def test_listar_banimentos_valida_limite_e_cursores():
    cliente = ClienteFalso()
    await cliente.listar_banimentos("10", limite=20, antes_de="50")
    assert cliente.chamadas[-1][2]["parametros"] == {"limit": 20, "before": "50"}
    await cliente.listar_banimentos("10", limite=20, depois_de="40")
    assert cliente.chamadas[-1][2]["parametros"] == {"limit": 20, "after": "40"}
    with pytest.raises(ValueError):
        await cliente.listar_banimentos("10", limite=0)
    with pytest.raises(ValueError):
        await cliente.listar_banimentos("10", antes_de="50", depois_de="40")


@pytest.mark.asyncio
async def test_listar_banimentos_modelados():
    cliente = ClienteFalso()
    itens = await cliente.listar_banimentos_modelados("10", limite=2)
    from pimcord.discord.recursos import Banimento
    assert isinstance(itens[0], Banimento)


@pytest.mark.asyncio
async def test_listar_integracoes_modeladas():
    cliente = ClienteFalso()
    itens = await cliente.listar_integracoes_modeladas("10")
    from pimcord.discord.recursos import Integracao
    assert isinstance(itens[0], Integracao)
    assert itens[0].id == "40"


@pytest.mark.asyncio
async def test_obter_instancia_stage_modelada():
    cliente = ClienteFalso()
    itens = await cliente.obter_instancia_stage_modelada("20")
    from pimcord.discord.recursos import InstanciaStage
    assert isinstance(itens, InstanciaStage)


@pytest.mark.asyncio
async def test_listar_regioes_voz_modeladas():
    cliente = ClienteFalso()
    itens = await cliente.listar_regioes_voz_modeladas()
    from pimcord.discord.recursos import RegiaoVoz
    assert isinstance(itens[0], RegiaoVoz)


@pytest.mark.asyncio
async def test_soundboard_modelado():
    cliente = ClienteFalso()
    lista = await cliente.listar_sons_servidor_modelados("10")
    som = await cliente.obter_som_servidor_modelado("10", "50")
    from pimcord.discord.recursos import SomSoundboard
    assert isinstance(lista[0], SomSoundboard)
    assert isinstance(som, SomSoundboard)
    assert lista[0].id == "50"


@pytest.mark.asyncio
async def test_sons_padrao_modelados():
    cliente = ClienteFalso()
    itens = await cliente.listar_sons_padrao_modelados()
    from pimcord.discord.recursos import SomSoundboard
    assert isinstance(itens[0], SomSoundboard)
    assert itens[0].id == "51"


def test_registro_auditoria_modela_usuarios_e_integracoes_sem_perder_payload():
    from pimcord.discord.recursos import RegistroAuditoria

    registro = RegistroAuditoria.de_dict({
        "audit_log_entries": [],
        "users": [{"id": "7", "username": "moderador", "bot": True}],
        "integrations": [{"id": "9", "name": "Webhook", "type": "webhook"}],
    })
    assert registro.usuarios[0]["id"] == "7"
    assert registro.usuarios_modelados[0].id == "7"
    assert registro.usuarios_modelados[0].bot is True
    assert registro.integrações_modeladas[0].id == "9"
    assert registro.integrações_modeladas[0].tipo == "webhook"


@pytest.mark.asyncio
async def test_entitlements_individual_teste_e_modelado():
    cliente = ClienteFalso()
    individual = await cliente.obter_entitlement("app", "ent-1")
    modelado = await cliente.obter_entitlement_modelado("app", "ent-1")
    criado = await cliente.criar_entitlement_teste("app", sku_id="sku-1", owner_id="user-1", tipo_dono=2)
    criado_modelado = await cliente.criar_entitlement_teste_modelado("app", sku_id="sku-1", owner_id="user-1", tipo_dono=2)
    await cliente.excluir_entitlement_teste("app", "ent-2")
    assert individual["id"] == "ent-1"
    assert modelado.id == "ent-1"
    assert criado["id"] == "ent-2"
    assert criado_modelado.id == "ent-2"
    assert cliente.chamadas[2][2]["json"] == {"sku_id": "sku-1", "owner_id": "user-1", "owner_type": 2}
    assert [(metodo, rota) for metodo, rota, _ in cliente.chamadas] == [
        ("GET", "/applications/app/entitlements/ent-1"),
        ("GET", "/applications/app/entitlements/ent-1"),
        ("POST", "/applications/app/entitlements"),
        ("POST", "/applications/app/entitlements"),
        ("DELETE", "/applications/app/entitlements/ent-2"),
    ]


def test_registro_auditoria_modela_mapas_oficiais_referenciados():
    from pimcord.discord.recursos import CanalCompleto, EventoAgendado, RegraAutomoderacao, RegistroAuditoria, WebhookInfo

    registro = RegistroAuditoria.de_dict({
        "application_commands": [{"id": "cmd-1", "name": "banir"}],
        "auto_moderation_rules": [{"id": "rule-1", "name": "filtro", "enabled": True}],
        "guild_scheduled_events": [{"id": "event-1", "name": "Reunião"}],
        "threads": [{"id": "thread-1", "type": 11, "name": "incidente"}],
        "webhooks": [{"id": "hook-1", "name": "logs", "type": 1}],
    })
    assert registro.comandos_aplicacao[0]["name"] == "banir"
    assert isinstance(registro.regras_automoderacao_modeladas[0], RegraAutomoderacao)
    assert isinstance(registro.eventos_agendados_modelados[0], EventoAgendado)
    assert isinstance(registro.threads_modeladas[0], CanalCompleto)
    assert isinstance(registro.webhooks_modelados[0], WebhookInfo)
    assert registro.threads_modeladas[0].bruto["name"] == "incidente"


@pytest.mark.asyncio
async def test_listar_convites_de_canal_e_servidor():
    cliente = ClienteFalso()
    await cliente.listar_convites_canal("canal-1")
    await cliente.listar_convites_servidor("guild-1")
    assert [(metodo, rota) for metodo, rota, _ in cliente.chamadas[-2:]] == [
        ("GET", "/channels/canal-1/invites"),
        ("GET", "/guilds/guild-1/invites"),
    ]


@pytest.mark.asyncio
async def test_emojis_de_aplicacao():
    cliente = ClienteFalso()
    await cliente.listar_emojis_aplicacao("app")
    criado = await cliente.criar_emoji_aplicacao("app", nome="pimcord", imagem="data:image/png;base64,AAA")
    obtido = await cliente.obter_emoji_aplicacao("app", "emoji")
    editado = await cliente.editar_emoji_aplicacao("app", "emoji", nome="novo")
    await cliente.excluir_emoji_aplicacao("app", "emoji")
    assert criado["name"] == "pimcord"
    assert obtido["rota"] == "/applications/app/emojis/emoji"
    assert editado["name"] == "novo"
    with pytest.raises(ValueError):
        await cliente.criar_emoji_aplicacao("app", nome="", imagem="data:image/png;base64,AAA")
    with pytest.raises(ValueError):
        await cliente.criar_emoji_aplicacao("app", nome="x", imagem="")
    assert [(metodo, rota) for metodo, rota, _ in cliente.chamadas] == [
        ("GET", "/applications/app/emojis"),
        ("POST", "/applications/app/emojis"),
        ("GET", "/applications/app/emojis/emoji"),
        ("PATCH", "/applications/app/emojis/emoji"),
        ("DELETE", "/applications/app/emojis/emoji"),
    ]
    assert cliente.chamadas[1][2]["json"] == {"name": "pimcord", "image": "data:image/png;base64,AAA"}
    assert cliente.chamadas[3][2]["json"] == {"name": "novo"}


@pytest.mark.asyncio
async def test_listar_comandos_aplicacao_global_e_servidor():
    cliente = ClienteFalso()
    await cliente.listar_comandos_aplicacao("app")
    await cliente.listar_comandos_aplicacao("app", servidor_id="guild")
    await cliente.listar_comandos_servidor("app", "guild")
    assert [(metodo, rota) for metodo, rota, _ in cliente.chamadas] == [
        ("GET", "/applications/app/commands"),
        ("GET", "/applications/app/guilds/guild/commands"),
        ("GET", "/applications/app/guilds/guild/commands"),
    ]


@pytest.mark.asyncio
async def test_editar_e_excluir_comando_global():
    cliente = ClienteFalso()
    await cliente.editar_comando_aplicacao("app", "cmd", nome="novo")
    await cliente.excluir_comando_aplicacao("app", "cmd")
    assert cliente.chamadas[-2:] == [
        ("PATCH", "/applications/app/commands/cmd", {"json": {"nome": "novo"}}),
        ("DELETE", "/applications/app/commands/cmd", {}),
    ]


@pytest.mark.asyncio
async def test_criar_comando_global():
    cliente = ClienteFalso()
    await cliente.criar_comando_aplicacao("app", nome="ping", descricao="Responde", tipo=1)
    assert cliente.chamadas[-1] == (
        "POST",
        "/applications/app/commands",
        {"json": {"nome": "ping", "descricao": "Responde", "tipo": 1}},
    )

@pytest.mark.asyncio
async def test_execucao_webhook_valida_payload_e_threads():
    cliente = ClienteFalso()
    with pytest.raises(ValueError):
        await cliente.executar_webhook("hook", "tok")
    await cliente.executar_webhook("hook", "tok", conteudo="oi", esperar=True, id_thread="thread-1")
    metodo, rota, kwargs = cliente.chamadas[-1]
    assert (metodo, rota) == ("POST", "/webhooks/hook/tok")
    assert kwargs["json"] == {"content": "oi"}
    assert kwargs["parametros"] == {"wait": "true", "thread_id": "thread-1"}


def test_webhook_modela_origens_oficiais():
    from pimcord.discord.recursos import WebhookInfo
    webhook = WebhookInfo.de_dict({
        "id": "hook", "type": 2, "source_guild": {"id": "guild"},
        "source_channel": {"id": "channel"}, "application_id": "app",
    })
    assert webhook.servidor_origem == {"id": "guild"}
    assert webhook.canal_origem == {"id": "channel"}

@pytest.mark.asyncio
async def test_execucao_webhook_encaminha_multipart():
    cliente = ClienteFalso()
    await cliente.executar_webhook("hook", "tok", conteudo="arquivo", arquivos=[("files[0]", "x.txt", b"dados")])
    kwargs = cliente.chamadas[-1][2]
    assert kwargs["json"] == {"content": "arquivo"}
    assert kwargs["arquivos"] == [("files[0]", "x.txt", b"dados")]


def test_audit_log_modela_comandos_referenciados():
    from pimcord.discord.recursos import RegistroAuditoria
    registro = RegistroAuditoria.de_dict({
        "application_commands": [{"id": "123", "name": "ping", "type": 1}],
    })
    assert registro.comandos_aplicacao_modelados[0].id == "123"
    assert registro.comandos_aplicacao_modelados[0].nome == "ping"


def test_audit_log_preserva_mapas_brutos_e_modelados():
    from pimcord.discord.recursos import RegistroAuditoria
    dados = {
        "auto_moderation_rules": [{"id": "rule"}],
        "guild_scheduled_events": [{"id": "event"}],
        "threads": [{"id": "thread", "name": "debate"}],
        "webhooks": [{"id": "hook", "type": 1}],
    }
    registro = RegistroAuditoria.de_dict(dados)
    assert registro.regras_automoderacao == dados["auto_moderation_rules"]
    assert registro.eventos_agendados == dados["guild_scheduled_events"]
    assert registro.threads == dados["threads"]
    assert registro.webhooks == dados["webhooks"]
    assert registro.regras_automoderacao_modeladas[0].id == "rule"
    assert registro.eventos_agendados_modelados[0].id == "event"
    assert registro.threads_modeladas[0].id == "thread"
    assert registro.webhooks_modelados[0].id == "hook"


def test_requisitar_valida_motivo_de_auditoria():
    cliente = ClienteHTTP("token-de-teste")
    with pytest.raises(ValueError, match="512"):
        import asyncio
        asyncio.run(cliente.requisitar("DELETE", "/guilds/10", motivo="x" * 513))
    with pytest.raises(TypeError, match="texto"):
        asyncio.run(cliente.requisitar("DELETE", "/guilds/10", motivo=123))


def test_endpoints_de_introspeccao_oauth2():
    import asyncio
    cliente = ClienteFalso()
    asyncio.run(cliente.obter_oauth2_atual())
    asyncio.run(cliente.obter_aplicacao_oauth2_atual())
    asyncio.run(cliente.obter_chaves_oauth2())
    asyncio.run(cliente.obter_userinfo_oauth2())
    assert [rota for _, rota, _ in cliente.chamadas[-4:]] == [
        "/oauth2/@me",
        "/oauth2/applications/@me",
        "/oauth2/keys",
        "/oauth2/userinfo",
    ]


def test_editar_usuario_atual():
    import asyncio
    cliente = ClienteFalso()
    asyncio.run(cliente.editar_usuario_atual(nome="Pimcord", avatar=None))
    metodo, rota, kwargs = cliente.chamadas[-1]
    assert (metodo, rota) == ("PATCH", "/users/@me")
    assert kwargs["json"] == {"nome": "Pimcord", "avatar": None}


def test_editar_membro_atual():
    import asyncio
    cliente = ClienteFalso()
    asyncio.run(cliente.editar_membro_atual("guild-1", apelido="Pimcord", motivo="ajuste"))
    metodo, rota, kwargs = cliente.chamadas[-1]
    assert (metodo, rota) == ("PATCH", "/guilds/guild-1/members/@me")
    assert kwargs["json"] == {"apelido": "Pimcord"}
    assert kwargs["motivo"] == "ajuste"


def test_obter_cargo():
    import asyncio
    cliente = ClienteFalso()
    asyncio.run(cliente.obter_cargo("guild-1", "role-1"))
    metodo, rota, _ = cliente.chamadas[-1]
    assert (metodo, rota) == ("GET", "/guilds/guild-1/roles/role-1")


def test_listar_votantes_enquete():
    import asyncio
    cliente = ClienteFalso()
    asyncio.run(cliente.listar_votantes_enquete("canal-1", "mensagem-1", "resposta-2", limite=50, depois_de="usuario-1"))
    metodo, rota, kwargs = cliente.chamadas[-1]
    assert (metodo, rota) == ("GET", "/channels/canal-1/polls/mensagem-1/answers/resposta-2")
    assert kwargs["parametros"] == {"limit": 50, "after": "usuario-1"}
    with pytest.raises(ValueError):
        asyncio.run(cliente.listar_votantes_enquete("c", "m", "r", limite=101))


def test_obter_banimento():
    import asyncio
    cliente = ClienteFalso()
    asyncio.run(cliente.obter_banimento("guild-1", "user-9"))
    metodo, rota, _ = cliente.chamadas[-1]
    assert (metodo, rota) == ("GET", "/guilds/guild-1/bans/user-9")


def test_obter_emoji_servidor():
    import asyncio
    cliente = ClienteFalso()
    asyncio.run(cliente.obter_emoji("guild-1", "emoji-7"))
    metodo, rota, _ = cliente.chamadas[-1]
    assert (metodo, rota) == ("GET", "/guilds/guild-1/emojis/emoji-7")


def test_obter_membro_thread():
    import asyncio
    cliente = ClienteFalso()
    asyncio.run(cliente.obter_membro_thread("thread-1", "user-4"))
    metodo, rota, _ = cliente.chamadas[-1]
    assert (metodo, rota) == ("GET", "/channels/thread-1/thread-members/user-4")


def test_listar_usuarios_reacao():
    import asyncio
    cliente = ClienteFalso()
    asyncio.run(cliente.listar_usuarios_reacao("canal-1", "mensagem-2", "%F0%9F%91%8D", limite=40, depois_de="user-2"))
    metodo, rota, kwargs = cliente.chamadas[-1]
    assert (metodo, rota) == ("GET", "/channels/canal-1/messages/mensagem-2/reactions/%F0%9F%91%8D")
    assert kwargs["parametros"] == {"limit": 40, "after": "user-2"}


def test_buscar_membros():
    import asyncio
    cliente = ClienteFalso()
    asyncio.run(cliente.buscar_membros("guild-1", "luna", limite=25))
    metodo, rota, kwargs = cliente.chamadas[-1]
    assert (metodo, rota) == ("GET", "/guilds/guild-1/members/search")
    assert kwargs["parametros"] == {"query": "luna", "limit": 25}

def test_operacoes_de_mensagem_auxiliares():
    import asyncio
    cliente = ClienteFalso()
    asyncio.run(cliente.indicar_digitacao("canal-1"))
    asyncio.run(cliente.publicar_mensagem("canal-1", "msg-1"))
    asyncio.run(cliente.encerrar_enquete("canal-1", "msg-2"))
    assert [(metodo, rota) for metodo, rota, _ in cliente.chamadas[-3:]] == [
        ("POST", "/channels/canal-1/typing"),
        ("POST", "/channels/canal-1/messages/msg-1/crosspost"),
        ("POST", "/channels/canal-1/polls/msg-2/expire"),
    ]

def test_threads_privadas_busca_e_participacao_do_usuario():
    import asyncio
    cliente = ClienteFalso()
    asyncio.run(cliente.listar_threads_privadas_do_usuario("canal-1", antes_de="10"))
    asyncio.run(cliente.buscar_threads("canal-1", query="suporte", limite=20))
    asyncio.run(cliente.entrar_thread_como_eu("thread-1"))
    asyncio.run(cliente.sair_thread_como_eu("thread-1"))
    assert [(metodo, rota) for metodo, rota, _ in cliente.chamadas[-4:]] == [
        ("GET", "/channels/canal-1/users/@me/threads/archived/private"),
        ("GET", "/channels/canal-1/threads/search"),
        ("PUT", "/channels/thread-1/thread-members/@me"),
        ("DELETE", "/channels/thread-1/thread-members/@me"),
    ]
    assert cliente.chamadas[-4][2]["parametros"] == {"antes_de": "10"}


@pytest.mark.asyncio
async def test_usuario_e_aplicacao_atual():
    cliente = ClienteFalso()
    await cliente.obter_usuario_atual()
    await cliente.obter_aplicacao_atual()
    await cliente.editar_aplicacao_atual(nome="Pimcord")
    assert [(metodo, rota) for metodo, rota, _ in cliente.chamadas[-3:]] == [
        ("GET", "/users/@me"),
        ("GET", "/applications/@me"),
        ("PATCH", "/applications/@me"),
    ]
    assert cliente.chamadas[-1][2]["json"] == {"nome": "Pimcord"}
    with pytest.raises(ValueError):
        await cliente.editar_aplicacao_atual()


@pytest.mark.asyncio
async def test_membro_atual_e_apelido_dedicado():
    cliente = ClienteFalso()
    await cliente.obter_membro_atual("guild-1")
    await cliente.alterar_apelido_atual("guild-1", "Pimcord", motivo="teste")
    assert [(metodo, rota) for metodo, rota, _ in cliente.chamadas[-2:]] == [
        ("GET", "/guilds/guild-1/members/@me"),
        ("PATCH", "/guilds/guild-1/members/@me/nick"),
    ]
    assert cliente.chamadas[-1][2]["json"] == {"nick": "Pimcord"}
    assert cliente.chamadas[-1][2]["motivo"] == "teste"


@pytest.mark.asyncio
async def test_lote_rest_oficial_pins_reacoes_destinatarios_e_servidor():
    cliente = ClienteFalso()
    await cliente.listar_mensagens_fixadas("canal-1")
    await cliente.fixar_mensagem_oficial("canal-1", "msg-1")
    await cliente.desafixar_mensagem_oficial("canal-1", "msg-1")
    await cliente.adicionar_reacao_atual("canal-1", "msg-1", "%F0%9F%91%8D")
    await cliente.remover_reacao_atual("canal-1", "msg-1", "%F0%9F%91%8D")
    await cliente.limpar_reacoes_emoji("canal-1", "msg-1", "%F0%9F%91%8D")
    await cliente.adicionar_destinatario("canal-1", "user-1", acesso="oauth")
    await cliente.remover_destinatario("canal-1", "user-1")
    await cliente.obter_sticker_servidor("guild-1", "sticker-1")
    await cliente.listar_regioes_servidor("guild-1")
    await cliente.obter_boas_vindas_novos_membros("guild-1")
    await cliente.remover_conexao_cargo_usuario("app-1")
    await cliente.buscar_mensagens_servidor("guild-1", consulta="Pimcord", limite=10, antes_de="100")
    await cliente.listar_contagens_cargos("guild-1")
    await cliente.obter_membro_usuario_atual("guild-1")
    rotas = [(metodo, rota) for metodo, rota, _ in cliente.chamadas[-15:]]
    assert rotas == [
        ("GET", "/channels/canal-1/messages/pins"),
        ("PUT", "/channels/canal-1/messages/pins/msg-1"),
        ("DELETE", "/channels/canal-1/messages/pins/msg-1"),
        ("PUT", "/channels/canal-1/messages/msg-1/reactions/%F0%9F%91%8D/@me"),
        ("DELETE", "/channels/canal-1/messages/msg-1/reactions/%F0%9F%91%8D/@me"),
        ("DELETE", "/channels/canal-1/messages/msg-1/reactions/%F0%9F%91%8D"),
        ("PUT", "/channels/canal-1/recipients/user-1"),
        ("DELETE", "/channels/canal-1/recipients/user-1"),
        ("GET", "/guilds/guild-1/stickers/sticker-1"),
        ("GET", "/guilds/guild-1/regions"),
        ("GET", "/guilds/guild-1/new-member-welcome"),
        ("DELETE", "/users/@me/applications/app-1/role-connection"),
        ("GET", "/guilds/guild-1/messages/search"),
        ("GET", "/guilds/guild-1/roles/member-counts"),
        ("GET", "/users/@me/guilds/guild-1/member"),
    ]
    assert cliente.chamadas[-3][2]["parametros"] == {"limit": 10, "content": "Pimcord", "min_id": "100"}
    with pytest.raises(ValueError):
        await cliente.buscar_mensagens_servidor("guild-1", limite=26)


@pytest.mark.asyncio
async def test_mensagens_de_webhook_por_token():
    cliente = ClienteFalso()
    await cliente.obter_mensagem_webhook_original("wh-1", "token")
    await cliente.editar_mensagem_webhook_original("wh-1", "token", content="novo")
    await cliente.apagar_mensagem_webhook_original("wh-1", "token")
    await cliente.obter_mensagem_webhook("wh-1", "token", "msg-1")
    await cliente.editar_mensagem_webhook("wh-1", "token", "msg-1", content="editado")
    await cliente.apagar_mensagem_webhook("wh-1", "token", "msg-1")
    assert [(metodo, rota) for metodo, rota, _ in cliente.chamadas[-6:]] == [
        ("GET", "/webhooks/wh-1/token/messages/@original"),
        ("PATCH", "/webhooks/wh-1/token/messages/@original"),
        ("DELETE", "/webhooks/wh-1/token/messages/@original"),
        ("GET", "/webhooks/wh-1/token/messages/msg-1"),
        ("PATCH", "/webhooks/wh-1/token/messages/msg-1"),
        ("DELETE", "/webhooks/wh-1/token/messages/msg-1"),
    ]


@pytest.mark.asyncio
async def test_lote_rest_gateway_monetizacao_e_operacoes_avancadas():
    cliente = ClienteFalso()
    await cliente.gateway_publico()
    await cliente.listar_pacotes_sticker()
    await cliente.obter_pacote_sticker("pack-1")
    await cliente.obter_instancia_atividade("app-1", "instance-1")
    await cliente.listar_entitlements_usuario("app-1", limit=10)
    await cliente.listar_contagens_inscritos_evento("guild-1", "event-1", after="100")
    await cliente.seguir_canal("channel-1", "webhook-channel-1")
    await cliente.banir_membros_em_lote("guild-1", ["user-1", "user-2"], dias_mensagens=2, motivo="limpeza")
    await cliente.alterar_status_voz("channel-1", status="ocupado")
    assert [(metodo, rota) for metodo, rota, _ in cliente.chamadas[-9:]] == [
        ("GET", "/gateway"),
        ("GET", "/sticker-packs"),
        ("GET", "/sticker-packs/pack-1"),
        ("GET", "/applications/app-1/activity-instances/instance-1"),
        ("GET", "/users/@me/applications/app-1/entitlements"),
        ("GET", "/guilds/guild-1/scheduled-events/event-1/users/counts"),
        ("POST", "/channels/channel-1/followers"),
        ("POST", "/guilds/guild-1/bulk-ban"),
        ("PUT", "/channels/channel-1/voice-status"),
    ]
    assert cliente.chamadas[-2][2]["json"] == {"user_ids": ["user-1", "user-2"], "delete_message_days": 2}
    with pytest.raises(ValueError):
        await cliente.banir_membros_em_lote("guild-1", [], dias_mensagens=0)


@pytest.mark.asyncio
async def test_excecoes_evento_e_limpeza_total_de_reacoes():
    cliente = ClienteFalso()
    await cliente.criar_excecao_evento("10", "20", "30", status="cancelado")
    await cliente.editar_excecao_evento("10", "20", "30", status="confirmado")
    await cliente.excluir_excecao_evento("10", "20", "30")
    await cliente.limpar_todas_reacoes("10", "20")
    assert [(metodo, rota) for metodo, rota, _ in cliente.chamadas[-4:]] == [
        ("POST", "/guilds/10/scheduled-events/20/exceptions/30"),
        ("PATCH", "/guilds/10/scheduled-events/20/exceptions/30"),
        ("DELETE", "/guilds/10/scheduled-events/20/exceptions/30"),
        ("DELETE", "/channels/10/messages/20/reactions"),
    ]
    with pytest.raises(ValueError):
        await cliente.editar_excecao_evento("10", "20", "30")


@pytest.mark.asyncio
async def test_widget_png_preserva_resposta_binaria():
    cliente = ClienteFalso()
    imagem = await cliente.obter_widget_png("guild-1")
    assert imagem == {"rota": "/guilds/guild-1/widget.png"}
    assert cliente.chamadas[-1][0:2] == ("GET", "/guilds/guild-1/widget.png")
    assert cliente.chamadas[-1][2]["bruto"] is True


@pytest.mark.asyncio
async def test_inscritos_de_excecao_evento_recorrente():
    cliente = ClienteFalso()
    await cliente.listar_inscritos_excecao_evento(
        "guild-1", "event-1", "occurrence-1", limite=25, depois_de="user-0", incluir_membro=True
    )
    assert cliente.chamadas[-1][0:2] == (
        "GET", "/guilds/guild-1/scheduled-events/event-1/occurrence-1/users"
    )
    assert cliente.chamadas[-1][2]["parametros"] == {
        "limit": 25, "after": "user-0", "with_member": "true"
    }
    with pytest.raises(ValueError):
        await cliente.listar_inscritos_excecao_evento("guild-1", "event-1", "", limite=25)
    with pytest.raises(ValueError):
        await cliente.listar_inscritos_excecao_evento("guild-1", "event-1", "occurrence-1", limite=101)
    with pytest.raises(ValueError):
        await cliente.listar_inscritos_excecao_evento(
            "guild-1", "event-1", "occurrence-1", antes_de="a", depois_de="b"
        )


@pytest.mark.asyncio
async def test_acoes_incidente_usam_put_e_timestamps_oficiais():
    cliente = ClienteFalso()
    retorno = await cliente.modificar_acoes_incidente(
        "10",
        invites_disabled_until="2026-08-18T12:00:00Z",
        dms_disabled_until=None,
    )
    assert retorno == {
        "invites_disabled_until": "2026-08-18T12:00:00Z",
        "dms_disabled_until": None,
    }
    metodo, rota, kwargs = cliente.chamadas[-1]
    assert metodo == "PUT"
    assert rota == "/guilds/10/incident-actions"
    assert kwargs["json"] == {
        "invites_disabled_until": "2026-08-18T12:00:00Z",
        "dms_disabled_until": None,
    }


@pytest.mark.asyncio
async def test_acoes_incidente_rejeitam_payload_inseguro_localmente():
    cliente = ClienteFalso()
    with pytest.raises(ValueError):
        await cliente.modificar_acoes_incidente("10")
    with pytest.raises(ValueError):
        await cliente.modificar_acoes_incidente("10", modo="bloquear")
    with pytest.raises(TypeError):
        await cliente.modificar_acoes_incidente("10", invites_disabled_until=3600)


@pytest.mark.asyncio
async def test_usuarios_alvo_de_convite_usam_csv_multipart_e_status():
    cliente = ClienteFalso()
    csv = await cliente.obter_usuarios_alvo_convite("abc")
    assert csv == {"rota": "/invites/abc/target-users"}
    await cliente.atualizar_usuarios_alvo_convite("abc", b"user_id\n123\n", nome_arquivo="alvos.csv")
    status = await cliente.obter_status_usuarios_alvo_convite("abc")
    assert status["rota"] == "/invites/abc/target-users/job-status"
    chamada = cliente.chamadas[-2]
    assert chamada[0:2] == ("PUT", "/invites/abc/target-users")
    assert chamada[2]["arquivos"] == [("target_users_file", "alvos.csv", b"user_id\n123\n")]
    assert cliente.chamadas[-1][0:2] == ("GET", "/invites/abc/target-users/job-status")


@pytest.mark.asyncio
async def test_requisitar_csv_bruto_preserva_bytes():
    cliente = ClienteHTTP("token")
    chamadas = []

    class Resposta:
        status = 200
        headers = {}
        async def read(self):
            return b"user_id\n123\n"
        async def text(self):
            return ""
        async def __aenter__(self):
            return self
        async def __aexit__(self, *args):
            return False

    class Sessao:
        closed = False
        def request(self, *args, **kwargs):
            chamadas.append((args, kwargs))
            return Resposta()

    cliente._sessao = Sessao()
    resultado = await cliente.requisitar("GET", "/invites/abc/target-users", bruto=True)
    assert resultado == b"user_id\n123\n"
    assert chamadas[0][1]["json"] is None


@pytest.mark.asyncio
async def test_excluir_integracao_usa_rota_oficial():
    cliente = ClienteFalso()
    await cliente.excluir_integracao("10", "40", motivo="limpeza")
    metodo, rota, kwargs = cliente.chamadas[-1]
    assert (metodo, rota) == ("DELETE", "/guilds/10/integrations/40")
    assert kwargs["motivo"] == "limpeza"


@pytest.mark.asyncio
async def test_solicitacoes_entrada_e_excecao_recorrente():
    cliente = ClienteFalso()
    await cliente.listar_solicitacoes_entrada("10", status="SUBMITTED", limite=25, depois_de="9")
    assert cliente.chamadas[-1][0:2] == ("GET", "/guilds/10/requests")
    assert cliente.chamadas[-1][2]["parametros"] == {"limit": 25, "status": "SUBMITTED", "after": "9"}
    await cliente.modificar_solicitacao_entrada("10", "77", acao="REJECTED", motivo_rejeicao="não atende")
    assert cliente.chamadas[-1][0:2] == ("PATCH", "/guilds/10/requests/77")
    assert cliente.chamadas[-1][2]["json"] == {"action": "REJECTED", "rejection_reason": "não atende"}
    await cliente.criar_excecao_evento("10", "20", inicio_original="2026-08-18T12:00:00Z", cancelada=True)
    assert cliente.chamadas[-1][0:2] == ("POST", "/guilds/10/scheduled-events/20/exceptions")
    assert cliente.chamadas[-1][2]["json"] == {"original_scheduled_start_time": "2026-08-18T12:00:00Z", "is_canceled": True}


@pytest.mark.asyncio
async def test_permissoes_de_todos_os_comandos_do_servidor():
    cliente = ClienteFalso()
    await cliente.obter_permissoes_comandos_servidor("app", "guild")
    assert cliente.chamadas[-1][0:2] == ("GET", "/applications/app/guilds/guild/commands/permissions")


@pytest.mark.asyncio
async def test_assinaturas_por_sku_usam_rotas_e_filtros_oficiais():
    cliente = ClienteFalso()
    await cliente.listar_assinaturas_sku("sku", antes="a", depois="d", limite=25, usuario_id="u")
    assert cliente.chamadas[-1][0:2] == ("GET", "/skus/sku/subscriptions")
    assert cliente.chamadas[-1][2]["parametros"] == {"before": "a", "after": "d", "limit": 25, "user_id": "u"}
    await cliente.obter_assinatura_sku("sku", "sub", usuario_id="u")
    assert cliente.chamadas[-1][0:2] == ("GET", "/skus/sku/subscriptions/sub")
    assert cliente.chamadas[-1][2]["parametros"] == {"user_id": "u"}


@pytest.mark.asyncio
async def test_lobbies_bot_token_com_rotas_especializadas():
    cliente = ClienteFalso()
    await cliente.atualizar_lobbies(nome="pimcord")
    await cliente.criar_lobby(nome="teste")
    await cliente.obter_lobby("lob")
    await cliente.excluir_lobby("lob")
    await cliente.editar_lobby("lob", nome="novo")
    await cliente.editar_vinculo_canal_lobby("lob", canal_id="canal")
    await cliente.sair_lobby("lob")
    await cliente.convidar_eu_para_lobby("lob")
    await cliente.adicionar_membros_lobby("lob", [{"user_id": "1"}])
    await cliente.adicionar_membro_lobby("lob", "2", username="usuario")
    await cliente.remover_membro_lobby("lob", "2")
    await cliente.convidar_membro_lobby("lob", "2")
    await cliente.listar_mensagens_lobby("lob", limite=20)
    await cliente.enviar_mensagem_lobby("lob", {"content": "ola"})
    await cliente.definir_metadata_moderacao_mensagem_lobby("lob", "msg", {"moderation": "ok"})
    with pytest.raises(TypeError):
        await cliente.adicionar_membros_lobby("lob", {"user_id": "1"})
    rotas = [(metodo, rota) for metodo, rota, _ in cliente.chamadas]
    assert rotas == [
        ("PUT", "/lobbies"),
        ("POST", "/lobbies"),
        ("GET", "/lobbies/lob"),
        ("DELETE", "/lobbies/lob"),
        ("PATCH", "/lobbies/lob"),
        ("PATCH", "/lobbies/lob/channel-linking"),
        ("DELETE", "/lobbies/lob/members/@me"),
        ("POST", "/lobbies/lob/members/@me/invites"),
        ("POST", "/lobbies/lob/members/bulk"),
        ("PUT", "/lobbies/lob/members/2"),
        ("DELETE", "/lobbies/lob/members/2"),
        ("POST", "/lobbies/lob/members/2/invites"),
        ("GET", "/lobbies/lob/messages"),
        ("POST", "/lobbies/lob/messages"),
        ("PUT", "/lobbies/lob/messages/msg/moderation-metadata"),
    ]


@pytest.mark.asyncio
async def test_partner_attachments_e_webhooks_especializados():
    cliente = ClienteFalso()
    await cliente.criar_anexo_aplicacao("app", b"png", nome_arquivo="x.png")
    await cliente.desvincular_conta_provisoria({"client_id": "1", "external_auth_token": "x", "external_auth_type": "oauth2"})
    await cliente.desvincular_conta_provisoria_bot("externo")
    await cliente.obter_token_partner({"client_id": "1", "external_auth_token": "x", "external_auth_type": "oauth2"})
    await cliente.obter_token_partner_bot("externo", provisional_user_id="2", preferred_global_name="Pimcord")
    await cliente.definir_metadata_moderacao_dm_partner("1", "2", "3", {"motivo": "teste"})
    await cliente.definir_metadata_moderacao_dm_partner("1", "2", "3", {"motivo": "teste"}, formulario=True)
    await cliente.executar_webhook_github("4", "segredo", {"action": "push"}, esperar=True, thread_id="5")
    await cliente.executar_webhook_slack("4", "segredo", {"text": "oi"}, esperar=True, thread_id="5")
    await cliente.executar_webhook_slack("4", "segredo", {"text": "oi"}, formulario=True)
    with pytest.raises(ValueError):
        await cliente.obter_token_partner({"client_id": "1"})
    with pytest.raises(ValueError):
        await cliente.definir_metadata_moderacao_dm_partner("1", "2", "3", {str(i): "x" for i in range(6)})
    assert ("POST", "/applications/app/attachment") in [(m, r) for m, r, _ in cliente.chamadas]
    assert ("POST", "/partner-sdk/token/bot") in [(m, r) for m, r, _ in cliente.chamadas]
    assert ("POST", "/webhooks/4/segredo/github") in [(m, r) for m, r, _ in cliente.chamadas]
    assert ("POST", "/webhooks/4/segredo/slack") in [(m, r) for m, r, _ in cliente.chamadas]
