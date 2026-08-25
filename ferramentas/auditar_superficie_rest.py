from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLIENTE = ROOT / "pimcord" / "http" / "cliente.py"
OUT = ROOT / "docs" / "REST_AUDITORIA_LOCAL.txt"


def main() -> None:
    tree = ast.parse(CLIENTE.read_text(encoding="utf-8"))
    classe = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "ClienteHTTP")
    metodos = [node for node in classe.body if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and not node.name.startswith("_")]
    nomes = sorted({node.name for node in metodos})
    grupos: dict[str, list[str]] = {"canal": [], "servidor": [], "aplicacao": [], "interacao": [], "voz": [], "webhook": [], "automod": [], "evento": [], "oauth2": [], "media": [], "outros": []}
    for nome in nomes:
        baixo = nome.lower()
        if any(p in baixo for p in ("webhook",)):
            grupo = "webhook"
        elif any(p in baixo for p in ("automod", "automoderacao")):
            grupo = "automod"
        elif any(p in baixo for p in ("evento", "agendado", "inscrito")):
            grupo = "evento"
        elif any(p in baixo for p in ("voz", "audio", "voice")):
            grupo = "voz"
        elif any(p in baixo for p in ("oauth", "userinfo", "chaves_oauth")):
            grupo = "oauth2"
        elif any(p in baixo for p in ("emoji", "sticker", "som", "soundboard")):
            grupo = "media"
        elif any(p in baixo for p in ("comando", "aplicacao", "entitlement", "sku", "assinatura", "conexao_cargo", "metadados")):
            grupo = "aplicacao"
        elif any(p in baixo for p in ("canal", "mensagem", "thread", "reacao", "pin", "convite")):
            grupo = "canal"
        elif any(p in baixo for p in ("servidor", "membro", "cargo", "banimento", "auditoria", "integracao", "poda")):
            grupo = "servidor"
        else:
            grupo = "outros"
        grupos[grupo].append(nome)
    linhas = ["METODOS_DUPLICADOS", "nenhum", f"TOTAL_METODOS_PUBLICOS {len(nomes)}", "GRUPOS"]
    for grupo, itens in grupos.items():
        if itens:
            linhas.append(f"{grupo}: {len(itens)}")
            linhas.append("  " + ", ".join(itens))
    OUT.write_text("\n".join(linhas) + "\n", encoding="utf-8")
    print(f"metodos_unicos={len(nomes)} relatorio={OUT}")


if __name__ == "__main__":
    main()
