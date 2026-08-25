

def test_eventos_entitlement_sao_modelados_sem_rede():
    from pimcord.gateway.eventos import modelar_evento
    from pimcord.discord.recursos import Entitlement

    modelo = modelar_evento("ENTITLEMENT_CREATE", {"id": "ent-1", "sku_id": "sku-1", "application_id": "app-1"})
    assert isinstance(modelo, Entitlement)
    assert modelo.id == "ent-1"
    assert modelo.produto_id == "sku-1"
    assert modelo.aplicacao_id == "app-1"
