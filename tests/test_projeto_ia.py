import json
from pathlib import Path

import pytest

import pimcord


class _Resposta:
    def __init__(self, conteudo):
        self.choices = [type("Escolha", (), {"message": type("Mensagem", (), {"content": conteudo})()})()]


class _Cliente:
    def __init__(self, projeto):
        self.projeto = projeto
        self.chat = type("Chat", (), {"completions": self})()
        self.chamada = None

    def create(self, **kwargs):
        self.chamada = kwargs
        return _Resposta(json.dumps(self.projeto))


def projeto_valido():
    return {
        "nome": "economia-bot",
        "resumo": "Bot de economia com SQLite",
        "arquivos": [
            {"caminho": "bot.py", "conteudo": "import os\nimport pimcord\nfrom pimcord import EconomiaSQLite\n\nbanco = EconomiaSQLite('economia.sqlite3')\n\n@pimcord.bot.comando_hibrido('saldo', descricao='Consulta o saldo de moedas')\nasync def saldo(ctx):\n    total = banco.saldo(ctx.autor_id or 'desconhecido')\n    await ctx.responder(f'Seu saldo é {total} moedas.')\n\nprint(os.environ.get('DISCORD_TOKEN', ''))\n"},
            {"caminho": "README.md", "conteudo": "# Economia\n"},
        ],
    }


def test_geracao_livre_valida_schema_e_salva(tmp_path):
    cliente = _Cliente(projeto_valido())
    projeto = pimcord.GeradorProjetoIA(cliente).gerar("Crie um bot de economia completo")
    raiz = projeto.salvar(tmp_path / "economia")
    assert (raiz / "bot.py").is_file()
    assert "DISCORD_TOKEN" not in cliente.chamada["messages"][1]["content"]


def test_rejeita_traversal():
    dado = projeto_valido()
    dado["arquivos"][0]["caminho"] = "../bot.py"
    with pytest.raises(pimcord.ErroProjetoIA):
        pimcord.validar_projeto(dado)


def test_ia_rejeita_traversal_no_prompt():
    with pytest.raises(pimcord.ErroGeradorIA, match="caminho inseguro|traversal"):
        pimcord.PimcordIA().gerar_projeto("gere ../../fora")


def test_rejeita_execucao_dinamica():
    dado = projeto_valido()
    dado["arquivos"][0]["conteudo"] = "exec('print(1)')"
    with pytest.raises(pimcord.ErroProjetoIA):
        pimcord.validar_projeto(dado)


def test_rejeita_segredo_literal():
    dado = projeto_valido()
    dado["arquivos"][0]["conteudo"] = "DISCORD_TOKEN='segredo'"
    with pytest.raises(pimcord.ErroProjetoIA):
        pimcord.validar_projeto(dado)


def test_projeto_local_gera_cogs_e_economia(tmp_path):
    from pimcord.projeto_ia import projeto_local_pimcord

    projeto = projeto_local_pimcord("crie um bot de economia completo")
    projeto.salvar(tmp_path)

    assert (tmp_path / "bot.py").is_file()
    assert (tmp_path / "cogs" / "economia.py").is_file()
    assert "comando_hibrido" in (tmp_path / "cogs" / "economia.py").read_text()
    assert (tmp_path / "README.md").is_file()


def test_bot_pronto_prompt_livre_com_diretorio_exige_checkpoint(tmp_path):
    with pytest.raises(pimcord.ErroGeradorIA, match="checkpoint neural"):
        pimcord.bot_pronto("crie um bot de economia completo", iniciar=False, diretorio=str(tmp_path))


def test_projeto_prompt_livre_sem_checkpoint_exige_modelo(tmp_path):
    with pytest.raises(pimcord.ErroGeradorIA, match="checkpoint neural"):
        pimcord.PimcordIA().gerar_projeto("crie um bot de economia")


def test_agente_construtor_sem_checkpoint_falha_explicitamente(tmp_path):
    from pimcord import AgenteConstrutorPimcord

    with pytest.raises(pimcord.ErroGeradorIA, match="checkpoint neural"):
        AgenteConstrutorPimcord().construir("crie um bot completo de economia e moderação", tmp_path)
