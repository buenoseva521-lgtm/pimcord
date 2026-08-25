import os
import pimcord

config = pimcord.Configuracao.ambiente()
config.application_id = os.environ.get("DISCORD_APPLICATION_ID")
bot = pimcord.Bot(configuracao=config)

@bot.slash("ola", descricao="Responde uma saudação")
async def ola(interacao):
    await interacao.responder("opa")

@bot.evento("pronto")
async def pronto():
    # Slash commands precisam ser sincronizados após o bot iniciar.
    await bot.sincronizar_comandos()
    print("Bot online e comandos sincronizados.")

bot.iniciar()
