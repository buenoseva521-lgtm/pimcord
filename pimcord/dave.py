"""Negociação DAVE/MLS com backend criptográfico injetável.

Este módulo implementa somente a máquina de protocolo e o enquadramento das
mensagens. A criptografia MLS/DAVE real continua delegada a um backend externo
compatível; nenhum algoritmo parcial é apresentado como E2EE completo.
"""
from __future__ import annotations

import struct
from dataclasses import dataclass
from enum import IntEnum, StrEnum
from typing import Protocol, FrozenSet


class OpcodeDAVE(IntEnum):
    PREPARAR_TRANSICAO = 21
    EXECUTAR_TRANSICAO = 22
    PRONTO_PARA_TRANSICAO = 23
    PREPARAR_EPOCA = 24
    REMETENTE_EXTERNO = 25
    PACOTE_CHAVE = 26
    PROPOSTAS = 27
    COMMIT_WELCOME = 28
    ANUNCIAR_COMMIT = 29
    WELCOME = 30
    COMMIT_WELCOME_INVALIDO = 31


class TipoMensagemMLS(StrEnum):
    """Tipos explícitos aceitos pela sessão DAVE/libdave."""

    PROPOSTAS = "propostas"
    COMMIT = "commit"
    WELCOME = "welcome"


@dataclass(frozen=True, slots=True)
class MensagemMLSDAVE:
    """Envelope semântico para impedir dispatch MLS por adivinhação de bytes."""

    tipo: TipoMensagemMLS
    dados: bytes
    usuarios_reconhecidos: FrozenSet[str] = frozenset()

    def __post_init__(self) -> None:
        if not self.dados:
            raise ValueError("Mensagem MLS vazia")
        if any(not isinstance(usuario, str) or not usuario for usuario in self.usuarios_reconhecidos):
            raise ValueError("usuarios_reconhecidos deve conter IDs não vazios")


class BackendDAVE(Protocol):
    versao_maxima: int

    def gerar_key_package(self) -> bytes: ...
    def processar_mensagem_mls(self, dados: bytes) -> None: ...
    def preparar_epoca(self, epoca: int) -> None: ...
    def exportar_chave_remetente(self, remetente_id: str) -> bytes: ...


class BackendDAVEEnvelope(Protocol):
    """Operações semânticas exigidas para encaminhar mensagens MLS com segurança."""

    def processar_propostas(self, dados: bytes) -> None: ...
    def processar_commit(self, dados: bytes) -> None: ...
    def processar_welcome(self, dados: bytes) -> None: ...


class BackendDAVEReal(BackendDAVE, BackendDAVEEnvelope, Protocol):
    """Contrato adicional exigido por um adaptador E2EE realmente integrado.

    Declarar este protocolo não implementa criptografia. Ele apenas torna visível
    a superfície que um binding libdave auditado precisa fornecer antes que o
    Pimcord possa habilitar mídia protegida.
    """

    e2ee_real: bool

    def cifrar_frame(self, remetente_id: str, frame: bytes) -> bytes: ...
    def decifrar_frame(self, remetente_id: str, frame: bytes) -> bytes: ...
    def autenticador_epoca(self, epoca: int, dados: bytes) -> bytes: ...


@dataclass(frozen=True, slots=True)
class MensagemDAVE:
    opcode: OpcodeDAVE
    payload: bytes = b""
    sequencia: int | None = None

    def serializar(self) -> bytes:
        prefixo = struct.pack(">H", self.sequencia & 0xFFFF) if self.sequencia is not None else b""
        return prefixo + bytes([int(self.opcode)]) + self.payload

    @classmethod
    def desserializar(cls, dados: bytes, *, tem_sequencia: bool = False) -> "MensagemDAVE":
        deslocamento = 0
        sequencia = None
        if tem_sequencia:
            if len(dados) < 3:
                raise ValueError("Mensagem DAVE binária truncada")
            sequencia = struct.unpack(">H", dados[:2])[0]
            deslocamento = 2
        if len(dados) <= deslocamento:
            raise ValueError("Mensagem DAVE sem opcode")
        try:
            opcode = OpcodeDAVE(dados[deslocamento])
        except ValueError as erro:
            raise ValueError(f"Opcode DAVE desconhecido: {dados[deslocamento]}") from erro
        return cls(opcode, dados[deslocamento + 1 :], sequencia)


def validar_backend_dave(backend: BackendDAVE) -> BackendDAVE:
    """Valida a capacidade mínima de um backend MLS/DAVE injetado.

    A função não implementa criptografia; ela evita que um adaptador incompleto
    seja aceito silenciosamente e falhe no meio de uma transição de época.
    """
    versao = getattr(backend, "versao_maxima", None)
    if not isinstance(versao, int) or versao < 1:
        raise TypeError("backend DAVE deve expor versao_maxima inteira positiva")
    obrigatorios = ("gerar_key_package", "processar_mensagem_mls", "preparar_epoca", "exportar_chave_remetente")
    ausentes = [nome for nome in obrigatorios if not callable(getattr(backend, nome, None))]
    if ausentes:
        raise TypeError(f"backend DAVE incompleto; faltam: {', '.join(ausentes)}")
    return backend


