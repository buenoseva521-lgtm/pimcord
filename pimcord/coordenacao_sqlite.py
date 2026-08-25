"""Coordenação persistente de workers usando SQLite da biblioteca padrão.

O transporte é adequado para múltiplos processos no mesmo dispositivo, inclusive
Pydroid/Termux. Ele não tenta substituir Redis em escala distribuída; usa WAL,
transação IMMEDIATE e expiração por relógio monotônico para impedir dupla posse
em um mesmo host durante falhas de processo.
"""
from __future__ import annotations

import json
import sqlite3
import time
from pathlib import Path
from typing import Any

from .coordenacao import Lease


class CoordenaçãoSQLite:
    """Implementa ``TransporteCoordenação`` com um arquivo SQLite compartilhado."""

    def __init__(self, caminho: str | Path):
        self.caminho = str(caminho)
        if self.caminho != ":memory:":
            Path(self.caminho).parent.mkdir(parents=True, exist_ok=True)
        self._preparar()

    def _conectar(self) -> sqlite3.Connection:
        conexao = sqlite3.connect(self.caminho, timeout=10.0)
        conexao.row_factory = sqlite3.Row
        conexao.execute("PRAGMA busy_timeout=10000")
        conexao.execute("PRAGMA journal_mode=WAL")
        return conexao

    def _preparar(self) -> None:
        with self._conectar() as conexao:
            conexao.executescript(
                """
                CREATE TABLE IF NOT EXISTS pimcord_leases (
                    chave TEXT PRIMARY KEY,
                    trabalhador TEXT NOT NULL,
                    epoca INTEGER NOT NULL,
                    expira_em REAL NOT NULL
                );
                CREATE TABLE IF NOT EXISTS pimcord_estados (
                    chave TEXT PRIMARY KEY,
                    estado_json TEXT NOT NULL
                );
                """
            )

    async def adquirir(self, chave: str, trabalhador: str, *, duração: float = 30.0) -> Lease | None:
        if duração <= 0:
            raise ValueError("duração do lease deve ser positiva")
        agora = time.monotonic()
        with self._conectar() as conexao:
            conexao.execute("BEGIN IMMEDIATE")
            atual = conexao.execute("SELECT * FROM pimcord_leases WHERE chave = ?", (chave,)).fetchone()
            if atual and atual["expira_em"] > agora and atual["trabalhador"] != trabalhador:
                return None
            epoca = int(atual["epoca"] if atual else 0) + 1
            lease = Lease(chave, trabalhador, epoca, agora + duração)
            conexao.execute(
                "INSERT INTO pimcord_leases(chave, trabalhador, epoca, expira_em) VALUES (?, ?, ?, ?) "
                "ON CONFLICT(chave) DO UPDATE SET trabalhador=excluded.trabalhador, epoca=excluded.epoca, expira_em=excluded.expira_em",
                (lease.chave, lease.trabalhador, lease.época, lease.expira_em),
            )
            return lease

    async def renovar(self, lease: Lease, *, duração: float = 30.0) -> Lease | None:
        if duração <= 0:
            raise ValueError("duração do lease deve ser positiva")
        expira = time.monotonic() + duração
        with self._conectar() as conexao:
            cursor = conexao.execute(
                "UPDATE pimcord_leases SET expira_em = ? WHERE chave = ? AND trabalhador = ? AND epoca = ? AND expira_em > ?",
                (expira, lease.chave, lease.trabalhador, lease.época, time.monotonic()),
            )
            if cursor.rowcount != 1:
                return None
            return Lease(lease.chave, lease.trabalhador, lease.época, expira)

    async def liberar(self, lease: Lease) -> bool:
        with self._conectar() as conexao:
            cursor = conexao.execute(
                "DELETE FROM pimcord_leases WHERE chave = ? AND trabalhador = ? AND epoca = ?",
                (lease.chave, lease.trabalhador, lease.época),
            )
            return cursor.rowcount == 1

    async def publicar(self, chave: str, estado: dict[str, Any]) -> None:
        texto = json.dumps(estado, ensure_ascii=False, sort_keys=True)
        with self._conectar() as conexao:
            conexao.execute(
                "INSERT INTO pimcord_estados(chave, estado_json) VALUES (?, ?) "
                "ON CONFLICT(chave) DO UPDATE SET estado_json=excluded.estado_json",
                (chave, texto),
            )

    async def estados(self) -> dict[str, dict[str, Any]]:
        with self._conectar() as conexao:
            linhas = conexao.execute("SELECT chave, estado_json FROM pimcord_estados").fetchall()
        return {str(linha["chave"]): json.loads(linha["estado_json"]) for linha in linhas}

    async def expurgar(self) -> int:
        with self._conectar() as conexao:
            cursor = conexao.execute("DELETE FROM pimcord_leases WHERE expira_em <= ?", (time.monotonic(),))
            return int(cursor.rowcount)

    def fechar(self) -> None:
        """Mantido por compatibilidade; cada operação abre sua própria conexão."""
        return None


__all__ = ["CoordenaçãoSQLite"]
