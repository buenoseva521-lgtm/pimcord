"""Primitivas de segurança para evitar exposição acidental de credenciais."""
from __future__ import annotations

import logging
import re
from collections.abc import Iterable
from typing import Any


class FiltroSegredos(logging.Filter):
    """Redige valores sensíveis em mensagens e argumentos de um LogRecord."""

    def __init__(self, segredos: Iterable[str] = ()) -> None:
        super().__init__()
        self._segredos = tuple(sorted({segredo for segredo in segredos if len(segredo) >= 6}, key=len, reverse=True))

    def adicionar(self, *segredos: str) -> None:
        self._segredos = tuple(sorted({*self._segredos, *(s for s in segredos if len(s) >= 6)}, key=len, reverse=True))

    def redigir(self, valor: Any) -> str:
        texto = str(valor)
        for segredo in self._segredos:
            texto = texto.replace(segredo, "[REDACTED]")
        texto = re.sub(r"(?i)(token|authorization|senha|password)(\s*[:=]\s*)([^\s,;]+)", r"\1\2[REDACTED]", texto)
        return texto

    def filter(self, registro: logging.LogRecord) -> bool:
        if isinstance(registro.msg, str):
            registro.msg = self.redigir(registro.msg)
        if isinstance(registro.args, dict):
            registro.args = {
                chave: self.redigir(valor) if isinstance(valor, str) else valor
                for chave, valor in registro.args.items()
            }
        elif isinstance(registro.args, tuple):
            registro.args = tuple(
                self.redigir(valor) if isinstance(valor, str) else valor
                for valor in registro.args
            )
        if registro.exc_info:
            registro.exc_text = None
        return True


def token_redigido(token: str | None) -> str:
    """Retorna uma representação segura para diagnóstico, sem revelar o token."""
    if not token:
        return "[ausente]"
    if len(token) < 8:
        return "[REDACTED]"
    return f"{token[:3]}…{token[-3:]}"


__all__ = ["FiltroSegredos", "token_redigido"]
