

def test_interacao_preserva_contexto_entitlements_e_limite_de_anexos():
    from pimcord.interacoes.modelos import Interacao

    interacao = Interacao({
        "id": "int-1",
        "token": "tok",
        "application_id": "app-1",
        "type": 2,
        "context": 0,
        "attachment_size_limit": 104857600,
        "authorizing_integration_owners": {"0": "guild-1"},
        "entitlements": [{"id": "ent-1", "sku_id": "sku-1", "application_id": "app-1", "owner_id": "user-1", "owner_type": 2}],
    }, cliente=object())

    assert interacao.contexto_interacao == 0
    assert interacao.limite_anexos == 104857600
    assert interacao.attachment_size_limit == 104857600
    assert interacao.authorizing_integration_owners == {"0": "guild-1"}
    assert interacao.entitlements_modelados[0].id == "ent-1"
