# FAQ

## O que é Pimcord?

Pimcord é uma biblioteca Python assíncrona para criação de bots Discord, com API pública em português e módulos de Gateway, REST, comandos, interações, modelos, tarefas, persistência, segurança, diagnóstico e voz.

## Como instalo?

A instalação normal é feita pelo PyPI:

```bash
python -m pip install pimcord
```

A versão publicada atual é 0.6.9. Clone e instalação editável são caminhos para contribuidores.

## Qual versão do Python é necessária?

O metadado atual do pacote declara Python 3.11 ou superior.

## Onde coloco o token?

Em uma variável de ambiente chamada `DISCORD_TOKEN`. Não o coloque no código, no GitHub, em prints, argumentos de shell, issues ou logs. Depois de um vazamento, revogue o token e gere outro.

## O que são intents?

Intents definem quais eventos o bot solicita ao Gateway. Use somente os intents necessários e habilite intents privilegiados no portal do Discord quando o recurso exigir essa configuração.

## Como crio um comando?

Use `@bot.comando("nome")` para comandos prefixados, `@bot.comando_slash("nome", descricao="...")` para slash ou `@bot.comando_hibrido(...)` quando o mesmo callback precisar dos dois caminhos. Consulte as assinaturas na [referência online](https://pimcorddocs-pvmazbtg.manus.space/api).

## Como verifico a versão instalada?

```bash
python -c "import pimcord; print(pimcord.__version__)"
```

## Pimcord é compatível com discord.py?

Pimcord não é uma substituição drop-in. Há conceitos comparáveis, mas nomes, assinaturas e comportamentos devem ser conferidos individualmente na [área de migração](https://pimcorddocs-pvmazbtg.manus.space/migrar).

## Onde encontro exemplos?

Os exemplos mantidos no repositório estão em [`examples/`](../examples/). A documentação online também oferece [receitas curtas](https://pimcorddocs-pvmazbtg.manus.space/receitas/criar-comando).

## Voz funciona em qualquer ambiente?

Voz e áudio estão classificados como experimentais. A implementação pode depender de libopus ou de outro backend compatível; trate `OpusIndisponivel` e valide o ambiente antes de liberar esse recurso em produção.
