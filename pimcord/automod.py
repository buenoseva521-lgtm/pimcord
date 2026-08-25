"""Motor offline-first de automoderação e tickets do Pimcord.

O motor decide e registra localmente; a aplicação escolhe como executar a ação
no Discord. Isso mantém testes determinísticos e evita punições acidentais sem
permissões explícitas.
"""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any, Iterable


class AcaoModeracao(StrEnum):
    AVISAR = "avisar"
    APAGAR = "apagar"
    SILENCIAR = "silenciar"
    EXPULSAR = "expulsar"
    BANIR = "banir"
    BLOQUEAR = "bloquear"


@dataclass(slots=True, frozen=True)
class RegraModeracao:
    """Regra local; padrões são comparados após normalização de texto."""

    nome: str
    padroes: tuple[str, ...]
    acao: AcaoModeracao = AcaoModeracao.AVISAR
    motivo: str = "Violação de regra de automoderação"
    habilitada: bool = True
    regex: bool = False
    abrir_ticket: bool = True

    def __post_init__(self) -> None:
        if not self.nome.strip():
            raise ValueError("nome da regra não pode ser vazio")
        if not self.padroes:
            raise ValueError("a regra precisa de pelo menos um padrão")
        if any(not str(padrao).strip() for padrao in self.padroes):
            raise ValueError("padrões vazios não são permitidos")


@dataclass(slots=True, frozen=True)
class DecisaoModeracao:
    detectada: bool
    regra: str | None = None
    acao: AcaoModeracao | None = None
    motivo: str | None = None
    correspondencia: str | None = None


@dataclass(slots=True, frozen=True)
class RegistroModeracao:
    criado_em: datetime
    servidor_id: str | None
    canal_id: str | None
    mensagem_id: str | None
    usuario_id: str | None
    decisao: DecisaoModeracao


@dataclass(slots=True)
class TicketModeracao:
    id: int
    registro: RegistroModeracao
    status: str = "aberto"
    observacoes: list[str] = field(default_factory=list)

    def fechar(self, observacao: str | None = None) -> None:
        self.status = "fechado"
        if observacao:
            self.observacoes.append(observacao)


def normalizar_texto(texto: str) -> str:
    """Remove variações Unicode e espaços para reduzir evasões triviais."""
    texto = unicodedata.normalize("NFKC", str(texto)).casefold()
    texto = "".join(
        caractere for caractere in unicodedata.normalize("NFKD", texto)
        if not unicodedata.combining(caractere)
    )
    return re.sub(r"\s+", " ", texto).strip()


class MotorAutomoderacao:
    """Avalia mensagens sem rede e conserva evidências de cada decisão."""

    def __init__(self, regras: Iterable[RegraModeracao] | None = None) -> None:
        self.regras: dict[str, RegraModeracao] = {}
        self.registros: list[RegistroModeracao] = []
        self.tickets: dict[int, TicketModeracao] = {}
        self._proximo_ticket = 1
        for regra in regras or ():
            self.adicionar_regra(regra)

    def adicionar_regra(self, regra: RegraModeracao) -> RegraModeracao:
        if regra.nome in self.regras:
            raise ValueError(f"regra já cadastrada: {regra.nome}")
        self.regras[regra.nome] = regra
        return regra

    def remover_regra(self, nome: str) -> RegraModeracao | None:
        return self.regras.pop(nome, None)

    def avaliar(self, conteudo: str, *, servidor_id: str | None = None, canal_id: str | None = None, mensagem_id: str | None = None, usuario_id: str | None = None) -> DecisaoModeracao:
        texto = normalizar_texto(conteudo)
        for regra in self.regras.values():
            if not regra.habilitada:
                continue
            for bruto in regra.padroes:
                padrao = normalizar_texto(bruto)
                encontrou = re.search(padrao, texto) if regra.regex else (padrao in texto)
                if encontrou:
                    decisao = DecisaoModeracao(True, regra.nome, regra.acao, regra.motivo, encontrou.group(0) if hasattr(encontrou, "group") else padrao)
                    registro = RegistroModeracao(datetime.now(timezone.utc), servidor_id, canal_id, mensagem_id, usuario_id, decisao)
                    self.registros.append(registro)
                    if regra.abrir_ticket:
                        ticket = TicketModeracao(self._proximo_ticket, registro)
                        self.tickets[ticket.id] = ticket
                        self._proximo_ticket += 1
                    return decisao
        return DecisaoModeracao(False)

    def tickets_abertos(self) -> list[TicketModeracao]:
        return [ticket for ticket in self.tickets.values() if ticket.status == "aberto"]

    def exportar_logs(self) -> list[dict[str, Any]]:
        return [
            {
                "criado_em": registro.criado_em.isoformat(),
                "servidor_id": registro.servidor_id,
                "canal_id": registro.canal_id,
                "mensagem_id": registro.mensagem_id,
                "usuario_id": registro.usuario_id,
                "regra": registro.decisao.regra,
                "acao": registro.decisao.acao.value if registro.decisao.acao else None,
                "motivo": registro.decisao.motivo,
                "correspondencia": registro.decisao.correspondencia,
            }
            for registro in self.registros
        ]


__all__ = [
    "AcaoModeracao",
    "DecisaoModeracao",
    "MotorAutomoderacao",
    "RegraModeracao",
    "RegistroModeracao",
    "TicketModeracao",
    "normalizar_texto",
]
