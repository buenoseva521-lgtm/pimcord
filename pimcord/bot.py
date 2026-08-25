from __future__ import annotations
import asyncio, importlib, inspect, json, logging, os, shlex, time
from getpass import getpass
from collections import OrderedDict
from pathlib import Path
from dataclasses import dataclass, field
from typing import Any, Callable, get_type_hints
from .nucleo import *
from .http.cliente import ClienteHTTP
from .gateway.cliente import Gateway
from .discord.modelos import Mensagem, Usuario, Servidor, Canal
from .interacoes.modelos import Interacao
from .comandos import GrupoDeComandos, executar_checks, preparar_argumentos
from .metricas import Metricas
from .tarefas import Agendador
from .extensoes import GerenciadorDeExtensoes
from .automod import MotorAutomoderacao, RegraModeracao


def _normalizar_token(token: str | None) -> str | None:
    """Normaliza o token uma única vez antes de HTTP e Gateway."""
    if token is None:
        return None
    return "".join(
        caractere for caractere in str(token)
        if not caractere.isspace() and 32 <= ord(caractere) != 127
    )


def _carregar_env_local() -> None:
    """Carrega variáveis simples do `.env` atual sem sobrescrever o ambiente."""
    caminho = Path.cwd() / ".env"
    if not caminho.is_file():
        return
    try:
        linhas = caminho.read_text(encoding="utf-8").splitlines()
    except OSError:
        return
    for linha in linhas:
        linha = linha.strip()
        if not linha or linha.startswith("#") or "=" not in linha:
            continue
        chave, valor = linha.split("=", 1)
        chave = chave.strip()
        valor = valor.strip().strip("\\\"'")
        if chave and chave.isidentifier():
            os.environ.setdefault(chave, valor)


@dataclass
class Comando:
    nome: str; callback: ComandoCallback; aliases: tuple[str, ...] = ()

@dataclass(slots=True)
class OpcaoSlash:
    nome: str
    descricao: str = "Opção do comando"
    tipo: type | int = str
    obrigatoria: bool = False
    escolhas: list[dict[str, Any]] = field(default_factory=list)
    autocompletar: bool = False

    def para_dict(self) -> dict[str, Any]:
        tipos = {str: 3, int: 4, bool: 5, float: 10}
        tipo = tipos.get(self.tipo, self.tipo if isinstance(self.tipo, int) else 3)
        dados: dict[str, Any] = {"name": self.nome, "description": self.descricao[:100], "type": tipo, "required": self.obrigatoria}
        if self.escolhas:
            dados["choices"] = self.escolhas
        if self.autocompletar:
            dados["autocomplete"] = True
        return dados

@dataclass(slots=True)
class ComandoSlash:
    nome: str; descricao: str; callback: ComandoCallback; hibrido: bool = False; opcoes: tuple[OpcaoSlash, ...] = (); permissoes: int | None = None

def _normalizar_opcoes(opcoes: list[OpcaoSlash | dict[str, Any]] | None) -> tuple[OpcaoSlash, ...]:
    resultado: list[OpcaoSlash] = []
    for opcao in opcoes or []:
        resultado.append(opcao if isinstance(opcao, OpcaoSlash) else OpcaoSlash(**opcao))
    return tuple(resultado)


def _opcoes_da_assinatura(callback: ComandoCallback) -> tuple[OpcaoSlash, ...]:
    try:
        assinatura = inspect.signature(callback)
        dicas = get_type_hints(callback)
    except (TypeError, ValueError, NameError):
        return ()
    tipos = {str: str, int: int, float: float, bool: bool}
    opcoes: list[OpcaoSlash] = []
    for parametro in list(assinatura.parameters.values())[1:]:
        if parametro.kind in {parametro.VAR_POSITIONAL, parametro.VAR_KEYWORD}:
            continue
        tipo = dicas.get(parametro.name, str)
        args = getattr(tipo, "__args__", ())
        if args:
            tipo = next((item for item in args if item is not type(None)), str)
        tipo = tipos.get(tipo, str)
        opcoes.append(OpcaoSlash(
            nome=parametro.name,
            descricao=f"Valor de {parametro.name.replace('_', ' ')}"[:100],
            tipo=tipo,
            obrigatoria=parametro.default is inspect.Parameter.empty,
        ))
    return tuple(opcoes)


def _opcoes_do_comando(callback: ComandoCallback, opcoes: list[OpcaoSlash | dict[str, Any]] | None) -> tuple[OpcaoSlash, ...]:
    return _normalizar_opcoes(opcoes) or _opcoes_da_assinatura(callback)


def _argumentos_da_interacao(callback: ComandoCallback, opcoes: dict[str, Any]) -> tuple[str, ...]:
    try:
        parametros = list(inspect.signature(callback).parameters.values())[1:]
    except (TypeError, ValueError):
        return tuple(str(valor) for valor in opcoes.values())
    valores: list[str] = []
    for parametro in parametros:
        if parametro.kind in {parametro.VAR_POSITIONAL, parametro.VAR_KEYWORD}:
            continue
        if parametro.name in opcoes:
            valores.append(str(opcoes[parametro.name]))
        elif parametro.default is inspect.Parameter.empty:
            raise ComandoInvalido(f"A opção slash obrigatória '{parametro.name}' não foi recebida.")
    return tuple(valores)

