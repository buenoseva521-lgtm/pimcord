"""Geração opcional de planos de bot com cliente OpenAI-compatible.

O módulo não importa SDK externo no núcleo. O cliente é injetado pelo chamador;
sem cliente, a aplicação deve usar o interpretador local de ``pronto.py``.
"""
from __future__ import annotations

import inspect
import json
import os
from typing import Any


def catalogar_api_pimcord() -> dict[str, dict[str, Any]]:
    """Retorna os símbolos públicos do catálogo runtime instalado."""
    try:
        from .catalogo import catalogar
        return catalogar().get("modulos", {}).get("pimcord", {})
    except Exception:
        return {}


def contexto_python_pimcord(descricao: str, *, limite: int = 12) -> str:
    """Recupera contexto local relevante de Python e da API Pimcord."""
    try:
        from .memoria_ia import contexto_local
        return contexto_local(descricao, limite=limite)
    except Exception:
        return ""


def resumo_api_pimcord() -> str:
    """Retorna um resumo compacto e legível para planejamento da IA."""
    try:
        from .catalogo import resumo_catalogo
        return resumo_catalogo()
    except Exception:
        linhas: list[str] = []
        for nome, item in catalogar_api_pimcord().items():
            assinatura = item.get("assinatura") or ""
            metodos = ", ".join(item.get("metodos", {}))
            linhas.append(f"{nome}{assinatura}: {metodos}")
        return "\n".join(linhas)
from urllib import request as urllib_request



class ErroGeradorIA(ValueError):
    """Resposta ausente, inválida ou fora do contrato seguro."""


SCHEMA_PLANO_BOT: dict[str, Any] = {
    "type": "object",
    "properties": {
        "prefixo": {"type": "string", "minLength": 1, "maxLength": 3},
        "intents": {"type": "string", "enum": ["basicos", "todos"]},
        "comandos": {
            "type": "array",
            "maxItems": 50,
            "items": {
                "type": "object",
                "properties": {
                    "nome": {"type": "string", "minLength": 1, "maxLength": 32},
                    "resposta": {"type": "string", "maxLength": 2000},
                    "aliases": {"type": "array", "items": {"type": "string", "maxLength": 32}, "maxItems": 10},
                },
                "required": ["nome", "resposta", "aliases"],
                "additionalProperties": False,
            },
        },
    },
    "required": ["prefixo", "intents", "comandos"],
    "additionalProperties": False,
}

_PROMPT_SISTEMA = (
    "Você transforma descrições em um plano JSON de bot Pimcord. "
    "Retorne somente o schema solicitado e implemente o pedido do usuário sem inventar recursos. "
    "Não inclua valores reais de CPF, documentos pessoais, senhas, cartões, tokens ou credenciais; "
    "quando necessário, use placeholders seguros e variáveis de ambiente."
)


def validar_plano(plano: Any) -> dict[str, Any]:
    if not isinstance(plano, dict):
        raise ErroGeradorIA("O plano da IA não é um objeto JSON.")
    if set(plano) != {"prefixo", "intents", "comandos"}:
        raise ErroGeradorIA("O plano contém campos não permitidos.")
    if not isinstance(plano["prefixo"], str) or not 1 <= len(plano["prefixo"]) <= 3 or any(c.isspace() for c in plano["prefixo"]):
        raise ErroGeradorIA("Prefixo inválido no plano.")
    if plano["intents"] not in {"basicos", "todos"}:
        raise ErroGeradorIA("Intents inválidos no plano.")
    comandos = plano["comandos"]
    if not isinstance(comandos, list) or len(comandos) > 50:
        raise ErroGeradorIA("Lista de comandos inválida.")
    vistos: set[str] = set()
    for comando in comandos:
        if not isinstance(comando, dict) or set(comando) != {"nome", "resposta", "aliases"}:
            raise ErroGeradorIA("Comando fora do schema seguro.")
        nome = comando["nome"]
        if not isinstance(nome, str) or not nome or len(nome) > 32 or any(c.isspace() for c in nome):
            raise ErroGeradorIA("Nome de comando inválido.")
        if nome.casefold() in vistos:
            raise ErroGeradorIA("Comandos duplicados não são permitidos.")
        vistos.add(nome.casefold())
        if not isinstance(comando["resposta"], str) or len(comando["resposta"]) > 2000:
            raise ErroGeradorIA("Resposta de comando inválida.")
        if not isinstance(comando["aliases"], list) or len(comando["aliases"]) > 10:
            raise ErroGeradorIA("Aliases inválidos.")
        for alias in comando["aliases"]:
            if not isinstance(alias, str) or not alias or len(alias) > 32 or any(c.isspace() for c in alias):
                raise ErroGeradorIA("Alias inválido.")
    return plano


