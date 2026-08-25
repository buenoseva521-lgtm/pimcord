"""Primitivas centrais do Pimcord."""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import IntFlag
from typing import Any, Awaitable, Callable, Optional
import os

class PimcordErro(Exception): pass
class ErroDeConfiguracao(PimcordErro): pass
class ErroDeConexao(PimcordErro): pass
class ErroDeAutenticacao(PimcordErro): pass
class ErroDePermissao(PimcordErro): pass
class ComandoNaoEncontrado(PimcordErro): pass
class ComandoInvalido(PimcordErro): pass
class InteracaoExpirada(PimcordErro): pass
class RateLimitado(PimcordErro):
    def __init__(self, mensagem: str = "Rate limitado", *, espera: float | None = None, global_: bool = False, rota: str | None = None):
        super().__init__(mensagem)
        self.mensagem = mensagem
        self.espera = espera
        self.global_ = global_
        self.rota = rota


class ErroDaAPI(PimcordErro):
    def __init__(self, mensagem: str = "Erro da API", *, status: int | None = None, codigo: int | str | None = None, erros: Any = None, rota: str | None = None, metodo: str | None = None):
        super().__init__(mensagem)
        self.mensagem = mensagem
        self.status = status
        self.codigo = codigo
        self.erros = erros
        self.rota = rota
        self.metodo = metodo


class ErroDoGateway(PimcordErro):
    def __init__(self, mensagem: str = "Erro do Gateway", *, codigo: int | None = None, reconectavel: bool = True):
        super().__init__(mensagem)
        self.mensagem = mensagem
        self.codigo = codigo
        self.reconectavel = reconectavel

class Permissoes(IntFlag):
    nenhum = 0; ver_canal = 1 << 10; enviar_mensagens = 1 << 11
    gerenciar_canal = 1 << 4; gerenciar_servidor = 1 << 5; administrador = 1 << 3
    gerenciar_mensagens = 1 << 13; banir_membros = 1 << 2; expulsar_membros = 1 << 1
    @classmethod
    def todas(cls) -> "Permissoes": return cls((1 << 53) - 1)

@dataclass(slots=True)
class Intents:
    servidores: bool = True; membros: bool = False; mensagens: bool = True
    conteudo_mensagens: bool = True
    @classmethod
    def todos(cls) -> "Intents":
        """Ativa todos os intents representados pela versão atual do Pimcord."""
        return cls(servidores=True, membros=True, mensagens=True, conteudo_mensagens=True)
    @classmethod
    def all(cls) -> "Intents":
        """Alias internacional de :meth:`todos`."""
        return cls.todos()
    def mascara(self) -> int:
        valor = 0
        if self.servidores: valor |= 1 << 0
        if self.membros: valor |= 1 << 1
        if self.mensagens: valor |= 1 << 9
        if self.conteudo_mensagens: valor |= 1 << 15
        return valor

@dataclass(slots=True)
class Configuracao:
    token: Optional[str] = None; prefixo: str = "!"; intents: Intents = field(default_factory=Intents)
    application_id: Optional[str] = None
    @classmethod
    def ambiente(cls, prefixo: str = "!") -> "Configuracao":
        return cls(token=os.getenv("DISCORD_TOKEN"), prefixo=prefixo, application_id=os.getenv("DISCORD_APPLICATION_ID"))
    def validar(self) -> None:
        if not self.token: raise ErroDeConfiguracao("Token ausente. Passe-o a iniciar() ou defina DISCORD_TOKEN.")
        if not self.prefixo: raise ErroDeConfiguracao("O prefixo não pode ser vazio.")

