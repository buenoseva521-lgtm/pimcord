"""Abstrações de permissões e sobrescritas por canal do Pimcord.

A API pública usa nomes em português, mas serializa os bits no formato exigido
pelo Discord. A classe não faz chamadas de rede; ela apenas representa a regra.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any
from .nucleo import Permissoes

@dataclass(frozen=True, slots=True)
class SobrescritaPermissao:
    """Regra de permissão para um cargo ou usuário em um canal."""
    alvo_id: str
    permitir: Permissoes = Permissoes(0)
    negar: Permissoes = Permissoes(0)
    tipo: int = 0

    @classmethod
    def cargo(cls, cargo_id: str, *, permitir: Permissoes = Permissoes(0), negar: Permissoes = Permissoes(0)) -> "SobrescritaPermissao":
        return cls(str(cargo_id), permitir, negar, 0)

    @classmethod
    def usuario(cls, usuario_id: str, *, permitir: Permissoes = Permissoes(0), negar: Permissoes = Permissoes(0)) -> "SobrescritaPermissao":
        return cls(str(usuario_id), permitir, negar, 1)

    def para_dict(self) -> dict[str, Any]:
        return {"id": self.alvo_id, "type": self.tipo, "allow": str(int(self.permitir)), "deny": str(int(self.negar))}

__all__ = ["Permissoes", "SobrescritaPermissao"]