CATALOGO_PIMCORD: dict[str, tuple[str, ...]] = {
    "economia": ("saldo", "diaria", "ranking", "pagar", "loja"),
    "moderacao": ("avisar", "silenciar", "expulsar", "banir", "desbanir", "limpar"),
    "tickets": ("ticket", "fechar_ticket", "adicionar_membro"),
    "boas_vindas": ("ola", "configurar_boas_vindas"),
    "utilidades": ("ajuda", "ping", "avatar", "userinfo", "servidor"),
    "diversao": ("moeda", "dado", "8ball", "sorteio"),
}


def _nomes_sugeridos(descricao: str) -> list[str]:
    """Extrai somente nomes de comandos escritos explicitamente pelo usuário.

    Palavras como ``asyncio``, ``pedido`` ou ``moderação`` são contexto, não
    comandos. Um comando livre precisa aparecer com ``!``, ``/`` ou ``.``.
    """
    import re
    import unicodedata
    texto = unicodedata.normalize("NFKD", descricao.casefold()).encode("ascii", "ignore").decode()
    encontrados: list[str] = []
    for bruto in re.findall(r"(?<![a-z0-9_])[.!/]([a-z][a-z0-9_-]{1,31})", texto):
        nome = re.sub(r"[^a-z0-9_]", "_", bruto.replace("-", "_")).strip("_")
        if nome and nome not in encontrados:
            encontrados.append(nome)
    return encontrados[:50]


def _validar_pedido_dados_sensiveis(descricao: str) -> None:
    """Recusa coleta ou extração de identificadores e credenciais pessoais."""
    import re
    import unicodedata
    texto = unicodedata.normalize("NFKD", descricao.casefold()).encode("ascii", "ignore").decode()
    padrao = r"(?<![a-z0-9])(?:cpf|cnpj|rg|titulo de eleitor|cartao de credito|cartao credito|senha|password|documento pessoal|dados bancarios|numero do cartao|token|chave secreta|chave de api|api key|credencial)(?![a-z0-9])"
    if re.search(padrao, texto):
        raise ErroGeradorIA("Por segurança, a PimcordIA não gera coleta ou extração de CPF, documentos, senhas, cartões, tokens, chaves ou credenciais.")


