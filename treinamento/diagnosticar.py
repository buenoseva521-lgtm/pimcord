"""Diagnóstico do ambiente para especialização da PimcordIA.

Não instala pacotes, não baixa pesos e não inicia treinamento. Serve para que
um usuário sem conhecimento técnico saiba qual etapa é segura executar.
"""
from __future__ import annotations

import importlib.util
import json
import platform
import shutil
from pathlib import Path


DEPENDENCIAS = ("torch", "transformers", "datasets", "peft", "accelerate")


def diagnosticar() -> dict[str, object]:
    disponiveis = {nome: bool(importlib.util.find_spec(nome)) for nome in DEPENDENCIAS}
    tem_gpu_nvidia = shutil.which("nvidia-smi") is not None
    treino_pronto = all(disponiveis.values()) and tem_gpu_nvidia
    return {
        "python": platform.python_version(),
        "sistema": platform.platform(),
        "dependencias": disponiveis,
        "gpu_nvidia_detectada": tem_gpu_nvidia,
        "treino_recomendado": treino_pronto,
        "inferência_móvel_recomendada": not treino_pronto,
        "mensagem": (
            "Ambiente apto para treino supervisionado."
            if treino_pronto
            else "Não iniciar treino aqui. Use um ambiente com GPU para adaptar o modelo; "
            "Pydroid/Termux ficam destinados à inferência de um modelo já quantizado."
        ),
    }


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--saida", type=Path, help="Arquivo JSON opcional para o diagnóstico.")
    args = parser.parse_args()
    resultado = diagnosticar()
    texto = json.dumps(resultado, ensure_ascii=False, indent=2) + "\n"
    if args.saida:
        args.saida.write_text(texto, encoding="utf-8")
    print(texto, end="")


if __name__ == "__main__":
    main()