@dataclass(slots=True)
class Embed:
    titulo: Optional[str] = None; descricao: Optional[str] = None; url: Optional[str] = None
    cor: Optional[int] = None; campos: list[dict[str, Any]] = field(default_factory=list)
    rodape: Optional[dict[str, Any]] = None; autor: Optional[dict[str, Any]] = None
    thumbnail: Optional[dict[str, Any]] = None; imagem: Optional[dict[str, Any]] = None
    def adicionar_campo(self, nome: str, valor: str, inline: bool = False) -> "Embed":
        self.campos.append({"name": nome, "value": valor, "inline": inline}); return self
    def para_dict(self) -> dict[str, Any]:
        d = {k: v for k, v in (("title", self.titulo), ("description", self.descricao), ("url", self.url), ("color", self.cor)) if v is not None}
        if self.campos: d["fields"] = self.campos
        if self.rodape: d["footer"] = self.rodape
        if self.autor: d["author"] = self.autor
        if self.thumbnail: d["thumbnail"] = self.thumbnail
        if self.imagem: d["image"] = self.imagem
        return d

@dataclass(slots=True)
class Contexto:
    bot: Any; mensagem: Any = None; comando: Any = None; argumentos: tuple[Any, ...] = ()
    autor: Any = None; servidor: Any = None; canal: Any = None; interacao: Any = None
    @property
    def message(self) -> Any:
        """Alias compatível para acessar a mensagem que disparou o comando."""
        return self.mensagem

    @property
    def canal_atual(self) -> Any:
        """Canal associado ao comando, seja prefixado ou slash."""
        if self.canal is not None:
            return self.canal
        if self.mensagem is not None:
            return getattr(self.mensagem, "canal", None)
        return getattr(self.interacao, "canal", None) if self.interacao is not None else None

    @property
    def autor_id(self) -> str | None:
        """ID do autor normalizado para mensagens e interações."""
        valor = getattr(self.autor, "id", self.autor)
        return str(valor) if valor is not None else None

    async def responder(self, conteudo: str = "", *, embed: Embed | None = None, view: Any = None, ephemeral: bool = False) -> Any:
        if self.interacao: return await self.interacao.responder(conteudo, embed=embed, view=view, ephemeral=ephemeral)
        if self.mensagem and getattr(self.mensagem, "canal", None): return await self.mensagem.canal.enviar(conteudo, embed=embed, view=view)
        return None
    async def responder_embed(self, embed: Embed) -> Any: return await self.responder(embed=embed)
    async def enviar(self, *args: Any, **kwargs: Any) -> Any: return await self.responder(*args, **kwargs)

@dataclass(slots=True)
class Botao:
    texto: str
    estilo: str = "primario"
    custom_id: str | None = None
    desabilitado: bool = False
    url: str | None = None
    linha: int = 0
    callback: Any = field(default=None, repr=False, compare=False)

    def __post_init__(self) -> None:
        if not self.texto or len(self.texto) > 80:
            raise ValueError("texto do botão deve ter entre 1 e 80 caracteres")
        if self.custom_id is not None and len(self.custom_id) > 100:
            raise ValueError("custom_id do botão não pode exceder 100 caracteres")
        if self.estilo not in {"primario", "secundario", "sucesso", "perigo", "link"}:
            raise ValueError("estilo de botão inválido")
        if self.estilo == "link" and not self.url:
            raise ValueError("botão de link exige URL")
        if self.estilo != "link" and self.url:
            raise ValueError("somente botão de link pode ter URL")

    def para_dict(self) -> dict[str, Any]:
        estilos = {"primario": 1, "secundario": 2, "sucesso": 3, "perigo": 4, "link": 5}
        dados: dict[str, Any] = {"type": 2, "style": estilos.get(self.estilo, 1), "label": self.texto, "disabled": self.desabilitado}
        if self.url:
            dados["url"] = self.url
        else:
            dados["custom_id"] = self.custom_id or self.texto.lower().replace(" ", "_")
        return dados

@dataclass(slots=True)
class OpcaoSelect:
    rotulo: str
    valor: str
    descricao: str | None = None
    emoji: str | None = None
    padrao: bool = False

    def para_dict(self) -> dict[str, Any]:
        dados = {"label": self.rotulo, "value": self.valor, "default": self.padrao}
        if self.descricao: dados["description"] = self.descricao
        if self.emoji: dados["emoji"] = {"name": self.emoji}
        return dados


