"""Diagnóstico e saúde do Pimcord em português."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class Verificacao:
    nome: str
    ok: bool
    mensagem: str
    severidade: str = "informacao"


@dataclass
class RelatorioSaude:
    verificacoes: list[Verificacao] = field(default_factory=list)

    @property
    def aprovado(self) -> bool:
        return not any(not item.ok and item.severidade == "erro" for item in self.verificacoes)

    @property
    def avisos(self) -> list[Verificacao]:
        return [item for item in self.verificacoes if not item.ok]

    def para_dict(self) -> dict[str, Any]:
        return {
            "aprovado": self.aprovado,
            "verificacoes": [item.__dict__ if hasattr(item, "__dict__") else {"nome": item.nome, "ok": item.ok, "mensagem": item.mensagem, "severidade": item.severidade} for item in self.verificacoes],
        }


def diagnosticar(bot: Any, *, exigir_token: bool = False) -> RelatorioSaude:
    """Analisa um Bot localmente sem executar rede ou expor o token."""
    relatorio = RelatorioSaude()
    configuracao = getattr(bot, "configuracao", None)
    token = getattr(configuracao, "token", None)
    application_id = getattr(configuracao, "application_id", None)
    intents = getattr(configuracao, "intents", None)
    relatorio.verificacoes.append(Verificacao("token", bool(token), "Token configurado." if token else "Token ainda não configurado.", "erro" if exigir_token else "aviso"))
    quantidade_prefixados = len(getattr(bot, "comandos", {}))
    quantidade_slash = len(getattr(bot, "comandos_slash", {}))
    relatorio.verificacoes.append(Verificacao("application_id", bool(application_id) or not quantidade_slash, "Application ID configurado." if application_id else "Application ID será descoberto no READY; slash commands aguardam a conexão.", "aviso"))
    relatorio.verificacoes.append(Verificacao("intents", intents is not None, "Intents disponíveis." if intents else "Intents não configurados; serão usados os padrões do Pimcord.", "aviso"))
    relatorio.verificacoes.append(Verificacao("mensagens", not quantidade_prefixados or bool(getattr(intents, "mensagens", False)), "Intent de mensagens habilitado." if not quantidade_prefixados or getattr(intents, "mensagens", False) else "Há comandos prefixados, mas o intent mensagens está desativado; o bot não receberá mensagens.", "erro"))
    relatorio.verificacoes.append(Verificacao("conteudo_mensagens", not quantidade_prefixados or bool(getattr(intents, "conteudo_mensagens", False)), "Conteúdo de mensagens habilitado." if not quantidade_prefixados or getattr(intents, "conteudo_mensagens", False) else "Há comandos prefixados, mas conteudo_mensagens está desativado; ative Message Content Intent no Portal do Discord.", "aviso"))
    relatorio.verificacoes.append(Verificacao("comandos", quantidade_prefixados > 0 or quantidade_slash > 0, f"{quantidade_prefixados} comandos prefixados e {quantidade_slash} slash registrados." if quantidade_prefixados or quantidade_slash else "Nenhum comando foi registrado; o bot poderá conectar, mas não responderá a comandos.", "aviso"))
    relatorio.verificacoes.append(Verificacao("views", True, f"{len(getattr(bot, 'views', []))} Views registradas."))
    gateway = getattr(bot, "gateway", None)
    relatorio.verificacoes.append(Verificacao("gateway", True, "Gateway inicializado." if gateway else "Gateway será inicializado após o diagnóstico."))
    return relatorio


__all__ = ["Verificacao", "RelatorioSaude", "diagnosticar"]
