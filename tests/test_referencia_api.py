from __future__ import annotations

import hashlib
import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def carregar_gerador():
    origem = ROOT / "ferramentas" / "gerar_referencia.py"
    especificacao = importlib.util.spec_from_file_location("gerar_referencia_pimcord", origem)
    assert especificacao and especificacao.loader
    modulo = importlib.util.module_from_spec(especificacao)
    especificacao.loader.exec_module(modulo)
    return modulo


def test_referencia_api_e_deterministica_e_cobre_simbolos_publicos(tmp_path):
    gerador = carregar_gerador()
    primeira = tmp_path / "API-1.md"
    segunda = tmp_path / "API-2.md"
    gerador.gerar(primeira)
    gerador.gerar(segunda)
    assert hashlib.sha256(primeira.read_bytes()).digest() == hashlib.sha256(segunda.read_bytes()).digest()
    conteudo = primeira.read_text(encoding="utf-8")
    assert "# Referência da API Pimcord" in conteudo
    assert "ClienteHTTP.listar_threads_arquivadas" in conteudo
    assert "SessaoVoz.receber_audio" in conteudo
    assert "Não é necessário importar o pacote" in conteudo
