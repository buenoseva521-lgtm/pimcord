from pimcord import AlteracaoAuditoria, Entitlement, EntradaAuditoria, OpcaoAuditoria, SkuAplicacao


def test_entrada_auditoria_modela_alteracoes_e_opcoes():
    entrada = EntradaAuditoria.de_dict({
        "id": "10", "action_type": 72, "target_id": "20", "user_id": "30",
        "changes": [{"key": "name", "old_value": "a", "new_value": "b"}],
        "options": {"channel_id": "40", "count": "3"},
    })
    assert entrada.id == "10"
    assert entrada.acao == 72
    assert isinstance(entrada.alteracoes[0], AlteracaoAuditoria)
    assert entrada.alteracoes[0].depois == "b"
    assert isinstance(entrada.opcoes, OpcaoAuditoria)
    assert entrada.opcoes.canal_id == "40"


def test_entitlement_mapeia_ids_e_datas_oficiais():
    entitlement = Entitlement.de_dict({
        "id": "1", "sku_id": "2", "application_id": "3", "guild_id": "4",
        "starts_at": "2026-01-01T00:00:00Z", "ends_at": "2026-02-01T00:00:00Z", "consumed": True,
    })
    assert entitlement.produto_id == "2"
    assert entitlement.aplicacao_id == "3"
    assert entitlement.servidor_id == "4"
    assert entitlement.consumido is True
    assert entitlement.inicia_em is not None and entitlement.termina_em is not None


def test_sku_mapeia_preco_taxas_e_sinalizadores():
    sku = SkuAplicacao.de_dict({
        "id": "7", "application_id": "8", "name": "Plano", "price": {"amount": 499, "currency": "brl"},
        "tax_inclusive": True, "flags": 1, "interval_count": 3,
    })
    assert sku.id == "7"
    assert sku.aplicacao_id == "8"
    assert sku.preco["amount"] == 499
    assert sku.taxas_incluidas is True
    assert sku.sinalizadores == 1
    assert sku.parcelas == 3


def test_canal_modela_campos_oficiais_da_aplicacao():
    from pimcord.discord.recursos import CanalCompleto

    canal = CanalCompleto.de_dict({
        "id": "10", "type": 0, "name": "privado", "application_id": None,
        "app_permissions": "1024", "obfuscated": True,
    })

    assert canal.aplicacao_id is None
    assert canal.permissoes_aplicacao == "1024"
    assert canal.obfuscado is True
    assert canal.bruto["application_id"] is None


def test_interacao_expoe_app_permissions_do_canal_resolvido():
    from pimcord.interacoes.modelos import Interacao

    interacao = Interacao({
        "id": "1", "token": "tok", "application_id": "app", "type": 2,
        "data": {"resolved": {"channels": {"10": {
            "id": "10", "app_permissions": "2048"
        }}}},
    }, object())

    assert interacao.app_permissions == "2048"
    assert interacao.canal_resolvido["id"] == "10"


def test_interacao_prioriza_app_permissions_do_evento():
    from pimcord.interacoes.modelos import Interacao

    interacao = Interacao({
        "id": "2", "token": "tok", "application_id": "app", "type": 2,
        "app_permissions": "4096",
        "data": {"resolved": {"channels": {"10": {"app_permissions": "2048"}}}},
    }, object())

    assert interacao.app_permissions == "4096"
