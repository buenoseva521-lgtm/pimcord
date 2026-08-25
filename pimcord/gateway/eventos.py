"""Catálogo de eventos Gateway e normalização de payloads do Pimcord."""
from __future__ import annotations

from typing import Any, Callable

from ..discord.modelos import Mensagem, Servidor, Usuario, Membro
from ..discord.recursos import (
    CanalCompleto, EntradaAuditoria, EventoAgendado, EstadoVoz, Presenca,
    Reacao, RegistroAuditoria, Convite, Integracao, InstanciaStage, RegraAutomoderacao, Entitlement,
)

# Nome oficial -> nome público em português. O nome oficial continua aceito.
EVENTOS_PORTUGUES = {
    "READY": "pronto", "RESUMED": "retomado", "GUILD_CREATE": "servidor_criado",
    "GUILD_UPDATE": "servidor_atualizado", "GUILD_DELETE": "servidor_excluido",
    "GUILD_BAN_ADD": "banimento_adicionado", "GUILD_BAN_REMOVE": "banimento_removido",
    "GUILD_AUDIT_LOG_ENTRY_CREATE": "entrada_auditoria_criada",
    "GUILD_EMOJIS_UPDATE": "emojis_atualizados", "GUILD_STICKERS_UPDATE": "adesivos_atualizados",
    "GUILD_INTEGRATIONS_UPDATE": "integracoes_atualizadas", "GUILD_MEMBER_ADD": "membro_adicionado",
    "GUILD_MEMBER_REMOVE": "membro_removido", "GUILD_MEMBER_UPDATE": "membro_atualizado",
    "GUILD_MEMBERS_CHUNK": "lote_membros_recebido", "GUILD_ROLE_CREATE": "cargo_criado",
    "GUILD_ROLE_UPDATE": "cargo_atualizado", "GUILD_ROLE_DELETE": "cargo_excluido",
    "GUILD_SCHEDULED_EVENT_CREATE": "evento_agendado_criado", "GUILD_SCHEDULED_EVENT_UPDATE": "evento_agendado_atualizado",
    "GUILD_SCHEDULED_EVENT_DELETE": "evento_agendado_excluido", "GUILD_SCHEDULED_EVENT_USER_ADD": "inscrito_evento_adicionado",
    "GUILD_SCHEDULED_EVENT_USER_REMOVE": "inscrito_evento_removido", "CHANNEL_CREATE": "canal_criado",
    "CHANNEL_UPDATE": "canal_atualizado", "CHANNEL_DELETE": "canal_excluido", "CHANNEL_PINS_UPDATE": "pins_atualizados",
    "THREAD_CREATE": "thread_criada", "THREAD_UPDATE": "thread_atualizada", "THREAD_DELETE": "thread_excluida",
    "THREAD_LIST_SYNC": "threads_sincronizadas", "THREAD_MEMBER_UPDATE": "membro_thread_atualizado",
    "THREAD_MEMBERS_UPDATE": "membros_thread_atualizados", "MESSAGE_CREATE": "mensagem_criada",
    "MESSAGE_UPDATE": "mensagem_atualizada", "MESSAGE_DELETE": "mensagem_excluida", "MESSAGE_DELETE_BULK": "mensagens_excluidas",
    "MESSAGE_REACTION_ADD": "reacao_adicionada", "MESSAGE_REACTION_REMOVE": "reacao_removida",
    "MESSAGE_REACTION_REMOVE_ALL": "reacoes_removidas", "MESSAGE_REACTION_REMOVE_EMOJI": "reacoes_emoji_removidas",
    "PRESENCE_UPDATE": "presenca_atualizada", "TYPING_START": "digitacao_iniciada", "VOICE_STATE_UPDATE": "estado_voz_atualizado",
    "VOICE_SERVER_UPDATE": "servidor_voz_atualizado", "STAGE_INSTANCE_CREATE": "instancia_stage_criada",
    "STAGE_INSTANCE_UPDATE": "instancia_stage_atualizada", "STAGE_INSTANCE_DELETE": "instancia_stage_excluida",
    "WEBHOOKS_UPDATE": "webhooks_atualizados", "INVITE_CREATE": "convite_criado", "INVITE_DELETE": "convite_excluido",
    "INTEGRATION_CREATE": "integracao_criada", "INTEGRATION_UPDATE": "integracao_atualizada", "INTEGRATION_DELETE": "integracao_excluida",
    "INTERACTION_CREATE": "interacao_criada", "AUTO_MODERATION_RULE_CREATE": "regra_automoderacao_criada",
    "AUTO_MODERATION_RULE_UPDATE": "regra_automoderacao_atualizada", "AUTO_MODERATION_RULE_DELETE": "regra_automoderacao_excluida",
    "AUTO_MODERATION_ACTION_EXECUTION": "acao_automoderacao_executada", "APPLICATION_COMMAND_PERMISSIONS_UPDATE": "permissoes_comando_atualizadas",
    "ENTITLEMENT_CREATE": "direito_criado", "ENTITLEMENT_UPDATE": "direito_atualizado", "ENTITLEMENT_DELETE": "direito_excluido",
    "READY_SUPPLEMENTAL": "pronto_suplementar", "USER_UPDATE": "usuario_atualizado",
    "GUILD_SOUNDBOARD_SOUND_CREATE": "som_criado",
    "GUILD_SOUNDBOARD_SOUND_UPDATE": "som_atualizado", "GUILD_SOUNDBOARD_SOUND_DELETE": "som_excluido",
    "GUILD_SOUNDBOARD_SOUNDS_UPDATE": "sons_atualizados", "MESSAGE_POLL_VOTE_ADD": "voto_enquete_adicionado",
    "MESSAGE_POLL_VOTE_REMOVE": "voto_enquete_removido",
}

