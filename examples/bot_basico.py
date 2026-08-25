import pimcord

bot = pimcord.Bot(prefixo="!")

@bot.comando("ola", aliases=["oi"])
async def ola(ctx, nome="mundo"):
    await ctx.responder(f"Olá, {nome}!")

@bot.evento("pronto")
async def pronto():
    print("Pimcord inicializado.")

if __name__ == "__main__":
    bot.iniciar()
