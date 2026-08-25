"""Geração segura de projetos Pimcord a partir de linguagem natural.

O modelo gera arquivos, mas o Pimcord apenas valida e salva o resultado. A execução
é uma ação explícita do usuário e nunca ocorre durante a geração.
"""
from __future__ import annotations

import ast
import importlib.util
import json
import os
from getpass import getpass
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable


class ErroProjetoIA(ValueError):
    """Projeto gerado fora do contrato ou com conteúdo não permitido."""


SCHEMA_PROJETO_BOT: dict[str, Any] = {
    "type": "object",
    "properties": {
        "nome": {"type": "string", "minLength": 1, "maxLength": 80},
        "resumo": {"type": "string", "maxLength": 2000},
        "arquivos": {
            "type": "array",
            "minItems": 1,
            "maxItems": 30,
            "items": {
                "type": "object",
                "properties": {
                    "caminho": {"type": "string", "pattern": "^[A-Za-z0-9_./-]+$", "maxLength": 160},
                    "conteudo": {"type": "string", "maxLength": 100000},
                },
                "required": ["caminho", "conteudo"],
                "additionalProperties": False,
            },
        },
    },
    "required": ["nome", "resumo", "arquivos"],
    "additionalProperties": False,
}

_CONTEXTO_PIMCORD = """
API Pimcord disponível: Bot(prefixo=..., intents=...), Intents.todos(),
@bot.comando_hibrido(nome, aliases=[...]), @bot.comando(nome), @bot.evento("pronto"),
ctx.responder(texto), ctx.mensagem, ctx.mensagem.autor.id, EconomiaSQLite,
GerenciadorDeExtensoes e módulos em cogs/ com função configurar(bot).
Comandos híbridos devem funcionar tanto com prefixo quanto com slash. Não invente
métodos que não estejam neste contexto; quando algo não existir, escreva uma
implementação local segura ou explique a limitação no README.
"""

_PROMPT = (
    "Você é um engenheiro Python sênior especializado em Pimcord. Transforme livremente o pedido "
    "do usuário em um projeto completo e executável, com a arquitetura, comandos, eventos, "
    "persistência e integrações solicitados. Retorne somente JSON conforme o schema. Gere código "
    "completo, tipado e legível, README com instruções e arquivos de configuração. Cada comando "
    "deve implementar o comportamento descrito, sem inventar módulos que não foram pedidos. "
    "Não inclua valores reais de dados sensíveis, tokens, senhas, chaves ou credenciais no código; "
    "use variáveis de ambiente quando uma credencial for necessária.\n\n"
    + _CONTEXTO_PIMCORD
)

_IMPORTS_PROIBIDOS = {"subprocess", "ctypes", "pickle", "marshal"}
_CHAMADAS_PROIBIDAS = {"eval", "exec", "compile", "system", "popen", "__import__"}
_ATRIBUTOS_PROIBIDOS = {"system", "popen", "spawn", "execv", "execve", "remove", "unlink", "rmtree"}


def _validar_python(caminho: str, conteudo: str) -> None:
    try:
        arvore = ast.parse(conteudo, filename=caminho)
    except SyntaxError as erro:
        raise ErroProjetoIA(f"Python inválido em {caminho}: {erro}") from erro
    for no in ast.walk(arvore):
        if isinstance(no, ast.Import):
            if any(alias.name.split(".")[0] in _IMPORTS_PROIBIDOS for alias in no.names):
                raise ErroProjetoIA(f"Import proibido em {caminho}.")
        elif isinstance(no, ast.ImportFrom) and (no.module or "").split(".")[0] in _IMPORTS_PROIBIDOS:
            raise ErroProjetoIA(f"Import proibido em {caminho}.")
        elif isinstance(no, ast.Call):
            nome_chamada = no.func.id if isinstance(no.func, ast.Name) else (no.func.attr if isinstance(no.func, ast.Attribute) else "")
            if nome_chamada in _CHAMADAS_PROIBIDAS or (isinstance(no.func, ast.Attribute) and no.func.attr in _ATRIBUTOS_PROIBIDOS):
                raise ErroProjetoIA(f"Chamada proibida em {caminho}: {nome_chamada}")


def _validar_acoes_reais(projeto: dict[str, Any], pedido: str) -> None:
    """Mantém o ponto de extensão para revisores sem bloquear ações do prompt."""
    if not isinstance(pedido, str) or not pedido.strip():
        raise ErroProjetoIA("O pedido não pode ser vazio.")


def _validar_grafo_imports(projeto: dict[str, Any]) -> None:
    """Confere imports relativos e módulos locais sem executar arquivos gerados."""
    arquivos = {item["caminho"] for item in projeto["arquivos"]}
    python = {caminho for caminho in arquivos if caminho.endswith(".py")}
    modulos_locais = {
        caminho[:-3].replace("/", ".") if caminho.endswith(".py") else caminho.replace("/", ".")
        for caminho in python
    }
    modulos_locais.update(caminho[:-12].replace("/", ".") for caminho in python if caminho.endswith("/__init__.py"))

    def existe_modulo(modulo: str, atual: str) -> bool:
        partes = [parte for parte in modulo.split(".") if parte]
        base = Path(atual).parent
        destino = base.joinpath(*partes)
        return str(destino.with_suffix(".py")) in python or str(destino / "__init__.py") in python

    for item in projeto["arquivos"]:
        caminho = item["caminho"]
        if not caminho.endswith(".py"):
            continue
        arvore = ast.parse(item["conteudo"], filename=caminho)
        for no in ast.walk(arvore):
            if isinstance(no, ast.ImportFrom):
                if no.level:
                    modulo = "." * no.level + (no.module or "")
                    if no.level == 1 and no.module and existe_modulo(no.module, caminho):
                        continue
                    if no.level >= 1 and no.module and not existe_modulo(no.module, caminho):
                        raise ErroProjetoIA(f"Import local ausente em {caminho}: {modulo}")
                elif no.module:
                    raiz = no.module.split(".", 1)[0]
                    if raiz in {nome.split(".", 1)[0] for nome in modulos_locais} or raiz == "pimcord":
                        continue
                    if importlib.util.find_spec(raiz) is None:
                        raise ErroProjetoIA(f"Módulo importado não encontrado em {caminho}: {no.module}")
            elif isinstance(no, ast.Import):
                for alias in no.names:
                    raiz = alias.name.split(".", 1)[0]
                    if raiz in {nome.split(".", 1)[0] for nome in modulos_locais}:
                        continue
                    if importlib.util.find_spec(raiz) is None and raiz != "pimcord":
                        raise ErroProjetoIA(f"Módulo importado não encontrado em {caminho}: {alias.name}")


