# Fontes para a matriz de paridade

## Discord Gateway Events

Fonte: https://docs.discord.com/developers/events/gateway-events

A documentação oficial define payloads com `op`, `d`, `s` e `t`, além dos eventos de envio Identify, Resume, Heartbeat, Request Guild Members, Update Voice State e Update Presence. Identify inclui token, propriedades, intents, shard, presença e large threshold. Resume usa token, session_id e seq. Heartbeat usa a última sequência recebida e deve seguir o heartbeat_interval recebido no Hello.

## discord.py API

Fonte: https://discordpy.readthedocs.io/en/latest/api.html

A API de Client inclui cache, intents, guilds, usuários, canais, emojis, stickers, tarefas de conexão, eventos, wait_for, presença, fetches REST, views e persistent views, além de opções de sharding, cache de membros, allowed mentions, timeout de heartbeat e rate limit.

## discord.py Commands

Fonte: https://discordpy.readthedocs.io/en/latest/ext/commands/api.html

A extensão de comandos inclui Bot, command, group, hybrid_command, checks globais, before_invoke, after_invoke, listeners, cogs/extensões, load/reload/unload, contexto, prefixos dinâmicos, aliases, help command, cooldowns, conversores e tratamento de erros.

## discord.py Interactions

Fonte: https://discordpy.readthedocs.io/en/latest/interactions/api.html

A camada de interações inclui Interaction, response única, followup webhook, respostas originais, edição e exclusão, componentes, comandos de aplicação, locale, permissions, expiração e traduções.
