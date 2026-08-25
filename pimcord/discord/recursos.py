"""Modelos ampliados de recursos Discord.

Os modelos são deliberadamente tolerantes a campos novos: preservam o payload bruto
para que a biblioteca continue funcionando quando o Discord adicionar propriedades.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, ClassVar, Generic, TypeVar

from .modelos import Usuario

T = TypeVar("T")


def _data(valor: Any) -> datetime | None:
    if not valor:
        return None
    if isinstance(valor, datetime):
        return valor
    try:
        return datetime.fromisoformat(str(valor).replace("Z", "+00:00"))
    except ValueError:
        return None


def _id(valor: Any) -> str | None:
    return None if valor is None else str(valor)


@dataclass(slots=True)
class ModeloDiscord:
    """Base comum que preserva campos não conhecidos pelo modelo."""
    bruto: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def de_dict(cls, dados: dict[str, Any] | None, **extras: Any):
        dados = dict(dados or {})
        conhecidos = set(getattr(cls, "__annotations__", {})) - {"bruto"}
        valores: dict[str, Any] = {}
        for campo in conhecidos:
            chave = campo
            aliases = {
                "servidor_id": "guild_id", "canal_id": "channel_id", "usuario_id": "user_id",
                "aplicacao_id": "application_id", "produto_id": "sku_id", "categoria_id": "parent_id", "dono_id": "owner_id",
                "ultima_mensagem_id": "last_message_id", "inicio_em": "scheduled_start_time",
                "fim_em": "scheduled_end_time", "inicia_em": "starts_at", "termina_em": "ends_at", "criado_em": "created_at", "atualizado_em": "updated_at",
                "nome": "name", "descricao": "description", "topico": "topic", "tipo": "type", "usuario": "user", "servidor_origem": "source_guild", "canal_origem": "source_channel", "consumido": "consumed", "excluido": "deleted", "cancelada": "canceled", "preco": "price", "taxas_incluidas": "tax_inclusive", "sinalizadores": "flags", "parcelas": "interval_count", "permissoes_aplicacao": "app_permissions", "obfuscado": "obfuscated",
            }
            chave = aliases.get(campo, campo)
            valor = dados.get(chave, extras.get(campo))
            if campo.endswith("_id") or campo == "id": valor = _id(valor)
            if campo.endswith("_em"): valor = _data(valor)
            if valor is not None: valores[campo] = valor
        valores["bruto"] = dados
        return cls(**valores)

    def para_dict(self) -> dict[str, Any]:
        resultado = dict(self.bruto)
        for nome in self.__dataclass_fields__:
            if nome == "bruto": continue
            valor = getattr(self, nome)
            if isinstance(valor, datetime): valor = valor.isoformat()
            if isinstance(valor, list):
                valor = [item.para_dict() if hasattr(item, "para_dict") else item for item in valor]
            elif hasattr(valor, "para_dict"):
                valor = valor.para_dict()
            resultado[nome] = valor
        return resultado


@dataclass(slots=True)
class Emoji(ModeloDiscord):
    id: str | None = None
    nome: str | None = None
    animado: bool = False
    gerenciado: bool = False
    disponivel: bool = True
    cargos: list[str] = field(default_factory=list)
    usuario_id: str | None = None

    @property
    def mencao(self) -> str:
        if not self.id: return self.nome or ""
        prefixo = "a" if self.animado else ""
        return f"<{prefixo}:{self.nome}:{self.id}>"


@dataclass(slots=True)
class EmojiParcial(ModeloDiscord):
    id: str | None = None
    nome: str | None = None
    animado: bool = False


@dataclass(slots=True)
class Adesivo(ModeloDiscord):
    id: str | None = None
    nome: str | None = None
    descricao: str | None = None
    tipo: int | None = None
    formato: int | None = None
    servidor_id: str | None = None
    tags: str | None = None
    disponivel: bool = True
    url: str | None = None


@dataclass(slots=True)
class MetadadosThread(ModeloDiscord):
    arquivada: bool = False
    auto_arquivamento_minutos: int | None = None
    bloqueada: bool = False
    criada: bool = False
    arquivada_em: datetime | None = None


@dataclass(slots=True)
class MembroThread(ModeloDiscord):
    id: str | None = None
    servidor_id: str | None = None
    membro_desde: datetime | None = None
    sinalizado: bool = False


@dataclass(slots=True)
class TagForum(ModeloDiscord):
    id: str | None = None
    nome: str | None = None
    moderada: bool = False
    emoji_id: str | None = None
    emoji_nome: str | None = None


@dataclass(slots=True)
class CanalCompleto(ModeloDiscord):
    id: str | None = None
    tipo: int | None = None
    nome: str | None = None
    servidor_id: str | None = None
    aplicacao_id: str | None = None
    obfuscado: bool = False
    permissoes_aplicacao: str | None = None
    categoria_id: str | None = None
    topico: str | None = None
    nsfw: bool = False
    posicao: int | None = None
    ultima_mensagem_id: str | None = None
    dono_id: str | None = None
    mensagem_count: int | None = None
    membro_count: int | None = None
    metadados_thread: MetadadosThread | None = None
    membro: MembroThread | None = None
    tags_forum: list[TagForum] = field(default_factory=list)
    tags_aplicadas: list[str] = field(default_factory=list)


@dataclass(slots=True)
class Banimento(ModeloDiscord):
    motivo: str | None = None
    usuario_id: str | None = None
    usuario: Any = None


@dataclass(slots=True)
class AlteracaoAuditoria(ModeloDiscord):
    chave: str | None = None
    antes: Any = None
    depois: Any = None

    @classmethod
    def de_dict(cls, dados: dict[str, Any] | None, **extras: Any):
        dados = dict(dados or {})
        return cls(chave=dados.get("key"), antes=dados.get("old_value"), depois=dados.get("new_value"), bruto=dados)


@dataclass(slots=True)
class OpcaoAuditoria(ModeloDiscord):
    membro_id: str | None = None
    canal_id: str | None = None
    mensagens_id: list[str] = field(default_factory=list)
    tipo_canal: int | None = None
    contagem: int | None = None

    @classmethod
    def de_dict(cls, dados: dict[str, Any] | None, **extras: Any):
        dados = dict(dados or {})
        return cls(
            membro_id=_id(dados.get("member_id")),
            canal_id=_id(dados.get("channel_id")),
            mensagens_id=[str(item) for item in dados.get("message_id", dados.get("message_ids", []))] if isinstance(dados.get("message_id", dados.get("message_ids", [])), list) else [],
            tipo_canal=dados.get("channel_type"), contagem=dados.get("count"), bruto=dados,
        )


@dataclass(slots=True)
class EntradaAuditoria(ModeloDiscord):
    id: str | None = None
    tipo: int | None = None
    acao: int | None = None
    alvo_id: str | None = None
    usuario_id: str | None = None
    motivo: str | None = None
    alteracoes: list[AlteracaoAuditoria] = field(default_factory=list)
    opcoes: OpcaoAuditoria | None = None
    entradas: list[dict[str, Any]] = field(default_factory=list)

    @classmethod
    def de_dict(cls, dados: dict[str, Any] | None, **extras: Any):
        dados = dict(dados or {})
        return cls(
            id=_id(dados.get("id")), tipo=dados.get("target_type"), acao=dados.get("action_type"),
            alvo_id=_id(dados.get("target_id")), usuario_id=_id(dados.get("user_id")), motivo=dados.get("reason"),
            alteracoes=[AlteracaoAuditoria.de_dict(item) for item in dados.get("changes", [])],
            opcoes=OpcaoAuditoria.de_dict(dados.get("options")) if dados.get("options") else None,
            entradas=list(dados.get("options", {}).get("entries", [])) if isinstance(dados.get("options"), dict) else [], bruto=dados,
        )


@dataclass(slots=True)
class RegistroAuditoria(ModeloDiscord):
    entradas: list[EntradaAuditoria] = field(default_factory=list)
    usuarios: list[dict[str, Any]] = field(default_factory=list)
    integrações: list[dict[str, Any]] = field(default_factory=list)
    usuarios_modelados: list[Usuario] = field(default_factory=list)
    integrações_modeladas: list[Integracao] = field(default_factory=list)
    comandos_aplicacao: list[dict[str, Any]] = field(default_factory=list)
    regras_automoderacao: list[dict[str, Any]] = field(default_factory=list)
    eventos_agendados: list[dict[str, Any]] = field(default_factory=list)
    threads: list[dict[str, Any]] = field(default_factory=list)
    webhooks: list[dict[str, Any]] = field(default_factory=list)
    comandos_aplicacao_modelados: list[AplicacaoComando] = field(default_factory=list)
    regras_automoderacao_modeladas: list[RegraAutomoderacao] = field(default_factory=list)
    eventos_agendados_modelados: list[EventoAgendado] = field(default_factory=list)
    threads_modeladas: list[CanalCompleto] = field(default_factory=list)
    webhooks_modelados: list[WebhookInfo] = field(default_factory=list)

    @classmethod
    def de_dict(cls, dados: dict[str, Any] | None, **extras: Any):
        dados = dict(dados or {})
        return cls(
            entradas=[EntradaAuditoria.de_dict(x) for x in dados.get("audit_log_entries", [])],
            usuarios=list(dados.get("users", [])),
            integrações=list(dados.get("integrations", [])),
            usuarios_modelados=[Usuario.de_dict(x) for x in dados.get("users", []) if isinstance(x, dict)],
            integrações_modeladas=[Integracao.de_dict(x) for x in dados.get("integrations", []) if isinstance(x, dict)],
            comandos_aplicacao=list(dados.get("application_commands", [])),
            regras_automoderacao=list(dados.get("auto_moderation_rules", [])),
            eventos_agendados=list(dados.get("guild_scheduled_events", [])),
            threads=list(dados.get("threads", [])),
            webhooks=list(dados.get("webhooks", [])),
            comandos_aplicacao_modelados=[AplicacaoComando.de_dict(x) for x in dados.get("application_commands", []) if isinstance(x, dict)],
            regras_automoderacao_modeladas=[RegraAutomoderacao.de_dict(x) for x in dados.get("auto_moderation_rules", []) if isinstance(x, dict)],
            eventos_agendados_modelados=[EventoAgendado.de_dict(x) for x in dados.get("guild_scheduled_events", []) if isinstance(x, dict)],
            threads_modeladas=[CanalCompleto.de_dict(x) for x in dados.get("threads", []) if isinstance(x, dict)],
            webhooks_modelados=[WebhookInfo.de_dict(x) for x in dados.get("webhooks", []) if isinstance(x, dict)],
            bruto=dados,
        )


@dataclass(slots=True)
class Entitlement(ModeloDiscord):
    id: str | None = None
    produto_id: str | None = None
    aplicacao_id: str | None = None
    usuario_id: str | None = None
    servidor_id: str | None = None
    tipo: int | None = None
    consumido: bool = False
    excluido: bool = False
    inicia_em: datetime | None = None
    termina_em: datetime | None = None


@dataclass(slots=True)
class AssinaturaAplicacao(ModeloDiscord):
    id: str | None = None
    produto_id: str | None = None
    aplicacao_id: str | None = None
    usuario_id: str | None = None
    status: int | None = None
    cancelada: bool = False
    inicia_em: datetime | None = None
    termina_em: datetime | None = None


@dataclass(slots=True)
class SkuAplicacao(ModeloDiscord):
    id: str | None = None
    tipo: int | None = None
    aplicacao_id: str | None = None
    nome: str | None = None
    slug: str | None = None
    preco: dict[str, Any] = field(default_factory=dict)
    taxas_incluidas: bool = False
    parcelas: int | None = None
    sinalizadores: int = 0


@dataclass(slots=True)
class Convite(ModeloDiscord):
    codigo: str | None = None
    servidor_id: str | None = None
    canal_id: str | None = None
    criador: Any = None
    max_age: int = 86400
    max_uses: int = 0
    usos: int = 0
    temporario: bool = False
    expira_em: datetime | None = None
    url: str | None = None


@dataclass(slots=True)
class Integracao(ModeloDiscord):
    id: str | None = None
    nome: str | None = None
    tipo: str | None = None
    servidor_id: str | None = None
    conta: dict[str, Any] = field(default_factory=dict)
    habilitada: bool = True
    sincronizada: bool = False
    usuario_id: str | None = None
    escopos: list[str] = field(default_factory=list)


@dataclass(slots=True)
class WebhookInfo(ModeloDiscord):
    id: str | None = None
    tipo: int | None = None
    nome: str | None = None
    avatar: str | None = None
    token: str | None = None
    servidor_id: str | None = None
    canal_id: str | None = None
    aplicacao_id: str | None = None
    url: str | None = None
    usuario: Usuario | None = None
    servidor_origem: dict[str, Any] | None = None
    canal_origem: dict[str, Any] | None = None


@dataclass(slots=True)
class EventoAgendado(ModeloDiscord):
    id: str | None = None
    servidor_id: str | None = None
    canal_id: str | None = None
    entidade_id: str | None = None
    nome: str | None = None
    descricao: str | None = None
    inicio_em: datetime | None = None
    fim_em: datetime | None = None
    status: int | None = None
    entidade_tipo: int | None = None
    privacidade: int | None = None
    criador_id: str | None = None
    imagem: str | None = None


@dataclass(slots=True)
class InstanciaStage(ModeloDiscord):
    id: str | None = None
    servidor_id: str | None = None
    canal_id: str | None = None
    topico: str | None = None
    descoberta: bool = False
    privacidade: int | None = None


@dataclass(slots=True)
class RegiaoVoz(ModeloDiscord):
    id: str | None = None
    nome: str | None = None
    vip: bool = False
    exemplo: bool = False
    disponivel: bool = True


@dataclass(slots=True)
class SomSoundboard(ModeloDiscord):
    id: str | None = None
    nome: str | None = None
    volume: float | None = None
    emoji_id: str | None = None
    emoji_nome: str | None = None
    servidor_id: str | None = None
    usuario_id: str | None = None

    @classmethod
    def de_dict(cls, dados: dict[str, Any] | None, **extras: Any):
        dados = dict(dados or {})
        return cls(
            id=dados.get("sound_id", dados.get("id")),
            nome=dados.get("name", dados.get("nome")),
            volume=dados.get("volume"),
            emoji_id=dados.get("emoji_id"),
            emoji_nome=dados.get("emoji_name", dados.get("emoji_nome")),
            servidor_id=dados.get("guild_id", dados.get("servidor_id")),
            usuario_id=dados.get("user_id", dados.get("usuario_id")),
            bruto=dados,
        )


@dataclass(slots=True)
class EstadoVoz(ModeloDiscord):
    servidor_id: str | None = None
    canal_id: str | None = None
    usuario_id: str | None = None
    membro: Any = None
    sessao_id: str | None = None
    surdo: bool = False
    surdo_servidor: bool = False
    auto_mudo: bool = False
    mudo_servidor: bool = False
    supressao: bool = False
    video: bool = False
    streaming: bool = False


@dataclass(slots=True)
class Presenca(ModeloDiscord):
    servidor_id: str | None = None
    usuario: Any = None
    status: str | None = None
    atividades: list[dict[str, Any]] = field(default_factory=list)
    cliente_status: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class Reacao(ModeloDiscord):
    contagem: int = 0
    eu_reagi: bool = False
    emoji: EmojiParcial = field(default_factory=EmojiParcial)


@dataclass(slots=True)
class AplicacaoComando(ModeloDiscord):
    id: str | None = None
    tipo: int | None = None
    nome: str | None = None
    descricao: str | None = None
    opcoes: list[dict[str, Any]] = field(default_factory=list)
    servidor_id: str | None = None
    version: str | None = None
    nsfw: bool = False


@dataclass(slots=True)
class IntegracaoAplicacao(ModeloDiscord):
    id: str | None = None
    nome: str | None = None
    tipo: str | None = None
    aplicacao_id: str | None = None
    ativo: bool = True
    sincronizado_em: datetime | None = None


@dataclass(slots=True)
class DireitoAplicacao(ModeloDiscord):
    id: str | None = None
    sku_id: str | None = None
    aplicacao_id: str | None = None
    usuario_id: str | None = None
    tipo: int | None = None
    consumido: bool = False
    criado_em: datetime | None = None


@dataclass(slots=True)
class ModeloServidor(ModeloDiscord):
    codigo: str | None = None
    nome: str | None = None
    descricao: str | None = None
    criador_id: str | None = None
    criador_nome: str | None = None
    uso_count: int = 0
    atualizado_em: datetime | None = None


@dataclass(slots=True)
class TelaBoasVindas(ModeloDiscord):
    descricao: str | None = None
    canais: list[dict[str, Any]] = field(default_factory=list)
    habilitada: bool = True


__all__ = [nome for nome, valor in globals().items() if isinstance(valor, type) and (issubclass(valor, ModeloDiscord) or valor is ModeloDiscord)]


@dataclass(slots=True)
class GatilhoAutomoderacao(ModeloDiscord):
    tipo: int | None = None
    palavra_chave: list[str] = field(default_factory=list)
    regex: list[str] = field(default_factory=list)
    presets: list[int] = field(default_factory=list)
    mencionar_total: int | None = None
    palavras_isentas: list[str] = field(default_factory=list)


@dataclass(slots=True)
class AcaoAutomoderacao(ModeloDiscord):
    tipo: int | None = None
    metadados: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class RegraAutomoderacao(ModeloDiscord):
    id: str | None = None
    servidor_id: str | None = None
    nome: str | None = None
    criador_id: str | None = None
    habilitada: bool = False
    evento_tipo: int | None = None
    gatilho: GatilhoAutomoderacao | None = None
    acoes: list[AcaoAutomoderacao] = field(default_factory=list)
    isenta_cargos: list[str] = field(default_factory=list)
    isenta_canais: list[str] = field(default_factory=list)


@dataclass(slots=True)
class EnqueteResposta(ModeloDiscord):
    id: int | None = None
    texto: str | None = None
    emoji: EmojiParcial | None = None
    votos: int = 0


@dataclass(slots=True)
class Enquete(ModeloDiscord):
    pergunta: str | None = None
    respostas: list[EnqueteResposta] = field(default_factory=list)
    duracao_horas: int | None = None
    encerrada: bool = False
    layout_tipo: int | None = None
    resultados_finais: bool = False


@dataclass(slots=True)
class MetadadoCargo(ModeloDiscord):
    id: str | None = None
    tipo: int | None = None
    nome: str | None = None
    descricao: str | None = None
    obrigatorio: bool = False


@dataclass(slots=True)
class MetadadoConexao(ModeloDiscord):
    tipo: str | None = None
    nome: str | None = None
    descricao: str | None = None
    chave: str | None = None
    tipo_dado: int | None = None
    ordem: int | None = None

    @classmethod
    def de_dict(cls, dados: dict[str, Any] | None, **extras: Any):
        dados = dict(dados or {})
        return cls(
            tipo=dados.get("type", dados.get("tipo")),
            nome=dados.get("name", dados.get("nome")),
            descricao=dados.get("description", dados.get("descricao")),
            chave=dados.get("key", dados.get("chave")),
            tipo_dado=dados.get("value_type", dados.get("tipo_dado")),
            ordem=dados.get("order", dados.get("ordem")),
            bruto=dados,
        )


@dataclass(slots=True)
class ConexaoUsuario(ModeloDiscord):
    id: str | None = None
    nome: str | None = None
    tipo: str | None = None
    revogada: bool = False
    verificada: bool = False
    sincronizacao_amigos: bool = False
    mostrar_atividade: bool = False
    visibilidade: int | None = None
    integracoes: list[Any] = field(default_factory=list)

    @classmethod
    def de_dict(cls, dados: dict[str, Any] | None, **extras: Any):
        dados = dict(dados or {})
        return cls(
            id=dados.get("id"),
            nome=dados.get("name", dados.get("nome")),
            tipo=dados.get("type", dados.get("tipo")),
            revogada=bool(dados.get("revoked", dados.get("revogada", False))),
            verificada=bool(dados.get("verified", dados.get("verificada", False))),
            sincronizacao_amigos=bool(dados.get("friend_sync", dados.get("sincronizacao_amigos", False))),
            mostrar_atividade=bool(dados.get("show_activity", dados.get("mostrar_atividade", False))),
            visibilidade=dados.get("visibility", dados.get("visibilidade")),
            integracoes=list(dados.get("integrations", dados.get("integracoes", [])) or []),
            bruto=dados,
        )
