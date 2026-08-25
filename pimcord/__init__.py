"""Pimcord: framework assíncrono em português para bots Discord."""
from .nucleo import (
    PimcordErro, ErroDeConfiguracao, ErroDeConexao, ErroDeAutenticacao,
    ErroDePermissao, ComandoNaoEncontrado, ComandoInvalido,
    InteracaoExpirada, RateLimitado, ErroDaAPI, ErroDoGateway,
    Permissoes, Intents, Configuracao, Embed, Contexto, Botao, View, Select,
    OpcaoSelect, EntradaModal, Modal, UploadArquivos,
)
from .bot import Bot, Cache, Tarefa, OpcaoSlash
from .pronto import ErroBotPronto, DefinicaoBot, DefinicaoComando, interpretar, construir, construir_plano, construir_com_ia, bot_pronto
from .ia import ErroGeradorIA, SCHEMA_PLANO_BOT, CATALOGO_PIMCORD, validar_plano, PimcordIA, IAIntegradaPimcord, GeradorPlanoIA
from .modelo_proprio import ErroModeloProprio, TokenizadorBytes, criar_modelo, carregar_checkpoint, gerar_texto
from .projeto_ia import ErroProjetoIA, SCHEMA_PROJETO_BOT, validar_projeto, ProjetoGerado, AgenteConstrutorPimcord, GeradorProjetoIA, criar_projeto_ia
from .banco import BancoSQLite
from .economia import EconomiaSQLite
from .interacoes.modelos import Interacao
from .discord.modelos import Usuario, Membro, Cargo, Anexo, Canal, Servidor, Mensagem
from .discord.recursos import (
    ModeloDiscord, Emoji, EmojiParcial, Adesivo, MetadadosThread, MembroThread,
    TagForum, CanalCompleto, Banimento, AlteracaoAuditoria, OpcaoAuditoria, EntradaAuditoria, RegistroAuditoria, Entitlement, AssinaturaAplicacao, SkuAplicacao,
    Convite, Integracao, WebhookInfo, EventoAgendado, InstanciaStage, RegiaoVoz,
    SomSoundboard, EstadoVoz, Presenca, Reacao, AplicacaoComando,
    IntegracaoAplicacao, DireitoAplicacao,     ModeloServidor, TelaBoasVindas, GatilhoAutomoderacao, AcaoAutomoderacao,
    RegraAutomoderacao, EnqueteResposta, Enquete, MetadadoCargo, MetadadoConexao, ConexaoUsuario,

)
from .comandos import limitar, verificar, autocomplete, GrupoDeComandos
from .extensoes import Extensao, GerenciadorDeExtensoes
from .webhooks import Webhook
from .http import ClienteHTTP
from .oauth2 import ClienteOAuth2, TokenOAuth2, URL_AUTORIZACAO, URL_TOKEN, URL_REVOGACAO
from .gateway import Gateway, EVENTOS_PORTUGUES, EVENTOS_DISCORD, MODELOS_EVENTO, modelar_evento
from .sharding import ShardInfo, GerenciadorDeShards
from .coordenacao import Lease, TransporteCoordenação, CoordenaçãoLocal
from .coordenacao_sqlite import CoordenaçãoSQLite
from .dave import OpcodeDAVE, TipoMensagemMLS, MensagemMLSDAVE, BackendDAVE, BackendDAVEEnvelope, BackendDAVEReal, MensagemDAVE, EstadoDAVE, validar_backend_dave, exigir_backend_dave_real
from .adaptador_dave import AdaptadorDAVEPy
from .seguranca import FiltroSegredos, token_redigido
from .automod import AcaoModeracao, DecisaoModeracao, MotorAutomoderacao, RegraModeracao, RegistroModeracao, TicketModeracao, normalizar_texto
from .permissoes import SobrescritaPermissao
from .simulador import Simulador, RegistroSimulado
from .saude import Verificacao, RelatorioSaude, diagnosticar
from .voz import InformacoesVoz, PacoteRTP, BufferJitter, TransporteUDP, SessaoVoz, ClienteGatewayVoz, FontePCM, FonteSilencio, FonteWAV, GravadorWAV, InterpoladorPCM, MisturadorPCM, ProcessadorPCMRecebido, CodificadorIdentidade, CodificadorOpus, CriptografiaVozOpcional, FilaAudio
from .tarefas import PoliticaRetentativa, TarefaAgendada, Agendador, FilaAssincrona
from .extensoes import Extensao, GerenciadorDeExtensoes

