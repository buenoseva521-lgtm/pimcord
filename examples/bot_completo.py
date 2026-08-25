"""Exemplo integrado do Pimcord 0.6.9.

Este arquivo usa somente APIs presentes no núcleo atual e não executa
nenhuma conexão quando apenas é importado.
"""

from __future__ import annotations

import os

import pimcord


intents = pimcord.Intents.todos()
bot = pimcord.Bot(prefixo="!", intents=intents)


@bot.evento
async def pronto():
    print("Pimcord conectado e pronto.")


@bot.comando_hibrido("ping", descricao="Verifica a latência lógica do bot")
async def ping(ctx):
    await ctx.responder("Pong — o callback funciona por prefixo e slash.")


@bot.comando("apagar", aliases=["del", "deletar"])
async def apagar(ctx, quantidade: int = 1):
    """Apaga mensagens recentes do canal, respeitando o limite informado."""
    quantidade = max(1, min(quantidade, 100))
    removidas = await ctx.canal.purge(limite=quantidade)
    await ctx.responder(f"Apaguei {len(removidas)} mensagem(ns).")


@bot.comando_slash("privado", descricao="Envia resposta efêmera e um follow-up")
async def privado(interacao):
    await interacao.responder("Resposta visível somente para você.", ephemeral=True)
    await interacao.followup("Follow-up privado.", ephemeral=True)


if __name__ == "__main__":
    bot.iniciar(os.environ["DISCORD_TOKEN"])
