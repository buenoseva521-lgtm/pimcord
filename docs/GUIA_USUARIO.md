# Guia de usuário do Pimcord

Este guia resume o caminho recomendado para sair da instalação ao primeiro bot. A versão publicada atual é **0.6.9** e a referência navegável está em [pimcorddocs-pvmazbtg.manus.space](https://pimcorddocs-pvmazbtg.manus.space/).

## Instalar

O requisito de Python declarado pelo pacote é 3.11 ou superior. Em um ambiente virtual:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install pimcord
```

Confirme a instalação com:

```bash
python -c "import pimcord; print(pimcord.__version__)"
```

## Criar um primeiro bot

```python
import os
import pimcord

bot = pimcord.Bot(prefixo="!")

@bot.comando("ola")
async def ola(ctx):
    await ctx.responder("Olá!")

@bot.evento("pronto")
async def pronto():
    print("Bot conectado")

bot.iniciar(os.environ["DISCORD_TOKEN"])
```

Antes de executar, defina `DISCORD_TOKEN` no ambiente. O token nunca deve aparecer no código, em prints, no GitHub, em issues ou em logs. Se ele for exposto, revogue-o no portal do Discord.

## Escolher o próximo passo

Depois do primeiro bot, consulte os [guias de comandos](https://pimcorddocs-pvmazbtg.manus.space/guias/comandos), [eventos](https://pimcorddocs-pvmazbtg.manus.space/guias/eventos), [mensagens e embeds](https://pimcorddocs-pvmazbtg.manus.space/guias/mensagens), [interações](https://pimcorddocs-pvmazbtg.manus.space/guias/interacoes) e [segurança](https://pimcorddocs-pvmazbtg.manus.space/guias/seguranca). Para uma tarefa específica, use as [receitas](https://pimcorddocs-pvmazbtg.manus.space/receitas/criar-comando). Para uma classe ou método, abra a [API completa](https://pimcorddocs-pvmazbtg.manus.space/api).

## Status dos recursos

Recursos marcados como estáveis têm contrato público confirmado no pacote e nos testes locais. Voz e áudio são experimentais porque podem depender de bibliotecas nativas, como libopus. Roadmaps e relatórios de versões futuras são planejamento ou histórico; não transformam uma funcionalidade em API publicada.
