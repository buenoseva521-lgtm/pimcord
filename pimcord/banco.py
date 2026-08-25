from __future__ import annotations
import sqlite3
from typing import Any, Iterable
class BancoSQLite:
    def __init__(self, caminho: str = ":memory:"): self.caminho = caminho; self.conexao: sqlite3.Connection | None = None
    def conectar(self) -> "BancoSQLite": self.conexao = sqlite3.connect(self.caminho); self.conexao.row_factory = sqlite3.Row; return self
    def _conn(self) -> sqlite3.Connection:
        if self.conexao is None: self.conectar()
        assert self.conexao is not None; return self.conexao
    def executar(self, sql: str, parametros: Iterable[Any] = ()) -> sqlite3.Cursor: return self._conn().execute(sql, tuple(parametros))
    def buscar(self, sql: str, parametros: Iterable[Any] = ()) -> list[dict[str, Any]]: return [dict(x) for x in self.executar(sql, parametros).fetchall()]
    def commit(self) -> None: self._conn().commit()
    def rollback(self) -> None: self._conn().rollback()
    def fechar(self) -> None:
        if self.conexao: self.conexao.close(); self.conexao = None
