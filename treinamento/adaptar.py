"""Especializa um modelo causal local com LoRA para a API Pimcord.

O script nunca baixa pesos: ``--base`` precisa ser um diretório local já obtido
pelo usuário e a execução exige dependências de treinamento instaladas fora do
pacote runtime. Por padrão, datasets pequenos são recusados.
"""
from __future__ import annotations

import argparse
import json
import random
from pathlib import Path
from typing import Any


MARCADOR_INICIO = "<|instrucao|>"
MARCADOR_CONTEXTO = "<|contexto|>"
MARCADOR_RESPOSTA = "<|resposta|>"
MARCADOR_FIM = "<|fim|>"


def carregar(caminho: Path, split: str) -> list[str]:
    exemplos: list[str] = []
    for linha in caminho.read_text(encoding="utf-8").splitlines():
        item = json.loads(linha)
        if item.get("split", "treino") != split:
            continue
        instrucao = str(item.get("instrucao", "")).strip()
        contexto = str(item.get("contexto", "")).strip()
        resposta = str(item.get("resposta") or item.get("codigo", "")).strip()
        if resposta:
            exemplos.append(
                f"{MARCADOR_INICIO}\n{instrucao}\n"
                f"{MARCADOR_CONTEXTO}\n{contexto}\n"
                f"{MARCADOR_RESPOSTA}\n{resposta}\n{MARCADOR_FIM}"
            )
    return exemplos


def _seed(seed: int) -> None:
    random.seed(seed)
    try:
        import numpy as np
        np.random.seed(seed)
    except ImportError:
        pass
    try:
        import torch
        torch.manual_seed(seed)
    except ImportError:
        pass


def adaptar(
    base: Path,
    dataset: Path,
    saida: Path,
    *,
    passos: int = 1000,
    seed: int = 42,
    rank: int = 16,
    alfa: int = 32,
    dropout: float = 0.05,
    minimo_treino: int = 100,
    permitir_dataset_pequeno: bool = False,
) -> dict[str, Any]:
    if not base.is_dir() or not (base / "config.json").is_file():
        raise ValueError("--base precisa ser um diretório local com config.json.")
    if passos <= 0 or rank <= 0 or alfa <= 0:
        raise ValueError("passos, rank e alfa devem ser maiores que zero.")
    treino = carregar(dataset, "treino")
    validacao = carregar(dataset, "validacao")
    minimo_validacao = max(10, minimo_treino // 10)
    if not treino:
        raise ValueError("O split treino está vazio.")
    if not permitir_dataset_pequeno and (len(treino) < minimo_treino or len(validacao) < minimo_validacao):
        raise ValueError(
            f"Corpus insuficiente para especialização: treino={len(treino)}, validação={len(validacao)}. "
            "Use --permitir-dataset-pequeno somente para smoke test."
        )
    try:
        from datasets import Dataset
        from peft import LoraConfig, TaskType, get_peft_model
        from transformers import AutoModelForCausalLM, AutoTokenizer, DataCollatorForLanguageModeling, Trainer, TrainingArguments, set_seed
    except ImportError as erro:
        raise RuntimeError("A adaptação exige datasets, peft, torch e transformers no ambiente de treino.") from erro
    _seed(seed)
    set_seed(seed)
    tokenizer = AutoTokenizer.from_pretrained(str(base), local_files_only=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    modelo = AutoModelForCausalLM.from_pretrained(str(base), local_files_only=True)
    config_lora = LoraConfig(
        r=rank,
        lora_alpha=alfa,
        lora_dropout=dropout,
        bias="none",
        task_type=TaskType.CAUSAL_LM,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
    )
    modelo = get_peft_model(modelo, config_lora)
    conjunto_treino = Dataset.from_dict({"texto": treino})
    conjunto_validacao = Dataset.from_dict({"texto": validacao}) if validacao else None

    def tokenizar(lote: dict[str, list[str]]) -> dict[str, list[list[int]]]:
        return tokenizer(lote["texto"], truncation=True, max_length=32768)

    tokenizado_treino = conjunto_treino.map(tokenizar, batched=True, remove_columns=["texto"])
    tokenizado_validacao = conjunto_validacao.map(tokenizar, batched=True, remove_columns=["texto"]) if conjunto_validacao else None
    saida.mkdir(parents=True, exist_ok=True)
    argumentos = TrainingArguments(
        output_dir=str(saida / "checkpoints"),
        max_steps=passos,
        per_device_train_batch_size=1,
        per_device_eval_batch_size=1,
        gradient_accumulation_steps=8,
        logging_steps=max(1, min(10, passos // 20 or 1)),
        eval_strategy="steps" if tokenizado_validacao else "no",
        eval_steps=max(1, passos // 10) if tokenizado_validacao else None,
        save_steps=max(1, passos // 10),
        save_total_limit=2,
        learning_rate=2e-4,
        report_to=[],
        seed=seed,
        data_seed=seed,
        remove_unused_columns=False,
    )
    treinador = Trainer(
        model=modelo,
        args=argumentos,
        train_dataset=tokenizado_treino,
        eval_dataset=tokenizado_validacao,
        data_collator=DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False),
        tokenizer=tokenizer,
    )
    resultado = treinador.train()
    modelo_dir = saida / "adaptador"
    treinador.save_model(str(modelo_dir))
    tokenizer.save_pretrained(str(modelo_dir))
    manifesto = {
        "base": str(base),
        "dataset": str(dataset),
        "treino_exemplos": len(treino),
        "validacao_exemplos": len(validacao),
        "passos": passos,
        "seed": seed,
        "lora": {"rank": rank, "alfa": alfa, "dropout": dropout},
        "metricas": dict(getattr(resultado, "metrics", {}) or {}),
        "status": "smoke_adaptador" if permitir_dataset_pequeno else "adaptador_experimental",
        "uso": "Carregar o modelo-base e este adaptador localmente; não é um modelo geral aprovado.",
    }
    (saida / "adaptacao.json").write_text(json.dumps(manifesto, ensure_ascii=False, indent=2, default=str) + "\n", encoding="utf-8")
    return manifesto


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", type=Path, required=True)
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--saida", type=Path, required=True)
    parser.add_argument("--passos", type=int, default=1000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--rank", type=int, default=16)
    parser.add_argument("--alfa", type=int, default=32)
    parser.add_argument("--dropout", type=float, default=0.05)
    parser.add_argument("--minimo-exemplos", type=int, default=100)
    parser.add_argument("--permitir-dataset-pequeno", action="store_true")
    args = parser.parse_args()
    manifesto = adaptar(args.base, args.dataset, args.saida, passos=args.passos, seed=args.seed, rank=args.rank, alfa=args.alfa, dropout=args.dropout, minimo_treino=args.minimo_exemplos, permitir_dataset_pequeno=args.permitir_dataset_pequeno)
    print(json.dumps(manifesto, ensure_ascii=False, indent=2, default=str))


if __name__ == "__main__":
    main()
