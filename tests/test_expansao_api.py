from __future__ import annotations

import asyncio

from pimcord.discord.recursos import CanalCompleto, RegistroAuditoria, EventoAgendado, EstadoVoz
from pimcord.gateway.eventos import EVENTOS_PORTUGUES, modelar_evento
from pimcord.gateway.cliente import Gateway
from pimcord.http.cliente import ClienteHTTP


class ClienteFalso(ClienteHTTP):
    def __init__(self):
        super().__init__("token")
        self.chamadas = []

    async def requisitar(self, metodo, rota, **kwargs):
        self.chamadas.append((metodo, rota, kwargs))
        return {"id": "123", "name": "gerado"}


def test_modelos_toleram_payloads_oficiais_e_preservam_bruto():
    canal = CanalCompleto.de_dict({"id": "1", "type": 15, "guild_id": "2", "thread_metadata": {"archived": False}, "novo_campo": True})
    auditoria = RegistroAuditoria.de_dict({"audit_log_entries": [{"id": "3", "action_type": 10}], "users": []})
    evento = EventoAgendado.de_dict({"id": "4", "guild_id": "2", "scheduled_start_time": "2026-08-16T00:00:00Z"})
    assert canal.id == "1" and canal.servidor_id == "2" and canal.bruto["novo_campo"] is True
    assert auditoria.entradas[0].id == "3"
    assert evento.id == "4" and evento.servidor_id == "2"


def test_catalogo_de_eventos_e_modelacao():
    assert EVENTOS_PORTUGUES["THREAD_CREATE"] == "thread_criada"
    estado = modelar_evento("VOICE_STATE_UPDATE", {"guild_id": "1", "channel_id": "2", "user_id": "3"})
    assert isinstance(estado, EstadoVoz)
    assert estado.servidor_id == "1" and estado.canal_id == "2"


def test_cliente_expone_endpoints_de_threads_e_moderacao():
    cliente = ClienteFalso()
    asyncio.run(cliente.criar_thread("10", name="discussao", auto_archive_duration=60))
    asyncio.run(cliente.banir_membro("20", "30", dias_mensagens=3, motivo="regra"))
    asyncio.run(cliente.obter_auditoria("20", limit=10))
    assert cliente.chamadas[0][1] == "/channels/10/threads"
    assert cliente.chamadas[1][1] == "/guilds/20/bans/30"
    assert cliente.chamadas[1][2]["motivo"] == "regra"
    assert cliente.chamadas[2][1] == "/guilds/20/audit-logs"


def test_gateway_despacha_alias_portugues_e_modelo():
    class BotFalso:
        http = None
        def __init__(self): self.eventos = {"thread_criada": [self.receber], "modelo_thread_criada": [self.receber_modelo]}; self.recebidos = []
        async def receber(self, valor): self.recebidos.append(("alias", valor))
        async def receber_modelo(self, valor): self.recebidos.append(("modelo", valor))
        async def disparar(self, nome, valor):
            for fn in self.eventos.get(nome, []): await fn(valor)
    bot = BotFalso()
    gateway = Gateway(bot, "wss://example.invalid", "token", 0)
    asyncio.run(gateway._evento("THREAD_CREATE", {"id": "8", "guild_id": "9", "type": 11}))
    assert bot.recebidos[0][0] == "alias"
    assert isinstance(bot.recebidos[0][1], CanalCompleto)
    assert bot.recebidos[1][0] == "modelo"
