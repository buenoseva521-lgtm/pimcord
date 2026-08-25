"""Treina a configuração experimental neural da PimcordIA.

Este script treina um modelo causal pequeno a partir de um dataset JSONL já
preparado. Ele registra configuração e métricas; não afirma que um checkpoint
pequeno possui conhecimento geral de Python sem benchmark posterior.
"""
from __future__ import annotations

import argparse
import json
import random
from pathlib import Path
from typing import Any

TOKENS_ESPECIAIS = ["<|pad|>", "<|unk|>", "<|instrucao|>", "<|contexto|>", "<|resposta|>", "<|fim|>"]


def carregar_dataset(caminho: Path, split: str | None = None) -> list[str]:
    textos: list[str] = []
    for linha in caminho.read_text(encoding="utf-8").splitlines():
        exemplo: dict[str, Any] = json.loads(linha)
        if split is not None and exemplo.get("split", "treino") != split:
            continue
        instrucao = str(exemplo.get("instrucao", "")).strip()
        contexto = str(exemplo.get("contexto", "")).strip()
        resposta = str(exemplo.get("resposta") or exemplo.get("codigo", "")).strip()
        if not resposta:
            continue
        textos.append(
            "<|instrucao|>\n" + instrucao + "\n"
            "<|contexto|>\n" + contexto + "\n"
            "<|resposta|>\n" + resposta + "\n<|fim|>"
        )
    return textos


def _configurar_seed(seed: int) -> None:
    random.seed(seed)
    try:
        import numpy as np
        np.random.seed(seed)
    except ImportError:
        pass
    try:
        import torch
        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)
    except ImportError:
        pass