def _plano_local(descricao: str) -> dict[str, Any]:
    """PimcordIA própria: interpreta intenções e compõe um plano seguro local."""
    import re
    _validar_pedido_dados_sensiveis(descricao)
    texto = descricao.casefold().strip()
    comandos: list[dict[str, Any]] = []

    def adicionar(nome: str, resposta: str, aliases: list[str] | None = None) -> None:
        if not any(item["nome"] == nome for item in comandos):
            comandos.append({"nome": nome, "resposta": resposta, "aliases": aliases or []})

    # Comandos auxiliares só entram quando foram pedidos explicitamente.
    nomes_explicitos = _nomes_sugeridos(descricao)
    if "ping" in nomes_explicitos or re.search(r"\b(?:comando|comandos?)\s+(?:de\s+)?ping\b", texto):
        adicionar("ping", "🏓 Pong! O Pimcord está online.", ["latencia"])
    if "ajuda" in nomes_explicitos or re.search(r"\b(?:comando|comandos?)\s+(?:de\s+)?ajuda\b", texto):
        adicionar("ajuda", "🧭 Use os comandos disponíveis neste bot Pimcord.")
    for nome in nomes_explicitos:
        if nome not in {"ping", "ajuda"}:
            adicionar(nome, f"🧩 O comando `{nome}` foi criado a partir do seu pedido.")
    dominios: set[str] = set()
    if any(chave in texto for chave in ("economia", "saldo", "moedas", "dinheiro", "banco")):
        dominios.add("economia")
        adicionar("saldo", "Seu saldo será consultado pelo módulo de economia.")
        adicionar("diaria", "Sua recompensa diária será processada pelo módulo de economia.", ["daily"])
        adicionar("ranking", "O ranking da economia será exibido aqui.", ["top"])
        adicionar("pagar", "Informe o usuário e o valor para realizar uma transferência segura.")
        adicionar("loja", "A loja do servidor está disponível.")
    if any(chave in texto for chave in ("moderação", "moderacao", "moderar", "administração", "administracao")):
        dominios.add("moderacao")
        adicionar("avisar", "Informe o membro para registrar uma advertência.")
        adicionar("silenciar", "Informe o membro e a duração do silêncio.", ["timeout"])
        adicionar("expulsar", "Informe o membro que deve ser expulso.")
        adicionar("banir", "Informe o membro que deve ser banido.")
        adicionar("limpar", "Informe a quantidade de mensagens que deseja limpar.", ["purge"])
    if any(chave in texto for chave in ("ticket", "suporte", "atendimento")):
        dominios.add("tickets")
        adicionar("ticket", "Seu ticket será aberto em um canal privado.")
        adicionar("fechar_ticket", "Este ticket será encerrado após confirmação.", ["fechar"])
    if any(chave in texto for chave in ("boas-vindas", "boas vindas", "saudação", "saudacoes", "saudações", "entrada")):
        dominios.add("boas_vindas")
        adicionar("ola", "Olá! Seja bem-vindo ao servidor.", ["oi"])
        adicionar("configurar_boas_vindas", "Configure o canal de boas-vindas nas opções do servidor.")
    if any(chave in texto for chave in ("musica", "música", "player", "audio", "som")):
        dominios.add("musica")
        adicionar("tocar", "🎵 Informe uma música ou URL para iniciar a reprodução.", ["play"])
        adicionar("pausar", "⏸️ A reprodução atual foi pausada.")
        adicionar("fila", "📃 A fila de reprodução deste servidor será exibida.")
        adicionar("parar", "⏹️ A reprodução foi encerrada.")
    if any(chave in texto for chave in ("lembrete", "lembretes", "lembrar", "agenda")):
        dominios.add("lembretes")
        adicionar("lembrar", "⏰ Informe o horário e o texto do lembrete.")
        adicionar("lembretes", "📌 Seus lembretes serão listados aqui.")
        adicionar("cancelar_lembrete", "🗑️ Informe o identificador do lembrete para cancelá-lo.")
    if any(chave in texto for chave in ("quiz", "perguntas", "trivia")):
        dominios.add("quiz")
        adicionar("quiz", "🧠 Uma pergunta será apresentada para você responder.")
        adicionar("ranking_quiz", "🏆 O ranking do quiz será exibido.")
    if any(chave in texto for chave in ("diversão", "diversao", "jogo", "entretenimento")):
        dominios.add("diversao")
        adicionar("moeda", "Resultado: cara ou coroa.")
        adicionar("dado", "Resultado do dado: 6.")
        adicionar("sorteio", "O sorteio será configurado com participantes do servidor.")
    if any(chave in texto for chave in ("utilidade", "utilidades", "informações", "informacoes", "perfil")):
        dominios.add("utilidades")
        adicionar("avatar", "O avatar solicitado será exibido.")
        adicionar("userinfo", "As informações públicas do usuário serão exibidas.")
        adicionar("servidor", "As informações públicas do servidor serão exibidas.")
    if any(chave in texto for chave in ("completo", "tudo", "super", "profissional")):
        for dominio in ("utilidades", "economia", "moderacao", "tickets"):
            dominios.add(dominio)
        adicionar("sobre", "Sou um bot Pimcord modular criado pela PimcordIA.")
    if not dominios:
        if len(comandos) <= 2:
            adicionar("sobre", "🔎 Descreva o módulo, ação e dados que o bot deve usar para gerar um projeto específico.")
        else:
            adicionar("sobre", "✅ Este bot foi planejado a partir do seu prompt; os comandos listados representam as funcionalidades solicitadas.")
    return validar_plano({"prefixo": "!", "intents": "todos" if dominios or "intents" in texto else "basicos", "comandos": comandos})


