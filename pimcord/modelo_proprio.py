"""Modelo causal próprio e pequeno da PimcordIA.

Este módulo não baixa pesos nem depende de um modelo-base externo. Ele define uma
arquitetura Transformer causal inicializada do zero e um tokenizador byte-level
reprodutível. A qualidade depende do corpus e do treinamento realizados pelo
usuário; um modelo recém-inicializado não possui conhecimento útil ainda.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class ErroModeloProprio(RuntimeError):
    """Indica configuração, dependência ou checkpoint inválido."""


class TokenizadorBytes:
    """Tokenizador determinístico: bytes UTF-8 + tokens reservados."""

    PAD = 256
    EOS = 257
    INICIO = 258
    RESPOSTA = 259
    FIM = 260
    TAMANHO = 261

    def encode(self, texto: str, *, incluir_fim: bool = True) -> list[int]:
        if not isinstance(texto, str):
            raise TypeError("texto deve ser str")
        ids = list(texto.encode("utf-8"))
        if incluir_fim:
            ids.append(self.EOS)
        return ids

    def decode(self, ids: list[int]) -> str:
        bytes_saida = bytes(indice for indice in ids if 0 <= indice < 256)
        return bytes_saida.decode("utf-8", errors="replace")

    def salvar(self, caminho: str | Path) -> None:
        Path(caminho).write_text(json.dumps({"tipo": "bytes", "tamanho": self.TAMANHO}, indent=2) + "\n", encoding="utf-8")

    @classmethod
    def carregar(cls, caminho: str | Path) -> "TokenizadorBytes":
        dados = json.loads(Path(caminho).read_text(encoding="utf-8"))
        if dados.get("tipo") != "bytes" or int(dados.get("tamanho", 0)) != cls.TAMANHO:
            raise ErroModeloProprio("Tokenizador incompatível com o modelo próprio.")
        return cls()


def _torch() -> Any:
    try:
        import torch
        import torch.nn as nn
    except ImportError as erro:
        raise ErroModeloProprio("O modelo próprio exige PyTorch instalado no ambiente de treino ou execução.") from erro
    return torch, nn


def criar_modelo(*, camadas: int = 4, dimensao: int = 256, cabecas: int = 8, contexto: int = 2048) -> Any:
    """Cria o Transformer causal próprio sem carregar pesos externos."""
    torch, nn = _torch()
    if dimensao % cabecas:
        raise ValueError("dimensao deve ser divisível por cabecas")

    class PimcordTransformer(nn.Module):
        def __init__(self) -> None:
            super().__init__()
            self.contexto = contexto
            self.token_embedding = nn.Embedding(TokenizadorBytes.TAMANHO, dimensao)
            self.pos_embedding = nn.Embedding(contexto, dimensao)
            bloco = nn.TransformerEncoderLayer(
                d_model=dimensao,
                nhead=cabecas,
                dim_feedforward=dimensao * 4,
                dropout=0.1,
                activation="gelu",
                batch_first=True,
                norm_first=True,
            )
            self.transformer = nn.TransformerEncoder(bloco, num_layers=camadas)
            self.normalizacao = nn.LayerNorm(dimensao)
            self.saida = nn.Linear(dimensao, TokenizadorBytes.TAMANHO, bias=False)
            self.saida.weight = self.token_embedding.weight

        def forward(self, ids: Any) -> Any:
            tamanho = ids.shape[1]
            if tamanho > self.contexto:
                raise ValueError(f"Sequência excede o contexto de {self.contexto} tokens.")
            posicoes = torch.arange(tamanho, device=ids.device).unsqueeze(0)
            x = self.token_embedding(ids) + self.pos_embedding(posicoes)
            mascara = torch.triu(torch.ones(tamanho, tamanho, device=ids.device, dtype=torch.bool), diagonal=1)
            x = self.transformer(x, mask=mascara)
            return self.saida(self.normalizacao(x))

        @torch.no_grad()
        def gerar(self, ids: Any, *, novos_tokens: int = 256, temperatura: float = 0.2) -> Any:
            self.eval()
            for _ in range(novos_tokens):
                entrada = ids[:, -self.contexto:]
                logits = self(entrada)[:, -1, :]
                if temperatura <= 0:
                    proximo = logits.argmax(dim=-1, keepdim=True)
                else:
                    probabilidades = torch.softmax(logits / max(temperatura, 0.05), dim=-1)
                    proximo = torch.multinomial(probabilidades, num_samples=1)
                ids = torch.cat((ids, proximo), dim=1)
                if int(proximo.item()) == TokenizadorBytes.EOS:
                    break
            return ids

    return PimcordTransformer()


def salvar_checkpoint(modelo: Any, caminho: str | Path, *, configuracao: dict[str, Any]) -> None:
    torch, _ = _torch()
    destino = Path(caminho)
    destino.mkdir(parents=True, exist_ok=True)
    torch.save(modelo.state_dict(), destino / "modelo.pt")
    (destino / "config.json").write_text(json.dumps(configuracao, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    TokenizadorBytes().salvar(destino / "tokenizador.json")


def carregar_checkpoint(caminho: str | Path, *, dispositivo: str = "cpu") -> Any:
    torch, _ = _torch()
    origem = Path(caminho)
    if not (origem / "modelo.pt").is_file() or not (origem / "config.json").is_file():
        raise ErroModeloProprio(f"Checkpoint próprio incompleto: {origem}")
    configuracao = json.loads((origem / "config.json").read_text(encoding="utf-8"))
    modelo = criar_modelo(
        camadas=int(configuracao["camadas"]),
        dimensao=int(configuracao["dimensao"]),
        cabecas=int(configuracao["cabecas"]),
        contexto=int(configuracao["contexto"]),
    )
    modelo.load_state_dict(torch.load(origem / "modelo.pt", map_location=dispositivo, weights_only=True))
    modelo.to(dispositivo).eval()
    return modelo


def gerar_texto(modelo: Any, prompt: str, *, dispositivo: str = "cpu", novos_tokens: int = 512, temperatura: float = 0.2) -> str:
    torch, _ = _torch()
    tokenizador = TokenizadorBytes()
    ids = torch.tensor([tokenizador.encode(prompt, incluir_fim=False)], dtype=torch.long, device=dispositivo)
    resultado = modelo.gerar(ids, novos_tokens=novos_tokens, temperatura=temperatura)
    return tokenizador.decode(resultado[0].tolist()[len(ids[0]):]).strip()