def treinar(
    dataset: Path,
    saida: Path,
    passos: int,
    retomada: str | None = None,
    *,
    seed: int = 42,
    tamanho_bloco: int = 1024,
    camadas: int = 8,
    dimensao: int = 512,
    cabecas: int = 8,
    minimo_treino: int = 100,
    permitir_dataset_pequeno: bool = False,
) -> dict[str, Any]:
    if passos <= 0:
        raise ValueError("--passos deve ser maior que zero.")
    if dimensao % cabecas != 0:
        raise ValueError("--dimensao deve ser divisível por --cabecas.")
    try:
        from datasets import Dataset
        from tokenizers import ByteLevelBPETokenizer
        from transformers import (
            DataCollatorForLanguageModeling,
            GPT2Config,
            GPT2LMHeadModel,
            GPT2TokenizerFast,
            Trainer,
            TrainingArguments,
            set_seed,
        )
    except ImportError as erro:
        raise RuntimeError(
            "O treinamento exige datasets, tokenizers e transformers. "
            "Instale as dependências apenas no ambiente de treino, não no Pydroid."
        ) from erro
    _configurar_seed(seed)
    set_seed(seed)
    textos_treino = carregar_dataset(dataset, "treino")
    textos_validacao = carregar_dataset(dataset, "validacao")
    if not textos_treino:
        raise ValueError("O split de treino está vazio; prepare exemplos licenciados antes do treino.")
    if not permitir_dataset_pequeno and (len(textos_treino) < minimo_treino or len(textos_validacao) < max(10, minimo_treino // 10)):
        raise ValueError(
            f"Dataset insuficiente para um checkpoint de qualidade: treino={len(textos_treino)}, "
            f"validação={len(textos_validacao)}. São necessários pelo menos {minimo_treino} e "
            "10% para validação. Para smoke test, use --permitir-dataset-pequeno; ele não é um modelo especialista."
        )
    saida.mkdir(parents=True, exist_ok=True)
    corpus = saida / "corpus.txt"
    corpus.write_text("\n".join(textos_treino + textos_validacao), encoding="utf-8")
    tokenizer_dir = saida / "tokenizer"
    tokenizer_dir.mkdir(parents=True, exist_ok=True)
    tokenizer = ByteLevelBPETokenizer()
    tokenizer.train(
        files=[str(corpus)],
        vocab_size=32_000,
        min_frequency=2,
        special_tokens=TOKENS_ESPECIAIS,
    )
    tokenizer.save_model(str(tokenizer_dir))
    fast = GPT2TokenizerFast(
        vocab_file=str(tokenizer_dir / "vocab.json"),
        merges_file=str(tokenizer_dir / "merges.txt"),
        pad_token="<|pad|>",
        unk_token="<|unk|>",
        bos_token="<|instrucao|>",
        eos_token="<|fim|>",
    )
    config = GPT2Config(
        vocab_size=len(fast),
        n_positions=tamanho_bloco,
        n_ctx=tamanho_bloco,
        n_embd=dimensao,
        n_layer=camadas,
        n_head=cabecas,
        bos_token_id=fast.bos_token_id,
        eos_token_id=fast.eos_token_id,
        pad_token_id=fast.pad_token_id,
    )
    modelo = GPT2LMHeadModel(config)
    conjunto_treino = Dataset.from_dict({"texto": textos_treino})
    conjunto_validacao = Dataset.from_dict({"texto": textos_validacao}) if textos_validacao else None

    def tokenizar(lote: dict[str, list[str]]) -> dict[str, list[list[int]]]:
        return fast(lote["texto"], truncation=True, max_length=tamanho_bloco)

    tokenizado_treino = conjunto_treino.map(tokenizar, batched=True, remove_columns=["texto"])
    tokenizado_validacao = (
        conjunto_validacao.map(tokenizar, batched=True, remove_columns=["texto"])
        if conjunto_validacao is not None else None
    )
    argumentos = TrainingArguments(
        output_dir=str(saida / "checkpoints"),
        max_steps=passos,
        per_device_train_batch_size=1,
        per_device_eval_batch_size=1,
        gradient_accumulation_steps=16,
        logging_steps=max(1, min(10, passos // 20 or 1)),
        eval_strategy="steps" if tokenizado_validacao is not None else "no",
        eval_steps=max(1, min(100, passos // 10 or 1)) if tokenizado_validacao is not None else None,
        save_steps=max(1, min(100, passos // 10 or 1)),
        save_total_limit=3,
        learning_rate=3e-4,
        warmup_steps=max(10, passos // 20),
        weight_decay=0.01,
        report_to=[],
        seed=seed,
        data_seed=seed,
        fp16=False,
        remove_unused_columns=False,
    )
    colador = DataCollatorForLanguageModeling(tokenizer=fast, mlm=False)
    treinador = Trainer(
        model=modelo,
        args=argumentos,
        train_dataset=tokenizado_treino,
        eval_dataset=tokenizado_validacao,
        data_collator=colador,
        tokenizer=fast,
    )
    resultado = treinador.train(resume_from_checkpoint=retomada)
    modelo_dir = saida / "modelo"
    treinador.save_model(str(modelo_dir))
    fast.save_pretrained(str(modelo_dir))
    metricas = dict(getattr(resultado, "metrics", {}) or {})
    if tokenizado_validacao is not None:
        metricas.update({f"avaliacao_{k}": v for k, v in treinador.evaluate().items()})
    manifesto = {
        "seed": seed,
        "dataset": str(dataset),
        "passos": passos,
        "treino_exemplos": len(textos_treino),
        "validacao_exemplos": len(textos_validacao),
        "tamanho_bloco": tamanho_bloco,
        "camadas": camadas,
        "dimensao": dimensao,
        "cabecas": cabecas,
        "metricas": metricas,
        "status": "smoke_checkpoint" if permitir_dataset_pequeno else "experimental_checkpoint",
    }
    (saida / "treino.json").write_text(
        json.dumps(manifesto, ensure_ascii=False, indent=2, default=str) + "\n",
        encoding="utf-8",
    )
    print(f"[PimcordIA] checkpoint experimental salvo em {modelo_dir}")
    return manifesto


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--saida", type=Path, required=True)
    parser.add_argument("--passos", type=int, default=1000)
    parser.add_argument("--retomar", default=None)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--tamanho-bloco", type=int, default=1024)
    parser.add_argument("--camadas", type=int, default=8)
    parser.add_argument("--dimensao", type=int, default=512)
    parser.add_argument("--cabecas", type=int, default=8)
    parser.add_argument("--minimo-exemplos", type=int, default=100)
    parser.add_argument("--permitir-dataset-pequeno", action="store_true")
    args = parser.parse_args()
    treinar(
        args.dataset, args.saida, args.passos, args.retomar,
        seed=args.seed, tamanho_bloco=args.tamanho_bloco,
        camadas=args.camadas, dimensao=args.dimensao, cabecas=args.cabecas,
        minimo_treino=args.minimo_exemplos,
        permitir_dataset_pequeno=args.permitir_dataset_pequeno,
    )


if __name__ == "__main__":
    main()
