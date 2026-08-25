"""Métricas leves e diagnóstico do Pimcord."""
from __future__ import annotations

from dataclasses import dataclass, field
from time import monotonic


@dataclass
class Metricas:
    inicio: float = field(default_factory=monotonic)
    mensagens: int = 0
    comandos: int = 0
    erros: int = 0
    reconexoes: int = 0
    eventos: dict[str, int] = field(default_factory=dict)

    def contar_evento(self, nome: str) -> None:
        self.eventos[nome] = self.eventos.get(nome, 0) + 1

    def snapshot(self) -> dict[str, object]:
        return {
            "tempo_ativo": round(monotonic() - self.inicio, 3),
            "mensagens": self.mensagens,
            "comandos": self.comandos,
            "erros": self.erros,
            "reconexoes": self.reconexoes,
            "eventos": dict(self.eventos),
        }
