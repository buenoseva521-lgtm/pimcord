"""Construtor declarativo local e seguro para bots Pimcord.

A DSL deste módulo não executa Python, shell, imports ou expressões arbitrárias.
Ela apenas registra comandos híbridos com respostas literais e eventos permitidos.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from getpass import getpass
from pathlib import Path
from typing import Any

from .ia import PimcordIA


class ErroBotPronto(ValueError):
    """Descrição inválida ou capacidade não permitida na DSL."""


_EVENTOS_PERMITIDOS = {"pronto", "ao_ligar"}
_CHAVES_PERMITIDAS = {"prefixo", "intents", "comando", "resposta", "aliases", "evento", "mensagem"}


@dataclass(slots=True)
class DefinicaoComando:
    nome: str
    resposta: str = ""
    aliases: tuple[str, ...] = ()


@dataclass(slots=True)
class DefinicaoBot:
    prefixo: str = "!"
    intents: str = "basicos"
    comandos: list[DefinicaoComando] = field(default_factory=list)
    eventos: dict[str, str] = field(default_factory=dict)


def _linha_chave(linha: str) -> tuple[str, str]:
    if ":" not in linha:
        raise ErroBotPronto(f"Linha inválida; use 'Chave: valor': {linha!r}")
    chave, valor = linha.split(":", 1)
    chave = chave.strip().casefold()
    if chave not in _CHAVES_PERMITIDAS:
        raise ErroBotPronto(f"Chave não permitida na DSL: {chave}")
    return chave, valor.strip()


def interpretar(descricao: str) -> DefinicaoBot:
    """Interpreta a DSL declarativa sem avaliar código fornecido pelo usuário."""
    if not isinstance(descricao, str) or not descricao.strip():
        raise ErroBotPronto("A descrição do bot não pode ser vazia.")
    definicao = DefinicaoBot()
    comando_atual: DefinicaoComando | None = None
    for numero, bruta in enumerate(descricao.splitlines(), 1):
        linha = bruta.strip()
        if not linha or linha.startswith("#"):
            continue
        try:
            chave, valor = _linha_chave(linha)
        except ErroBotPronto as erro:
            raise ErroBotPronto(f"Linha {numero}: {erro}") from erro
        if chave == "prefixo":
            if not valor or len(valor) > 3 or any(c.isspace() for c in valor):
                raise ErroBotPronto("O prefixo deve ter de 1 a 3 caracteres sem espaços.")
            definicao.prefixo = valor
        elif chave == "intents":
            valor = valor.casefold()
            if valor not in {"basicos", "todos"}:
                raise ErroBotPronto("Intents permitidos: basicos ou todos.")
            definicao.intents = valor
        elif chave == "comando":
            nome = valor.casefold()
            if not nome or any(c.isspace() for c in nome) or len(nome) > 32:
                raise ErroBotPronto("O nome do comando deve ser uma palavra de até 32 caracteres.")
            comando_atual = DefinicaoComando(nome)
            definicao.comandos.append(comando_atual)
        elif chave == "resposta":
            if comando_atual is None:
                raise ErroBotPronto("Resposta precisa vir depois de Comando.")
            if len(valor) > 2000:
                raise ErroBotPronto("A resposta não pode exceder 2000 caracteres.")
            comando_atual.resposta = valor
        elif chave == "aliases":
            if comando_atual is None:
                raise ErroBotPronto("Aliases precisa vir depois de Comando.")
            aliases = tuple(a.strip().casefold() for a in valor.split(",") if a.strip())
            if any(any(c.isspace() for c in alias) or len(alias) > 32 for alias in aliases):
                raise ErroBotPronto("Cada alias deve ser uma palavra de até 32 caracteres.")
            comando_atual.aliases = aliases
        elif chave in {"evento", "mensagem"}:
            evento = valor.casefold() if chave == "evento" else "pronto"
            if evento not in _EVENTOS_PERMITIDOS:
                raise ErroBotPronto("Eventos permitidos nesta versão: pronto ou ao_ligar.")
            definicao.eventos[evento] = valor if chave == "mensagem" else ""
    if not definicao.comandos and not definicao.eventos:
        raise ErroBotPronto("A descrição precisa declarar pelo menos um comando ou evento.")
    return definicao


def _normalizar_token(token: str) -> str:
    """Remove espaços e controles inseridos por cópia no terminal/mobile."""
    if not isinstance(token, str):
        raise ErroBotPronto("O token do bot precisa ser texto.")
    normalizado = "".join(
        caractere for caractere in token
        if not caractere.isspace() and 32 <= ord(caractere) != 127
    )
    if not normalizado:
        raise ErroBotPronto("Token vazio; o bot não foi iniciado.")
    return normalizado


def _obter_token(token: str | None) -> str:
    if token is None or not str(token).strip():
        token = getpass("Token do bot (não será exibido): ")
    return _normalizar_token(str(token))


def _persistir_token(token: str, diretorio: str | None = None) -> Path:
    """Salva o token apenas no `.env` local e ignora esse arquivo no Git."""
    raiz = Path(diretorio or ".").expanduser().resolve()
    raiz.mkdir(parents=True, exist_ok=True)
    caminho_env = raiz / ".env"
    linhas = caminho_env.read_text(encoding="utf-8").splitlines() if caminho_env.exists() else []
    linhas = [linha for linha in linhas if not linha.lstrip().startswith(("DISCORD_TOKEN=", "PIMCORD_TOKEN="))]
    linhas.append(f"DISCORD_TOKEN={token}")
    temporario = caminho_env.with_suffix(".env.tmp")
    temporario.write_text("\n".join(linhas) + "\n", encoding="utf-8")
    temporario.replace(caminho_env)
    try:
        caminho_env.chmod(0o600)
    except OSError:
        pass
    caminho_gitignore = raiz / ".gitignore"
    existentes = caminho_gitignore.read_text(encoding="utf-8").splitlines() if caminho_gitignore.exists() else []
    if ".env" not in {linha.strip() for linha in existentes}:
        existentes.append(".env")
        caminho_gitignore.write_text("\n".join(existentes) + "\n", encoding="utf-8")
    return caminho_env


def construir_plano(plano: dict[str, Any], *, token: str | None = None) -> Any:
    """Cria um Bot a partir de um plano JSON já validado."""
    from .bot import Bot
    from . import Intents

    if not isinstance(plano, dict) or set(plano) != {"prefixo", "intents", "comandos"}:
        raise ErroBotPronto("Plano precisa conter somente prefixo, intents e comandos.")
    prefixo = plano["prefixo"]
    intents_nome = plano["intents"]
    if not isinstance(prefixo, str) or not 1 <= len(prefixo) <= 3 or any(c.isspace() for c in prefixo):
        raise ErroBotPronto("Prefixo inválido no plano.")
    if intents_nome not in {"basicos", "todos"}:
        raise ErroBotPronto("Intents inválidos no plano.")
    definicao = DefinicaoBot(prefixo=prefixo, intents=intents_nome)
    for item in plano["comandos"]:
        if not isinstance(item, dict) or set(item) != {"nome", "resposta", "aliases"}:
            raise ErroBotPronto("Comando fora do plano permitido.")
        definicao.comandos.append(DefinicaoComando(item["nome"], item["resposta"], tuple(item["aliases"])))
    return _construir_definicao(definicao, token=token)


def _construir_definicao(definicao: DefinicaoBot, *, token: str | None = None) -> Any:
    from .bot import Bot
    from . import Intents

    intents = Intents.todos() if definicao.intents == "todos" else Intents()
    bot = Bot(prefixo=definicao.prefixo, intents=intents)
    from . import Permissoes
    for comando in definicao.comandos:
        nome_normalizado = comando.nome.casefold().strip()
        if nome_normalizado in {"limpar", "clear", "purge"}:
            async def limpar_mensagens(ctx, quantidade: int = 10):
                canal = ctx.canal_atual
                if canal is None:
                    await ctx.responder("Este comando precisa ser usado em um canal de texto.")
                    return
                quantidade = max(1, min(100, int(quantidade)))
                apagadas = await canal.purge(limite=quantidade)
                total = len(apagadas) if apagadas is not None else quantidade
                await ctx.responder(f"Apaguei {total} mensagem(ns).")

            bot.comando_hibrido(
                comando.nome,
                descricao="Apaga de 1 a 100 mensagens deste canal",
                aliases=list(comando.aliases),
                permissoes=int(Permissoes.gerenciar_mensagens),
            )(limpar_mensagens)
            continue

        resposta = comando.resposta

        async def callback(ctx, _resposta=resposta):
            return await ctx.responder(_resposta)

        bot.comando_hibrido(comando.nome, aliases=list(comando.aliases))(callback)
    for evento, mensagem in definicao.eventos.items():
        async def callback_evento(_mensagem=mensagem):
            if _mensagem:
                bot.logger.info("%s", _mensagem)
        bot.evento(evento)(callback_evento)
    if token is not None:
        bot.configuracao.token = token.strip()
    return bot


def construir(descricao: str, *, token: str | None = None) -> Any:
    """Cria um :class:`pimcord.Bot` sem conectar e sem solicitar token."""
    definicao = interpretar(descricao)
    return _construir_definicao(definicao, token=token)


def construir_com_ia(descricao: str, gerador: Any, *, token: str | None = None) -> Any:
    """Gera e valida um plano com um provedor injetado e constrói o Bot."""
    plano = gerador.gerar_plano(descricao)
    return construir_plano(plano, token=token)

def _parece_dsl(descricao: str) -> bool:
    chaves = ("prefixo:", "comando:", "resposta:", "aliases:", "intents:", "evento:", "mensagem:")
    linhas = [linha.strip().casefold() for linha in descricao.splitlines() if linha.strip() and not linha.strip().startswith("#")]
    return bool(linhas) and all(linha.startswith(chaves) for linha in linhas)


def bot_pronto(descricao: str, *, token: str | None = None, iniciar: bool = True, gerador: Any = None, diretorio: str | None = None) -> Any:
    """Cria um bot a partir de linguagem natural usando a IA nativa do Pimcord.

    Uma descrição livre, como ``"crie um bot de economia completo"``, passa pela
    ``PimcordIA`` própria. Quando ``diretorio`` é informado, o agente mostra etapas
    de entendimento, arquitetura, implementação e revisão, criando os arquivos do
    projeto antes de retornar. O usuário não importa SDK de IA nem configura chave
    externa. A DSL antiga continua aceita para compatibilidade. Passe ``iniciar=False``
    para construir sem conectar.
    """
    if gerador is not None:
        bot = construir_com_ia(descricao, gerador, token=token)
    elif _parece_dsl(descricao):
        bot = construir(descricao, token=token)
    else:
        print("🧠 PimcordIA: analisando o pedido...", flush=True)
        ia = PimcordIA()
        plano = ia.gerar_plano(descricao)
        print(f"🧩 PimcordIA Neural: plano encontrado com {len(plano['comandos'])} comando(s).", flush=True)
        bot = construir_plano(plano, token=token)
        if diretorio is not None:
            print("🛠️ PimcordIA Neural: construindo arquivos específicos do seu prompt...", flush=True)
            projeto = ia.gerar_projeto(descricao)
            print("🔎 PimcordIA Neural: revisando sintaxe, AST, imports e estrutura do projeto...", flush=True)
            projeto.salvar(diretorio, token=token if token else None)
            bot.projeto_gerado = projeto
            print(f"✅ PimcordIA Neural: projeto revisado em {diretorio}.", flush=True)
    token_utilizado: str | None = None
    if iniciar:
        token_utilizado = _obter_token(token)
    elif token is not None and str(token).strip():
        token_utilizado = _normalizar_token(str(token))
    if token_utilizado:
        bot.configuracao.token = token_utilizado
        _persistir_token(token_utilizado, diretorio)
    if iniciar:
        print("🚀 Pimcord: iniciando conexão com o Discord...", flush=True)
        bot.rodar(token_utilizado)
    return bot


__all__ = ["ErroBotPronto", "DefinicaoBot", "DefinicaoComando", "interpretar", "construir", "construir_plano", "construir_com_ia", "bot_pronto"]