__version__ = "0.6.9"
__all__ = [
    "Bot", "OpcaoSlash", "bot_pronto", "ErroBotPronto", "DefinicaoBot", "DefinicaoComando", "interpretar", "construir", "construir_plano", "construir_com_ia", "ErroGeradorIA", "SCHEMA_PLANO_BOT", "CATALOGO_PIMCORD", "validar_plano", "PimcordIA", "IAIntegradaPimcord", "GeradorPlanoIA", "ErroModeloProprio", "TokenizadorBytes", "criar_modelo", "carregar_checkpoint", "gerar_texto", "ErroProjetoIA", "SCHEMA_PROJETO_BOT", "validar_projeto", "ProjetoGerado", "AgenteConstrutorPimcord", "GeradorProjetoIA", "criar_projeto_ia", "Configuracao", "Intents", "Permissoes", "Embed", "Contexto",
    "View", "Botao", "Select", "OpcaoSelect", "EntradaModal", "Modal", "UploadArquivos", "Cache", "Tarefa", "BancoSQLite", "EconomiaSQLite", "Interacao",
    "limitar", "verificar", "autocomplete", "GrupoDeComandos", "Extensao",
    "GerenciadorDeExtensoes", "OpcodeDAVE", "TipoMensagemMLS", "MensagemMLSDAVE", "BackendDAVE", "BackendDAVEEnvelope", "BackendDAVEReal", "AdaptadorDAVEPy", "MensagemDAVE", "EstadoDAVE", "validar_backend_dave", "exigir_backend_dave_real", "Usuario", "Membro", "Cargo", "Anexo",
    "Canal", "Servidor", "Mensagem", "Webhook", "ShardInfo", "GerenciadorDeShards", "Lease", "TransporteCoordenação", "CoordenaçãoLocal", "CoordenaçãoSQLite", "FiltroSegredos", "token_redigido", "SobrescritaPermissao",
    "AcaoModeracao", "DecisaoModeracao", "MotorAutomoderacao", "RegraModeracao", "RegistroModeracao", "TicketModeracao", "normalizar_texto",
    "ModeloDiscord", "Emoji", "EmojiParcial", "Adesivo", "MetadadosThread", "MembroThread", "AlteracaoAuditoria", "OpcaoAuditoria", "Entitlement", "AssinaturaAplicacao", "SkuAplicacao",
    "TagForum", "CanalCompleto", "Banimento", "EntradaAuditoria", "RegistroAuditoria", "Convite",
    "Integracao", "WebhookInfo", "EventoAgendado", "InstanciaStage", "RegiaoVoz", "SomSoundboard",
    "EstadoVoz", "Presenca", "Reacao", "AplicacaoComando", "IntegracaoAplicacao", "DireitoAplicacao",
    "ModeloServidor", "TelaBoasVindas", "GatilhoAutomoderacao", "AcaoAutomoderacao",
    "ClienteHTTP", "ClienteOAuth2", "TokenOAuth2", "URL_AUTORIZACAO", "URL_TOKEN", "URL_REVOGACAO", "Gateway", "EVENTOS_PORTUGUES", "EVENTOS_DISCORD", "MODELOS_EVENTO", "modelar_evento",
    "RegraAutomoderacao", "EnqueteResposta", "Enquete", "MetadadoCargo", "MetadadoConexao", "ConexaoUsuario",
    "Simulador", "RegistroSimulado", "Verificacao", "RelatorioSaude", "diagnosticar",
    "InformacoesVoz", "PacoteRTP", "BufferJitter", "TransporteUDP", "SessaoVoz", "ClienteGatewayVoz", "FontePCM", "FonteSilencio", "FonteWAV", "GravadorWAV", "InterpoladorPCM", "MisturadorPCM", "ProcessadorPCMRecebido", "CodificadorIdentidade", "CodificadorOpus", "CriptografiaVozOpcional", "FilaAudio",
    "PoliticaRetentativa", "TarefaAgendada", "Agendador", "FilaAssincrona", "Extensao", "GerenciadorDeExtensoes",
]