def validar_projeto(projeto: Any) -> dict[str, Any]:
    if not isinstance(projeto, dict) or set(projeto) != {"nome", "resumo", "arquivos"}:
        raise ErroProjetoIA("Projeto fora do schema permitido.")
    arquivos = projeto["arquivos"]
    if not isinstance(arquivos, list) or not arquivos or len(arquivos) > 30:
        raise ErroProjetoIA("O projeto precisa conter entre 1 e 30 arquivos.")
    vistos: set[str] = set()
    for arquivo in arquivos:
        if not isinstance(arquivo, dict) or set(arquivo) != {"caminho", "conteudo"}:
            raise ErroProjetoIA("Arquivo fora do schema permitido.")
        caminho = arquivo["caminho"]
        conteudo = arquivo["conteudo"]
        if not isinstance(caminho, str):
            raise ErroProjetoIA("Caminho de arquivo precisa ser texto.")
        normalizado = Path(caminho)
        if caminho.startswith(("/", "\\")) or ".." in normalizado.parts:
            raise ErroProjetoIA(f"Caminho inseguro: {caminho!r}")
        if not re.fullmatch(r"[A-Za-z0-9_./-]+", caminho) or caminho in vistos:
            raise ErroProjetoIA(f"Caminho inválido ou duplicado: {caminho!r}")
        if not isinstance(conteudo, str) or len(conteudo) > 100000:
            raise ErroProjetoIA(f"Conteúdo inválido: {caminho!r}")
        vistos.add(caminho)
        if caminho.endswith(".py"):
            _validar_python(caminho, conteudo)
        if caminho not in {".env.example", ".env.template"}:
            for correspondencia in re.finditer(r"(?i)(discord_token|token_do_bot|api_key)\s*=\s*[\"']?([^\s\"'`]+)", conteudo):
                valor = correspondencia.group(2).strip()
                if valor not in {"...", "placeholder", "seu_token", "cole_o_token_apenas_no_ambiente_local"}:
                    raise ErroProjetoIA(f"Possível segredo embutido em {caminho}.")
    return projeto


@dataclass(slots=True)
class ProjetoGerado:
    plano: dict[str, Any]

    @property
    def nome(self) -> str:
        return self.plano["nome"]

    def caminhos(self) -> tuple[str, ...]:
        return tuple(item["caminho"] for item in self.plano["arquivos"])

    def salvar(self, diretorio: str | os.PathLike[str], *, token: str | None = None) -> Path:
        raiz = Path(diretorio).expanduser().resolve()
        raiz.mkdir(parents=True, exist_ok=True)
        validar_projeto(self.plano)
        for item in self.plano["arquivos"]:
            destino = (raiz / item["caminho"]).resolve()
            if raiz not in destino.parents and destino != raiz:
                raise ErroProjetoIA("Tentativa de sair do diretório do projeto.")
            destino.parent.mkdir(parents=True, exist_ok=True)
            destino.write_text(item["conteudo"], encoding="utf-8")
        if token:
            token_limpo = "".join(caractere for caractere in str(token) if not caractere.isspace() and 32 <= ord(caractere) != 127)
            if not token_limpo:
                raise ErroProjetoIA("Token vazio; o projeto não foi iniciado.")
            (raiz / ".env").write_text(f"DISCORD_TOKEN={token_limpo}\n", encoding="utf-8")
            gitignore = raiz / ".gitignore"
            atual = gitignore.read_text(encoding="utf-8") if gitignore.exists() else ""
            if ".env" not in {linha.strip() for linha in atual.splitlines()}:
                gitignore.write_text((atual.rstrip() + "\n.env\n") if atual.strip() else ".env\n", encoding="utf-8")
        return raiz

    def executar(self, diretorio: str | os.PathLike[str], *, token: str | None = None) -> int:
        """Executa explicitamente o bot salvo; nunca é chamado por ``gerar``."""
        raiz = Path(diretorio).expanduser().resolve()
        validar_projeto(self.plano)
        arquivo = raiz / "bot.py"
        if not arquivo.is_file():
            raise ErroProjetoIA("O projeto precisa ter bot.py para ser executado.")
        ambiente = os.environ.copy()
        if token:
            ambiente["DISCORD_TOKEN"] = token
        return subprocess.call([sys.executable, str(arquivo)], cwd=raiz, env=ambiente)


class AgenteConstrutorPimcord:
    """Agente local de construção iterativa para projetos Pimcord.

    O agente expõe as etapas de trabalho, compõe o projeto, revisa todos os
    arquivos Python com ``ast`` e só então salva. Ele não executa código gerado
    automaticamente e não finge possuir conhecimento de um modelo neural geral.
    """

    ETAPAS = (
        "Entendendo o pedido",
        "Planejando a arquitetura Python",
        "Criando os arquivos do projeto",
        "Implementando comandos híbridos e cogs",
        "Revisando imports e sintaxe",
        "Validando segurança",
        "Projeto concluído",
    )

    def __init__(self, *, progresso: Callable[[str], Any] | None = None, modelo_neural: Any | None = None, max_iteracoes: int = 3):
        # Sem callback, a IA trabalha em silêncio para não poluir o terminal do bot.
        # O chamador pode passar `progresso=print` ou um logger quando quiser acompanhar etapas.
        self.progresso = progresso
        self.modelo_neural = modelo_neural
        if max_iteracoes < 1 or max_iteracoes > 8:
            raise ValueError("max_iteracoes deve estar entre 1 e 8.")
        self.max_iteracoes = max_iteracoes

    def _informar(self, etapa: str) -> None:
        if self.progresso is not None:
            self.progresso(f"[PimcordIA] {etapa}...")

    def construir(self, pedido: str, diretorio: str | os.PathLike[str] | None = None) -> ProjetoGerado:
        if not isinstance(pedido, str) or not pedido.strip():
            raise ErroProjetoIA("O pedido não pode ser vazio.")
        from .ia import PimcordIA
        self._informar(self.ETAPAS[0])
        inteligencia = PimcordIA()
        analise = inteligencia.analisar(pedido)
        self._informar(f"Arquitetura: {', '.join(analise['dominios']) or 'núcleo Pimcord'}")
        self._informar(self.ETAPAS[2])
        if self.modelo_neural is None:
            projeto = inteligencia.gerar_projeto(pedido)
        else:
            from .modelo_neural import AgenteNeuralLocal
            agente_neural = AgenteNeuralLocal(self.modelo_neural, max_iteracoes=self.max_iteracoes, progresso=self.progresso)
            projeto = agente_neural.construir(pedido)
        _validar_acoes_reais(projeto.plano, pedido)
        self._informar(self.ETAPAS[3])
        validar_projeto(projeto.plano)
        _validar_grafo_imports(projeto.plano)
        self._informar(self.ETAPAS[4])
        caminhos = {arquivo["caminho"] for arquivo in projeto.plano["arquivos"]}
        obrigatorios = {"bot.py", "config.py", "README.md", ".env.example", "cogs/__init__.py"}
        ausentes = sorted(obrigatorios - caminhos)
        if ausentes:
            raise ErroProjetoIA("Projeto incompleto; arquivos obrigatórios ausentes: " + ", ".join(ausentes))
        for arquivo in projeto.plano["arquivos"]:
            if arquivo["caminho"].endswith(".py"):
                _validar_python(arquivo["caminho"], arquivo["conteudo"])
                try:
                    compile(arquivo["conteudo"], arquivo["caminho"], "exec")
                except SyntaxError as erro:
                    raise ErroProjetoIA(f"Falha de compilação em {arquivo['caminho']}: {erro}") from erro
        self._informar(self.ETAPAS[5])
        validar_projeto(projeto.plano)
        if diretorio is not None:
            projeto.salvar(diretorio)
        self._informar(self.ETAPAS[6])
        return projeto