class Cache:
    """Cache local LRU com TTL opcional e métricas de acesso."""
    def __init__(self, limite: int | None = None, ttl: float | None = None):
        self.limite = limite
        self.ttl = ttl
        self._dados: OrderedDict[str, tuple[Any, float | None]] = OrderedDict()
        self.acertos = 0
        self.falhas = 0
        self.expirados = 0
        self.evictados = 0

    def obter(self, chave: str, padrao: Any = None) -> Any:
        item = self._dados.get(chave)
        if item is None:
            self.falhas += 1
            return padrao
        valor, expira_em = item
        if expira_em is not None and expira_em <= time.monotonic():
            self._dados.pop(chave, None)
            self.expirados += 1
            self.falhas += 1
            return padrao
        self._dados.move_to_end(chave)
        self.acertos += 1
        return valor

    def definir(self, chave: str, valor: Any, *, ttl: float | None = None) -> None:
        self._dados.pop(chave, None)
        duracao = self.ttl if ttl is None else ttl
        expira_em = None if duracao is None else time.monotonic() + max(0.0, duracao)
        self._dados[chave] = (valor, expira_em)
        if self.limite is not None:
            while len(self._dados) > self.limite:
                self._dados.popitem(last=False)
                self.evictados += 1

    def remover(self, chave: str) -> None:
        self._dados.pop(chave, None)

    def limpar(self) -> None:
        self._dados.clear()

    def expurgar(self) -> int:
        agora = time.monotonic()
        expirados = [chave for chave, (_, expira_em) in self._dados.items() if expira_em is not None and expira_em <= agora]
        for chave in expirados:
            self._dados.pop(chave, None)
        self.expirados += len(expirados)
        return len(expirados)

    def estatisticas(self) -> dict[str, int | float | None]:
        total = self.acertos + self.falhas
        return {"itens": len(self._dados), "limite": self.limite, "ttl": self.ttl, "acertos": self.acertos, "falhas": self.falhas, "expirados": self.expirados, "evictados": self.evictados, "taxa_acerto": self.acertos / total if total else 0.0}

    def __len__(self) -> int:
        return len(self._dados)

class Tarefa:
    def __init__(self, callback: Callable[..., Any], intervalo: float): self.callback, self.intervalo, self._task = callback, intervalo, None
    async def _loop(self):
        while True:
            try: resultado = self.callback(); await resultado if inspect.isawaitable(resultado) else asyncio.sleep(0)
            except asyncio.CancelledError: raise
            except Exception: logging.getLogger("pimcord.tarefa").exception("Erro na tarefa %s", self.callback.__name__)
            await asyncio.sleep(self.intervalo)
    def iniciar(self) -> None: self._task = asyncio.create_task(self._loop())
    def parar(self) -> None:
        if self._task: self._task.cancel()