@dataclass(slots=True)
class Select:
    custom_id: str
    placeholder: str | None = None
    minimo: int = 1
    maximo: int = 1
    opcoes: list[OpcaoSelect] = field(default_factory=list)
    callback: Any = field(default=None, repr=False, compare=False)
    linha: int = 0

    def __post_init__(self) -> None:
        if not self.custom_id or len(self.custom_id) > 100:
            raise ValueError("custom_id do select deve ter entre 1 e 100 caracteres")
        if not 0 <= self.minimo <= self.maximo <= 25:
            raise ValueError("minimo/maximo do select devem estar entre 0 e 25")

    def adicionar_opcao(self, rotulo: str, valor: str, *, descricao: str | None = None, emoji: str | None = None, padrao: bool = False) -> "Select":
        if len(self.opcoes) >= 25:
            raise ValueError("select não pode ter mais de 25 opções")
        if not 1 <= len(rotulo) <= 100 or not 1 <= len(valor) <= 100:
            raise ValueError("rótulo e valor da opção devem ter entre 1 e 100 caracteres")
        if descricao is not None and len(descricao) > 100:
            raise ValueError("descrição da opção não pode exceder 100 caracteres")
        self.opcoes.append(OpcaoSelect(rotulo, valor, descricao, emoji, padrao))
        return self

    def para_dict(self) -> dict[str, Any]:
        dados: dict[str, Any] = {"type": 3, "custom_id": self.custom_id, "min_values": self.minimo, "max_values": self.maximo, "options": [item.para_dict() for item in self.opcoes]}
        if self.placeholder: dados["placeholder"] = self.placeholder
        return dados


@dataclass(slots=True)
class EntradaModal:
    custom_id: str
    rotulo: str
    estilo: int = 1
    placeholder: str | None = None
    obrigatorio: bool = True
    minimo: int | None = None
    maximo: int | None = None
    valor: str | None = None

    def __post_init__(self) -> None:
        if not self.custom_id or len(self.custom_id) > 100:
            raise ValueError("custom_id da entrada deve ter entre 1 e 100 caracteres")
        if not 1 <= len(self.rotulo) <= 45:
            raise ValueError("rótulo da entrada deve ter entre 1 e 45 caracteres")
        if self.estilo not in {1, 2}:
            raise ValueError("estilo da entrada deve ser 1 (curto) ou 2 (parágrafo)")
        if self.placeholder is not None and len(self.placeholder) > 100:
            raise ValueError("placeholder da entrada não pode exceder 100 caracteres")
        if self.minimo is not None and not 0 <= self.minimo <= 4000:
            raise ValueError("mínimo da entrada deve estar entre 0 e 4000")
        if self.maximo is not None and not 1 <= self.maximo <= 4000:
            raise ValueError("máximo da entrada deve estar entre 1 e 4000")
        if self.minimo is not None and self.maximo is not None and self.minimo > self.maximo:
            raise ValueError("mínimo da entrada não pode exceder o máximo")
        if self.valor is not None and len(self.valor) > 4000:
            raise ValueError("valor da entrada não pode exceder 4000 caracteres")

    def para_dict(self) -> dict[str, Any]:
        dados: dict[str, Any] = {"type": 4, "custom_id": self.custom_id, "label": self.rotulo, "style": self.estilo, "required": self.obrigatorio}
        if self.placeholder: dados["placeholder"] = self.placeholder
        if self.minimo is not None: dados["min_length"] = self.minimo
        if self.maximo is not None: dados["max_length"] = self.maximo
        if self.valor is not None: dados["value"] = self.valor
        return dados


@dataclass(slots=True)
class Modal:
    titulo: str
    custom_id: str
    entradas: list[EntradaModal] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not 1 <= len(self.titulo) <= 45:
            raise ValueError("título do modal deve ter entre 1 e 45 caracteres")
        if not self.custom_id or len(self.custom_id) > 100:
            raise ValueError("custom_id do modal deve ter entre 1 e 100 caracteres")

    def adicionar_entrada(self, entrada: EntradaModal) -> "Modal":
        if len(self.entradas) >= 5:
            raise ValueError("modal não pode ter mais de 5 entradas")
        self.entradas.append(entrada)
        return self

    def para_dict(self) -> dict[str, Any]:
        return {"title": self.titulo, "custom_id": self.custom_id, "components": [{"type": 1, "components": [entrada.para_dict()]} for entrada in self.entradas]}


