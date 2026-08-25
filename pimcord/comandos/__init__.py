"""Sistema de comandos avançados do Pimcord."""
from __future__ import annotations

import inspect
import time
from dataclasses import dataclass, field
from typing import Any, Awaitable, Callable, get_args, get_origin, get_type_hints
from ..nucleo import ComandoInvalido, ErroDePermissao

Callback = Callable[..., Awaitable[Any]]

@dataclass(slots=True)
class Cooldown:
    chamadas: int
    por: float
    _usos: dict[str, list[float]] = field(default_factory=dict)
    def verificar(self, chave: str) -> bool:
        agora = time.monotonic()
        usos = [t for t in self._usos.get(chave, []) if agora - t < self.por]
        if len(usos) >= self.chamadas:
            self._usos[chave] = usos
            return False
        usos.append(agora); self._usos[chave] = usos
        return True

def limitar(chamadas: int, por: float) -> Callable[[Callback], Callback]:
    def decorar(callback: Callback) -> Callback:
        setattr(callback, "__pimcord_cooldown__", Cooldown(chamadas, por)); return callback
    return decorar

def autocomplete(funcao: Callable[[Any], Any]) -> Callable[[Callback], Callback]:
    """Marca uma função que fornece sugestões para uma opção slash."""
    def decorar(callback: Callback) -> Callback:
        setattr(callback, "__pimcord_autocomplete__", funcao)
        return callback
    return decorar


def verificar(check: Callable[[Any], bool | Awaitable[bool]]) -> Callable[[Callback], Callback]:
    def decorar(callback: Callback) -> Callback:
        checks = list(getattr(callback, "__pimcord_checks__", [])); checks.append(check)
        setattr(callback, "__pimcord_checks__", checks); return callback
    return decorar

def converter(tipo: type) -> Callable[[str], Any]:
    if tipo is str: return str
    if tipo is int: return int
    if tipo is float: return float
    if tipo is bool: return lambda valor: valor.lower() in {"1", "sim", "true", "verdadeiro", "on"}
    return tipo

async def preparar_argumentos(callback: Callback, argumentos: tuple[str, ...]) -> tuple[Any, ...]:
    assinatura = inspect.signature(callback); parametros = list(assinatura.parameters.values())[1:]
    hints = get_type_hints(callback); resultado: list[Any] = []; posicao = 0
    for parametro in parametros:
        tipo = hints.get(parametro.name, str); origem = get_origin(tipo)
        if origem is not None and type(None) in get_args(tipo): tipo = next((x for x in get_args(tipo) if x is not type(None)), str)
        if parametro.kind is parametro.VAR_POSITIONAL:
            while posicao < len(argumentos):
                try: resultado.append(converter(tipo)(argumentos[posicao]))
                except Exception as erro: raise ComandoInvalido(f"Não consegui converter '{argumentos[posicao]}'.") from erro
                posicao += 1
            continue
        if posicao >= len(argumentos):
            if parametro.default is not inspect.Parameter.empty: resultado.append(parametro.default); continue
            raise ComandoInvalido(f"Falta o argumento obrigatório '{parametro.name}'.")
        valor = argumentos[posicao] if parametro.kind is not parametro.KEYWORD_ONLY else " ".join(argumentos[posicao:])
        posicao = len(argumentos) if parametro.kind is parametro.KEYWORD_ONLY else posicao + 1
        try: resultado.append(converter(tipo)(valor))
        except Exception as erro: raise ComandoInvalido(f"O argumento '{parametro.name}' é inválido.") from erro
    if posicao < len(argumentos): raise ComandoInvalido("Foram enviados argumentos demais.")
    return tuple(resultado)

async def executar_checks(callback: Callback, contexto: Any) -> None:
    for check in getattr(callback, "__pimcord_checks__", []):
        resultado = check(contexto)
        if inspect.isawaitable(resultado): resultado = await resultado
        if not resultado: raise ErroDePermissao("Você não tem permissão para usar este comando.")
    cooldown = getattr(callback, "__pimcord_cooldown__", None)
    if cooldown is not None:
        autor = getattr(getattr(contexto, "autor", None), "id", "global")
        if not cooldown.verificar(str(autor)): raise ComandoInvalido("Este comando está em cooldown.")

@dataclass(slots=True)
class Subcomando:
    nome: str
    callback: Callback
    descricao: str = "Subcomando Pimcord"
    opcoes: list[dict[str, Any]] = field(default_factory=list)

    def para_dict(self) -> dict[str, Any]:
        dados: dict[str, Any] = {
            "type": 1,
            "name": self.nome,
            "description": self.descricao[:100],
        }
        if self.opcoes:
            dados["options"] = self.opcoes
        return dados


@dataclass(slots=True)
class SubgrupoDeComandos:
    nome: str
    descricao: str = "Subgrupo de comandos Pimcord"
    comandos: dict[str, Subcomando] = field(default_factory=dict)

    def subcomando(
        self,
        nome: str,
        *,
        descricao: str = "Subcomando Pimcord",
        opcoes: list[dict[str, Any]] | None = None,
    ) -> Callable[[Callback], Callback]:
        def registrar(callback: Callback) -> Callback:
            self.comandos[nome] = Subcomando(nome, callback, descricao, list(opcoes or []))
            return callback
        return registrar

    def para_dict(self) -> dict[str, Any]:
        return {
            "type": 2,
            "name": self.nome,
            "description": self.descricao[:100],
            "options": [comando.para_dict() for comando in self.comandos.values()],
        }


@dataclass(slots=True)
class GrupoDeComandos:
    nome: str
    callback: Callback
    descricao: str = "Grupo de comandos Pimcord"
    comandos: dict[str, Subcomando | SubgrupoDeComandos] = field(default_factory=dict)

    def subcomando(
        self,
        nome: str,
        *,
        descricao: str = "Subcomando Pimcord",
        opcoes: list[dict[str, Any]] | None = None,
    ) -> Callable[[Callback], Callback]:
        def registrar(callback: Callback) -> Callback:
            self.comandos[nome] = Subcomando(nome, callback, descricao, list(opcoes or []))
            return callback
        return registrar

    def subgrupo(self, nome: str, *, descricao: str = "Subgrupo de comandos Pimcord") -> Callable[[Callable[..., Any]], SubgrupoDeComandos]:
        def registrar(callback: Callable[..., Any]) -> SubgrupoDeComandos:
            subgrupo = SubgrupoDeComandos(nome, descricao)
            self.comandos[nome] = subgrupo
            return subgrupo
        return registrar

    def para_dict(self) -> dict[str, Any]:
        return {
            "type": 1,
            "name": self.nome,
            "description": self.descricao[:100],
            "options": [comando.para_dict() for comando in self.comandos.values()],
        }

__all__ = ["Cooldown", "limitar", "verificar", "autocomplete", "preparar_argumentos", "executar_checks", "Subcomando", "SubgrupoDeComandos", "GrupoDeComandos"]