class Bot:
    def __str__(self) -> str:
        """Retorna somente o nome do usuário conectado."""
        usuario = self._usuario
        if usuario is None:
            return "Pimcord"
        nome = getattr(usuario, "nome", None) or getattr(usuario, "username", None)
        return str(nome or "Pimcord")

    def __repr__(self) -> str:
        return f"<Bot nome={str(self)!r}>"

    def __init__(self, prefixo: str = "!", *, intents: Intents | None = None, configuracao: Configuracao | None = None, limite_cache: int | None = None, ttl_cache: float | None = None):
        self.configuracao = configuracao or Configuracao(prefixo=prefixo, intents=intents or Intents())
        self.comandos: dict[str, Comando] = {}; self.comandos_slash: dict[str, ComandoSlash] = {}; self.comandos_hibridos: dict[str, ComandoSlash] = {}; self.eventos: dict[str, list[Callable[..., Any]]] = {}; self.tarefas: list[Tarefa] = []
        self.cache = Cache(limite=limite_cache, ttl=ttl_cache); self.metricas = Metricas(); self.logger = logging.getLogger("pimcord"); self._parar = asyncio.Event(); self._pronto = asyncio.Event()
        self.http: ClienteHTTP | None = None; self.gateway: Gateway | None = None
        self._comandos_sincronizados = False
        self._avisou_intent_conteudo = False
        self._diagnostico_mensagens_task: asyncio.Task[Any] | None = None
        self._sessoes_voz: dict[str, Any] = {}
        self._usuario: Usuario | None = None
        self._servidores: dict[str, Servidor] = {}
        self._canais: dict[str, Canal] = {}
        self._estado_conexao = "desconectado"
        self.checks_globais: list[Callable[..., Any]] = []; self.hooks_antes: list[Callable[..., Any]] = []; self.hooks_depois: list[Callable[..., Any]] = []
        self.extensoes: dict[str, Any] = {}; self.gerenciador_extensoes = GerenciadorDeExtensoes(self); self.agendador = Agendador(); self.views: list[Any] = []; self.case_insensitive = False; self.descricao = ""
        self.automod = MotorAutomoderacao()
        self.arquivo_views_persistentes = Path(".pimcord_views.json")
        self._carregar_views_persistentes()

    async def entrar_em_voz(self, servidor_id: str, canal_id: str, *, auto_mudo: bool = False, auto_surdo: bool = False) -> Any:
        """Entra em um canal de voz usando uma sessão reutilizável."""
        from .voz import SessaoVoz
        sessao = self._sessoes_voz.get(str(servidor_id))
        if sessao is None:
            if not self._usuario:
                raise RuntimeError("O usuário do bot ainda não foi recebido pelo Gateway")
            sessao = SessaoVoz(self, str(servidor_id), str(self._usuario.id or ""))
            self._sessoes_voz[str(servidor_id)] = sessao
        await sessao.entrar(str(canal_id), auto_mudo=auto_mudo, auto_surdo=auto_surdo)
        return sessao

    def voz_do_servidor(self, servidor_id: str) -> Any:
        """Retorna a sessão de voz de um servidor, se existir."""
        return self._sessoes_voz.get(str(servidor_id))

    async def sair_da_voz(self, servidor_id: str) -> None:
        sessao = self._sessoes_voz.pop(str(servidor_id), None)
        if sessao:
            await sessao.sair()

    async def _processar_estado_voz(self, dados: dict[str, Any]) -> None:
        """Atualiza a sessão de voz própria sem tratar estados de outros membros como handshake."""
        servidor_id = str(dados.get("guild_id", ""))
        usuario_id = str(dados.get("user_id", ""))
        if not servidor_id or not self._usuario or usuario_id != str(self._usuario.id):
            return
        sessao = self._sessoes_voz.get(servidor_id)
        if sessao is None:
            return
        sessao._sessao_gateway_id = dados.get("session_id") or sessao._sessao_gateway_id
        if dados.get("channel_id") is None:
            sessao.estado = "desconectada"

    async def _processar_servidor_voz(self, dados: dict[str, Any]) -> None:
        """Prepara e inicia o Voice Gateway após os dois eventos de voz oficiais."""
        servidor_id = str(dados.get("guild_id", ""))
        sessao = self._sessoes_voz.get(servidor_id)
        if sessao is None or not sessao._sessao_gateway_id:
            self.logger.warning("VOICE_SERVER_UPDATE recebido sem VOICE_STATE_UPDATE correspondente")
            return
        sessao.preparar_servidor(dados, sessao._sessao_gateway_id)
        from .voz import ClienteGatewayVoz
        if sessao.gateway_voz is None:
            sessao.gateway_voz = ClienteGatewayVoz(sessao)
        if sessao._tarefa_gateway_voz is None or sessao._tarefa_gateway_voz.done():
            sessao._parar.clear()
            sessao._tarefa_gateway_voz = asyncio.create_task(sessao.gateway_voz.executar())

    @property
    def user(self) -> Usuario | None:
        """Usuário autenticado do bot, disponível depois do evento `pronto`."""
        return self._usuario

    @property
    def usuario(self) -> Usuario | None:
        """Alias em português para :attr:`user`."""
        return self._usuario

    @property
    def me(self) -> Usuario | None:
        """Alias compatível para o usuário autenticado do bot."""
        return self._usuario

    @property
    def application_id(self) -> str | None:
        return self.configuracao.application_id

    @property
    def id(self) -> str | None:
        return self._usuario.id if self._usuario else None

    @property
    def servidores(self) -> list[Servidor]:
        """Servidores conhecidos pelo cache local."""
        return list(self._servidores.values())

    @property
    def guilds(self) -> list[Servidor]:
        """Alias compatível para :attr:`servidores`."""
        return self.servidores

    @property
    def canais(self) -> list[Canal]:
        """Canais conhecidos pelo cache local."""
        return list(self._canais.values())

    @property
    def latency(self) -> float | None:
        """Alias em inglês para a latência do último heartbeat confirmado."""
        return self.latencia

    @property
    def latencia(self) -> float | None:
        return self.gateway.latencia if self.gateway else None

    @property
    def latencia_ms(self) -> float | None:
        return self.latencia * 1000 if self.latencia is not None else None

    @property
    def conectado(self) -> bool:
        return self._estado_conexao in {"conectando", "identificando", "conectado", "pronto"}

    @property
    def estado_conexao(self) -> str:
        return self._estado_conexao

    @property
    def ws(self) -> Any:
        return self.gateway.ws if self.gateway else None

    def configurar_logs(self, nivel: int = logging.INFO) -> None:
        """Ativa logs básicos do Pimcord quando o projeto ainda não configurou logging."""
        raiz = logging.getLogger()
        if not raiz.handlers:
            logging.basicConfig(level=nivel, format="%(asctime)s | %(levelname)s | %(name)s | %(message)s")
        self.logger.setLevel(nivel)

    def _definir_estado_conexao(self, estado: str) -> None:
        self._estado_conexao = estado

    def _aplicar_ready(self, dados: dict[str, Any]) -> None:
        usuario = dados.get("user") or {}
        if usuario:
            self._usuario = Usuario.de_dict(usuario)
            self.cache.definir(f"usuario:{self._usuario.id}", self._usuario)
            if not self.configuracao.application_id and self._usuario.id:
                # Em bots do Discord, o ID do usuário do bot é o application_id.
                self.configuracao.application_id = str(self._usuario.id)
        for item in dados.get("guilds", []) or []:
            servidor = Servidor.de_dict(item, self.http)
            if servidor.id:
                self._servidores[servidor.id] = servidor
                self.cache.definir(f"servidor:{servidor.id}", servidor)
        self._pronto.set()
        self._agendar_diagnostico_mensagens()

    def _agendar_diagnostico_mensagens(self) -> None:
        if self._diagnostico_mensagens_task and not self._diagnostico_mensagens_task.done():
            self._diagnostico_mensagens_task.cancel()
        if self.comandos:
            self._diagnostico_mensagens_task = asyncio.create_task(self._verificar_mensagens_recebidas())

    async def _verificar_mensagens_recebidas(self) -> None:
        try:
            await asyncio.sleep(10)
            if self._pronto.is_set() and self.metricas.mensagens == 0 and self.comandos:
                self.logger.warning("Nenhum MESSAGE_CREATE recebido após a conexão. Ative Message Content Intent no Portal do Discord e confira Ver mensagens, Ler histórico e Enviar mensagens no canal.")
        except asyncio.CancelledError:
            return

    def _aplicar_servidor(self, dados: dict[str, Any]) -> Servidor:
        servidor = Servidor.de_dict(dados, self.http)
        if servidor.id:
            self._servidores[servidor.id] = servidor
            self.cache.definir(f"servidor:{servidor.id}", servidor)
        return servidor

    def _aplicar_canal(self, dados: dict[str, Any]) -> Canal:
        canal = Canal(str(dados.get("id", "")), self.http, dados.get("name"), dados.get("type"), dados.get("guild_id"))
        if canal.id:
            self._canais[canal.id] = canal
            self.cache.definir(f"canal:{canal.id}", canal)
        return canal

    def _invalidar_servidor(self, servidor_id: str) -> None:
        servidor_id = str(servidor_id)
        self._servidores.pop(servidor_id, None)
        self.cache.remover(f"servidor:{servidor_id}")
        canais_removidos = [
            canal_id for canal_id, canal in self._canais.items()
            if str(getattr(canal, "servidor_id", "")) == servidor_id
        ]
        for canal_id in canais_removidos:
            self._canais.pop(canal_id, None)
            self.cache.remover(f"canal:{canal_id}")

    @property
    def comando_prefixo(self) -> str:
        return self.configuracao.prefixo

    @property
    def commands(self) -> list[Comando]:
        """Comandos únicos registrados, preservando a ordem de inserção."""
        resultado: list[Comando] = []
        vistos: set[int] = set()
        for comando in self.comandos.values():
            identidade = id(comando)
            if identidade not in vistos:
                vistos.add(identidade)
                resultado.append(comando)
        return resultado

    @property
    def is_ready(self) -> bool:
        return self._pronto.is_set()

    @property
    def is_closed(self) -> bool:
        return self._parar.is_set()

    def adicionar_comando(self, comando: Comando) -> Comando:
        self.comandos[comando.nome] = comando
        for alias in comando.aliases: self.comandos[alias] = comando
        return comando

    def obter_comando(self, nome: str) -> Comando | None:
        return self.comandos.get(nome.lower() if self.case_insensitive else nome)

    def remover_comando(self, nome: str) -> Comando | None:
        comando = self.comandos.pop(nome, None)
        if comando:
            for chave in list(self.comandos):
                if self.comandos[chave] is comando: self.comandos.pop(chave, None)
        return comando

    def event(self, fn):
        nome = fn.__name__
        if nome.startswith("on_"): nome = nome[3:]
        self.eventos.setdefault(nome, []).append(fn)
        return fn

    def listen(self, nome: str | None = None):
        def registrar(fn):
            evento = nome or fn.__name__.removeprefix("on_")
            self.eventos.setdefault(evento, []).append(fn)
            return fn
        return registrar

    def check(self, fn):
        self.checks_globais.append(fn); return fn

    def antes_de_comando(self, fn):
        self.hooks_antes.append(fn); return fn

    def depois_de_comando(self, fn):
        self.hooks_depois.append(fn); return fn

    def _identidade_view(self, view: Any) -> str | None:
        classe = type(view)
        modulo = getattr(classe, "__module__", "")
        nome = getattr(classe, "__qualname__", "")
        if not modulo or not nome or modulo == "__main__" or (modulo == "pimcord.nucleo" and nome == "View"):
            return None
        return f"{modulo}:{nome}"

    def _salvar_views_persistentes(self) -> None:
        identidades = sorted({identidade for view in self.views if getattr(view, "persistente", False) if (identidade := self._identidade_view(view))})
        if identidades:
            self.arquivo_views_persistentes.write_text(json.dumps(identidades, ensure_ascii=False, indent=2), encoding="utf-8")
        elif self.arquivo_views_persistentes.exists():
            self.arquivo_views_persistentes.unlink()

    def _carregar_views_persistentes(self) -> None:
        if not self.arquivo_views_persistentes.exists():
            return
        try:
            identidades = json.loads(self.arquivo_views_persistentes.read_text(encoding="utf-8"))
            for identidade in identidades if isinstance(identidades, list) else []:
                modulo, _, nome = str(identidade).partition(":")
                classe = importlib.import_module(modulo)
                atual: Any = classe
                for parte in nome.split("."):
                    atual = getattr(atual, parte)
                view = atual()
                if getattr(view, "persistente", False):
                    self.views.append(view)
        except (OSError, ImportError, AttributeError, TypeError, ValueError):
            self.logger.warning("Não foi possível reidratar todas as Views persistentes", exc_info=True)

    def adicionar_regra_automoderacao(self, regra: RegraModeracao) -> RegraModeracao:
        """Adiciona uma regra local; decisões são emitidas em `automod_acionada`."""
        return self.automod.adicionar_regra(regra)

    def remover_regra_automoderacao(self, nome: str) -> RegraModeracao | None:
        return self.automod.remover_regra(nome)

    def adicionar_view(self, view: Any) -> Any:
        if view not in self.views:
            self.views.append(view)
            if getattr(view, "persistente", False):
                self._salvar_views_persistentes()
        return view

    def registrar_view(self, view: Any) -> Any:
        """Registra a View e persiste automaticamente subclasses importáveis."""
        return self.adicionar_view(view)

    def add_view(self, view: Any) -> Any:
        """Alias compatível para registrar uma View persistente ou temporária."""
        return self.adicionar_view(view)

    def obter_servidor(self, servidor_id: str) -> Servidor | None:
        return self._servidores.get(str(servidor_id))

    def get_guild(self, guild_id: str) -> Servidor | None:
        return self.obter_servidor(guild_id)

    def obter_canal(self, canal_id: str) -> Canal | None:
        return self._canais.get(str(canal_id))

    def get_channel(self, channel_id: str) -> Canal | None:
        return self.obter_canal(channel_id)

    def obter_usuario(self, usuario_id: str) -> Usuario | None:
        valor = self.cache.obter(f"usuario:{usuario_id}")
        return valor if isinstance(valor, Usuario) else None

    def get_user(self, user_id: str) -> Usuario | None:
        return self.obter_usuario(user_id)

    async def _despachar_componente(self, interacao: Interacao) -> bool:
        custom_id = interacao.custom_id
        if not custom_id:
            return False
        for view in self.views:
            itens = [*getattr(view, "botoes", []), *getattr(view, "selecoes", []), *getattr(view, "uploads", [])]
            for item in itens:
                if getattr(item, "custom_id", None) != custom_id or getattr(item, "callback", None) is None:
                    continue
                resultado = item.callback(interacao)
                if inspect.isawaitable(resultado):
                    await resultado
                return True
        return False

    async def esperar_pronto(self) -> None:
        await self._pronto.wait()

    async def setup_hook(self) -> None:
        """Hook assíncrono executado antes da conexão; subclasses podem sobrescrever."""
        return None

    async def wait_for(self, evento: str, *, check: Callable[..., Any] | None = None, timeout: float | None = None) -> Any:
        """Aguarda o próximo evento que passar por `check`, sem conexão externa."""
        loop = asyncio.get_running_loop()
        futuro: asyncio.Future[Any] = loop.create_future()
        nome = evento.removeprefix("on_")

        async def capturar(*args: Any, **kwargs: Any) -> None:
            valor: Any = args[0] if len(args) == 1 and not kwargs else (args, kwargs)
            aceito = True if check is None else check(*args, **kwargs)
            if inspect.isawaitable(aceito):
                aceito = await aceito
            if aceito and not futuro.done():
                futuro.set_result(valor)

        self.eventos.setdefault(nome, []).append(capturar)
        try:
            return await asyncio.wait_for(futuro, timeout=timeout)
        finally:
            if capturar in self.eventos.get(nome, []):
                self.eventos[nome].remove(capturar)

    async def wait_until_ready(self) -> None:
        """Alias compatível para aguardar o handshake READY."""
        await self.esperar_pronto()

    async def fechar(self) -> None:
        self.logger.info("Encerrando conexão com o Discord")
        self.parar()
        if self.http: await self.http.fechar()

    async def close(self) -> None:
        """Alias compatível para fechar o bot com segurança."""
        await self.fechar()

    async def conectar(self, token: str | None = None) -> None:
        await self.executar(token)

    def rodar(self, token: str | None = None) -> Any:
        """Inicia o bot usando o token informado ou já armazenado.

        Quando ``token`` é omitido, reaproveita o token passado a ``bot_pronto``
        ou configurado no Bot. Só solicita entrada no terminal se não houver
        token disponível. A normalização ocorre antes de qualquer transporte.
        """
        token = _normalizar_token(token) or _normalizar_token(getattr(self.configuracao, "token", None))
        if not token:
            token = _normalizar_token(getpass("Token do bot (não será exibido): "))
        if not token:
            raise ErroDeConfiguracao("Token vazio; o bot não foi iniciado.")
        self.configuracao.token = token
        return self.iniciar(token)
    def comando(self, nome: str, *, aliases: list[str] | None = None):
        def registrar(fn: ComandoCallback):
            c = Comando(nome, fn, tuple(aliases or [])); self.adicionar_comando(c)
            return fn
        return registrar
    def slash(self, nome: str, *, descricao: str = "Executa o comando", opcoes: list[OpcaoSlash | dict[str, Any]] | None = None, permissoes: int | None = None):
        def registrar(fn: ComandoCallback):
            self.comandos_slash[nome] = ComandoSlash(nome, descricao, fn, opcoes=_opcoes_do_comando(fn, opcoes), permissoes=permissoes); return fn
        return registrar
    def comando_slash(self, nome: str, *, descricao: str = "Executa o comando", opcoes: list[OpcaoSlash | dict[str, Any]] | None = None, permissoes: int | None = None):
        """Alias em português para :meth:`slash`."""
        return self.slash(nome, descricao=descricao, opcoes=opcoes, permissoes=permissoes)

    def hibrido(self, nome: str, *, descricao: str = "Executa o comando", aliases: list[str] | None = None, opcoes: list[OpcaoSlash | dict[str, Any]] | None = None, permissoes: int | None = None):
        """Registra um único callback para prefixo e slash."""
        def registrar(fn: ComandoCallback):
            self.adicionar_comando(Comando(nome, fn, tuple(aliases or [])))
            comando = ComandoSlash(nome, descricao, fn, hibrido=True, opcoes=_opcoes_do_comando(fn, opcoes), permissoes=permissoes)
            self.comandos_slash[nome] = comando
            self.comandos_hibridos[nome] = comando
            return fn
        return registrar

    def comando_hibrido(self, nome: str, *, descricao: str = "Executa o comando", aliases: list[str] | None = None, opcoes: list[OpcaoSlash | dict[str, Any]] | None = None, permissoes: int | None = None):
        """Alias em português para :meth:`hibrido`."""
        return self.hibrido(nome, descricao=descricao, aliases=aliases, opcoes=opcoes, permissoes=permissoes)

    async def sincronizar_comandos(self) -> Any:
        if not self.http or not self.configuracao.application_id:
            raise ErroDeConfiguracao("application_id é necessário para sincronizar comandos slash.")
        dados: list[dict[str, Any]] = []
        for comando in self.comandos_slash.values():
            grupo = getattr(comando.callback, "__pimcord_grupo__", None)
            if grupo is not None:
                dados.append(grupo.para_dict())
                continue
            dados.append({"name": comando.nome, "description": comando.descricao[:100], "type": 1, **({"options": [opcao.para_dict() for opcao in comando.opcoes]} if comando.opcoes else {}), **({"default_member_permissions": str(comando.permissoes)} if comando.permissoes is not None else {})})
        resultado = await self.http.requisitar("PUT", f"/applications/{self.configuracao.application_id}/commands", json=dados)
        self._comandos_sincronizados = True
        self.logger.info("%d comando(s) slash/híbrido sincronizado(s)", len(dados))
        return resultado

    async def _sincronizar_automaticamente(self) -> None:
        if self._comandos_sincronizados or not self.comandos_slash or not self.application_id:
            return
        try:
            await self.sincronizar_comandos()
        except Exception:
            self.logger.exception("Não foi possível sincronizar comandos slash; o bot continuará conectado")

    def grupo(self, nome: str, *, descricao: str = "Grupo de comandos Pimcord"):
        """Registra um grupo slash e prefixado com subcomandos em português."""
        def registrar(fn: ComandoCallback):
            grupo = GrupoDeComandos(nome, fn, descricao=descricao)
            self.comandos[nome] = Comando(nome, fn)
            self.comandos_slash[nome] = ComandoSlash(nome, descricao, fn)
            setattr(fn, "__pimcord_grupo__", grupo)
            return grupo
        return registrar
    def evento(self, nome: str | Callable[..., Any] | None = None):
        """Registra eventos com `@bot.evento` ou `@bot.evento(\"pronto\")`."""
        mapa = {
            "ao_ligar": "pronto",
            "ao_receber_mensagem": "mensagem",
            "ao_receber_interacao": "interacao",
            "ao_dar_erro": "erro_comando",
        }
        if callable(nome):
            fn = nome
            evento = mapa.get(fn.__name__, fn.__name__)
            self.eventos.setdefault(evento, []).append(fn)
            return fn
        def registrar(fn):
            evento = nome or mapa.get(fn.__name__, fn.__name__)
            self.eventos.setdefault(evento, []).append(fn)
            return fn
        return registrar
    def tarefa(self, intervalo: float):
        def registrar(fn): self.tarefas.append(Tarefa(fn, intervalo)); return fn
        return registrar

    def agendar(self, nome: str, intervalo: float, *, politica: Any = None):
        """Registra uma tarefa resiliente no agendador português do Bot."""
        def registrar(fn):
            self.agendador.registrar(nome, fn, intervalo, politica=politica)
            return fn
        return registrar

    async def carregar_extensao(self, caminho: str, *, dependencias: tuple[str, ...] = ()) -> Any:
        return await self.gerenciador_extensoes.carregar(caminho, dependencias=dependencias)

    async def descarregar_extensao(self, caminho: str) -> None:
        await self.gerenciador_extensoes.descarregar(caminho)

    async def recarregar_extensao(self, caminho: str) -> Any:
        return await self.gerenciador_extensoes.recarregar(caminho)
    async def disparar(self, nome: str, *args: Any, **kwargs: Any) -> list[Any]:
        """Dispara um evento sem deixar falha de callback derrubar o Gateway.

        Eventos sem payload, como ``pronto``, podem ser declarados sem parâmetros;
        eventos com modelo continuam recebendo o payload normalmente.
        """
        self.metricas.contar_evento(nome)
        resultados: list[Any] = []
        for fn in self.eventos.get(nome, []):
            try:
                args_chamada = args
                kwargs_chamada = kwargs
                if args or kwargs:
                    try:
                        assinatura = inspect.signature(fn)
                        aceita_posicional = any(
                            parametro.kind in (
                                inspect.Parameter.POSITIONAL_ONLY,
                                inspect.Parameter.POSITIONAL_OR_KEYWORD,
                                inspect.Parameter.VAR_POSITIONAL,
                            )
                            for parametro in assinatura.parameters.values()
                        )
                        aceita_kwargs = any(
                            parametro.kind == inspect.Parameter.VAR_KEYWORD
                            for parametro in assinatura.parameters.values()
                        )
                        if not aceita_posicional and not aceita_kwargs:
                            args_chamada = ()
                            kwargs_chamada = {}
                    except (TypeError, ValueError):
                        pass
                resultado = fn(*args_chamada, **kwargs_chamada)
                resultados.append(await resultado if inspect.isawaitable(resultado) else resultado)
            except asyncio.CancelledError:
                raise
            except Exception:
                self.logger.exception("Erro no evento %s", nome)
        return resultados
    def diagnostico_saude(self, *, exigir_token: bool = False) -> Any:
        from .saude import diagnosticar
        return diagnosticar(self, exigir_token=exigir_token)

    def criar_simulador(self) -> Any:
        from .simulador import Simulador
        return Simulador(self)

    def diagnostico(self) -> dict[str, Any]:
        return {
            "versao": __import__("pimcord").__version__,
            "prefixo": self.configuracao.prefixo,
            "comandos": len(self.comandos),
            "comandos_slash": len(self.comandos_slash),
            "comandos_hibridos": len(self.comandos_hibridos),
            "eventos": sum(len(funcoes) for funcoes in self.eventos.values()),
            "tarefas": len(self.tarefas) + len(self.agendador.tarefas),
            "extensoes": self.gerenciador_extensoes.diagnostico(),
            "cache": len(self.cache),
            "metricas": self.metricas.snapshot(),
            "gateway_conectado": self.conectado,
            "estado_conexao": self.estado_conexao,
            "usuario": self.user.nome if self.user else None,
            "usuario_id": self.user.id if self.user else None,
            "servidores": len(self.servidores),
            "canais": len(self.canais),
            "latencia": self.latencia,
        }
    async def processar_comando(self, conteudo: str, *, autor: Any = None, mensagem: Any = None) -> Any:
        if not conteudo.startswith(self.configuracao.prefixo): return None
        partes = shlex.split(conteudo[len(self.configuracao.prefixo):]);
        if not partes: return None
        nome_comando = partes[0].lower() if self.case_insensitive else partes[0]
        comando = self.obter_comando(nome_comando)
        if not comando: raise ComandoNaoEncontrado(partes[0])
        self.metricas.comandos += 1
        ctx = Contexto(self, mensagem=mensagem, comando=comando, argumentos=tuple(partes[1:]), autor=autor)
        for check in self.checks_globais:
            resultado = check(ctx)
            if inspect.isawaitable(resultado): resultado = await resultado
            if resultado is False: raise PermissaoNegada("check global rejeitou o comando")
        await executar_checks(comando.callback, ctx)
        for hook in self.hooks_antes:
            resultado = hook(ctx)
            if inspect.isawaitable(resultado): await resultado
        grupo = getattr(comando.callback, "__pimcord_grupo__", None)
        if grupo and len(partes) > 1 and partes[1] in grupo.comandos:
            callback = grupo.comandos[partes[1]]
            argumentos = tuple(partes[2:])
            ctx.comando = callback
            await executar_checks(callback, ctx)
            valores = await preparar_argumentos(callback, argumentos)
            try:
                return await callback(ctx, *valores)
            finally:
                for hook in self.hooks_depois:
                    resultado = hook(ctx)
                    if inspect.isawaitable(resultado): await resultado
        valores = await preparar_argumentos(comando.callback, tuple(partes[1:]))
        try:
            return await comando.callback(ctx, *valores)
        finally:
            for hook in self.hooks_depois:
                resultado = hook(ctx)
                if inspect.isawaitable(resultado): await resultado
    async def receber_interacao(self, dados: dict[str, Any]) -> None:
        interacao = Interacao(dados, self.http)
        tipo = dados.get("type")
        if tipo == 4:
            nome = dados.get("data", {}).get("name")
            comando = self.comandos_slash.get(nome)
            callback_autocomplete = getattr(comando, "callback", None)
            grupo = getattr(callback_autocomplete, "__pimcord_grupo__", None)
            if grupo is not None and interacao.subcomando:
                entrada = grupo.comandos.get(interacao.grupo_subcomando or interacao.subcomando)
                if interacao.grupo_subcomando and hasattr(entrada, "comandos"):
                    entrada = entrada.comandos.get(interacao.subcomando)
                callback_autocomplete = getattr(entrada, "callback", callback_autocomplete)
            gerador = getattr(callback_autocomplete, "__pimcord_autocomplete__", None)
            if gerador is not None:
                resultado = gerador(interacao)
                if inspect.isawaitable(resultado):
                    resultado = await resultado
                await interacao.responder_autocomplete(list(resultado or []))
            return
        if tipo == 2:
            nome = dados.get("data", {}).get("name")
            comando = self.comandos_slash.get(nome)
            if comando:
                grupo = getattr(comando.callback, "__pimcord_grupo__", None)
                if grupo is not None and interacao.subcomando:
                    entrada = grupo.comandos.get(interacao.grupo_subcomando or interacao.subcomando)
                    subcomando = entrada
                    if interacao.grupo_subcomando and hasattr(entrada, "comandos"):
                        subcomando = entrada.comandos.get(interacao.subcomando)
                    callback = getattr(subcomando, "callback", None)
                    if callback is not None:
                        argumentos = _argumentos_da_interacao(callback, interacao.opcoes)
                        contexto = Contexto(self, comando=callback, argumentos=argumentos, autor=interacao.usuario_id, interacao=interacao)
                        await executar_checks(callback, contexto)
                        valores = await preparar_argumentos(callback, argumentos)
                        await callback(contexto, *valores)
                        await self.disparar("interacao", interacao)
                        return
                if comando.hibrido:
                    valores_brutos = _argumentos_da_interacao(comando.callback, interacao.opcoes)
                    contexto = Contexto(self, comando=comando, argumentos=valores_brutos, autor=interacao.usuario_id, interacao=interacao)
                    await executar_checks(comando.callback, contexto)
                    valores = await preparar_argumentos(comando.callback, valores_brutos)
                    await comando.callback(contexto, *valores)
                else:
                    parametros = list(inspect.signature(comando.callback).parameters.values())[1:]
                    if parametros:
                        argumentos = tuple(str(interacao.opcoes[parametro.name]) for parametro in parametros if parametro.name in interacao.opcoes)
                        valores = await preparar_argumentos(comando.callback, argumentos)
                        await comando.callback(interacao, *valores)
                    else:
                        await comando.callback(interacao)
        elif tipo in {3, 5, 19}:
            await self._despachar_componente(interacao)
        await self.disparar("interacao", interacao)
    async def receber_mensagem(self, dados: dict[str, Any]) -> None:
        mensagem = Mensagem.de_gateway(dados, self.http)
        self.metricas.mensagens += 1
        if not self._pronto.is_set() and self.gateway is not None: self._pronto.set()
        if mensagem.autor.bot: return
        if not mensagem.conteudo and self.comandos and not self._avisou_intent_conteudo:
            self._avisou_intent_conteudo = True
            self.logger.warning("Mensagem recebida sem conteúdo; ative Message Content Intent no Portal do Desenvolvedor para comandos de prefixo")
        self.cache.definir(f"mensagem:{mensagem.id}", mensagem)
        decisao = self.automod.avaliar(
            mensagem.conteudo,
            servidor_id=getattr(mensagem, "servidor_id", None),
            canal_id=getattr(mensagem, "canal_id", None),
            mensagem_id=getattr(mensagem, "id", None),
            usuario_id=getattr(mensagem.autor, "id", None),
        )
        if decisao.detectada:
            await self.disparar("automod_acionada", mensagem, decisao)
            return
        await self.disparar("mensagem", mensagem)
        try:
            await self.processar_comando(mensagem.conteudo, autor=mensagem.autor, mensagem=mensagem)
        except ComandoNaoEncontrado:
            pass
        except Exception:
            self.metricas.erros += 1
            self.logger.exception("Erro ao executar comando")
            await self.disparar("erro_comando", mensagem)
    async def executar(self, token: str | None = None) -> None:
        self.configurar_logs()
        _carregar_env_local()
        token_normalizado = _normalizar_token(token) or _normalizar_token(self.configuracao.token) or _normalizar_token(os.environ.get("DISCORD_TOKEN"))
        self.configuracao.token = token_normalizado
        self.configuracao.validar()
        from . import __version__
        self.logger.info("Pimcord %s ativo | prefixo=%r | comandos=%d | híbridos=%d | conteudo_mensagens=%s", __version__, self.configuracao.prefixo, len(self.comandos), len(self.comandos_hibridos), self.configuracao.intents.conteudo_mensagens)
        relatorio = self.diagnostico_saude(exigir_token=True)
        for verificacao in relatorio.avisos:
            if verificacao.nome == "token":
                continue
            if not verificacao.ok:
                nivel = self.logger.error if verificacao.severidade == "erro" else self.logger.warning
                nivel("Diagnóstico: %s", verificacao.mensagem)
        self._parar.clear(); self._pronto.clear(); self._definir_estado_conexao("conectando")
        self.logger.info("Conectando ao Discord...")
        await self.setup_hook()
        self.agendador.iniciar_todas()
        self.http = ClienteHTTP(self.configuracao.token)
        try:
            try:
                url = await self.http.gateway()
            except ErroDaAPI as erro:
                if getattr(erro, "status", None) == 401:
                    self._definir_estado_conexao("erro_autenticacao")
                    self.logger.error("Token rejeitado pelo Discord (HTTP 401 Unauthorized); verifique o token do bot.")
                    return
                raise
            self.logger.info("Gateway do Discord localizado")
            self.gateway = Gateway(self, url, self.configuracao.token, self.configuracao.intents.mascara())
            for tarefa in self.tarefas: tarefa.iniciar()
            await self.gateway.executar()
        finally:
            if self._diagnostico_mensagens_task and not self._diagnostico_mensagens_task.done():
                self._diagnostico_mensagens_task.cancel()
            for tarefa in self.tarefas: tarefa.parar()
            await self.agendador.parar_todas()
            await self.http.fechar()
    def iniciar(self, token: str | None = None) -> Any:
        """Inicia o bot sem aninhar `asyncio.run` em Pydroid/asyncio ativo.

        Fora de um loop, bloqueia como a API tradicional. Dentro de um loop,
        retorna uma Task; nesse contexto o chamador deve mantê-la viva ou usar
        `await bot.conectar(token)`.
        """
        self.configurar_logs()
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            try:
                return asyncio.run(self.executar(token))
            except KeyboardInterrupt:
                return None
        return asyncio.create_task(self.executar(token))

    async def start(self, token: str | None = None) -> None:
        """Alias assíncrono para iniciar a conexão do bot."""
        await self.executar(token)

    def run(self, token: str | None = None) -> None:
        """Alias para iniciar o bot com o loop de eventos gerenciado."""
        self.iniciar(token)

    def parar(self) -> None:
        self._parar.set()
        self._definir_estado_conexao("encerrando")
        if self.gateway: asyncio.create_task(self.gateway.parar())