class PimcordIA:
    """Núcleo próprio da PimcordIA, sem provider, SDK ou chave externa.

    Este motor usa o catálogo local da API Pimcord, análise de intenção e
    composição segura de módulos. Ele não promete ser um modelo neural geral;
    sua especialidade é transformar pedidos em projetos Pimcord verificáveis.
    """

    nome = "PimcordIA"
    versao_conhecimento = "0.6.7"

    def __init__(self, modelo_local: str | os.PathLike[str] | None = None) -> None:
        configurado = modelo_local or os.environ.get("PIMCORDIA_MODELO")
        self.modelo_local = str(configurado).strip() if configurado else None

    def analisar(self, descricao: str) -> dict[str, Any]:
        if not isinstance(descricao, str) or not descricao.strip():
            raise ErroGeradorIA("Descrição vazia.")
        texto = descricao.casefold()
        dominios = [nome for nome, sinais in {
            "economia": ("economia", "saldo", "moedas", "dinheiro"),
            "moderacao": ("moderação", "moderacao", "moderar", "banir"),
            "tickets": ("ticket", "suporte", "atendimento"),
            "boas_vindas": ("boas-vindas", "saudação", "entrada"),
            "diversao": ("diversão", "diversao", "jogo", "sorteio"),
            "musica": ("música", "musica", "player", "áudio", "audio", "som"),
            "lembretes": ("lembrete", "lembretes", "lembrar", "agenda"),
            "quiz": ("quiz", "perguntas", "trivia"),
            "utilidades": ("utilidade", "perfil", "informações", "userinfo"),
        }.items() if any(sinal in texto for sinal in sinais)]
        se_completo = any(sinal in texto for sinal in ("completo", "profissional", "super", "tudo"))
        if se_completo:
            dominios = list(dict.fromkeys([*dominios, "utilidades", "economia", "moderacao", "tickets"]))
        catalogo = catalogar_api_pimcord()
        return {
            "descricao": descricao.strip(),
            "dominios": dominios,
            "api": catalogo,
            "resumo_api": resumo_api_pimcord(),
            "contexto_local": contexto_python_pimcord(descricao),
            "completo": se_completo,
            "comandos_catalogados": tuple(dict.fromkeys(
                comando for dominio in dominios for comando in CATALOGO_PIMCORD.get(dominio, ())
            )),
            "comandos_hibridos": True,
            "persistencia": any(palavra in texto for palavra in ("sqlite", "banco", "persistente", "economia")),
        }

    def planejar(self, descricao: str) -> dict[str, Any]:
        """Cria um plano técnico verificável antes da escrita dos arquivos."""
        analise = self.analisar(descricao)
        simbolos = analise["api"]
        necessarios: set[str] = {"Bot", "Intents"}
        validacoes = ["compilar todos os arquivos Python", "validar AST e caminhos"]
        riscos: list[str] = []
        if "moderacao" in analise["dominios"]:
            necessarios.update(("Canal", "Permissoes"))
            validacoes.append("confirmar purge limitado a 100 e permissão de gerenciar mensagens")
        if "tickets" in analise["dominios"]:
            necessarios.update(("Canal", "Permissoes"))
            validacoes.append("confirmar criação de canal e proteção contra nomes inválidos")
        if "economia" in analise["dominios"]:
            necessarios.add("EconomiaSQLite")
            validacoes.append("confirmar persistência SQLite e consultas parametrizadas")
        if "musica" in analise["dominios"]:
            validacoes.append("confirmar comandos de reprodução sem prometer conexão de voz não implementada")
        if "lembretes" in analise["dominios"]:
            validacoes.append("confirmar persistência e validação de horários dos lembretes")
        if "quiz" in analise["dominios"]:
            validacoes.append("confirmar perguntas, respostas e ranking sem repetir argumentos")
        if analise["persistencia"]:
            validacoes.append("confirmar .env.example e ausência de segredo no código")
        ausentes = sorted(nome for nome in necessarios if nome not in simbolos)
        if ausentes:
            riscos.append("Símbolos indisponíveis na instalação: " + ", ".join(ausentes))
        return {
            "pedido": analise["descricao"],
            "dominios": analise["dominios"],
            "simbolos_necessarios": sorted(necessarios),
            "validacoes": validacoes,
            "riscos": riscos,
            "arquitetura": ["bot.py", "config.py", "cogs/__init__.py", "README.md", ".env.example"],
            "comandos": analise["comandos_catalogados"],
        }

    def gerar_plano(self, descricao: str) -> dict[str, Any]:
        """Retorna um plano neural local quando configurado ou usa o fallback."""
        if not isinstance(descricao, str) or not descricao.strip():
            raise ErroGeradorIA("Descrição vazia.")
        _validar_pedido_dados_sensiveis(descricao)
        if self.modelo_local:
            from .modelo_neural import ErroModeloNeural, ModeloNeuralLocal
            try:
                modelo = ModeloNeuralLocal(self.modelo_local, base=os.environ.get("PIMCORDIA_MODELO_BASE"))
                prompt = (
                    _PROMPT_SISTEMA + "\nSchema obrigatório:\n" + json.dumps(SCHEMA_PLANO_BOT, ensure_ascii=False)
                    + "\nMemória local relevante:\n" + contexto_python_pimcord(descricao, limite=16)
                    + "\nPedido:\n" + descricao[:12000]
                )
                return validar_plano(modelo.gerar_json(prompt, max_novos_tokens=2048, temperatura=0.1))
            except ErroModeloNeural as erro:
                raise ErroGeradorIA(f"Falha no modelo local configurado: {erro}") from erro
        raise ErroGeradorIA(
            "Nenhum checkpoint neural local foi configurado. Configure PIMCORDIA_MODELO "
            "com um modelo PimcordIA treinado; a geração fallback foi removida."
        )

    def gerar_projeto(self, descricao: str):
        """Gera um projeto neural quando há checkpoint local; senão usa fallback."""
        if not isinstance(descricao, str) or not descricao.strip():
            raise ErroGeradorIA("Descrição vazia.")
        _validar_pedido_dados_sensiveis(descricao)
        texto = descricao.casefold()
        tokens_inseguros = ("../", "..\\", "/etc/", "\\windows\\", "../../", "\\\\")
        if any(token in texto for token in tokens_inseguros):
            raise ErroGeradorIA("A descrição contém um caminho inseguro ou tentativa de traversal.")
        self.analisar(descricao)
        if self.modelo_local:
            from .modelo_neural import AgenteNeuralLocal, ModeloNeuralLocal, ErroModeloNeural
            try:
                base_local = os.environ.get("PIMCORDIA_MODELO_BASE")
                return AgenteNeuralLocal(ModeloNeuralLocal(self.modelo_local, base=base_local), max_iteracoes=3).construir(descricao)
            except ErroModeloNeural:
                raise
        raise ErroGeradorIA(
            "Nenhum checkpoint neural local foi configurado. Configure PIMCORDIA_MODELO "
            "com um modelo PimcordIA treinado; a geração fallback foi removida."
        )


