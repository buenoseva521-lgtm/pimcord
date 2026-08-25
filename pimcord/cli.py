"""Linha de comando do Pimcord."""
from __future__ import annotations

import argparse
import pathlib
import sys

MODELO_BOT = '''import os\nimport pimcord\n\nintents = pimcord.Intents(mensagens=True, conteudo_mensagens=True)\nbot = pimcord.Bot(prefixo="!", intents=intents)\n\n@bot.comando("ola")\nasync def ola(ctx):\n    await ctx.responder("opa")\n\n@bot.evento("pronto")\nasync def pronto():\n    print("Pimcord conectado")\n\nbot.iniciar(os.environ["DISCORD_TOKEN"])\n'''


def novo(caminho: str) -> int:
    raiz = pathlib.Path(caminho)
    raiz.mkdir(parents=True, exist_ok=True)
    (raiz / "bot.py").write_text(MODELO_BOT, encoding="utf-8")
    (raiz / ".env.example").write_text("DISCORD_TOKEN=cole_seu_token_aqui\n", encoding="utf-8")
    (raiz / "README.md").write_text(f"# {raiz.name}\n\nProjeto criado pelo Pimcord CLI.\n", encoding="utf-8")
    print(f"Projeto criado em {raiz.resolve()}")
    return 0


def diagnostico() -> int:
    import platform
    import pimcord
    print(f"Pimcord {pimcord.__version__}")
    print(f"Python {platform.python_version()}")
    print(f"Sistema: {platform.system()} {platform.release()}")
    print("Importação: OK")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="pimcord", description="Ferramentas de desenvolvimento do Pimcord")
    subparsers = parser.add_subparsers(dest="comando")
    novo_parser = subparsers.add_parser("novo", help="Cria um projeto de bot")
    novo_parser.add_argument("caminho", nargs="?", default="meu-bot")
    subparsers.add_parser("diagnostico", help="Verifica Python e instalação")
    subparsers.add_parser("versao", help="Mostra a versão instalada")
    args = parser.parse_args(argv)
    if args.comando == "novo":
        return novo(args.caminho)
    if args.comando == "diagnostico":
        return diagnostico()
    if args.comando == "versao":
        from . import __version__
        print(__version__)
        return 0
    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