def exigir_backend_dave_real(backend: BackendDAVE) -> BackendDAVE:
    """Exige marcadores explícitos de um backend E2EE, sem aceitar simuladores."""
    validar_backend_dave(backend)
    if getattr(backend, "e2ee_real", False) is not True:
        raise TypeError("backend DAVE não foi declarado como E2EE real; use um adaptador MLS auditado")
    obrigatorios = (
        "cifrar_frame",
        "decifrar_frame",
        "autenticador_epoca",
        "processar_propostas",
        "processar_commit",
        "processar_welcome",
    )
    ausentes = [nome for nome in obrigatorios if not callable(getattr(backend, nome, None))]
    if ausentes:
        raise TypeError(f"backend DAVE E2EE incompleto; faltam: {', '.join(ausentes)}")
    return backend


class EstadoDAVE:
    """Máquina de transição DAVE sem operações criptográficas embutidas."""
    def __init__(self, backend: BackendDAVE):
        self.backend = validar_backend_dave(backend)
        self.versao = 0
        self.epoca = 0
        self.transicao_id: int | None = None
        self.pronto = False
        self.em_transicao = False

    def identificar(self) -> dict[str, int]:
        return {"max_dave_protocol_version": int(self.backend.versao_maxima)}

    def receber_preparacao(self, *, versao: int, epoca: int, transicao_id: int) -> bytes | None:
        if versao <= 0 or versao > self.backend.versao_maxima:
            raise ValueError(f"Versão DAVE não suportada: {versao}")
        if epoca < 1:
            raise ValueError("A época DAVE deve ser positiva")
        if epoca < self.epoca:
            raise ValueError("Época DAVE antiga foi rejeitada")
        if epoca == self.epoca and self.transicao_id is not None and transicao_id != self.transicao_id:
            raise ValueError("Transição DAVE conflitante para a época atual")
        self.versao = versao
        self.epoca = epoca
        self.transicao_id = transicao_id
        self.em_transicao = True
        self.pronto = False
        if epoca == 1:
            return self.backend.gerar_key_package()
        self.backend.preparar_epoca(epoca)
        return None

    def receber_mensagem_mls(self, dados: bytes) -> None:
        if not dados:
            raise ValueError("Mensagem MLS vazia")
        self.backend.processar_mensagem_mls(dados)

    def receber_remetente_externo(self, dados: bytes) -> None:
        """Entrega o pacote de external sender ao backend nativo.

        O envelope interno é deliberadamente opaco: o formato pertence ao
        protocolo DAVE/MLS e não pode ser inferido com segurança pelo cliente.
        """
        if not dados:
            raise ValueError("Pacote de remetente externo vazio")
        metodo = getattr(self.backend, "processar_remetente_externo", None)
        if not callable(metodo):
            raise TypeError("backend DAVE não expõe processar_remetente_externo")
        metodo(dados)

    def receber_propostas(self, dados: bytes) -> None:
        if not dados:
            raise ValueError("Propostas MLS vazias")
        metodo = getattr(self.backend, "processar_propostas", None)
        if not callable(metodo):
            raise TypeError("backend DAVE não expõe processar_propostas")
        metodo(dados)

    def receber_commit(self, dados: bytes) -> None:
        if not dados:
            raise ValueError("Commit MLS vazio")
        metodo = getattr(self.backend, "processar_commit", None)
        if not callable(metodo):
            raise TypeError("backend DAVE não expõe processar_commit")
        metodo(dados)

    def receber_welcome(self, dados: bytes) -> None:
        if not dados:
            raise ValueError("Welcome MLS vazio")
        metodo = getattr(self.backend, "processar_welcome", None)
        if not callable(metodo):
            raise TypeError("backend DAVE não expõe processar_welcome")
        metodo(dados)

    def receber_mensagem_mls_tipada(self, mensagem: MensagemMLSDAVE) -> None:
        """Encaminha MLS pelo tipo explícito, sem adivinhar o conteúdo binário."""
        if not isinstance(mensagem, MensagemMLSDAVE):
            raise TypeError("mensagem deve ser MensagemMLSDAVE")
        metodos = {
            TipoMensagemMLS.PROPOSTAS: "processar_propostas",
            TipoMensagemMLS.COMMIT: "processar_commit",
            TipoMensagemMLS.WELCOME: "processar_welcome",
        }
        metodo = getattr(self.backend, metodos[mensagem.tipo], None)
        if not callable(metodo):
            raise TypeError(
                f"backend DAVE não expõe o processador semântico de {mensagem.tipo.value}"
            )
        metodo(mensagem.dados)

    def exportar_chave_remetente(self, remetente_id: str) -> bytes:
        if self.epoca < 1 or self.em_transicao:
            raise RuntimeError("A sessão DAVE ainda não está estabelecida")
        return self.backend.exportar_chave_remetente(remetente_id)

    def marcar_pronto(self) -> MensagemDAVE:
        if not self.em_transicao or self.transicao_id is None:
            raise RuntimeError("Nenhuma transição DAVE foi preparada")
        self.pronto = True
        return MensagemDAVE(OpcodeDAVE.PRONTO_PARA_TRANSICAO, struct.pack(">I", self.transicao_id))

    def executar(self, *, transicao_id: int) -> None:
        if transicao_id != self.transicao_id:
            raise ValueError("transicao_id DAVE inesperado")
        if not self.pronto:
            raise RuntimeError("A sessão ainda não está pronta para a transição DAVE")
        self.em_transicao = False


__all__ = ["OpcodeDAVE", "TipoMensagemMLS", "MensagemMLSDAVE", "BackendDAVE", "BackendDAVEEnvelope", "BackendDAVEReal", "MensagemDAVE", "EstadoDAVE", "validar_backend_dave", "exigir_backend_dave_real"]
