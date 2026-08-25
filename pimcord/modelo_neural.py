"""Inferência opcional da PimcordIA Neural com modelos armazenados localmente.

O módulo é deliberadamente opt-in: importar Pimcord não baixa pesos, não acessa
rede e não substitui o gerador determinístico até que o usuário forneça um
checkpoint local. Todo projeto retornado passa pelo contrato de ``projeto_ia``.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable


@dataclass(frozen=True, slots=True)
class ConfiguracaoModelo:
    """Contrato de um modelo local especializado, sem download implícito."""

    familia: str = "qwen2.5-coder"
    contexto: int = 32768
    somente_local: bool = True
    nome_recomendado: str = "Qwen2.5-Coder-7B-Instruct"


CONFIGURACAO_RECOMENDADA = ConfiguracaoModelo()


class ErroModeloNeural(RuntimeError):
    """Checkpoint ausente, dependência não instalada ou saída inválida."""


class ModeloNeuralLocal:
    """Carrega um checkpoint causal local exclusivamente em modo offline."""

    def __init__(self, diretorio: str | Path, *, base: str | Path | None = None, dispositivo: str = "auto", configuracao: ConfiguracaoModelo = CONFIGURACAO_RECOMENDADA) -> None:
        self.diretorio = Path(diretorio).expanduser().resolve()
        self.configuracao = configuracao
        if not self.diretorio.is_dir():
            raise ErroModeloNeural(f"Checkpoint não encontrado: {self.diretorio}")
        self._proprio = (self.diretorio / "modelo.pt").is_file() and (self.diretorio / "tokenizador.json").is_file()
        if self._proprio:
            try:
                from .modelo_proprio import TokenizadorBytes, carregar_checkpoint
                self.tokenizador = TokenizadorBytes.carregar(self.diretorio / "tokenizador.json")
                self.modelo = carregar_checkpoint(self.diretorio, dispositivo="cpu" if dispositivo == "auto" else dispositivo)
            except Exception as erro:
                raise ErroModeloNeural(f"Falha ao carregar o checkpoint próprio da PimcordIA: {erro}") from erro
            self.dispositivo = "cpu" if dispositivo == "auto" else dispositivo
            return
        e_adaptador = (self.diretorio / "adapter_config.json").is_file()
        base_caminho = Path(base).expanduser().resolve() if base else None
        if e_adaptador and base_caminho is None:
            raise ErroModeloNeural(
                "Este diretório é um adaptador LoRA. Informe o modelo-base local com "
                "PIMCORDIA_MODELO_BASE ou ModeloNeuralLocal(..., base=...)."
            )
        origem_modelo = base_caminho or self.diretorio
        if not (origem_modelo / "config.json").is_file():
            raise ErroModeloNeural(f"Modelo-base sem config.json: {origem_modelo}")
        try:
            from transformers import AutoModelForCausalLM, AutoTokenizer
        except ImportError as erro:
            raise ErroModeloNeural(
                "Inferência neural exige transformers no ambiente de execução. "
                "No Pydroid, instale uma versão compatível ou use o fallback local."
            ) from erro
        kwargs: dict[str, Any] = {"local_files_only": self.configuracao.somente_local}
        tokenizer_origem = self.diretorio if (self.diretorio / "tokenizer_config.json").is_file() else origem_modelo
        self.tokenizador = AutoTokenizer.from_pretrained(str(tokenizer_origem), **kwargs)
        self.modelo = AutoModelForCausalLM.from_pretrained(str(origem_modelo), **kwargs)
        if e_adaptador:
            try:
                from peft import PeftModel
                self.modelo = PeftModel.from_pretrained(self.modelo, str(self.diretorio), **kwargs)
            except ImportError as erro:
                raise ErroModeloNeural("Este checkpoint LoRA exige a dependência peft.") from erro
            except Exception as erro:
                raise ErroModeloNeural(f"Falha ao carregar o adaptador LoRA: {erro}") from erro
        if dispositivo == "auto":
            dispositivo = "cuda" if self._tem_cuda() else "cpu"
        self.dispositivo = dispositivo
        self.modelo.to(dispositivo)
        self.modelo.eval()

    @staticmethod
    def _tem_cuda() -> bool:
        try:
            import torch
            return bool(torch.cuda.is_available())
        except ImportError:
            return False

    def gerar(self, prompt: str, *, max_novos_tokens: int = 2048, temperatura: float = 0.2) -> str:
        if not isinstance(prompt, str) or not prompt.strip():
            raise ErroModeloNeural("O prompt não pode ser vazio.")
        if self._proprio:
            try:
                from .modelo_proprio import gerar_texto
                return gerar_texto(self.modelo, prompt, dispositivo=self.dispositivo, novos_tokens=max_novos_tokens, temperatura=temperatura)
            except Exception as erro:
                raise ErroModeloNeural(f"Falha na inferência do modelo próprio: {erro}") from erro
        try:
            import torch
            if getattr(self.tokenizador, "chat_template", None):
                mensagens = [{"role": "system", "content": "Você é a PimcordIA, especialista em Python e na API Pimcord. Responda somente ao pedido técnico."}, {"role": "user", "content": prompt}]
                entradas = self.tokenizador.apply_chat_template(mensagens, add_generation_prompt=True, tokenize=True, return_tensors="pt")
                if hasattr(entradas, "items"):
                    entradas = {chave: valor.to(self.dispositivo) for chave, valor in entradas.items()}
                else:
                    entradas = {"input_ids": entradas.to(self.dispositivo)}
            else:
                entradas = self.tokenizador(prompt, return_tensors="pt")
                entradas = {chave: valor.to(self.dispositivo) for chave, valor in entradas.items()}
            with torch.no_grad():
                saida = self.modelo.generate(
                    **entradas,
                    max_new_tokens=max_novos_tokens,
                    do_sample=temperatura > 0,
                    temperature=max(0.05, temperatura) if temperatura > 0 else None,
                    pad_token_id=self.tokenizador.pad_token_id or self.tokenizador.eos_token_id,
                    eos_token_id=self.tokenizador.eos_token_id,
                )
            inicio = entradas["input_ids"].shape[-1]
            return self.tokenizador.decode(saida[0][inicio:], skip_special_tokens=True).strip()
        except Exception as erro:
            raise ErroModeloNeural(f"Falha na inferência local: {erro}") from erro

    def gerar_json(self, prompt: str, **opcoes: Any) -> dict[str, Any]:
        texto = self.gerar(prompt, **opcoes)
        candidato = texto.strip()
        if "```" in candidato:
            partes = [parte.strip() for parte in candidato.split("```") if parte.strip()]
            candidato = next((parte[4:].lstrip() if parte.startswith("json") else parte for parte in partes if "{" in parte), candidato)
        inicio, fim = candidato.find("{"), candidato.rfind("}")
        if inicio < 0 or fim <= inicio:
            raise ErroModeloNeural("O checkpoint não retornou um objeto JSON.")
        try:
            valor = json.loads(candidato[inicio:fim + 1])
        except json.JSONDecodeError as erro:
            raise ErroModeloNeural("A saída neural contém JSON inválido.") from erro
        if not isinstance(valor, dict):
            raise ErroModeloNeural("A saída neural precisa ser um objeto JSON.")
        return valor


class AgenteNeuralLocal:
    """Gera, valida e revisa projetos com limite explícito de iterações."""

    def __init__(self, modelo: ModeloNeuralLocal, *, max_iteracoes: int = 3, progresso: Callable[[str], Any] | None = None) -> None:
        if max_iteracoes < 1 or max_iteracoes > 8:
            raise ValueError("max_iteracoes deve estar entre 1 e 8.")
        self.modelo = modelo
        self.max_iteracoes = max_iteracoes
        self.progresso = progresso

    def _informar(self, texto: str) -> None:
        if self.progresso is not None:
            self.progresso(f"[PimcordIA Neural] {texto}")

    def construir(self, pedido: str) -> Any:
        if not isinstance(pedido, str) or not pedido.strip():
            raise ErroModeloNeural("O pedido não pode ser vazio.")
        from .ia import contexto_python_pimcord, resumo_api_pimcord, _validar_pedido_dados_sensiveis
        from .projeto_ia import ProjetoGerado, validar_projeto, _validar_acoes_reais
        _validar_pedido_dados_sensiveis(pedido)
        memoria = contexto_python_pimcord(pedido, limite=16)
        base = (
            "Você é um gerador local de projetos Pimcord. Retorne exclusivamente JSON com "
            "nome, resumo e arquivos; cada arquivo tem caminho e conteudo. Implemente livremente "
            "o comportamento solicitado e use a API instalada quando apropriado. Não inclua valores "
            "reais de CPF, documentos, senhas, cartões, tokens ou credenciais. O projeto não será "
            "executado automaticamente.\nAPI instalada:\n" + resumo_api_pimcord() + "\nMemória local relevante:\n" + memoria + "\nPedido:\n" + pedido[:20000]
        )
        feedback = ""
        ultimo_erro = ""
        for tentativa in range(1, self.max_iteracoes + 1):
            self._informar(f"tentativa {tentativa}/{self.max_iteracoes}")
            prompt = base + ("\nErros da tentativa anterior; corrija somente o necessário:\n" + feedback if feedback else "")
            try:
                plano = self.modelo.gerar_json(prompt, max_novos_tokens=4096)
                plano = validar_projeto(plano)
                _validar_acoes_reais(plano, pedido)
                return ProjetoGerado(plano)
            except Exception as erro:
                ultimo_erro = str(erro)
                feedback = ultimo_erro[:4000]
        raise ErroModeloNeural(f"O agente não produziu um projeto válido após {self.max_iteracoes} tentativas: {ultimo_erro}")