MODELOS_EVENTO: dict[str, Callable[..., Any]] = {
    "GUILD_CREATE": Servidor, "GUILD_UPDATE": Servidor, "CHANNEL_CREATE": CanalCompleto,
    "CHANNEL_UPDATE": CanalCompleto, "THREAD_CREATE": CanalCompleto, "THREAD_UPDATE": CanalCompleto,
    "GUILD_MEMBER_ADD": Membro, "GUILD_MEMBER_UPDATE": Membro, "MESSAGE_CREATE": Mensagem,
    "MESSAGE_UPDATE": Mensagem, "PRESENCE_UPDATE": Presenca, "VOICE_STATE_UPDATE": EstadoVoz,
    "GUILD_SCHEDULED_EVENT_CREATE": EventoAgendado, "GUILD_SCHEDULED_EVENT_UPDATE": EventoAgendado,
    "STAGE_INSTANCE_CREATE": InstanciaStage, "STAGE_INSTANCE_UPDATE": InstanciaStage,
    "GUILD_AUDIT_LOG_ENTRY_CREATE": EntradaAuditoria, "INVITE_CREATE": Convite,
    "INTEGRATION_CREATE": Integracao, "INTEGRATION_UPDATE": Integracao,
    "MESSAGE_REACTION_ADD": Reacao, "MESSAGE_REACTION_REMOVE": Reacao,
    "AUTO_MODERATION_RULE_CREATE": RegraAutomoderacao, "AUTO_MODERATION_RULE_UPDATE": RegraAutomoderacao,
    "ENTITLEMENT_CREATE": Entitlement, "ENTITLEMENT_UPDATE": Entitlement,
    "ENTITLEMENT_DELETE": Entitlement, "USER_UPDATE": Usuario,
}

EVENTOS_DISCORD = tuple(EVENTOS_PORTUGUES)



def modelar_evento(nome: str, dados: dict[str, Any], cliente: Any = None) -> Any:
    """Converte um dispatch em modelo quando existe mapeamento; caso contrário preserva o dict."""
    classe = MODELOS_EVENTO.get(nome)
    if classe is None:
        return dados
    if classe is Mensagem:
        return classe.de_gateway(dados, cliente)
    if classe is Servidor:
        return classe.de_dict(dados, cliente=cliente)
    if classe is Membro:
        return classe.de_dict(dados, str(dados.get("guild_id", "")))
    return classe.de_dict(dados)


__all__ = ["EVENTOS_PORTUGUES", "EVENTOS_DISCORD", "MODELOS_EVENTO", "modelar_evento"]
