"""Recurso de economia local para projetos Pimcord.

A classe usa somente SQLite parametrizado e não conhece Discord; o bot gerado
pode adaptá-la aos seus comandos sem permitir SQL vindo da descrição do usuário.
"""
from __future__ import annotations

import time
from typing import Any

from .banco import BancoSQLite


class EconomiaSQLite:
    def __init__(self, caminho: str = "economia.sqlite3", *, saldo_inicial: int = 0, diaria: int = 100):
        self.banco = BancoSQLite(caminho).conectar()
        self.saldo_inicial = saldo_inicial
        self.valor_diaria = diaria
        self.banco.executar(
            "CREATE TABLE IF NOT EXISTS economia_usuarios (usuario_id TEXT PRIMARY KEY, saldo INTEGER NOT NULL DEFAULT 0, ultima_diaria REAL)"
        )
        self.banco.commit()

    def _garantir(self, usuario_id: str) -> None:
        self.banco.executar(
            "INSERT OR IGNORE INTO economia_usuarios (usuario_id, saldo, ultima_diaria) VALUES (?, ?, NULL)",
            (str(usuario_id), self.saldo_inicial),
        )
        self.banco.commit()

    def saldo(self, usuario_id: str) -> int:
        self._garantir(usuario_id)
        linha = self.banco.buscar("SELECT saldo FROM economia_usuarios WHERE usuario_id = ?", (str(usuario_id),))[0]
        return int(linha["saldo"])

    def diaria(self, usuario_id: str, *, agora: float | None = None) -> int:
        agora = time.time() if agora is None else agora
        self._garantir(usuario_id)
        linhas = self.banco.buscar("SELECT saldo, ultima_diaria FROM economia_usuarios WHERE usuario_id = ?", (str(usuario_id),))
        linha = linhas[0]
        ultima = linha["ultima_diaria"]
        if ultima is not None and agora - float(ultima) < 86400:
            raise ValueError("A recompensa diária ainda está em cooldown.")
        novo_saldo = int(linha["saldo"]) + self.valor_diaria
        self.banco.executar("UPDATE economia_usuarios SET saldo = ?, ultima_diaria = ? WHERE usuario_id = ?", (novo_saldo, agora, str(usuario_id)))
        self.banco.commit()
        return novo_saldo

    def transferir(self, remetente: str, destinatario: str, valor: int) -> tuple[int, int]:
        if not isinstance(valor, int) or isinstance(valor, bool) or valor <= 0:
            raise ValueError("O valor precisa ser um inteiro positivo.")
        if str(remetente) == str(destinatario):
            raise ValueError("Não é possível transferir para si mesmo.")
        self._garantir(remetente)
        self._garantir(destinatario)
        origem = self.saldo(remetente)
        if origem < valor:
            raise ValueError("Saldo insuficiente.")
        self.banco.executar("UPDATE economia_usuarios SET saldo = saldo - ? WHERE usuario_id = ?", (valor, str(remetente)))
        self.banco.executar("UPDATE economia_usuarios SET saldo = saldo + ? WHERE usuario_id = ?", (valor, str(destinatario)))
        self.banco.commit()
        return self.saldo(remetente), self.saldo(destinatario)

    def ranking(self, limite: int = 10) -> list[dict[str, Any]]:
        if not isinstance(limite, int) or limite <= 0 or limite > 100:
            raise ValueError("O limite deve estar entre 1 e 100.")
        return self.banco.buscar("SELECT usuario_id, saldo FROM economia_usuarios ORDER BY saldo DESC, usuario_id ASC LIMIT ?", (limite,))

    def fechar(self) -> None:
        self.banco.fechar()


__all__ = ["EconomiaSQLite"]
