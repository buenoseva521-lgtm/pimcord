# Guia completo de configuração do Pimcord

Este guia explica como qualquer desenvolvedor pode criar uma aplicação Discord, adicionar um bot, configurar intents, convidá-lo para um servidor e executar um projeto Pimcord.

## 1. Criar a aplicação

Acesse o [Discord Developer Portal](https://discord.com/developers/applications), entre com sua conta Discord e escolha **New Application**. Informe o nome da aplicação e confirme.

Na página **General Information**, copie o **Application ID** somente se precisar gerar links ou registrar comandos. Ele não é o token do bot.

## 2. Criar e proteger o bot

Abra a seção **Bot** e adicione um bot à aplicação, caso ainda não exista. Na área de token, use **Reset Token** para gerar um token novo e copie-o imediatamente para um gerenciador de segredos ou variável de ambiente.

O token concede autenticação à API e deve ser tratado como uma senha. Nunca o publique no GitHub, não coloque o valor no `bot.py`, não o envie para outra pessoa e não o registre em logs. Se ele for exposto, volte à página **Bot**, faça reset e substitua o segredo em todos os ambientes.

## 3. Ativar intents

Na página do bot, em **Privileged Gateway Intents**, ative **Message Content Intent** se o bot precisar ler mensagens de texto para comandos prefixados. O Pimcord usa isso quando você configura:

```python
intents = pimcord.Intents(
    servidores=True,
    mensagens=True,
    conteudo_mensagens=True,
)
```

O intent precisa ser ativado no portal e solicitado pelo código. Ativar apenas um dos dois não é suficiente.

## 4. Gerar o convite

Na seção de instalação ou OAuth2, use os escopos `bot` e `applications.commands`. Depois selecione somente as permissões necessárias, como **View Channels**, **Send Messages**, **Read Message History** e **Embed Links**.

Não conceda **Administrator** sem necessidade. O dono de um servidor precisa autorizar a instalação. O bot não pode ser adicionado como uma conta comum; a instalação é feita pelo fluxo OAuth2 oficial.

## 5. Instalar o Pimcord

Para uma cópia local do projeto:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install .
```

Quando uma versão estiver publicada no PyPI:

```bash
python -m pip install pimcord
```

O nome de distribuição do PyPI e o nome usado em `import pimcord` são conceitos relacionados, mas podem ser diferentes. O proprietário do projeto precisa verificar a disponibilidade do nome antes de publicar.

## 6. Criar o primeiro bot

```python
import os
import pimcord

intents = pimcord.Intents(
    servidores=True,
    mensagens=True,
    conteudo_mensagens=True,
)

bot = pimcord.Bot(prefixo="!", intents=intents)

@bot.comando("ola", aliases=["oi"])
async def ola(ctx):
    await ctx.responder("opa")

@bot.evento("pronto")
async def pronto():
    print("Bot conectado ao Discord")

bot.iniciar(os.environ["DISCORD_TOKEN"])
```

Defina o token no ambiente:

```bash
export DISCORD_TOKEN="token-do-seu-bot"
python bot.py
```

Em Windows PowerShell:

```powershell
$env:DISCORD_TOKEN = "token-do-seu-bot"
python bot.py
```

## Estado de maturidade

A versão atual do projeto contém um caminho real de Gateway, heartbeat, Identify, evento de mensagem e resposta REST. Para equivalência completa com uma biblioteca madura, ainda devem ser implementados e estabilizados slash commands, componentes, modelos completos, sincronização, rate limits abrangentes, resume, voz, webhooks, extensões e uma suíte de testes de integração.

## Referências oficiais

- [Discord: Building your first Discord Bot](https://docs.discord.com/developers/quick-start/getting-started)
- [Discord: Gateway](https://docs.discord.com/developers/events/gateway)
- [Discord: Gateway Events](https://docs.discord.com/developers/events/gateway-events)
- [Discord: OAuth2](https://docs.discord.com/developers/topics/oauth2)
- [Python Packaging User Guide](https://packaging.python.org/tutorials/packaging-projects/)