def _catalogo_runtime(pedido: str = "") -> str:
    try:
        from .ia import contexto_python_pimcord, resumo_api_pimcord
        contexto = contexto_python_pimcord(pedido, limite=16) if pedido else ""
        return resumo_api_pimcord() + ("\n\nCONTEXTO PYTHON/PIMCORD RECUPERADO:\n" + contexto if contexto else "")
    except Exception:
        return "Catálogo indisponível; use somente o contexto fixo acima."


class GeradorProjetoIA:
    """Gera um projeto completo estruturado, sem executar o resultado."""

    def __init__(self, cliente: Any, *, modelo: str = "gpt-5"):
        if cliente is None:
            raise ErroProjetoIA("Injete um cliente LLM para geração livre.")
        self.cliente = cliente
        self.modelo = modelo

    def gerar(self, pedido: str) -> ProjetoGerado:
        if not isinstance(pedido, str) or not pedido.strip():
            raise ErroProjetoIA("O pedido não pode ser vazio.")
        argumentos = {
            "model": self.modelo,
            "messages": [{"role": "system", "content": _PROMPT + "\n\nCATÁLOGO E MEMÓRIA LOCAL ATUAIS:\n" + _catalogo_runtime(pedido)}, {"role": "user", "content": pedido[:20000]}],
            "response_format": {"type": "json_schema", "json_schema": {"name": "projeto_pimcord", "strict": True, "schema": SCHEMA_PROJETO_BOT}},
        }
        if self.modelo.casefold().startswith("claude"):
            argumentos["max_tokens"] = 16000
            argumentos["extra_body"] = {"thinking": {"type": "enabled", "budget_tokens": 4096}}
        elif self.modelo.casefold().startswith("gemini"):
            argumentos["max_tokens"] = 16000
        else:
            argumentos["max_completion_tokens"] = 16000
        resposta = self.cliente.chat.completions.create(**argumentos)
        try:
            plano = json.loads(resposta.choices[0].message.content)
        except (TypeError, json.JSONDecodeError) as erro:
            raise ErroProjetoIA("A IA não retornou um projeto JSON válido.") from erro
        plano_validado = validar_projeto(plano)
        _validar_acoes_reais(plano_validado, pedido)
        return ProjetoGerado(plano_validado)


def criar_projeto_ia(pedido: str, cliente: Any, diretorio: str | os.PathLike[str], *, modelo: str = "gpt-5-mini", executar: bool = False, token: str | None = None) -> ProjetoGerado:
    """Gera e salva um projeto; só executa quando ``executar=True`` explícito.

    Quando executar for verdadeiro e nenhum token for passado, a entrada é solicitada
    mascarada no terminal. O token nunca participa da chamada ao modelo.
    """
    projeto = GeradorProjetoIA(cliente, modelo=modelo).gerar(pedido)
    projeto.salvar(diretorio)
    if executar:
        segredo = token or os.environ.get("DISCORD_TOKEN") or getpass("Token do bot (não será exibido): ")
        if not segredo.strip():
            raise ErroProjetoIA("Token vazio; o projeto não foi iniciado.")
        projeto.executar(diretorio, token=segredo)
    return projeto


def _extrair_recursos_livres(pedido: str) -> list[str]:
    """Extrai somente comandos livres explicitamente nomeados no pedido.

    O fallback não transforma substantivos, bibliotecas, verbos ou trechos
    descritivos em comandos. Domínios conhecidos são tratados por seus cogs;
    nomes personalizados precisam aparecer como ``.nome``, ``!nome`` ou
    ``/nome``.
    """
    import re
    import unicodedata

    texto = unicodedata.normalize("NFKD", pedido.casefold()).encode("ascii", "ignore").decode()
    recursos: list[str] = []
    for comando in re.findall(r"(?<![a-z0-9_])[.!/]([a-z][a-z0-9_-]{1,31})", texto):
        slug = re.sub(r"[^a-z0-9_]", "", comando.replace("-", "_"))
        if slug and slug not in recursos:
            recursos.append(slug)
    return recursos[:50]


def _analisar_comandos_livres(pedido: str, recursos: list[str]) -> list[dict[str, Any]]:
    """Converte cada comando explícito em requisitos estruturados.

    O fallback não tenta fingir que qualquer frase é uma implementação pronta:
    ele preserva a intenção próxima ao comando, identifica parâmetros e ações
    reconhecíveis e entrega essa estrutura ao renderer e ao modelo neural.
    """
    import re
    texto = " ".join(pedido.strip().split())
    resultado: list[dict[str, Any]] = []
    ocorrencias = list(re.finditer(r"(?<![a-z0-9_])[.!/]([a-z][a-z0-9_-]{1,31})", texto.casefold()))
    for indice, recurso in enumerate(recursos):
        ocorrencia = next((item for item in ocorrencias if item.group(1).replace("-", "_") == recurso), None)
        inicio = ocorrencia.start() if ocorrencia else 0
        fim = ocorrencias[indice + 1].start() if indice + 1 < len(ocorrencias) else len(texto)
        trecho = texto[inicio:fim].strip(" ,.;:")
        trecho_sem_nome = re.sub(r"^[.!/]" + re.escape(recurso.replace("_", "[-_]")), "", trecho, flags=re.IGNORECASE).strip(" ,.;:")
        parametros: list[str] = []
        if re.search(r"quantidade|numero|n[uú]mero|at[eé]|mensagens?", trecho_sem_nome, re.IGNORECASE):
            parametros.append("quantidade: int")
        if re.search(r"\b(?:membro|usu[aá]rio|pessoa|id)\b", trecho_sem_nome, re.IGNORECASE):
            parametros.append("membro: str")
        if re.search(r"motivo|raz[aã]o", trecho_sem_nome, re.IGNORECASE):
            parametros.append("motivo: str")
        if re.search(r"texto|mensagem|nome|assunto", trecho_sem_nome, re.IGNORECASE):
            parametros.append("texto: str")
        acoes = [
            verbo for verbo, marcador in (("apagar", "apag"), ("banir", "ban"), ("criar", "cri"), ("consultar", "consult"), ("salvar", "salv"), ("listar", "list"), ("enviar", "envi"))
            if marcador in trecho_sem_nome.casefold()
        ]
        descricao = trecho_sem_nome or f"Executa a funcionalidade solicitada para {recurso}."
        resultado.append({"nome": recurso, "descricao": descricao[:100], "requisitos": trecho_sem_nome, "parametros": parametros, "acoes": list(dict.fromkeys(acoes))})
    return resultado