@dataclass(slots=True)
class UploadArquivos:
    """Componente Discord de upload de arquivos (tipo 19)."""
    custom_id: str
    minimo: int = 1
    maximo: int = 1
    obrigatorio: bool = True
    tipos_arquivo: list[str] = field(default_factory=list)
    linha: int = 0
    callback: Any = field(default=None, repr=False, compare=False)

    def __post_init__(self) -> None:
        if not self.custom_id:
            raise ValueError("custom_id do upload é obrigatório")
        if not 0 <= self.minimo <= self.maximo <= 10:
            raise ValueError("minimo/maximo do upload devem estar entre 0 e 10")
        self.tipos_arquivo = [str(tipo) for tipo in self.tipos_arquivo]

    def para_dict(self) -> dict[str, Any]:
        dados: dict[str, Any] = {
            "type": 19,
            "custom_id": self.custom_id,
            "min_values": self.minimo,
            "max_values": self.maximo,
            "required": self.obrigatorio,
        }
        if self.tipos_arquivo:
            dados["file_types"] = list(self.tipos_arquivo)
        return dados


@dataclass(slots=True)
class View:
    timeout: float | None = None
    botoes: list[Botao] = field(default_factory=list)
    selecoes: list[Select] = field(default_factory=list)
    uploads: list[UploadArquivos] = field(default_factory=list)
    encerrada: bool = False

    @property
    def persistente(self) -> bool:
        return self.timeout is None and all(getattr(item, "custom_id", None) for item in (*self.botoes, *self.selecoes, *self.uploads))

    def adicionar_item(self, item: Any) -> "View":
        if isinstance(item, Select): self.selecoes.append(item)
        elif isinstance(item, UploadArquivos): self.uploads.append(item)
        else: self.botoes.append(item)
        return self

    def adicionar_select(self, select: Select) -> "View":
        self.selecoes.append(select)
        return self

    def select(self, custom_id: str, *, placeholder: str | None = None, minimo: int = 1, maximo: int = 1, linha: int = 0):
        def registrar(callback: Callable[..., Any]) -> Callable[..., Any]:
            self.selecoes.append(Select(custom_id, placeholder, minimo, maximo, callback=callback, linha=linha))
            return callback
        return registrar

    def botao(self, custom_id: str, *, texto: str, estilo: str = "primario", linha: int = 0):
        def registrar(callback: Callable[..., Any]) -> Callable[..., Any]:
            self.botoes.append(Botao(texto, estilo, custom_id, linha=linha, callback=callback))
            return callback
        return registrar

    def upload(self, custom_id: str, *, minimo: int = 1, maximo: int = 1, obrigatorio: bool = True, tipos_arquivo: list[str] | None = None, linha: int = 0):
        def registrar(callback: Callable[..., Any]) -> Callable[..., Any]:
            self.uploads.append(UploadArquivos(custom_id, minimo, maximo, obrigatorio, list(tipos_arquivo or []), linha=linha, callback=callback))
            return callback
        return registrar

    def para_componentes(self) -> list[dict[str, Any]]:
        linhas: dict[int, list[dict[str, Any]]] = {}
        for botao in self.botoes:
            linhas.setdefault(botao.linha, []).append(botao.para_dict())
        for select in self.selecoes:
            linhas.setdefault(select.linha, []).append(select.para_dict())
        for upload in self.uploads:
            linhas.setdefault(upload.linha, []).append(upload.para_dict())
        return [{"type": 1, "components": componentes} for _, componentes in sorted(linhas.items())]

    def encerrar(self) -> None:
        self.encerrada = True
        for botao in self.botoes:
            botao.desabilitado = True

ComandoCallback = Callable[..., Awaitable[Any]]
