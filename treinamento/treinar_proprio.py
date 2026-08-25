"""Treina a PimcordIA própria do zero usando apenas um dataset local.

O script não baixa modelo-base, tokenizer, pesos ou dados. É uma implementação
experimental para especialização em Python/Pimcord; qualidade depende do corpus,
do hardware e da quantidade de passos.
"""
from __future__ import annotations

import argparse
import json
import random
from pathlib import Path
from typing import Any

from pimcord.modelo_proprio import TokenizadorBytes, criar_modelo, salvar_checkpoint


def carregar_textos(caminho: Path, split: str = "treino") -> list[str]:
    textos: list[str] = []
    for linha in caminho.read_text(encoding="utf-8").splitlines():
        item = json.loads(linha)
        if item.get("split", "treino") != split:
            continue
        instrucao = str(item.get("instrucao", "")).strip()
        contexto = str(item.get("contexto", "")).strip()
        resposta = str(item.get("resposta") or item.get("codigo", "")).strip()
        if resposta:
            textos.append(
                "<|instrucao|>\n" + instrucao + "\n<|contexto|>\n" + contexto +
                "\n<|resposta|>\n" + resposta + "\n<|fim|>"
            )
    return textos


def _perda_media(modelo: Any, sequencias: list[list[int]], torch: Any, F: Any, dispositivo: str) -> float:
    if not sequencias:
        return 0.0
    modelo.eval()
    perdas: list[float] = []
    with torch.no_grad():
        for ids in sequencias:
            entrada = torch.tensor([ids[:-1]], dtype=torch.long, device=dispositivo)
            esperado = torch.tensor([ids[1:]], dtype=torch.long, device=dispositivo)
            logits = modelo(entrada)
            perdas.append(float(F.cross_entropy(logits.reshape(-1, TokenizadorBytes.TAMANHO), esperado.reshape(-1)).cpu()))
    modelo.train()
    return sum(perdas) / len(perdas)


def treinar(
    dataset: Path,
    saida: Path,
    *,
    passos: int = 1000,
    taxa_aprendizado: float = 3e-4,
    camadas: int = 4,
    dimensao: int = 256,
    cabecas: int = 8,
    contexto: int = 2048,
    dispositivo: str = "cpu",
    intervalo_checkpoint: int = 250,
    seed: int = 42,
) -> dict[str, Any]:
    try:
        import torch
        import torch.nn.functional as F
    except ImportError as erro:
        raise RuntimeError("O treinamento próprio exige PyTorch instalado; nenhum modelo externo é necessário.") from erro
    if passos <= 0:
        raise ValueError("passos deve ser maior que zero")
    if intervalo_checkpoint <= 0:
        raise ValueError("intervalo_checkpoint deve ser maior que zero")
    random.seed(seed)
    torch.manual_seed(seed)
    textos = carregar_textos(dataset)
    textos_validacao = carregar_textos(dataset, split="validacao")
    if not textos:
        raise ValueError("O split treino está vazio; prepare um dataset local antes de treinar.")
    tokenizador = TokenizadorBytes()
    sequencias = [tokenizador.encode(texto)[:contexto + 1] for texto in textos]
    sequencias = [ids for ids in sequencias if len(ids) >= 2]
    sequencias_validacao = [tokenizador.encode(texto)[:contexto + 1] for texto in textos_validacao]
    sequencias_validacao = [ids for ids in sequencias_validacao if len(ids) >= 2]
    if not sequencias:
        raise ValueError("Nenhum exemplo possui tokens suficientes para treinamento.")
    modelo = criar_modelo(camadas=camadas, dimensao=dimensao, cabecas=cabecas, contexto=contexto).to(dispositivo)
    otimizador = torch.optim.AdamW(modelo.parameters(), lr=taxa_aprendizado)
    modelo.train()
    perdas: list[float] = []
    historico_validacao: list[dict[str, float | int]] = []
    pasta_checkpoints = saida / "checkpoints"
    pasta_checkpoints.mkdir(parents=True, exist_ok=True)
    for passo in range(1, passos + 1):
        ids = sequencias[(passo - 1) % len(sequencias)]
        entrada = torch.tensor([ids[:-1]], dtype=torch.long, device=dispositivo)
        esperado = torch.tensor([ids[1:]], dtype=torch.long, device=dispositivo)
        logits = modelo(entrada)
        perda = F.cross_entropy(logits.reshape(-1, TokenizadorBytes.TAMANHO), esperado.reshape(-1))
        otimizador.zero_grad(set_to_none=True)
        perda.backward()
        torch.nn.utils.clip_grad_norm_(modelo.parameters(), 1.0)
        otimizador.step()
        perdas.append(float(perda.detach().cpu()))
        if passo == 1 or passo % intervalo_checkpoint == 0 or passo == passos:
            perda_validacao = _perda_media(modelo, sequencias_validacao, torch, F, dispositivo)
            historico_validacao.append({"passo": passo, "perda_treino": perdas[-1], "perda_validacao": perda_validacao})
            salvar_checkpoint(modelo, pasta_checkpoints / f"passo-{passo:06d}", configuracao={"passo": passo, "seed": seed})
    configuracao = {
        "familia": "pimcordia-propria-transformer",
        "camadas": camadas,
        "dimensao": dimensao,
        "cabecas": cabecas,
        "contexto": contexto,
        "vocabulario": TokenizadorBytes.TAMANHO,
        "exemplos_treino": len(sequencias),
        "passos": passos,
        "perda_final": perdas[-1],
        "perda_validacao_final": historico_validacao[-1]["perda_validacao"] if historico_validacao else 0.0,
        "historico_validacao": historico_validacao,
        "seed": seed,
        "intervalo_checkpoint": intervalo_checkpoint,
        "sem_modelo_base": True,
    }
    salvar_checkpoint(modelo, saida, configuracao=configuracao)
    (saida / "treinamento.json").write_text(json.dumps(configuracao, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return configuracao


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--saida", type=Path, required=True)
    parser.add_argument("--passos", type=int, default=1000)
    parser.add_argument("--taxa-aprendizado", type=float, default=3e-4)
    parser.add_argument("--camadas", type=int, default=4)
    parser.add_argument("--dimensao", type=int, default=256)
    parser.add_argument("--cabecas", type=int, default=8)
    parser.add_argument("--contexto", type=int, default=2048)
    parser.add_argument("--dispositivo", default="cpu")
    parser.add_argument("--intervalo-checkpoint", type=int, default=250)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    resultado = treinar(
        args.dataset, args.saida, passos=args.passos, taxa_aprendizado=args.taxa_aprendizado,
        camadas=args.camadas, dimensao=args.dimensao, cabecas=args.cabecas,
        contexto=args.contexto, dispositivo=args.dispositivo,
        intervalo_checkpoint=args.intervalo_checkpoint, seed=args.seed,
    )
    print(json.dumps(resultado, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