class IAIntegradaPimcord:
    """Compatibilidade para o núcleo próprio e provider HTTP opcional."""

    def __init__(self, *, url: str | None = None, chave: str | None = None, modelo: str | None = None, timeout: float = 30.0):
        self.url = url or os.environ.get("PIMCORD_IA_URL")
        self.chave = chave or os.environ.get("PIMCORD_IA_CHAVE")
        self.modelo = modelo or os.environ.get("PIMCORD_IA_MODELO", "gpt-5")
        self.timeout = timeout

    def gerar_projeto(self, descricao: str):
        """Gera arquivos, cogs e configuração usando provider ou fallback local."""
        _validar_pedido_dados_sensiveis(descricao)
        from .projeto_ia import GeradorProjetoIA, projeto_local_pimcord
        if not self.url or not self.chave:
            raise ErroGeradorIA(
                "Nenhum provider ou checkpoint neural foi configurado; a geração genérica foi removida."
            )

        class ClienteHTTP:
            def __init__(self, url: str, chave: str, timeout: float):
                self.url, self.chave, self.timeout = url, chave, timeout

            @property
            def chat(self):
                return self

            @property
            def completions(self):
                return self

            def create(self, **kwargs):
                requisicao = urllib_request.Request(
                    self.url.rstrip("/") + "/chat/completions",
                    data=json.dumps(kwargs).encode("utf-8"),
                    headers={"Authorization": f"Bearer {self.chave}", "Content-Type": "application/json"},
                    method="POST",
                )
                with urllib_request.urlopen(requisicao, timeout=self.timeout) as resposta:
                    return type("Resposta", (), {"choices": [type("Escolha", (), {"message": type("Mensagem", (), {"content": json.loads(resposta.read().decode("utf-8"))["choices"][0]["message"]["content"]})()})()]})()

        cliente = ClienteHTTP(self.url, self.chave, self.timeout)
        return GeradorProjetoIA(cliente, modelo=self.modelo).gerar(descricao)

    def gerar_plano(self, descricao: str) -> dict[str, Any]:
        if not isinstance(descricao, str) or not descricao.strip():
            raise ErroGeradorIA("Descrição vazia.")
        _validar_pedido_dados_sensiveis(descricao)
        if not self.url or not self.chave:
            return _plano_local(descricao)
        dados = json.dumps({
            "model": self.modelo,
            "messages": [{"role": "system", "content": _PROMPT_SISTEMA}, {"role": "user", "content": descricao[:12000]}],
            "response_format": {"type": "json_schema", "json_schema": {"name": "plano_bot_pimcord", "strict": True, "schema": SCHEMA_PLANO_BOT}},
            "max_completion_tokens": 3000,
        }).encode("utf-8")
        requisicao = urllib_request.Request(self.url.rstrip("/") + "/chat/completions", data=dados, headers={"Authorization": f"Bearer {self.chave}", "Content-Type": "application/json"}, method="POST")
        try:
            with urllib_request.urlopen(requisicao, timeout=self.timeout) as resposta:
                corpo = json.loads(resposta.read().decode("utf-8"))
            plano = json.loads(corpo["choices"][0]["message"]["content"])
            return validar_plano(plano)
        except Exception as erro:
            raise ErroGeradorIA(f"A IA configurada não respondeu com um plano válido: {erro}") from erro


