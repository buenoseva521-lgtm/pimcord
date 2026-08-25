"""Exemplos de interações do Pimcord 0.6.9."""

import pimcord


class Confirmacao(pimcord.View):
    def __init__(self):
        super().__init__()
        self.adicionar_item(
            pimcord.Botao("confirmar", texto="Confirmar", estilo="sucesso")
        )


bot = pimcord.Bot(prefixo="!")


@bot.comando("painel")
async def painel(ctx):
    view = Confirmacao()
    await ctx.responder("Escolha uma ação:", view=view)


@bot.comando_slash("processar", descricao="Demonstra adiamento e follow-up")
async def processar(interacao):
    await interacao.adiar(ephemeral=True)
    # Faça o trabalho assíncrono da aplicação aqui.
    await interacao.editar_resposta("Processamento concluído.")
    await interacao.followup("O resultado foi salvo.", ephemeral=True)