def projeto_local_pimcord(pedido: str) -> ProjetoGerado:
    """Gera um projeto completo offline para prompts comuns, sem SDK de IA."""
    if not isinstance(pedido, str) or not pedido.strip():
        raise ErroProjetoIA("O pedido não pode ser vazio.")
    from .ia import _validar_pedido_dados_sensiveis
    _validar_pedido_dados_sensiveis(pedido)
    texto = pedido.casefold()
    nome = "bot_pimcord_gerado"
    dominios = {
        'economia': 'from pimcord import EconomiaSQLite\n\ndef configurar(bot):\n    banco = EconomiaSQLite("economia.sqlite3", diaria=100)\n\n    @bot.comando_hibrido("saldo", descricao="Consulta o saldo de moedas do autor")\n    async def saldo(ctx):\n        total = banco.saldo(ctx.autor_id or "desconhecido")\n        await ctx.responder(f"Seu saldo atual é {total} moedas.")\n\n    @bot.comando_hibrido("diaria", descricao="Resgata a recompensa diária de 100 moedas", aliases=["daily"])\n    async def diaria(ctx):\n        total = banco.diaria(ctx.autor_id or "desconhecido")\n        await ctx.responder(f"Recompensa resgatada. Seu saldo agora é {total} moedas.")\n\n    @bot.comando_hibrido("ranking", descricao="Mostra os maiores saldos do servidor", aliases=["top"])\n    async def ranking(ctx):\n        linhas = banco.ranking()\n        if not linhas:\n            await ctx.responder("Ainda não há usuários no ranking.")\n            return\n        texto = "\\n".join(f"{i}. {linha[\'usuario_id\']}: {linha[\'saldo\']} moedas" for i, linha in enumerate(linhas, 1))\n        await ctx.responder(texto)\n',
        'moderacao': 'import sqlite3\nfrom pimcord import Permissoes\n\ndef configurar(bot):\n    @bot.comando_hibrido(\n        "limpar",\n        descricao="Apaga de 1 a 100 mensagens deste canal",\n        aliases=["purge"],\n        permissoes=int(Permissoes.gerenciar_mensagens),\n    )\n    async def limpar(ctx, quantidade: int = 10):\n        canal = ctx.canal_atual\n        if canal is None:\n            await ctx.responder("Este comando precisa ser usado em um canal de texto.")\n            return\n        quantidade = max(1, min(100, quantidade))\n        apagadas = await canal.purge(limite=quantidade)\n        total = len(apagadas) if apagadas is not None else quantidade\n        await ctx.responder(f"Apaguei {total} mensagem(ns).")\n\n    @bot.comando_hibrido(\n        "avisar",\n        descricao="Registra uma advertência persistente para um membro",\n        permissoes=int(Permissoes.gerenciar_mensagens),\n    )\n    async def avisar(ctx, membro: str, motivo: str = "Sem motivo informado"):\n        with sqlite3.connect("moderacao.sqlite3") as banco:\n            banco.execute("CREATE TABLE IF NOT EXISTS avisos (id INTEGER PRIMARY KEY, servidor_id TEXT, membro TEXT, motivo TEXT, autor TEXT)")\n            banco.execute("INSERT INTO avisos (servidor_id, membro, motivo, autor) VALUES (?, ?, ?, ?)", (getattr(ctx.canal_atual, "servidor_id", None), membro, motivo, ctx.autor_id))\n            banco.commit()\n        await ctx.responder(f"Advertência registrada para {membro}: {motivo}.")\n',
        'tickets': 'from pimcord import Permissoes\n\ndef configurar(bot):\n    @bot.comando_hibrido("ticket", descricao="Cria um canal privado de atendimento", aliases=["suporte"])\n    async def ticket(ctx, assunto: str = "atendimento"):\n        canal = ctx.canal_atual\n        servidor_id = getattr(canal, "servidor_id", None)\n        cliente = getattr(canal, "cliente", None)\n        if not servidor_id or cliente is None:\n            await ctx.responder("Não consegui identificar o servidor deste atendimento.")\n            return\n        nome = "ticket-" + "-".join(assunto.lower().split())[:70]\n        criado = await cliente.criar_canal(servidor_id, name=nome, type=0, topic=f"Atendimento de {ctx.autor_id}: {assunto}")\n        await ctx.responder(f"Ticket criado: <#{criado.get(\'id\', \'\')}>.")\n\n    @bot.comando_hibrido("fechar_ticket", descricao="Fecha o canal atual de atendimento", aliases=["fechar"], permissoes=int(Permissoes.gerenciar_canais))\n    async def fechar_ticket(ctx):\n        canal = ctx.canal_atual\n        cliente = getattr(canal, "cliente", None)\n        if canal is None or cliente is None:\n            await ctx.responder("Este comando precisa ser usado em um canal de ticket.")\n            return\n        await cliente.excluir_canal(canal.id)\n',
        'boas_vindas': 'def configurar(bot):\n    @bot.evento("membro_adicionado")\n    async def membro_entrou(membro):\n        bot.logger.info("Novo membro recebido: %s", getattr(membro, "nome", membro))\n\n    @bot.comando_hibrido("configurar_boas_vindas", descricao="Mostra o estado do módulo de boas-vindas")\n    async def configurar_boas_vindas(ctx):\n        await ctx.responder("Boas-vindas ativas. Registre um canal específico para enviar mensagens de entrada.")\n',
        'diversao': 'import random\n\ndef configurar(bot):\n    @bot.comando_hibrido("dado", descricao="Rola um dado de seis lados")\n    async def dado(ctx):\n        await ctx.responder(f"{ctx.autor_id or \'Jogador\'} rolou: {random.randint(1, 6)}.")\n\n    @bot.comando_hibrido("moeda", descricao="Lança uma moeda e informa o resultado")\n    async def moeda(ctx):\n        await ctx.responder(f"Resultado: {random.choice((\'cara\', \'coroa\'))}.")\n',
        'musica': 'def configurar(bot):\n    fila = []\n\n    @bot.comando_hibrido("tocar", descricao="Adiciona uma faixa à fila de reprodução", aliases=["play"])\n    async def tocar(ctx, faixa: str):\n        fila.append(faixa)\n        await ctx.responder(f"🎵 Adicionei **{faixa}** à fila. Posição: {len(fila)}.")\n\n    @bot.comando_hibrido("fila", descricao="Mostra a fila de reprodução")\n    async def fila_atual(ctx):\n        await ctx.responder("📃 Fila vazia." if not fila else "📃 Fila: " + "\\n".join(f"{i}. {item}" for i, item in enumerate(fila, 1)))\n\n    @bot.comando_hibrido("pausar", descricao="Marca a reprodução como pausada")\n    async def pausar(ctx):\n        await ctx.responder("⏸️ Reprodução pausada. A fila foi preservada.")\n\n    @bot.comando_hibrido("parar", descricao="Limpa a fila de reprodução")\n    async def parar(ctx):\n        fila.clear()\n        await ctx.responder("⏹️ Reprodução encerrada e fila limpa.")\n',
        'lembretes': 'import sqlite3\nfrom datetime import datetime\n\n\ndef configurar(bot):\n    banco = sqlite3.connect("lembretes.sqlite3", check_same_thread=False)\n    banco.execute("CREATE TABLE IF NOT EXISTS lembretes (id INTEGER PRIMARY KEY AUTOINCREMENT, autor TEXT, texto TEXT, horario TEXT)")\n    banco.commit()\n\n    @bot.comando_hibrido("lembrar", descricao="Salva um lembrete com texto e horário")\n    async def lembrar(ctx, horario: str, texto: str):\n        datetime.strptime(horario, "%Y-%m-%d %H:%M")\n        cursor = banco.execute("INSERT INTO lembretes (autor, texto, horario) VALUES (?, ?, ?)", (ctx.autor_id, texto, horario))\n        banco.commit()\n        await ctx.responder(f"⏰ Lembrete #{cursor.lastrowid} salvo para {horario}.")\n\n    @bot.comando_hibrido("lembretes", descricao="Lista seus lembretes salvos")\n    async def listar_lembretes(ctx):\n        linhas = banco.execute("SELECT id, horario, texto FROM lembretes WHERE autor = ? ORDER BY horario", (ctx.autor_id,)).fetchall()\n        await ctx.responder("📌 Você não possui lembretes." if not linhas else "📌 " + "\\n".join(f"#{id_} — {horario} — {texto}" for id_, horario, texto in linhas))\n',
        'quiz': 'import random\n\n\ndef configurar(bot):\n    perguntas = [("Qual linguagem o Pimcord usa?", "python"), ("Qual comando testa a conexão?", "ping")]\n\n    @bot.comando_hibrido("quiz", descricao="Apresenta uma pergunta do quiz")\n    async def quiz(ctx):\n        pergunta, resposta = random.choice(perguntas)\n        await ctx.responder(f"🧠 Pergunta: {pergunta}\\nResponda com `!responder {resposta}`.")\n\n    @bot.comando_hibrido("responder", descricao="Confere uma resposta do quiz")\n    async def responder(ctx, resposta: str):\n        correta = any(resposta.casefold() == item[1] for item in perguntas)\n        await ctx.responder("✅ Resposta aceita!" if correta else "❌ Resposta incorreta. Tente novamente.")\n\n    @bot.comando_hibrido("ranking_quiz", descricao="Mostra o ranking do quiz")\n    async def ranking_quiz(ctx):\n        await ctx.responder("🏆 O ranking será preenchido conforme as respostas corretas forem registradas.")\n',
        'musica': 'def configurar(bot):\n    fila = []\n\n    @bot.comando_hibrido("tocar", descricao="Adiciona uma faixa à fila de reprodução", aliases=["play"])\n    async def tocar(ctx, faixa: str):\n        fila.append(faixa)\n        await ctx.responder(f"🎵 Adicionei **{faixa}** à fila. Posição: {len(fila)}.")\n\n    @bot.comando_hibrido("fila", descricao="Mostra a fila de reprodução")\n    async def fila_atual(ctx):\n        await ctx.responder("📃 Fila vazia." if not fila else "📃 Fila: " + "\\n".join(f"{i}. {item}" for i, item in enumerate(fila, 1)))\n\n    @bot.comando_hibrido("pausar", descricao="Marca a reprodução como pausada")\n    async def pausar(ctx):\n        await ctx.responder("⏸️ Reprodução pausada. A fila foi preservada.")\n\n    @bot.comando_hibrido("parar", descricao="Limpa a fila de reprodução")\n    async def parar(ctx):\n        fila.clear()\n        await ctx.responder("⏹️ Reprodução encerrada e fila limpa.")\n',
        'lembretes': 'import sqlite3\nfrom datetime import datetime\n\n\ndef configurar(bot):\n    banco = sqlite3.connect("lembretes.sqlite3", check_same_thread=False)\n    banco.execute("CREATE TABLE IF NOT EXISTS lembretes (id INTEGER PRIMARY KEY AUTOINCREMENT, autor TEXT, texto TEXT, horario TEXT)")\n    banco.commit()\n\n    @bot.comando_hibrido("lembrar", descricao="Salva um lembrete com texto e horário")\n    async def lembrar(ctx, horario: str, texto: str):\n        datetime.strptime(horario, "%Y-%m-%d %H:%M")\n        cursor = banco.execute("INSERT INTO lembretes (autor, texto, horario) VALUES (?, ?, ?)", (ctx.autor_id, texto, horario))\n        banco.commit()\n        await ctx.responder(f"⏰ Lembrete #{cursor.lastrowid} salvo para {horario}.")\n\n    @bot.comando_hibrido("lembretes", descricao="Lista seus lembretes salvos")\n    async def listar_lembretes(ctx):\n        linhas = banco.execute("SELECT id, horario, texto FROM lembretes WHERE autor = ? ORDER BY horario", (ctx.autor_id,)).fetchall()\n        await ctx.responder("📌 Você não possui lembretes." if not linhas else "📌 " + "\\n".join(f"#{id_} — {horario} — {texto}" for id_, horario, texto in linhas))\n',
        'quiz': 'import random\n\n\ndef configurar(bot):\n    perguntas = [("Qual linguagem o Pimcord usa?", "python"), ("Qual comando testa a conexão?", "ping")]\n\n    @bot.comando_hibrido("quiz", descricao="Apresenta uma pergunta do quiz")\n    async def quiz(ctx):\n        pergunta, resposta = random.choice(perguntas)\n        await ctx.responder(f"🧠 Pergunta: {pergunta}\\nResponda com `!responder {resposta}`.")\n\n    @bot.comando_hibrido("responder", descricao="Confere uma resposta do quiz")\n    async def responder(ctx, resposta: str):\n        correta = any(resposta.casefold() == item[1] for item in perguntas)\n        await ctx.responder("✅ Resposta aceita!" if correta else "❌ Resposta incorreta. Tente novamente.")\n\n    @bot.comando_hibrido("ranking_quiz", descricao="Mostra o ranking do quiz")\n    async def ranking_quiz(ctx):\n        await ctx.responder("🏆 O ranking será preenchido conforme as respostas corretas forem registradas.")\n',
        'utilidades': 'def configurar(bot):\n    @bot.comando_hibrido("userinfo", descricao="Mostra o identificador do autor", aliases=["perfil"])\n    async def userinfo(ctx):\n        await ctx.responder(f"Seu ID é {ctx.autor_id or \'desconhecido\'}.")\n\n    @bot.comando_hibrido("servidor", descricao="Mostra o identificador do servidor atual")\n    async def servidor(ctx):\n        servidor_id = getattr(ctx.canal_atual, "servidor_id", None)\n        await ctx.responder(f"Servidor atual: {servidor_id or \'mensagem privada\'}.")\n',
    }
    sinais_dominios = {
        "economia": ("economia", "saldo", "moedas", "dinheiro"),
        "geral": ("ping", "ajuda", "comando de ajuda"),
        "limpeza": ("clear", "limpar", "purge", "apagar mensagens", "limpar mensagens"),
        "moderacao": ("moderação", "moderacao", "moderar", "banir", "advertência", "warn"),
        "tickets": ("ticket", "tickets", "suporte", "atendimento"),
        "views": ("view", "botão", "botao", "timeout", "componente"),
        "permissoes": ("permissão", "permissao", "sobrescrita", "categoria privada"),
        "tarefas": ("tarefa", "tarefas", "periódica", "periodica", "agendamento", "cancelar"),
        "rest": ("histórico", "historico", "paginado", "limite rest", "mensagens"),
        "seguranca": ("segurança", "seguranca", "tratamento de erros", "comandos híbridos", "comandos hibridos"),
        "boas_vindas": ("boas-vindas", "saudação", "entrada", "novo membro"),
        "diversao": ("diversão", "diversao", "jogo", "sorteio", "dado", "moeda"),
        "musica": ("música", "musica", "player", "áudio", "audio", "som", "fila", "tocar", "pausar"),
        "lembretes": ("lembrete", "lembretes", "lembrar", "agenda"),
        "quiz": ("quiz", "perguntas", "trivia", "ranking"),
        "utilidades": ("utilidade", "perfil", "informações", "userinfo", "servidor"),
    }
    texto_palavras = " " + re.sub(r"[^\w]+", " ", texto, flags=re.UNICODE) + " "

    def tem_sinal(sinal: str) -> bool:
        sinal_palavras = re.sub(r"[^\w]+", " ", sinal.casefold(), flags=re.UNICODE).strip()
        return f" {sinal_palavras} " in texto_palavras

    dominios = {dominio: any(tem_sinal(sinal) for sinal in sinais) for dominio, sinais in sinais_dominios.items()}
    recursos_livres = _extrair_recursos_livres(pedido)
    # Um comando já implementado por um domínio não deve reaparecer no cog
    # personalizado (por exemplo, `.clear` não cria um segundo clear).
    comandos_cobertos = {
        "clear", "limpar", "purge", "saldo", "diaria", "daily", "ranking", "top",
        "avisar", "ticket", "suporte", "fechar_ticket", "fechar", "ping", "latencia",
        "ajuda", "tocar", "play", "fila", "pausar", "parar", "lembrar", "lembretes",
        "quiz", "responder", "userinfo", "perfil", "servidor", "dado", "moeda",
    }
    recursos_livres = [recurso for recurso in recursos_livres if recurso not in comandos_cobertos]
    if recursos_livres:
        dominios["personalizado"] = True
    # Não há limite artificial de quantidade: todos os comandos e recursos
    # explicitamente descritos podem coexistir no mesmo projeto.
    # “completo” qualifica os recursos pedidos; nunca inventa domínios ausentes.
    arquivos: list[dict[str, str]] = [
        {"caminho": "bot.py", "conteudo": '''import os\nimport pimcord\nfrom config import PREFIXO, TOKEN\nfrom cogs import configurar\n\nbot = pimcord.Bot(prefixo=PREFIXO, intents=pimcord.Intents.todos())\nconfigurar(bot)\n\n\nif __name__ == "__main__":\n    bot.rodar(TOKEN)\n'''},
        {"caminho": "config.py", "conteudo": '''import os\nfrom pathlib import Path\n\ndef _carregar_env():\n    caminho = Path(__file__).with_name(".env")\n    if not caminho.is_file():\n        return\n    for linha in caminho.read_text(encoding="utf-8").splitlines():\n        linha = linha.strip()\n        if not linha or linha.startswith("#") or "=" not in linha:\n            continue\n        chave, valor = linha.split("=", 1)\n        os.environ.setdefault(chave.strip(), valor.strip().strip("\\\"'"))\n\n_carregar_env()\nPREFIXO = os.environ.get("PIMCORD_PREFIXO", "!")\nTOKEN = os.environ.get("DISCORD_TOKEN", "")\n'''},
        {"caminho": ".env.example", "conteudo": "DISCORD_TOKEN=cole_o_token_apenas_no_ambiente_local\nPIMCORD_PREFIXO=!\n"},
        {"caminho": "README.md", "conteudo": f'''# {nome}\n\nProjeto gerado pelo Pimcord a partir do pedido:\n\n> {pedido.strip()}\n\nO projeto usa cogs separados, comandos híbridos, eventos e configuração por variáveis de ambiente. Nunca coloque o token diretamente neste arquivo.\n\nOs comandos slash e híbridos são sincronizados automaticamente depois do READY; comandos globais podem levar alguns minutos para aparecer. Para comandos de prefixo, ative Message Content Intent no Portal do Desenvolvedor.\n\nExecute com `DISCORD_TOKEN=... python bot.py`.\n'''}
    ]
    cog_conteudos = {
        'geral': """def configurar(bot):
    @bot.comando_hibrido("ping", descricao="Verifica se o bot está online", aliases=["latencia"])
    async def ping(ctx):
        await ctx.responder("Pong! O Pimcord está online.")

    @bot.comando_hibrido("ajuda", descricao="Lista os comandos disponíveis no bot")
    async def ajuda(ctx):
        await ctx.responder("Use os comandos disponíveis no servidor.")
""",
        'limpeza': """from pimcord import Permissoes


def configurar(bot):
    @bot.comando_hibrido(
        "clear",
        descricao="Apaga de 1 a 100 mensagens deste canal",
        aliases=["limpar"],
        permissoes=int(Permissoes.gerenciar_mensagens),
    )
    async def clear(ctx, quantidade: int = 10):
        canal = ctx.canal_atual
        if canal is None or not hasattr(canal, "purge"):
            await ctx.responder("Este comando precisa ser usado em um canal de texto.")
            return
        quantidade = max(1, min(100, quantidade))
        apagadas = await canal.purge(limite=quantidade)
        total = len(apagadas) if apagadas is not None else quantidade
        await ctx.responder(f"🧹 Apaguei {total} mensagem(ns).")
""",
        'economia': """from pimcord import EconomiaSQLite


def configurar(bot):
    banco = EconomiaSQLite("economia.sqlite3", diaria=100)

    @bot.comando_hibrido("saldo", descricao="Consulta o saldo de moedas do autor")
    async def saldo(ctx):
        total = banco.saldo(ctx.autor_id or "desconhecido")
        await ctx.responder(f"Seu saldo atual é {total} moedas.")

    @bot.comando_hibrido("diaria", descricao="Resgata a recompensa diária de 100 moedas", aliases=["daily"])
    async def diaria(ctx):
        total = banco.diaria(ctx.autor_id or "desconhecido")
        await ctx.responder(f"Recompensa resgatada. Seu saldo agora é {total} moedas.")

    @bot.comando_hibrido("ranking", descricao="Mostra os maiores saldos do servidor", aliases=["top"])
    async def ranking(ctx):
        linhas = banco.ranking()
        if not linhas:
            await ctx.responder("Ainda não há usuários no ranking.")
            return
        texto = "\\n".join(f"{i}. {linha['usuario_id']}: {linha['saldo']} moedas" for i, linha in enumerate(linhas, 1))
        await ctx.responder(texto)
""",
        'moderacao': """import sqlite3
from pimcord import Permissoes


def configurar(bot):
    @bot.comando_hibrido(
        "limpar",
        descricao="Apaga de 1 a 100 mensagens deste canal",
        aliases=["purge"],
        permissoes=int(Permissoes.gerenciar_mensagens),
    )
    async def limpar(ctx, quantidade: int = 10):
        canal = ctx.canal_atual
        if canal is None:
            await ctx.responder("Este comando precisa ser usado em um canal de texto.")
            return
        quantidade = max(1, min(100, quantidade))
        apagadas = await canal.purge(limite=quantidade)
        total = len(apagadas) if apagadas is not None else quantidade
        await ctx.responder(f"Apaguei {total} mensagem(ns).")

    @bot.comando_hibrido(
        "avisar",
        descricao="Registra uma advertência persistente para um membro",
        permissoes=int(Permissoes.gerenciar_mensagens),
    )
    async def avisar(ctx, membro: str, motivo: str = "Sem motivo informado"):
        with sqlite3.connect("moderacao.sqlite3") as banco:
            banco.execute("CREATE TABLE IF NOT EXISTS avisos (id INTEGER PRIMARY KEY, servidor_id TEXT, membro TEXT, motivo TEXT, autor TEXT)")
            banco.execute("INSERT INTO avisos (servidor_id, membro, motivo, autor) VALUES (?, ?, ?, ?)", (getattr(ctx.canal_atual, "servidor_id", None), membro, motivo, ctx.autor_id))
            banco.commit()
        await ctx.responder(f"Advertência registrada para {membro}: {motivo}.")
""",
        'tickets': """from pimcord import Permissoes


def configurar(bot):
    @bot.comando_hibrido("ticket", descricao="Cria um canal de atendimento", aliases=["suporte"])
    async def ticket(ctx, assunto: str = "atendimento"):
        canal = ctx.canal_atual
        servidor_id = getattr(canal, "servidor_id", None)
        cliente = getattr(canal, "cliente", None)
        if not servidor_id or cliente is None:
            await ctx.responder("Não consegui identificar o servidor deste atendimento.")
            return
        nome = "ticket-" + "-".join(assunto.lower().split())[:70]
        criado = await cliente.criar_canal(servidor_id, name=nome, type=0, topic=f"Atendimento de {ctx.autor_id}: {assunto}")
        await ctx.responder(f"Ticket criado: <#{criado.get('id', '')}>.")

    @bot.comando_hibrido("fechar_ticket", descricao="Fecha o canal atual de atendimento", aliases=["fechar"], permissoes=int(Permissoes.gerenciar_canais))
    async def fechar_ticket(ctx):
        canal = ctx.canal_atual
        cliente = getattr(canal, "cliente", None)
        if canal is None or cliente is None:
            await ctx.responder("Este comando precisa ser usado em um canal de ticket.")
            return
        await cliente.excluir_canal(canal.id)
""",
        'boas_vindas': """def configurar(bot):
    @bot.evento("membro_adicionado")
    async def membro_entrou(membro):
        bot.logger.info("Novo membro recebido: %s", getattr(membro, "nome", membro))

    @bot.comando_hibrido("configurar_boas_vindas", descricao="Mostra o estado do módulo de boas-vindas")
    async def configurar_boas_vindas(ctx):
        await ctx.responder("Boas-vindas ativas. Registre um canal específico para mensagens de entrada.")
""",
        'diversao': """import random


def configurar(bot):
    @bot.comando_hibrido("dado", descricao="Rola um dado de seis lados")
    async def dado(ctx):
        await ctx.responder(f"{ctx.autor_id or 'Jogador'} rolou: {random.randint(1, 6)}.")

    @bot.comando_hibrido("moeda", descricao="Lança uma moeda e informa o resultado")
    async def moeda(ctx):
        await ctx.responder(f"Resultado: {random.choice(('cara', 'coroa'))}.")
""",
        'musica': """def configurar(bot):
    fila = []

    @bot.comando_hibrido("tocar", descricao="Adiciona uma faixa à fila de reprodução", aliases=["play"])
    async def tocar(ctx, faixa: str):
        fila.append(faixa)
        await ctx.responder(f"🎵 Adicionei **{faixa}** à fila. Posição: {len(fila)}.")

    @bot.comando_hibrido("fila", descricao="Mostra a fila de reprodução")
    async def fila_atual(ctx):
        await ctx.responder("📃 Fila vazia." if not fila else "📃 Fila: " + "\\n".join(f"{i}. {item}" for i, item in enumerate(fila, 1)))

    @bot.comando_hibrido("pausar", descricao="Marca a reprodução como pausada")
    async def pausar(ctx):
        await ctx.responder("⏸️ Reprodução pausada. A fila foi preservada.")

    @bot.comando_hibrido("parar", descricao="Limpa a fila de reprodução")
    async def parar(ctx):
        fila.clear()
        await ctx.responder("⏹️ Reprodução encerrada e fila limpa.")
""",
        'lembretes': """import sqlite3
from datetime import datetime


def configurar(bot):
    banco = sqlite3.connect("lembretes.sqlite3", check_same_thread=False)
    banco.execute("CREATE TABLE IF NOT EXISTS lembretes (id INTEGER PRIMARY KEY AUTOINCREMENT, autor TEXT, texto TEXT, horario TEXT)")
    banco.commit()

    @bot.comando_hibrido("lembrar", descricao="Salva um lembrete com texto e horário")
    async def lembrar(ctx, horario: str, texto: str):
        datetime.strptime(horario, "%Y-%m-%d %H:%M")
        cursor = banco.execute("INSERT INTO lembretes (autor, texto, horario) VALUES (?, ?, ?)", (ctx.autor_id, texto, horario))
        banco.commit()
        await ctx.responder(f"⏰ Lembrete #{cursor.lastrowid} salvo para {horario}.")

    @bot.comando_hibrido("lembretes", descricao="Lista seus lembretes salvos")
    async def listar_lembretes(ctx):
        linhas = banco.execute("SELECT id, horario, texto FROM lembretes WHERE autor = ? ORDER BY horario", (ctx.autor_id,)).fetchall()
        await ctx.responder("📌 Você não possui lembretes." if not linhas else "📌 " + "\\n".join(f"#{id_} — {horario} — {texto}" for id_, horario, texto in linhas))
""",
        'quiz': """import random


def configurar(bot):
    perguntas = [("Qual linguagem o Pimcord usa?", "python"), ("Qual comando testa a conexão?", "ping")]

    @bot.comando_hibrido("quiz", descricao="Apresenta uma pergunta do quiz")
    async def quiz(ctx):
        pergunta, resposta = random.choice(perguntas)
        await ctx.responder(f"🧠 Pergunta: {pergunta}\\nResponda com `!responder {resposta}`.")

    @bot.comando_hibrido("responder", descricao="Confere uma resposta do quiz")
    async def responder(ctx, resposta: str):
        correta = any(resposta.casefold() == item[1] for item in perguntas)
        await ctx.responder("✅ Resposta aceita!" if correta else "❌ Resposta incorreta. Tente novamente.")

    @bot.comando_hibrido("ranking_quiz", descricao="Mostra o ranking do quiz")
    async def ranking_quiz(ctx):
        await ctx.responder("🏆 O ranking será preenchido conforme as respostas corretas forem registradas.")
""",
        'utilidades': """def configurar(bot):
    @bot.comando_hibrido("userinfo", descricao="Mostra o identificador do autor", aliases=["perfil"])
    async def userinfo(ctx):
        await ctx.responder(f"Seu ID é {ctx.autor_id or 'desconhecido'}.")

    @bot.comando_hibrido("servidor", descricao="Mostra o identificador do servidor atual")
    async def servidor(ctx):
        servidor_id = getattr(ctx.canal_atual, "servidor_id", None)
        await ctx.responder(f"Servidor atual: {servidor_id or 'mensagem privada'}.")
""",
        'views': """from pimcord import View


def configurar(bot):
    view = View(timeout=None)

    @view.botao("confirmar", texto="Confirmar", estilo="sucesso")
    async def confirmar(interacao):
        await interacao.responder("Ação confirmada.", ephemeral=True)

    @view.botao("cancelar", texto="Cancelar", estilo="perigo")
    async def cancelar(interacao):
        await interacao.responder("Ação cancelada.", ephemeral=True)

    bot.registrar_view(view)

    @bot.comando_hibrido("painel", descricao="Envia uma View persistente com botões")
    async def painel(ctx):
        await ctx.responder("Escolha uma ação:", view=view)
""",
        'permissoes': """from pimcord import Permissoes, SobrescritaPermissao


def configurar(bot):
    @bot.comando_hibrido("privado", descricao="Define permissão privada para o autor")
    async def privado(ctx):
        canal = ctx.canal_atual
        if canal is None or not ctx.autor_id:
            await ctx.responder("Este comando precisa de um autor e um canal.")
            return
        regra = SobrescritaPermissao.usuario(ctx.autor_id, permitir=Permissoes.ver_canal | Permissoes.enviar_mensagens)
        await canal.definir_permissoes(regra)
        await ctx.responder("Permissão privada aplicada ao autor.")
""",
        'tarefas': """import asyncio
from pimcord import TarefaAgendada


def configurar(bot):
    async def consultar():
        await asyncio.sleep(0)

    tarefa = TarefaAgendada(consultar, intervalo=60, nome="consulta_periodica")
    bot.agendador.registrar(tarefa)

    async def cancelar():
        tarefa.parar()

    @bot.evento("ao_desligar")
    async def encerrar_tarefas():
        await cancelar()
        await bot.agendador.encerrar()
""",
        'rest': """def configurar(bot):
    @bot.comando_hibrido("historico", descricao="Consulta o histórico com limite REST")
    async def historico(ctx, limite: int = 50):
        canal = ctx.canal_atual
        if canal is None:
            await ctx.responder("Este comando precisa de um canal.")
            return
        limite = max(1, min(100, limite))
        mensagens = await canal.historico(limite=limite)
        await ctx.responder(f"Foram encontradas {len(mensagens)} mensagem(ns), respeitando o limite {limite}.")
""",
        'seguranca': """def configurar(bot):
    @bot.comando_hibrido("diagnostico", descricao="Executa uma verificação segura do bot")
    async def diagnostico(ctx):
        try:
            await ctx.responder("✅ Bot operacional e tratamento de erros ativo.")
        except Exception:
            bot.logger.exception("Falha ao responder ao diagnóstico")
""",
    }
    if dominios.get("personalizado"):
        import json
        analises = _analisar_comandos_livres(pedido, recursos_livres)
        linhas = ["from pimcord import Permissoes", "", "", "def configurar(bot):"]
        for analise in analises:
            nome_comando = analise["nome"]
            identificador = re.sub(r"[^a-zA-Z0-9_]", "_", nome_comando)
            descricao = analise["descricao"].replace('"', '\\"')
            parametros = ["ctx"] + [item.split(":", 1)[0] + ": " + item.split(":", 1)[1].strip() for item in analise["parametros"]]
            assinatura = ", ".join(parametros)
            requisito = analise["requisitos"].replace('"', '\\"') or "requisito explícito"
            corpo = [f'    @bot.comando_hibrido("{nome_comando}", descricao="{descricao[:100]}")', f"    async def {identificador}({assinatura}):", f'        """Implementação gerada para: {requisito[:180]}"""']
            requisito_json = json.dumps(requisito[:180], ensure_ascii=False)
            if "apagar" in analise["acoes"] and "mensag" in requisito.casefold():
                corpo.extend(["        limite = max(1, min(100, quantidade)) if 'quantidade' in locals() else 100", "        apagadas = await ctx.canal_atual.purge(limite=limite)", '        await ctx.responder(f"✅ {len(apagadas)} mensagens apagadas.")'])
            elif "listar" in analise["acoes"] and "mensag" in requisito.casefold():
                corpo.extend(["        limite = max(1, min(100, quantidade)) if 'quantidade' in locals() else 50", "        mensagens = await ctx.canal_atual.historico(limite=limite)", '        texto = "\\n".join(f"{item.autor.nome}: {item.conteudo}" for item in mensagens)', '        await ctx.responder(texto or "Não há mensagens para listar.")'])
            elif "enviar" in analise["acoes"]:
                corpo.extend([f"        await ctx.responder({requisito_json})"])
            elif "banir" in analise["acoes"] and "membro" in requisito.casefold():
                corpo.extend(["        canal = ctx.canal_atual", "        cliente = getattr(canal, 'cliente', None)", "        servidor_id = getattr(canal, 'servidor_id', None)", "        if cliente is None or not servidor_id:", '            await ctx.responder("Não consegui identificar o servidor para banir o membro.")', "            return", "        await cliente.banir_membro(servidor_id, membro, motivo=motivo if 'motivo' in locals() else None)", '        await ctx.responder("✅ Membro banido.")'])
            else:
                corpo.extend([f'        await ctx.responder("✅ Requisito recebido: {requisito[:180]}")'])
            corpo.append("")
            linhas.extend(corpo)
        cog_conteudos["comandos"] = "\n".join(linhas) + "\n"
        especificacao = {
            "pedido": pedido.strip(),
            "comandos": analises,
            "dominios_detectados": [nome for nome, ativo in dominios.items() if ativo and nome != "personalizado"],
            "observacao": "Estrutura intermediária usada pelo renderer local e pelo agente neural.",
        }
        cog_conteudos["especificacao"] = "# Especificação estruturada pela PimcordIA.\n" + json.dumps(especificacao, ensure_ascii=False, indent=2) + "\n"
        dominios["comandos"] = True
        dominios["especificacao"] = True
        dominios.pop("personalizado", None)
    imports = []
    configuracoes = []
    for dominio, ativo in dominios.items():
        if ativo:
            caminho = f"cogs/{dominio}.py"
            arquivos.append({"caminho": caminho, "conteudo": cog_conteudos[dominio]})
            imports.append(f"from .{dominio} import configurar as configurar_{dominio}")
            configuracoes.append(f"    configurar_{dominio}(bot)")
    conteudo_cogs = "\n".join(imports) + "\n\ndef configurar(bot):\n"
    conteudo_cogs += "\n".join(configuracoes) if configuracoes else "    pass"
    conteudo_cogs += "\n"
    arquivos.append({"caminho": "cogs/__init__.py", "conteudo": conteudo_cogs})
    return ProjetoGerado(validar_projeto({"nome": nome, "resumo": pedido.strip()[:2000], "arquivos": arquivos}))


__all__ = ["ErroProjetoIA", "SCHEMA_PROJETO_BOT", "validar_projeto", "ProjetoGerado", "AgenteConstrutorPimcord", "GeradorProjetoIA", "criar_projeto_ia", "projeto_local_pimcord"]
