"""Benchmark offline de geração de projetos Pimcord.

O resultado mede contratos observáveis: compilação, segurança, presença de
capacidades e taxa de tarefas aprovadas. Ele não simula usuários nem converte
semelhança textual em qualidade de código.
"""
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable


@dataclass(frozen=True)
class Tarefa:
    nome: str
    pedido: str
    requisitos: tuple[str, ...]


TAREFAS_PUBLICAS = (
    Tarefa("nucleo", "Crie um bot Pimcord com ping e ajuda.", ("bot.py", "config.py")),
    Tarefa("moderacao", "Crie um bot de moderação com comando híbrido para limpar mensagens.", ("purge", "gerenciar_mensagens")),
    Tarefa("economia", "Crie um bot de economia com saldo persistente em SQLite.", ("EconomiaSQLite", "saldo")),
    Tarefa("tickets", "Crie um sistema de tickets com criação de canal privado.", ("criar_canal", "ticket")),
    Tarefa("seguranca", "Crie um bot com comandos híbridos e tratamento de erros seguro.", ("comando_hibrido", "try")),
)

# Retenção: não é usada para ajustar o gerador. Deve permanecer separada dos
# exemplos de treino e serve para impedir otimização apenas para os pedidos públicos.
TAREFAS_RETIDAS = (
    Tarefa("view_persistente", "Gere uma View persistente com botão de confirmação e tratamento de timeout.", ("View", "timeout", "botao")),
    Tarefa("permissoes", "Gere uma categoria privada com sobrescritas de permissão para autor e equipe.", ("SobrescritaPermissao", "definir_permissoes")),
    Tarefa("tarefas", "Gere uma tarefa periódica que consulta dados e encerra corretamente ao desligar.", ("asyncio", "cancelar")),
    Tarefa("rest_paginado", "Gere um comando que consulta histórico paginado sem ultrapassar o limite REST.", ("historico", "limite")),
)


def avaliar_projeto(projeto: Any, tarefa: Tarefa) -> dict[str, Any]:
    from pimcord.projeto_ia import _validar_python, validar_projeto
    try:
        plano = projeto.plano if hasattr(projeto, "plano") else projeto
        validar_projeto(plano)
        codigo = "\n".join(item["conteudo"] for item in plano["arquivos"] if item["caminho"].endswith(".py"))
        for item in plano["arquivos"]:
            if item["caminho"].endswith(".py"):
                _validar_python(item["caminho"], item["conteudo"])
                compile(item["conteudo"], item["caminho"], "exec")
        ausentes = [requisito for requisito in tarefa.requisitos if requisito not in (codigo + "\n" + "\n".join(item["caminho"] for item in plano["arquivos"]))]
        return {
            "tarefa": tarefa.nome,
            "aprovado": not ausentes,
            "arquivos": len(plano["arquivos"]),
            "ausentes": ausentes,
            "erro": None,
        }
    except Exception as erro:
        return {"tarefa": tarefa.nome, "aprovado": False, "arquivos": 0, "ausentes": [], "erro": str(erro)}


def executar(gerador: Callable[[str], Any], tarefas: tuple[Tarefa, ...] = TAREFAS_PUBLICAS, *, nome_conjunto: str = "publico", minimo_aprovacao: float = 0.8) -> dict[str, Any]:
    resultados = []
    for tarefa in tarefas:
        try:
            projeto = gerador(tarefa.pedido)
            resultados.append(avaliar_projeto(projeto, tarefa))
        except Exception as erro:
            resultados.append({"tarefa": tarefa.nome, "aprovado": False, "arquivos": 0, "ausentes": [], "erro": str(erro)})
    aprovados = sum(1 for item in resultados if item["aprovado"])
    taxa = aprovados / len(resultados) if resultados else 0.0
    return {
        "conjunto": nome_conjunto,
        "tarefas": len(resultados),
        "aprovadas": aprovados,
        "taxa_de_tarefas_aprovadas": taxa,
        "minimo_aprovacao": minimo_aprovacao,
        "gate_aprovado": bool(resultados) and taxa >= minimo_aprovacao,
        "resultados": resultados,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--modelo", type=Path, required=True, help="Diretório de checkpoint local já treinado.")
    parser.add_argument("--saida", type=Path, default=Path("benchmark.json"))
    parser.add_argument("--conjunto", choices=("publico", "retido", "todos"), default="todos")
    parser.add_argument("--minimo-aprovacao", type=float, default=0.8)
    args = parser.parse_args()
    if not 0.0 <= args.minimo_aprovacao <= 1.0:
        parser.error("--minimo-aprovacao deve estar entre 0 e 1.")
    from pimcord.modelo_neural import AgenteNeuralLocal, ModeloNeuralLocal
    agente = AgenteNeuralLocal(ModeloNeuralLocal(args.modelo), max_iteracoes=3)
    gerador = agente.construir
    conjuntos = []
    if args.conjunto in ("publico", "todos"):
        conjuntos.append(executar(gerador, TAREFAS_PUBLICAS, nome_conjunto="publico", minimo_aprovacao=args.minimo_aprovacao))
    if args.conjunto in ("retido", "todos"):
        conjuntos.append(executar(gerador, TAREFAS_RETIDAS, nome_conjunto="retido", minimo_aprovacao=args.minimo_aprovacao))
    resultado = {"modo": "checkpoint_local", "conjuntos": conjuntos}
    resultado["gate_global_aprovado"] = bool(conjuntos) and all(item["gate_aprovado"] for item in conjuntos)
    args.saida.write_text(json.dumps(resultado, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(resultado, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
