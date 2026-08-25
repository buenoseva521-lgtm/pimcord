# Fontes externas da auditoria comparativa

## Referências oficiais

1. **discord.py — API Reference**: https://discordpy.readthedocs.io/en/latest/api.html

   A referência lista, entre outros, `Client`, cache de mensagens, guilds, usuários, canais, emojis, stickers, soundboard, voice clients, Views persistentes, eventos, `wait_for`, presença, criação/edição/remoção de recursos e APIs de busca/fetch. Também documenta opções de produção como `application_id`, `member_cache_flags`, `allowed_mentions`, `heartbeat_timeout`, `max_ratelimit_timeout`, tracing HTTP, proxy e controles de cache.

2. **discord.py — Interactions API Reference**: https://discordpy.readthedocs.io/en/latest/interactions/api.html

   A referência cobre `Interaction`, resposta inicial, follow-up webhook, resposta original, edição/exclusão da resposta original, Views, LayoutView, Items, DynamicItem, Buttons, Selects, Modals, TextInput, CommandTree, grupos, checks, cooldowns, transformers, choices, tradução e componentes adicionais.

3. **discord.py — Ext commands API Reference**: https://discordpy.readthedocs.io/en/latest/ext/commands/api.html

   A extensão de comandos documenta Bot, AutoShardedBot, comandos, Groups, HybridCommand, HybridGroup, Cogs, GroupCog, help commands, paginadores, checks, converters, flag converters, hooks `before_invoke`/`after_invoke`, listeners, load/reload/unload de extensões, `wait_for`, prefixos dinâmicos e gerenciamento de comandos.

4. **Discord Developer Documentation — API Reference**: https://docs.discord.com/developers/reference

   A referência oficial da plataforma documenta API versionada, autenticação, erros estruturados, IDs snowflake, paginação, REST e requisitos do protocolo. A versão de API indicada como disponível/default na página consultada é v10.

## Uso das fontes

Essas fontes foram usadas apenas para comparar a superfície funcional e os contratos documentados. Nenhum código foi copiado. O relatório do Pimcord separa recursos implementados, parciais, placeholders e ausentes.