class GeradorPlanoIA:
    """Gera planos seguros a partir de um cliente OpenAI-compatible injetado."""

    def __init__(self, cliente: Any, *, modelo: str = "gpt-5-mini"):
        if cliente is None:
            raise ErroGeradorIA("Injete um cliente LLM; o núcleo não cria conexões automaticamente.")
        self.cliente = cliente
        self.modelo = modelo

    def gerar_plano(self, descricao: str) -> dict[str, Any]:
        if not isinstance(descricao, str) or not descricao.strip():
            raise ErroGeradorIA("Descrição vazia.")
        _validar_pedido_dados_sensiveis(descricao)
        resposta = self.cliente.chat.completions.create(
            model=self.modelo,
            messages=[
                {"role": "system", "content": _PROMPT_SISTEMA},
                {"role": "user", "content": descricao[:12000]},
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {"name": "plano_bot_pimcord", "strict": True, "schema": SCHEMA_PLANO_BOT},
            },
            max_completion_tokens=3000,
        )
        conteudo = resposta.choices[0].message.content
        try:
            plano = json.loads(conteudo)
        except (TypeError, json.JSONDecodeError) as erro:
            raise ErroGeradorIA("A IA não retornou JSON válido.") from erro
        return validar_plano(plano)


__all__ = ["ErroGeradorIA", "SCHEMA_PLANO_BOT", "CATALOGO_PIMCORD", "catalogar_api_pimcord", "resumo_api_pimcord", "validar_plano", "PimcordIA", "IAIntegradaPimcord", "GeradorPlanoIA"]
