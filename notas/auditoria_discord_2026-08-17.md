# Auditoria oficial do Discord — 2026-08-17

Fontes consultadas:
- https://docs.discord.com/developers/reference
- https://docs.discord.com/developers/change-log

Achados relevantes:

- A referência oficial informa que a API atual disponível é a v10; v9 também está disponível, v8/v7 estão depreciadas e versões anteriores foram descontinuadas.
- IDs Discord são snowflakes serializados como strings; a paginação usa IDs e parâmetros before/after/around em várias rotas.
- Erros HTTP podem conter `code`, `message` e uma árvore `errors` detalhada, inclusive erros de formulário; o cliente deve preservar status, código, rota, método e detalhes.
- O changelog de 12/08/2026 anunciou obfuscação de canais para usuários e bots: em HTTP, `GET /guilds/{guild.id}/channels` omitirá canais sem VIEW_CHANNEL a partir de 16/11/2026; no Gateway haverá campos obfuscados, flag `CHANNEL_OBFUSCATED` e overwrite negando VIEW_CHANNEL. O Pimcord deve documentar/representar essa possibilidade em modelos e cache.
- O changelog de 05/08/2026 tornou `channel.application_id` anulável; modelos não devem exigir snowflake sempre que esse campo estiver presente.
- O changelog de 05/08/2026 adicionou `file_types` a File Upload components e opções ATTACHMENT; isso é uma lacuna de interações/comandos, não apenas REST.
- O changelog de 16/07/2026 registra `app_permissions` em canais resolvidos de interações.

Uso no Pimcord:
- Manter o bloqueador de paridade REST aberto.
- Priorizar modelos/caches tolerantes a canais obfuscados e `application_id=None`.
- Auditar componentes de upload e modelos de interação para `file_types` e `app_permissions`.
- Não tratar mudanças futuras do changelog como implementadas sem contrato offline específico.

Observação: a referência e o changelog foram extraídos de docs.discord.com em 2026-08-17; o changelog foi retornado parcialmente, então apenas os itens visíveis acima foram registrados.

Tabela de rotas/documentação já cobertas localmente no Pimcord: onboarding, Soundboard, role-connections metadata, Widget, prune, vanity URL, Voice States/Resource, SKUs, assinaturas, stickers multipart, paginação segura e webhooks por token. A matriz integral ainda não foi declarada completa.

Status de validação local no momento do registro: 106 testes aprovados; wheel pimcord-0.7.0-py3-none-any.whl gerada; E2EE MLS/DAVE real ainda ausente.

Referências:
[1]: https://docs.discord.com/developers/reference
[2]: https://docs.discord.com/developers/change-log

## Fontes
- [Documentação oficial — API Reference][1]
- [Documentação oficial — Change Log][2]

## Mudanças oficiais que exigem acompanhamento

A documentação oficial consultada informa que a API v10 é a versão disponível atual e que IDs Discord são snowflakes serializados como strings. A paginação segue o padrão de identificadores e parâmetros `before`, `after` e `around` em várias rotas. Erros de formulário podem trazer `code`, `message` e uma árvore detalhada `errors`, portanto o cliente deve preservar status, código, rota, método e detalhes.

O changelog de 12/08/2026 anunciou obfuscação de canais para usuários e bots. Em HTTP, `GET /guilds/{guild.id}/channels` passará a omitir canais sem `VIEW_CHANNEL` a partir de 16/11/2026; no Gateway, canais podem ter metadados obfuscados, a flag `CHANNEL_OBFUSCATED` e um overwrite negando `VIEW_CHANNEL`. O changelog de 05/08/2026 tornou `channel.application_id` anulável. Também foi documentado `file_types` em File Upload components/opções `ATTACHMENT`, e `app_permissions` em canais resolvidos de interações.

Esses itens devem orientar uma próxima rodada de modelos, cache e interações. Eles não são considerados implementados apenas por estarem documentados aqui.

## Matriz local já coberta

No código local já existem rotas para onboarding, Soundboard, role-connections metadata, Widget, prune, vanity URL, Voice States/Resource, SKUs, assinaturas, stickers multipart, paginação segura e webhooks por token. A matriz integral ainda está aberta.

Validação local no registro: 106 testes aprovados; wheel `pimcord-0.7.0-py3-none-any.whl` gerada; E2EE MLS/DAVE real ausente.

## Referências

[1]: https://docs.discord.com/developers/reference
[2]: https://docs.discord.com/developers/change-log

- [Documentação oficial — API Reference][1]
- [Documentação oficial — Change Log][2]

## Mudanças oficiais que exigem acompanhamento

A documentação oficial consultada informa que a API v10 é a versão disponível atual e que IDs Discord são snowflakes serializados como strings. A paginação segue o padrão de identificadores e parâmetros `before`, `after` e `around` em várias rotas. Erros de formulário podem trazer `code`, `message` e uma árvore detalhada `errors`, portanto o cliente deve preservar status, código, rota, método e detalhes.

O changelog de 12/08/2026 anunciou obfuscação de canais para usuários e bots. Em HTTP, `GET /guilds/{guild.id}/channels` passará a omitir canais sem `VIEW_CHANNEL` a partir de 16/11/2026; no Gateway, canais podem ter metadados obfuscados, a flag `CHANNEL_OBFUSCATED` e um overwrite negando `VIEW_CHANNEL`. O changelog de 05/08/2026 tornou `channel.application_id` anulável. Também foi documentado `file_types` em File Upload components/opções `ATTACHMENT`, e `app_permissions` em canais resolvidos de interações.

Esses itens devem orientar uma próxima rodada de modelos, cache e interações. Eles não são considerados implementados apenas por estarem documentados aqui.

## Matriz local já coberta

No código local já existem rotas para onboarding, Soundboard, role-connections metadata, Widget, prune, vanity URL, Voice States/Resource, SKUs, assinaturas, stickers multipart, paginação segura e webhooks por token. A matriz integral ainda está aberta.

Validação local no registro: 106 testes aprovados; wheel `pimcord-0.7.0-py3-none-any.whl` gerada; E2EE MLS/DAVE real ausente.

## Referências

[1]: https://docs.discord.com/developers/reference
[2]: https://docs.discord.com/developers/change-log

- [Documentação oficial — API Reference][1]
- [Documentação oficial — Change Log][2]

## Mudanças oficiais que exigem acompanhamento

A documentação oficial consultada informa que a API v10 é a versão disponível atual e que IDs Discord são snowflakes serializados como strings. A paginação segue o padrão de identificadores e parâmetros `before`, `after` e `around` em várias rotas. Erros de formulário podem trazer `code`, `message` e uma árvore detalhada `errors`, portanto o cliente deve preservar status, código, rota, método e detalhes.

O changelog de 12/08/2026 anunciou obfuscação de canais para usuários e bots. Em HTTP, `GET /guilds/{guild.id}/channels` passará a omitir canais sem `VIEW_CHANNEL` a partir de 16/11/2026; no Gateway, canais podem ter metadados obfuscados, a flag `CHANNEL_OBFUSCATED` e um overwrite negando `VIEW_CHANNEL`. O changelog de 05/08/2026 tornou `channel.application_id` anulável. Também foi documentado `file_types` em File Upload components/opções `ATTACHMENT`, e `app_permissions` em canais resolvidos de interações.

Esses itens devem orientar uma próxima rodada de modelos, cache e interações. Eles não são considerados implementados apenas por estarem documentados aqui.

## Matriz local já coberta

No código local já existem rotas para onboarding, Soundboard, role-connections metadata, Widget, prune, vanity URL, Voice States/Resource, SKUs, assinaturas, stickers multipart, paginação segura e webhooks por token. A matriz integral ainda está aberta.

Validação local no registro: 106 testes aprovados; wheel `pimcord-0.7.0-py3-none-any.whl` gerada; E2EE MLS/DAVE real ausente.

## Referências

[1]: https://docs.discord.com/developers/reference
[2]: https://docs.discord.com/developers/change-log

- [Documentação oficial — API Reference][1]
- [Documentação oficial — Change Log][2]

## Mudanças oficiais que exigem acompanhamento

A documentação oficial consultada informa que a API v10 é a versão disponível atual e que IDs Discord são snowflakes serializados como strings. A paginação segue o padrão de identificadores e parâmetros `before`, `after` e `around` em várias rotas. Erros de formulário podem trazer `code`, `message` e uma árvore detalhada `errors`, portanto o cliente deve preservar status, código, rota, método e detalhes.

O changelog de 12/08/2026 anunciou obfuscação de canais para usuários e bots. Em HTTP, `GET /guilds/{guild.id}/channels` passará a omitir canais sem `VIEW_CHANNEL` a partir de 16/11/2026; no Gateway, canais podem ter metadados obfuscados, a flag `CHANNEL_OBFUSCATED` e um overwrite negando `VIEW_CHANNEL`. O changelog de 05/08/2026 tornou `channel.application_id` anulável. Também foi documentado `file_types` em File Upload components/opções `ATTACHMENT`, e `app_permissions` em canais resolvidos de interações.

Esses itens devem orientar uma próxima rodada de modelos, cache e interações. Eles não são considerados implementados apenas por estarem documentados aqui.

## Matriz local já coberta

No código local já existem rotas para onboarding, Soundboard, role-connections metadata, Widget, prune, vanity URL, Voice States/Resource, SKUs, assinaturas, stickers multipart, paginação segura e webhooks por token. A matriz integral ainda está aberta.

Validação local no registro: 106 testes aprovados; wheel `pimcord-0.7.0-py3-none-any.whl` gerada; E2EE MLS/DAVE real ausente.

## Referências

[1]: https://docs.discord.com/developers/reference
[2]: https://docs.discord.com/developers/change-log

- [Documentação oficial — API Reference][1]
- [Documentação oficial — Change Log][2]

## Mudanças oficiais que exigem acompanhamento

A documentação oficial consultada informa que a API v10 é a versão disponível atual e que IDs Discord são snowflakes serializados como strings. A paginação segue o padrão de identificadores e parâmetros `before`, `after` e `around` em várias rotas. Erros de formulário podem trazer `code`, `message` e uma árvore detalhada `errors`, portanto o cliente deve preservar status, código, rota, método e detalhes.

O changelog de 12/08/2026 anunciou obfuscação de canais para usuários e bots. Em HTTP, `GET /guilds/{guild.id}/channels` passará a omitir canais sem `VIEW_CHANNEL` a partir de 16/11/2026; no Gateway, canais podem ter metadados obfuscados, a flag `CHANNEL_OBFUSCATED` e um overwrite negando `VIEW_CHANNEL`. O changelog de 05/08/2026 tornou `channel.application_id` anulável. Também foi documentado `file_types` em File Upload components/opções `ATTACHMENT`, e `app_permissions` em canais resolvidos de interações.

Esses itens devem orientar uma próxima rodada de modelos, cache e interações. Eles não são considerados implementados apenas por estarem documentados aqui.

## Matriz local já coberta

No código local já existem rotas para onboarding, Soundboard, role-connections metadata, Widget, prune, vanity URL, Voice States/Resource, SKUs, assinaturas, stickers multipart, paginação segura e webhooks por token. A matriz integral ainda está aberta.

Validação local no registro: 106 testes aprovados; wheel `pimcord-0.7.0-py3-none-any.whl` gerada; E2EE MLS/DAVE real ausente.

## Referências

[1]: https://docs.discord.com/developers/reference
[2]: https://docs.discord.com/developers/change-log

- [Documentação oficial — API Reference][1]
- [Documentação oficial — Change Log][2]

## Mudanças oficiais que exigem acompanhamento

A documentação oficial consultada informa que a API v10 é a versão disponível atual e que IDs Discord são snowflakes serializados como strings. A paginação segue o padrão de identificadores e parâmetros `before`, `after` e `around` em várias rotas. Erros de formulário podem trazer `code`, `message` e uma árvore detalhada `errors`, portanto o cliente deve preservar status, código, rota, método e detalhes.

O changelog de 12/08/2026 anunciou obfuscação de canais para usuários e bots. Em HTTP, `GET /guilds/{guild.id}/channels` passará a omitir canais sem `VIEW_CHANNEL` a partir de 16/11/2026; no Gateway, canais podem ter metadados obfuscados, a flag `CHANNEL_OBFUSCATED` e um overwrite negando `VIEW_CHANNEL`. O changelog de 05/08/2026 tornou `channel.application_id` anulável. Também foi documentado `file_types` em File Upload components/opções `ATTACHMENT`, e `app_permissions` em canais resolvidos de interações.

Esses itens devem orientar uma próxima rodada de modelos, cache e interações. Eles não são considerados implementados apenas por estarem documentados aqui.

## Matriz local já coberta

No código local já existem rotas para onboarding, Soundboard, role-connections metadata, Widget, prune, vanity URL, Voice States/Resource, SKUs, assinaturas, stickers multipart, paginação segura e webhooks por token. A matriz integral ainda está aberta.

Validação local no registro: 106 testes aprovados; wheel `pimcord-0.7.0-py3-none-any.whl` gerada; E2EE MLS/DAVE real ausente.

## Referências

[1]: https://docs.discord.com/developers/reference
[2]: https://docs.discord.com/developers/change-log

- [Documentação oficial — API Reference][1]
- [Documentação oficial — Change Log][2]

## Mudanças oficiais que exigem acompanhamento

A documentação oficial consultada informa que a API v10 é a versão disponível atual e que IDs Discord são snowflakes serializados como strings. A paginação segue o padrão de identificadores e parâmetros `before`, `after` e `around` em várias rotas. Erros de formulário podem trazer `code`, `message` e uma árvore detalhada `errors`, portanto o cliente deve preservar status, código, rota, método e detalhes.

O changelog de 12/08/2026 anunciou obfuscação de canais para usuários e bots. Em HTTP, `GET /guilds/{guild.id}/channels` passará a omitir canais sem `VIEW_CHANNEL` a partir de 16/11/2026; no Gateway, canais podem ter metadados obfuscados, a flag `CHANNEL_OBFUSCATED` e um overwrite negando `VIEW_CHANNEL`. O changelog de 05/08/2026 tornou `channel.application_id` anulável. Também foi documentado `file_types` em File Upload components/opções `ATTACHMENT`, e `app_permissions` em canais resolvidos de interações.

Esses itens devem orientar uma próxima rodada de modelos, cache e interações. Eles não são considerados implementados apenas por estarem documentados aqui.

## Matriz local já coberta

No código local já existem rotas para onboarding, Soundboard, role-connections metadata, Widget, prune, vanity URL, Voice States/Resource, SKUs, assinaturas, stickers multipart, paginação segura e webhooks por token. A matriz integral ainda está aberta.

Validação local no registro: 106 testes aprovados; wheel `pimcord-0.7.0-py3-none-any.whl` gerada; E2EE MLS/DAVE real ausente.

## Referências

[1]: https://docs.discord.com/developers/reference
[2]: https://docs.discord.com/developers/change-log

- [Documentação oficial — API Reference][1]
- [Documentação oficial — Change Log][2]

## Mudanças oficiais que exigem acompanhamento

A documentação oficial consultada informa que a API v10 é a versão disponível atual e que IDs Discord são snowflakes serializados como strings. A paginação segue o padrão de identificadores e parâmetros `before`, `after` e `around` em várias rotas. Erros de formulário podem trazer `code`, `message` e uma árvore detalhada `errors`, portanto o cliente deve preservar status, código, rota, método e detalhes.

O changelog de 12/08/2026 anunciou obfuscação de canais para usuários e bots. Em HTTP, `GET /guilds/{guild.id}/channels` passará a omitir canais sem `VIEW_CHANNEL` a partir de 16/11/2026; no Gateway, canais podem ter metadados obfuscados, a flag `CHANNEL_OBFUSCATED` e um overwrite negando `VIEW_CHANNEL`. O changelog de 05/08/2026 tornou `channel.application_id` anulável. Também foi documentado `file_types` em File Upload components/opções `ATTACHMENT`, e `app_permissions` em canais resolvidos de interações.

Esses itens devem orientar uma próxima rodada de modelos, cache e interações. Eles não são considerados implementados apenas por estarem documentados aqui.

## Matriz local já coberta

No código local já existem rotas para onboarding, Soundboard, role-connections metadata, Widget, prune, vanity URL, Voice States/Resource, SKUs, assinaturas, stickers multipart, paginação segura e webhooks por token. A matriz integral ainda está aberta.

Validação local no registro: 106 testes aprovados; wheel `pimcord-0.7.0-py3-none-any.whl` gerada; E2EE MLS/DAVE real ausente.

## Referências

[1]: https://docs.discord.com/developers/reference
[2]: https://docs.discord.com/developers/change-log

- [Documentação oficial — API Reference][1]
- [Documentação oficial — Change Log][2]

## Mudanças oficiais que exigem acompanhamento

A documentação oficial consultada informa que a API v10 é a versão disponível atual e que IDs Discord são snowflakes serializados como strings. A paginação segue o padrão de identificadores e parâmetros `before`, `after` e `around` em várias rotas. Erros de formulário podem trazer `code`, `message` e uma árvore detalhada `errors`, portanto o cliente deve preservar status, código, rota, método e detalhes.

O changelog de 12/08/2026 anunciou obfuscação de canais para usuários e bots. Em HTTP, `GET /guilds/{guild.id}/channels` passará a omitir canais sem `VIEW_CHANNEL` a partir de 16/11/2026; no Gateway, canais podem ter metadados obfuscados, a flag `CHANNEL_OBFUSCATED` e um overwrite negando `VIEW_CHANNEL`. O changelog de 05/08/2026 tornou `channel.application_id` anulável. Também foi documentado `file_types` em File Upload components/opções `ATTACHMENT`, e `app_permissions` em canais resolvidos de interações.

Esses itens devem orientar uma próxima rodada de modelos, cache e interações. Eles não são considerados implementados apenas por estarem documentados aqui.

## Matriz local já coberta

No código local já existem rotas para onboarding, Soundboard, role-connections metadata, Widget, prune, vanity URL, Voice States/Resource, SKUs, assinaturas, stickers multipart, paginação segura e webhooks por token. A matriz integral ainda está aberta.

Validação local no registro: 106 testes aprovados; wheel `pimcord-0.7.0-py3-none-any.whl` gerada; E2EE MLS/DAVE real ausente.

## Referências

[1]: https://docs.discord.com/developers/reference
[2]: https://docs.discord.com/developers/change-log

- [Documentação oficial — API Reference][1]
- [Documentação oficial — Change Log][2]

## Mudanças oficiais que exigem acompanhamento

A documentação oficial consultada informa que a API v10 é a versão disponível atual e que IDs Discord são snowflakes serializados como strings. A paginação segue o padrão de identificadores e parâmetros `before`, `after` e `around` em várias rotas. Erros de formulário podem trazer `code`, `message` e uma árvore detalhada `errors`, portanto o cliente deve preservar status, código, rota, método e detalhes.

O changelog de 12/08/2026 anunciou obfuscação de canais para usuários e bots. Em HTTP, `GET /guilds/{guild.id}/channels` passará a omitir canais sem `VIEW_CHANNEL` a partir de 16/11/2026; no Gateway, canais podem ter metadados obfuscados, a flag `CHANNEL_OBFUSCATED` e um overwrite negando `VIEW_CHANNEL`. O changelog de 05/08/2026 tornou `channel.application_id` anulável. Também foi documentado `file_types` em File Upload components/opções `ATTACHMENT`, e `app_permissions` em canais resolvidos de interações.

Esses itens devem orientar uma próxima rodada de modelos, cache e interações. Eles não são considerados implementados apenas por estarem documentados aqui.

## Matriz local já coberta

No código local já existem rotas para onboarding, Soundboard, role-connections metadata, Widget, prune, vanity URL, Voice States/Resource, SKUs, assinaturas, stickers multipart, paginação segura e webhooks por token. A matriz integral ainda está aberta.

Validação local no registro: 106 testes aprovados; wheel `pimcord-0.7.0-py3-none-any.whl` gerada; E2EE MLS/DAVE real ausente.

## Referências

[1]: https://docs.discord.com/developers/reference
[2]: https://docs.discord.com/developers/change-log

- [Documentação oficial — API Reference][1]
- [Documentação oficial — Change Log][2]

## Mudanças oficiais que exigem acompanhamento

A documentação oficial consultada informa que a API v10 é a versão disponível atual e que IDs Discord são snowflakes serializados como strings. A paginação segue o padrão de identificadores e parâmetros `before`, `after` e `around` em várias rotas. Erros de formulário podem trazer `code`, `message` e uma árvore detalhada `errors`, portanto o cliente deve preservar status, código, rota, método e detalhes.

O changelog de 12/08/2026 anunciou obfuscação de canais para usuários e bots. Em HTTP, `GET /guilds/{guild.id}/channels` passará a omitir canais sem `VIEW_CHANNEL` a partir de 16/11/2026; no Gateway, canais podem ter metadados obfuscados, a flag `CHANNEL_OBFUSCATED` e um overwrite negando `VIEW_CHANNEL`. O changelog de 05/08/2026 tornou `channel.application_id` anulável. Também foi documentado `file_types` em File Upload components/opções `ATTACHMENT`, e `app_permissions` em canais resolvidos de interações.

Esses itens devem orientar uma próxima rodada de modelos, cache e interações. Eles não são considerados implementados apenas por estarem documentados aqui.

## Matriz local já coberta

No código local já existem rotas para onboarding, Soundboard, role-connections metadata, Widget, prune, vanity URL, Voice States/Resource, SKUs, assinaturas, stickers multipart, paginação segura e webhooks por token. A matriz integral ainda está aberta.

Validação local no registro: 106 testes aprovados; wheel `pimcord-0.7.0-py3-none-any.whl` gerada; E2EE MLS/DAVE real ausente.

## Referências

[1]: https://docs.discord.com/developers/reference
[2]: https://docs.discord.com/developers/change-log

- [Documentação oficial — API Reference][1]
- [Documentação oficial — Change Log][2]

## Mudanças oficiais que exigem acompanhamento

A documentação oficial consultada informa que a API v10 é a versão disponível atual e que IDs Discord são snowflakes serializados como strings. A paginação segue o padrão de identificadores e parâmetros `before`, `after` e `around` em várias rotas. Erros de formulário podem trazer `code`, `message` e uma árvore detalhada `errors`, portanto o cliente deve preservar status, código, rota, método e detalhes.

O changelog de 12/08/2026 anunciou obfuscação de canais para usuários e bots. Em HTTP, `GET /guilds/{guild.id}/channels` passará a omitir canais sem `VIEW_CHANNEL` a partir de 16/11/2026; no Gateway, canais podem ter metadados obfuscados, a flag `CHANNEL_OBFUSCATED` e um overwrite negando `VIEW_CHANNEL`. O changelog de 05/08/2026 tornou `channel.application_id` anulável. Também foi documentado `file_types` em File Upload components/opções `ATTACHMENT`, e `app_permissions` em canais resolvidos de interações.

Esses itens devem orientar uma próxima rodada de modelos, cache e interações. Eles não são considerados implementados apenas por estarem documentados aqui.

## Matriz local já coberta

No código local já existem rotas para onboarding, Soundboard, role-connections metadata, Widget, prune, vanity URL, Voice States/Resource, SKUs, assinaturas, stickers multipart, paginação segura e webhooks por token. A matriz integral ainda está aberta.

Validação local no registro: 106 testes aprovados; wheel `pimcord-0.7.0-py3-none-any.whl` gerada; E2EE MLS/DAVE real ausente.

## Referências

[1]: https://docs.discord.com/developers/reference
[2]: https://docs.discord.com/developers/change-log

- [Documentação oficial — API Reference][1]
- [Documentação oficial — Change Log][2]

## Mudanças oficiais que exigem acompanhamento

A documentação oficial consultada informa que a API v10 é a versão disponível atual e que IDs Discord são snowflakes serializados como strings. A paginação segue o padrão de identificadores e parâmetros `before`, `after` e `around` em várias rotas. Erros de formulário podem trazer `code`, `message` e uma árvore detalhada `errors`, portanto o cliente deve preservar status, código, rota, método e detalhes.

O changelog de 12/08/2026 anunciou obfuscação de canais para usuários e bots. Em HTTP, `GET /guilds/{guild.id}/channels` passará a omitir canais sem `VIEW_CHANNEL` a partir de 16/11/2026; no Gateway, canais podem ter metadados obfuscados, a flag `CHANNEL_OBFUSCATED` e um overwrite negando `VIEW_CHANNEL`. O changelog de 05/08/2026 tornou `channel.application_id` anulável. Também foi documentado `file_types` em File Upload components/opções `ATTACHMENT`, e `app_permissions` em canais resolvidos de interações.

Esses itens devem orientar uma próxima rodada de modelos, cache e interações. Eles não são considerados implementados apenas por estarem documentados aqui.

## Matriz local já coberta

No código local já existem rotas para onboarding, Soundboard, role-connections metadata, Widget, prune, vanity URL, Voice States/Resource, SKUs, assinaturas, stickers multipart, paginação segura e webhooks por token. A matriz integral ainda está aberta.

Validação local no registro: 106 testes aprovados; wheel `pimcord-0.7.0-py3-none-any.whl` gerada; E2EE MLS/DAVE real ausente.

## Referências

[1]: https://docs.discord.com/developers/reference
[2]: https://docs.discord.com/developers/change-log

- [Documentação oficial — API Reference][1]
- [Documentação oficial — Change Log][2]

## Mudanças oficiais que exigem acompanhamento

A documentação oficial consultada informa que a API v10 é a versão disponível atual e que IDs Discord são snowflakes serializados como strings. A paginação segue o padrão de identificadores e parâmetros `before`, `after` e `around` em várias rotas. Erros de formulário podem trazer `code`, `message` e uma árvore detalhada `errors`, portanto o cliente deve preservar status, código, rota, método e detalhes.

O changelog de 12/08/2026 anunciou obfuscação de canais para usuários e bots. Em HTTP, `GET /guilds/{guild.id}/channels` passará a omitir canais sem `VIEW_CHANNEL` a partir de 16/11/2026; no Gateway, canais podem ter metadados obfuscados, a flag `CHANNEL_OBFUSCATED` e um overwrite negando `VIEW_CHANNEL`. O changelog de 05/08/2026 tornou `channel.application_id` anulável. Também foi documentado `file_types` em File Upload components/opções `ATTACHMENT`, e `app_permissions` em canais resolvidos de interações.

Esses itens devem orientar uma próxima rodada de modelos, cache e interações. Eles não são considerados implementados apenas por estarem documentados aqui.

## Matriz local já coberta

No código local já existem rotas para onboarding, Soundboard, role-connections metadata, Widget, prune, vanity URL, Voice States/Resource, SKUs, assinaturas, stickers multipart, paginação segura e webhooks por token. A matriz integral ainda está aberta.

Validação local no registro: 106 testes aprovados; wheel `pimcord-0.7.0-py3-none-any.whl` gerada; E2EE MLS/DAVE real ausente.

## Referências

[1]: https://docs.discord.com/developers/reference
[2]: https://docs.discord.com/developers/change-log

- [Documentação oficial — API Reference][1]
- [Documentação oficial — Change Log][2]

## Mudanças oficiais que exigem acompanhamento

A documentação oficial consultada informa que a API v10 é a versão disponível atual e que IDs Discord são snowflakes serializados como strings. A paginação segue o padrão de identificadores e parâmetros `before`, `after` e `around` em várias rotas. Erros de formulário podem trazer `code`, `message` e uma árvore detalhada `errors`, portanto o cliente deve preservar status, código, rota, método e detalhes.

O changelog de 12/08/2026 anunciou obfuscação de canais para usuários e bots. Em HTTP, `GET /guilds/{guild.id}/channels` passará a omitir canais sem `VIEW_CHANNEL` a partir de 16/11/2026; no Gateway, canais podem ter metadados obfuscados, a flag `CHANNEL_OBFUSCATED` e um overwrite negando `VIEW_CHANNEL`. O changelog de 05/08/2026 tornou `channel.application_id` anulável. Também foi documentado `file_types` em File Upload components/opções `ATTACHMENT`, e `app_permissions` em canais resolvidos de interações.

Esses itens devem orientar uma próxima rodada de modelos, cache e interações. Eles não são considerados implementados apenas por estarem documentados aqui.

## Matriz local já coberta

No código local já existem rotas para onboarding, Soundboard, role-connections metadata, Widget, prune, vanity URL, Voice States/Resource, SKUs, assinaturas, stickers multipart, paginação segura e webhooks por token. A matriz integral ainda está aberta.

Validação local no registro: 106 testes aprovados; wheel `pimcord-0.7.0-py3-none-any.whl` gerada; E2EE MLS/DAVE real ausente.

## Referências

[1]: https://docs.discord.com/developers/reference
[2]: https://docs.discord.com/developers/change-log

- [Documentação oficial — API Reference][1]
- [Documentação oficial — Change Log][2]

## Mudanças oficiais que exigem acompanhamento

A documentação oficial consultada informa que a API v10 é a versão disponível atual e que IDs Discord são snowflakes serializados como strings. A paginação segue o padrão de identificadores e parâmetros `before`, `after` e `around` em várias rotas. Erros de formulário podem trazer `code`, `message` e uma árvore detalhada `errors`, portanto o cliente deve preservar status, código, rota, método e detalhes.

O changelog de 12/08/2026 anunciou obfuscação de canais para usuários e bots. Em HTTP, `GET /guilds/{guild.id}/channels` passará a omitir canais sem `VIEW_CHANNEL` a partir de 16/11/2026; no Gateway, canais podem ter metadados obfuscados, a flag `CHANNEL_OBFUSCATED` e um overwrite negando `VIEW_CHANNEL`. O changelog de 05/08/2026 tornou `channel.application_id` anulável. Também foi documentado `file_types` em File Upload components/opções `ATTACHMENT`, e `app_permissions` em canais resolvidos de interações.

Esses itens devem orientar uma próxima rodada de modelos, cache e interações. Eles não são considerados implementados apenas por estarem documentados aqui.

## Matriz local já coberta

No código local já existem rotas para onboarding, Soundboard, role-connections metadata, Widget, prune, vanity URL, Voice States/Resource, SKUs, assinaturas, stickers multipart, paginação segura e webhooks por token. A matriz integral ainda está aberta.

Validação local no registro: 106 testes aprovados; wheel `pimcord-0.7.0-py3-none-any.whl` gerada; E2EE MLS/DAVE real ausente.

## Referências

[1]: https://docs.discord.com/developers/reference
[2]: https://docs.discord.com/developers/change-log

- [Documentação oficial — API Reference][1]
- [Documentação oficial — Change Log][2]

## Mudanças oficiais que exigem acompanhamento

A documentação oficial consultada informa que a API v10 é a versão disponível atual e que IDs Discord são snowflakes serializados como strings. A paginação segue o padrão de identificadores e parâmetros `before`, `after` e `around` em várias rotas. Erros de formulário podem trazer `code`, `message` e uma árvore detalhada `errors`, portanto o cliente deve preservar status, código, rota, método e detalhes.

O changelog de 12/08/2026 anunciou obfuscação de canais para usuários e bots. Em HTTP, `GET /guilds/{guild.id}/channels` passará a omitir canais sem `VIEW_CHANNEL` a partir de 16/11/2026; no Gateway, canais podem ter metadados obfuscados, a flag `CHANNEL_OBFUSCATED` e um overwrite negando `VIEW_CHANNEL`. O changelog de 05/08/2026 tornou `channel.application_id` anulável. Também foi documentado `file_types` em File Upload components/opções `ATTACHMENT`, e `app_permissions` em canais resolvidos de interações.

Esses itens devem orientar uma próxima rodada de modelos, cache e interações. Eles não são considerados implementados apenas por estarem documentados aqui.

## Matriz local já coberta

No código local já existem rotas para onboarding, Soundboard, role-connections metadata, Widget, prune, vanity URL, Voice States/Resource, SKUs, assinaturas, stickers multipart, paginação segura e webhooks por token. A matriz integral ainda está aberta.

Validação local no registro: 106 testes aprovados; wheel `pimcord-0.7.0-py3-none-any.whl` gerada; E2EE MLS/DAVE real ausente.

## Referências

[1]: https://docs.discord.com/developers/reference
[2]: https://docs.discord.com/developers/change-log

- [Documentação oficial — API Reference][1]
- [Documentação oficial — Change Log][2]

## Mudanças oficiais que exigem acompanhamento

A documentação oficial consultada informa que a API v10 é a versão disponível atual e que IDs Discord são snowflakes serializados como strings. A paginação segue o padrão de identificadores e parâmetros `before`, `after` e `around` em várias rotas. Erros de formulário podem trazer `code`, `message` e uma árvore detalhada `errors`, portanto o cliente deve preservar status, código, rota, método e detalhes.

O changelog de 12/08/2026 anunciou obfuscação de canais para usuários e bots. Em HTTP, `GET /guilds/{guild.id}/channels` passará a omitir canais sem `VIEW_CHANNEL` a partir de 16/11/2026; no Gateway, canais podem ter metadados obfuscados, a flag `CHANNEL_OBFUSCATED` e um overwrite negando `VIEW_CHANNEL`. O changelog de 05/08/2026 tornou `channel.application_id` anulável. Também foi documentado `file_types` em File Upload components/opções `ATTACHMENT`, e `app_permissions` em canais resolvidos de interações.

Esses itens devem orientar uma próxima rodada de modelos, cache e interações. Eles não são considerados implementados apenas por estarem documentados aqui.

## Matriz local já coberta

No código local já existem rotas para onboarding, Soundboard, role-connections metadata, Widget, prune, vanity URL, Voice States/Resource, SKUs, assinaturas, stickers multipart, paginação segura e webhooks por token. A matriz integral ainda está aberta.

Validação local no registro: 106 testes aprovados; wheel `pimcord-0.7.0-py3-none-any.whl` gerada; E2EE MLS/DAVE real ausente.

## Referências

[1]: https://docs.discord.com/developers/reference
[2]: https://docs.discord.com/developers/change-log

- [Documentação oficial — API Reference][1]
- [Documentação oficial — Change Log][2]

## Mudanças oficiais que exigem acompanhamento

A documentação oficial consultada informa que a API v10 é a versão disponível atual e que IDs Discord são snowflakes serializados como strings. A paginação segue o padrão de identificadores e parâmetros `before`, `after` e `around` em várias rotas. Erros de formulário podem trazer `code`, `message` e uma árvore detalhada `errors`, portanto o cliente deve preservar status, código, rota, método e detalhes.

O changelog de 12/08/2026 anunciou obfuscação de canais para usuários e bots. Em HTTP, `GET /guilds/{guild.id}/channels` passará a omitir canais sem `VIEW_CHANNEL` a partir de 16/11/2026; no Gateway, canais podem ter metadados obfuscados, a flag `CHANNEL_OBFUSCATED` e um overwrite negando `VIEW_CHANNEL`. O changelog de 05/08/2026 tornou `channel.application_id` anulável. Também foi documentado `file_types` em File Upload components/opções `ATTACHMENT`, e `app_permissions` em canais resolvidos de interações.

Esses itens devem orientar uma próxima rodada de modelos, cache e interações. Eles não são considerados implementados apenas por estarem documentados aqui.

## Matriz local já coberta

No código local já existem rotas para onboarding, Soundboard, role-connections metadata, Widget, prune, vanity URL, Voice States/Resource, SKUs, assinaturas, stickers multipart, paginação segura e webhooks por token. A matriz integral ainda está aberta.

Validação local no registro: 106 testes aprovados; wheel `pimcord-0.7.0-py3-none-any.whl` gerada; E2EE MLS/DAVE real ausente.

## Referências

[1]: https://docs.discord.com/developers/reference
[2]: https://docs.discord.com/developers/change-log

- [Documentação oficial — API Reference][1]
- [Documentação oficial — Change Log][2]

## Mudanças oficiais que exigem acompanhamento

A documentação oficial consultada informa que a API v10 é a versão disponível atual e que IDs Discord são snowflakes serializados como strings. A paginação segue o padrão de identificadores e parâmetros `before`, `after` e `around` em várias rotas. Erros de formulário podem trazer `code`, `message` e uma árvore detalhada `errors`, portanto o cliente deve preservar status, código, rota, método e detalhes.

O changelog de 12/08/2026 anunciou obfuscação de canais para usuários e bots. Em HTTP, `GET /guilds/{guild.id}/channels` passará a omitir canais sem `VIEW_CHANNEL` a partir de 16/11/2026; no Gateway, canais podem ter metadados obfuscados, a flag `CHANNEL_OBFUSCATED` e um overwrite negando `VIEW_CHANNEL`. O changelog de 05/08/2026 tornou `channel.application_id` anulável. Também foi documentado `file_types` em File Upload components/opções `ATTACHMENT`, e `app_permissions` em canais resolvidos de interações.

Esses itens devem orientar uma próxima rodada de modelos, cache e interações. Eles não são considerados implementados apenas por estarem documentados aqui.

## Matriz local já coberta

No código local já existem rotas para onboarding, Soundboard, role-connections metadata, Widget, prune, vanity URL, Voice States/Resource, SKUs, assinaturas, stickers multipart, paginação segura e webhooks por token. A matriz integral ainda está aberta.

Validação local no registro: 106 testes aprovados; wheel `pimcord-0.7.0-py3-none-any.whl` gerada; E2EE MLS/DAVE real ausente.

## Referências

[1]: https://docs.discord.com/developers/reference
[2]: https://docs.discord.com/developers/change-log

- [Documentação oficial — API Reference][1]
- [Documentação oficial — Change Log][2]

## Mudanças oficiais que exigem acompanhamento

A documentação oficial consultada informa que a API v10 é a versão disponível atual e que IDs Discord são snowflakes serializados como strings. A paginação segue o padrão de identificadores e parâmetros `before`, `after` e `around` em várias rotas. Erros de formulário podem trazer `code`, `message` e uma árvore detalhada `errors`, portanto o cliente deve preservar status, código, rota, método e detalhes.

O changelog de 12/08/2026 anunciou obfuscação de canais para usuários e bots. Em HTTP, `GET /guilds/{guild.id}/channels` passará a omitir canais sem `VIEW_CHANNEL` a partir de 16/11/2026; no Gateway, canais podem ter metadados obfuscados, a flag `CHANNEL_OBFUSCATED` e um overwrite negando `VIEW_CHANNEL`. O changelog de 05/08/2026 tornou `channel.application_id` anulável. Também foi documentado `file_types` em File Upload components/opções `ATTACHMENT`, e `app_permissions` em canais resolvidos de interações.

Esses itens devem orientar uma próxima rodada de modelos, cache e interações. Eles não são considerados implementados apenas por estarem documentados aqui.

## Matriz local já coberta

No código local já existem rotas para onboarding, Soundboard, role-connections metadata, Widget, prune, vanity URL, Voice States/Resource, SKUs, assinaturas, stickers multipart, paginação segura e webhooks por token. A matriz integral ainda está aberta.

Validação local no registro: 106 testes aprovados; wheel `pimcord-0.7.0-py3-none-any.whl` gerada; E2EE MLS/DAVE real ausente.

## Referências

[1]: https://docs.discord.com/developers/reference
[2]: https://docs.discord.com/developers/change-log

- [Documentação oficial — API Reference][1]
- [Documentação oficial — Change Log][2]

## Mudanças oficiais que exigem acompanhamento

A documentação oficial consultada informa que a API v10 é a versão disponível atual e que IDs Discord são snowflakes serializados como strings. A paginação segue o padrão de identificadores e parâmetros `before`, `after` e `around` em várias rotas. Erros de formulário podem trazer `code`, `message` e uma árvore detalhada `errors`, portanto o cliente deve preservar status, código, rota, método e detalhes.

O changelog de 12/08/2026 anunciou obfuscação de canais para usuários e bots. Em HTTP, `GET /guilds/{guild.id}/channels` passará a omitir canais sem `VIEW_CHANNEL` a partir de 16/11/2026; no Gateway, canais podem ter metadados obfuscados, a flag `CHANNEL_OBFUSCATED` e um overwrite negando `VIEW_CHANNEL`. O changelog de 05/08/2026 tornou `channel.application_id` anulável. Também foi documentado `file_types` em File Upload components/opções `ATTACHMENT`, e `app_permissions` em canais resolvidos de interações.

Esses itens devem orientar uma próxima rodada de modelos, cache e interações. Eles não são considerados implementados apenas por estarem documentados aqui.

## Matriz local já coberta

No código local já existem rotas para onboarding, Soundboard, role-connections metadata, Widget, prune, vanity URL, Voice States/Resource, SKUs, assinaturas, stickers multipart, paginação segura e webhooks por token. A matriz integral ainda está aberta.

Validação local no registro: 106 testes aprovados; wheel `pimcord-0.7.0-py3-none-any.whl` gerada; E2EE MLS/DAVE real ausente.

## Referências

[1]: https://docs.discord.com/developers/reference
[2]: https://docs.discord.com/developers/change-log

- [Documentação oficial — API Reference][1]
- [Documentação oficial — Change Log][2]

## Mudanças oficiais que exigem acompanhamento

A documentação oficial consultada informa que a API v10 é a versão disponível atual e que IDs Discord são snowflakes serializados como strings. A paginação segue o padrão de identificadores e parâmetros `before`, `after` e `around` em várias rotas. Erros de formulário podem trazer `code`, `message` e uma árvore detalhada `errors`, portanto o cliente deve preservar status, código, rota, método e detalhes.

O changelog de 12/08/2026 anunciou obfuscação de canais para usuários e bots. Em HTTP, `GET /guilds/{guild.id}/channels` passará a omitir canais sem `VIEW_CHANNEL` a partir de 16/11/2026; no Gateway, canais podem ter metadados obfuscados, a flag `CHANNEL_OBFUSCATED` e um overwrite negando `VIEW_CHANNEL`. O changelog de 05/08/2026 tornou `channel.application_id` anulável. Também foi documentado `file_types` em File Upload components/opções `ATTACHMENT`, e `app_permissions` em canais resolvidos de interações.

Esses itens devem orientar uma próxima rodada de modelos, cache e interações. Eles não são considerados implementados apenas por estarem documentados aqui.

## Matriz local já coberta

No código local já existem rotas para onboarding, Soundboard, role-connections metadata, Widget, prune, vanity URL, Voice States/Resource, SKUs, assinaturas, stickers multipart, paginação segura e webhooks por token. A matriz integral ainda está aberta.

Validação local no registro: 106 testes aprovados; wheel `pimcord-0.7.0-py3-none-any.whl` gerada; E2EE MLS/DAVE real ausente.

## Referências

[1]: https://docs.discord.com/developers/reference
[2]: https://docs.discord.com/developers/change-log

- [Documentação oficial — API Reference][1]
- [Documentação oficial — Change Log][2]

## Mudanças oficiais que exigem acompanhamento

A documentação oficial consultada informa que a API v10 é a versão disponível atual e que IDs Discord são snowflakes serializados como strings. A paginação segue o padrão de identificadores e parâmetros `before`, `after` e `around` em várias rotas. Erros de formulário podem trazer `code`, `message` e uma árvore detalhada `errors`, portanto o cliente deve preservar status, código, rota, método e detalhes.

O changelog de 12/08/2026 anunciou obfuscação de canais para usuários e bots. Em HTTP, `GET /guilds/{guild.id}/channels` passará a omitir canais sem `VIEW_CHANNEL` a partir de 16/11/2026; no Gateway, canais podem ter metadados obfuscados, a flag `CHANNEL_OBFUSCATED` e um overwrite negando `VIEW_CHANNEL`. O changelog de 05/08/2026 tornou `channel.application_id` anulável. Também foi documentado `file_types` em File Upload components/opções `ATTACHMENT`, e `app_permissions` em canais resolvidos de interações.

Esses itens devem orientar uma próxima rodada de modelos, cache e interações. Eles não são considerados implementados apenas por estarem documentados aqui.

## Matriz local já coberta

No código local já existem rotas para onboarding, Soundboard, role-connections metadata, Widget, prune, vanity URL, Voice States/Resource, SKUs, assinaturas, stickers multipart, paginação segura e webhooks por token. A matriz integral ainda está aberta.

Validação local no registro: 106 testes aprovados; wheel `pimcord-0.7.0-py3-none-any.whl` gerada; E2EE MLS/DAVE real ausente.

## Referências

[1]: https://docs.discord.com/developers/reference
[2]: https://docs.discord.com/developers/change-log

- [Documentação oficial — API Reference][1]
- [Documentação oficial — Change Log][2]

## Mudanças oficiais que exigem acompanhamento

A documentação oficial consultada informa que a API v10 é a versão disponível atual e que IDs Discord são snowflakes serializados como strings. A paginação segue o padrão de identificadores e parâmetros `before`, `after` e `around` em várias rotas. Erros de formulário podem trazer `code`, `message` e uma árvore detalhada `errors`, portanto o cliente deve preservar status, código, rota, método e detalhes.

O changelog de 12/08/2026 anunciou obfuscação de canais para usuários e bots. Em HTTP, `GET /guilds/{guild.id}/channels` passará a omitir canais sem `VIEW_CHANNEL` a partir de 16/11/2026; no Gateway, canais podem ter metadados obfuscados, a flag `CHANNEL_OBFUSCATED` e um overwrite negando `VIEW_CHANNEL`. O changelog de 05/08/2026 tornou `channel.application_id` anulável. Também foi documentado `file_types` em File Upload components/opções `ATTACHMENT`, e `app_permissions` em canais resolvidos de interações.

Esses itens devem orientar uma próxima rodada de modelos, cache e interações. Eles não são considerados implementados apenas por estarem documentados aqui.

## Matriz local já coberta

No código local já existem rotas para onboarding, Soundboard, role-connections metadata, Widget, prune, vanity URL, Voice States/Resource, SKUs, assinaturas, stickers multipart, paginação segura e webhooks por token. A matriz integral ainda está aberta.

Validação local no registro: 106 testes aprovados; wheel `pimcord-0.7.0-py3-none-any.whl` gerada; E2EE MLS/DAVE real ausente.

## Referências

[1]: https://docs.discord.com/developers/reference
[2]: https://docs.discord.com/developers/change-log

- [Documentação oficial — API Reference][1]
- [Documentação oficial — Change Log][2]

## Mudanças oficiais que exigem acompanhamento

A documentação oficial consultada informa que a API v10 é a versão disponível atual e que IDs Discord são snowflakes serializados como strings. A paginação segue o padrão de identificadores e parâmetros `before`, `after` e `around` em várias rotas. Erros de formulário podem trazer `code`, `message` e uma árvore detalhada `errors`, portanto o cliente deve preservar status, código, rota, método e detalhes.

O changelog de 12/08/2026 anunciou obfuscação de canais para usuários e bots. Em HTTP, `GET /guilds/{guild.id}/channels` passará a omitir canais sem `VIEW_CHANNEL` a partir de 16/11/2026; no Gateway, canais podem ter metadados obfuscados, a flag `CHANNEL_OBFUSCATED` e um overwrite negando `VIEW_CHANNEL`. O changelog de 05/08/2026 tornou `channel.application_id` anulável. Também foi documentado `file_types` em File Upload components/opções `ATTACHMENT`, e `app_permissions` em canais resolvidos de interações.

Esses itens devem orientar uma próxima rodada de modelos, cache e interações. Eles não são considerados implementados apenas por estarem documentados aqui.

## Matriz local já coberta

No código local já existem rotas para onboarding, Soundboard, role-connections metadata, Widget, prune, vanity URL, Voice States/Resource, SKUs, assinaturas, stickers multipart, paginação segura e webhooks por token. A matriz integral ainda está aberta.

Validação local no registro: 106 testes aprovados; wheel `pimcord-0.7.0-py3-none-any.whl` gerada; E2EE MLS/DAVE real ausente.

## Referências

[1]: https://docs.discord.com/developers/reference
[2]: https://docs.discord.com/developers/change-log

- [Documentação oficial — API Reference][1]
- [Documentação oficial — Change Log][2]

## Mudanças oficiais que exigem acompanhamento

A documentação oficial consultada informa que a API v10 é a versão disponível atual e que IDs Discord são snowflakes serializados como strings. A paginação segue o padrão de identificadores e parâmetros `before`, `after` e `around` em várias rotas. Erros de formulário podem trazer `code`, `message` e uma árvore detalhada `errors`, portanto o cliente deve preservar status, código, rota, método e detalhes.

O changelog de 12/08/2026 anunciou obfuscação de canais para usuários e bots. Em HTTP, `GET /guilds/{guild.id}/channels` passará a omitir canais sem `VIEW_CHANNEL` a partir de 16/11/2026; no Gateway, canais podem ter metadados obfuscados, a flag `CHANNEL_OBFUSCATED` e um overwrite negando `VIEW_CHANNEL`. O changelog de 05/08/2026 tornou `channel.application_id` anulável. Também foi documentado `file_types` em File Upload components/opções `ATTACHMENT`, e `app_permissions` em canais resolvidos de interações.

Esses itens devem orientar uma próxima rodada de modelos, cache e interações. Eles não são considerados implementados apenas por estarem documentados aqui.

## Matriz local já coberta

No código local já existem rotas para onboarding, Soundboard, role-connections metadata, Widget, prune, vanity URL, Voice States/Resource, SKUs, assinaturas, stickers multipart, paginação segura e webhooks por token. A matriz integral ainda está aberta.

Validação local no registro: 106 testes aprovados; wheel `pimcord-0.7.0-py3-none-any.whl` gerada; E2EE MLS/DAVE real ausente.

## Referências

[1]: https://docs.discord.com/developers/reference
[2]: https://docs.discord.com/developers/change-log

- [Documentação oficial — API Reference][1]
- [Documentação oficial — Change Log][2]

## Mudanças oficiais que exigem acompanhamento

A documentação oficial consultada informa que a API v10 é a versão disponível atual e que IDs Discord são snowflakes serializados como strings. A paginação segue o padrão de identificadores e parâmetros `before`, `after` e `around` em várias rotas. Erros de formulário podem trazer `code`, `message` e uma árvore detalhada `errors`, portanto o cliente deve preservar status, código, rota, método e detalhes.

O changelog de 12/08/2026 anunciou obfuscação de canais para usuários e bots. Em HTTP, `GET /guilds/{guild.id}/channels` passará a omitir canais sem `VIEW_CHANNEL` a partir de 16/11/2026; no Gateway, canais podem ter metadados obfuscados, a flag `CHANNEL_OBFUSCATED` e um overwrite negando `VIEW_CHANNEL`. O changelog de 05/08/2026 tornou `channel.application_id` anulável. Também foi documentado `file_types` em File Upload components/opções `ATTACHMENT`, e `app_permissions` em canais resolvidos de interações.

Esses itens devem orientar uma próxima rodada de modelos, cache e interações. Eles não são considerados implementados apenas por estarem documentados aqui.

## Matriz local já coberta

No código local já existem rotas para onboarding, Soundboard, role-connections metadata, Widget, prune, vanity URL, Voice States/Resource, SKUs, assinaturas, stickers multipart, paginação segura e webhooks por token. A matriz integral ainda está aberta.

Validação local no registro: 106 testes aprovados; wheel `pimcord-0.7.0-py3-none-any.whl` gerada; E2EE MLS/DAVE real ausente.

## Referências

[1]: https://docs.discord.com/developers/reference
[2]: https://docs.discord.com/developers/change-log

- [Documentação oficial — API Reference][1]
- [Documentação oficial — Change Log][2]

## Mudanças oficiais que exigem acompanhamento

A documentação oficial consultada informa que a API v10 é a versão disponível atual e que IDs Discord são snowflakes serializados como strings. A paginação segue o padrão de identificadores e parâmetros `before`, `after` e `around` em várias rotas. Erros de formulário podem trazer `code`, `message` e uma árvore detalhada `errors`, portanto o cliente deve preservar status, código, rota, método e detalhes.

O changelog de 12/08/2026 anunciou obfuscação de canais para usuários e bots. Em HTTP, `GET /guilds/{guild.id}/channels` passará a omitir canais sem `VIEW_CHANNEL` a partir de 16/11/2026; no Gateway, canais podem ter metadados obfuscados, a flag `CHANNEL_OBFUSCATED` e um overwrite negando `VIEW_CHANNEL`. O changelog de 05/08/2026 tornou `channel.application_id` anulável. Também foi documentado `file_types` em File Upload components/opções `ATTACHMENT`, e `app_permissions` em canais resolvidos de interações.

Esses itens devem orientar uma próxima rodada de modelos, cache e interações. Eles não são considerados implementados apenas por estarem documentados aqui.

## Matriz local já coberta

No código local já existem rotas para onboarding, Soundboard, role-connections metadata, Widget, prune, vanity URL, Voice States/Resource, SKUs, assinaturas, stickers multipart, paginação segura e webhooks por token. A matriz integral ainda está aberta.

Validação local no registro: 106 testes aprovados; wheel `pimcord-0.7.0-py3-none-any.whl` gerada; E2EE MLS/DAVE real ausente.

## Referências

[1]: https://docs.discord.com/developers/reference
[2]: https://docs.discord.com/developers/change-log

- [Documentação oficial — API Reference][1]
- [Documentação oficial — Change Log][2]

## Mudanças oficiais que exigem acompanhamento

A documentação oficial consultada informa que a API v10 é a versão disponível atual e que IDs Discord são snowflakes serializados como strings. A paginação segue o padrão de identificadores e parâmetros `before`, `after` e `around` em várias rotas. Erros de formulário podem trazer `code`, `message` e uma árvore detalhada `errors`, portanto o cliente deve preservar status, código, rota, método e detalhes.

O changelog de 12/08/2026 anunciou obfuscação de canais para usuários e bots. Em HTTP, `GET /guilds/{guild.id}/channels` passará a omitir canais sem `VIEW_CHANNEL` a partir de 16/11/2026; no Gateway, canais podem ter metadados obfuscados, a flag `CHANNEL_OBFUSCATED` e um overwrite negando `VIEW_CHANNEL`. O changelog de 05/08/2026 tornou `channel.application_id` anulável. Também foi documentado `file_types` em File Upload components/opções `ATTACHMENT`, e `app_permissions` em canais resolvidos de interações.

Esses itens devem orientar uma próxima rodada de modelos, cache e interações. Eles não são considerados implementados apenas por estarem documentados aqui.

## Matriz local já coberta

No código local já existem rotas para onboarding, Soundboard, role-connections metadata, Widget, prune, vanity URL, Voice States/Resource, SKUs, assinaturas, stickers multipart, paginação segura e webhooks por token. A matriz integral ainda está aberta.

Validação local no registro: 106 testes aprovados; wheel `pimcord-0.7.0-py3-none-any.whl` gerada; E2EE MLS/DAVE real ausente.

## Referências

[1]: https://docs.discord.com/developers/reference
[2]: https://docs.discord.com/developers/change-log

- [Documentação oficial — API Reference][1]
- [Documentação oficial — Change Log][2]

## Mudanças oficiais que exigem acompanhamento

A documentação oficial consultada informa que a API v10 é a versão disponível atual e que IDs Discord são snowflakes serializados como strings. A paginação segue o padrão de identificadores e parâmetros `before`, `after` e `around` em várias rotas. Erros de formulário podem trazer `code`, `message` e uma árvore detalhada `errors`, portanto o cliente deve preservar status, código, rota, método e detalhes.

O changelog de 12/08/2026 anunciou obfuscação de canais para usuários e bots. Em HTTP, `GET /guilds/{guild.id}/channels` passará a omitir canais sem `VIEW_CHANNEL` a partir de 16/11/2026; no Gateway, canais podem ter metadados obfuscados, a flag `CHANNEL_OBFUSCATED` e um overwrite negando `VIEW_CHANNEL`. O changelog de 05/08/2026 tornou `channel.application_id` anulável. Também foi documentado `file_types` em File Upload components/opções `ATTACHMENT`, e `app_permissions` em canais resolvidos de interações.

Esses itens devem orientar uma próxima rodada de modelos, cache e interações. Eles não são considerados implementados apenas por estarem documentados aqui.

## Matriz local já coberta

No código local já existem rotas para onboarding, Soundboard, role-connections metadata, Widget, prune, vanity URL, Voice States/Resource, SKUs, assinaturas, stickers multipart, paginação segura e webhooks por token. A matriz integral ainda está aberta.

Validação local no registro: 106 testes aprovados; wheel `pimcord-0.7.0-py3-none-any.whl` gerada; E2EE MLS/DAVE real ausente.

## Referências

[1]: https://docs.discord.com/developers/reference
[2]: https://docs.discord.com/developers/change-log

- [Documentação oficial — API Reference][1]
- [Documentação oficial — Change Log][2]

## Mudanças oficiais que exigem acompanhamento

A documentação oficial consultada informa que a API v10 é a versão disponível atual e que IDs Discord são snowflakes serializados como strings. A paginação segue o padrão de identificadores e parâmetros `before`, `after` e `around` em várias rotas. Erros de formulário podem trazer `code`, `message` e uma árvore detalhada `errors`, portanto o cliente deve preservar status, código, rota, método e detalhes.

O changelog de 12/08/2026 anunciou obfuscação de canais para usuários e bots. Em HTTP, `GET /guilds/{guild.id}/channels` passará a omitir canais sem `VIEW_CHANNEL` a partir de 16/11/2026; no Gateway, canais podem ter metadados obfuscados, a flag `CHANNEL_OBFUSCATED` e um overwrite negando `VIEW_CHANNEL`. O changelog de 05/08/2026 tornou `channel.application_id` anulável. Também foi documentado `file_types` em File Upload components/opções `ATTACHMENT`, e `app_permissions` em canais resolvidos de interações.

Esses itens devem orientar uma próxima rodada de modelos, cache e interações. Eles não são considerados implementados apenas por estarem documentados aqui.

## Matriz local já coberta

No código local já existem rotas para onboarding, Soundboard, role-connections metadata, Widget, prune, vanity URL, Voice States/Resource, SKUs, assinaturas, stickers multipart, paginação segura e webhooks por token. A matriz integral ainda está aberta.

Validação local no registro: 106 testes aprovados; wheel `pimcord-0.7.0-py3-none-any.whl` gerada; E2EE MLS/DAVE real ausente.

## Referências

[1]: https://docs.discord.com/developers/reference
[2]: https://docs.discord.com/developers/change-log

- [Documentação oficial — API Reference][1]
- [Documentação oficial — Change Log][2]

## Mudanças oficiais que exigem acompanhamento

A documentação oficial consultada informa que a API v10 é a versão disponível atual e que IDs Discord são snowflakes serializados como strings. A paginação segue o padrão de identificadores e parâmetros `before`, `after` e `around` em várias rotas. Erros de formulário podem trazer `code`, `message` e uma árvore detalhada `errors`, portanto o cliente deve preservar status, código, rota, método e detalhes.

O changelog de 12/08/2026 anunciou obfuscação de canais para usuários e bots. Em HTTP, `GET /guilds/{guild.id}/channels` passará a omitir canais sem `VIEW_CHANNEL` a partir de 16/11/2026; no Gateway, canais podem ter metadados obfuscados, a flag `CHANNEL_OBFUSCATED` e um overwrite negando `VIEW_CHANNEL`. O changelog de 05/08/2026 tornou `channel.application_id` anulável. Também foi documentado `file_types` em File Upload components/opções `ATTACHMENT`, e `app_permissions` em canais resolvidos de interações.

Esses itens devem orientar uma próxima rodada de modelos, cache e interações. Eles não são considerados implementados apenas por estarem documentados aqui.

## Matriz local já coberta

No código local já existem rotas para onboarding, Soundboard, role-connections metadata, Widget, prune, vanity URL, Voice States/Resource, SKUs, assinaturas, stickers multipart, paginação segura e webhooks por token. A matriz integral ainda está aberta.

Validação local no registro: 106 testes aprovados; wheel `pimcord-0.7.0-py3-none-any.whl` gerada; E2EE MLS/DAVE real ausente.

## Referências

[1]: https://docs.discord.com/developers/reference
[2]: https://docs.discord.com/developers/change-log

- [Documentação oficial — API Reference][1]
- [Documentação oficial — Change Log][2]

## Mudanças oficiais que exigem acompanhamento

A documentação oficial consultada informa que a API v10 é a versão disponível atual e que IDs Discord são snowflakes serializados como strings. A paginação segue o padrão de identificadores e parâmetros `before`, `after` e `around` em várias rotas. Erros de formulário podem trazer `code`, `message` e uma árvore detalhada `errors`, portanto o cliente deve preservar status, código, rota, método e detalhes.

O changelog de 12/08/2026 anunciou obfuscação de canais para usuários e bots. Em HTTP, `GET /guilds/{guild.id}/channels` passará a omitir canais sem `VIEW_CHANNEL` a partir de 16/11/2026; no Gateway, canais podem ter metadados obfuscados, a flag `CHANNEL_OBFUSCATED` e um overwrite negando `VIEW_CHANNEL`. O changelog de 05/08/2026 tornou `channel.application_id` anulável. Também foi documentado `file_types` em File Upload components/opções `ATTACHMENT`, e `app_permissions` em canais resolvidos de interações.

Esses itens devem orientar uma próxima rodada de modelos, cache e interações. Eles não são considerados implementados apenas por estarem documentados aqui.

## Matriz local já coberta

No código local já existem rotas para onboarding, Soundboard, role-connections metadata, Widget, prune, vanity URL, Voice States/Resource, SKUs, assinaturas, stickers multipart, paginação segura e webhooks por token. A matriz integral ainda está aberta.

Validação local no registro: 106 testes aprovados; wheel `pimcord-0.7.0-py3-none-any.whl` gerada; E2EE MLS/DAVE real ausente.

## Referências

[1]: https://docs.discord.com/developers/reference
[2]: https://docs.discord.com/developers/change-log

- [Documentação oficial — API Reference][1]
- [Documentação oficial — Change Log][2]

## Mudanças oficiais que exigem acompanhamento

A documentação oficial consultada informa que a API v10 é a versão disponível atual e que IDs Discord são snowflakes serializados como strings. A paginação segue o padrão de identificadores e parâmetros `before`, `after` e `around` em várias rotas. Erros de formulário podem trazer `code`, `message` e uma árvore detalhada `errors`, portanto o cliente deve preservar status, código, rota, método e detalhes.

O changelog de 12/08/2026 anunciou obfuscação de canais para usuários e bots. Em HTTP, `GET /guilds/{guild.id}/channels` passará a omitir canais sem `VIEW_CHANNEL` a partir de 16/11/2026; no Gateway, canais podem ter metadados obfuscados, a flag `CHANNEL_OBFUSCATED` e um overwrite negando `VIEW_CHANNEL`. O changelog de 05/08/2026 tornou `channel.application_id` anulável. Também foi documentado `file_types` em File Upload components/opções `ATTACHMENT`, e `app_permissions` em canais resolvidos de interações.

Esses itens devem orientar uma próxima rodada de modelos, cache e interações. Eles não são considerados implementados apenas por estarem documentados aqui.

## Matriz local já coberta

No código local já existem rotas para onboarding, Soundboard, role-connections metadata, Widget, prune, vanity URL, Voice States/Resource, SKUs, assinaturas, stickers multipart, paginação segura e webhooks por token. A matriz integral ainda está aberta.

Validação local no registro: 106 testes aprovados; wheel `pimcord-0.7.0-py3-none-any.whl` gerada; E2EE MLS/DAVE real ausente.

## Referências

[1]: https://docs.discord.com/developers/reference
[2]: https://docs.discord.com/developers/change-log

- [Documentação oficial — API Reference][1]
- [Documentação oficial — Change Log][2]

## Mudanças oficiais que exigem acompanhamento

A documentação oficial consultada informa que a API v10 é a versão disponível atual e que IDs Discord são snowflakes serializados como strings. A paginação segue o padrão de identificadores e parâmetros `before`, `after` e `around` em várias rotas. Erros de formulário podem trazer `code`, `message` e uma árvore detalhada `errors`, portanto o cliente deve preservar status, código, rota, método e detalhes.

O changelog de 12/08/2026 anunciou obfuscação de canais para usuários e bots. Em HTTP, `GET /guilds/{guild.id}/channels` passará a omitir canais sem `VIEW_CHANNEL` a partir de 16/11/2026; no Gateway, canais podem ter metadados obfuscados, a flag `CHANNEL_OBFUSCATED` e um overwrite negando `VIEW_CHANNEL`. O changelog de 05/08/2026 tornou `channel.application_id` anulável. Também foi documentado `file_types` em File Upload components/opções `ATTACHMENT`, e `app_permissions` em canais resolvidos de interações.

Esses itens devem orientar uma próxima rodada de modelos, cache e interações. Eles não são considerados implementados apenas por estarem documentados aqui.

## Matriz local já coberta

No código local já existem rotas para onboarding, Soundboard, role-connections metadata, Widget, prune, vanity URL, Voice States/Resource, SKUs, assinaturas, stickers multipart, paginação segura e webhooks por token. A matriz integral ainda está aberta.

Validação local no registro: 106 testes aprovados; wheel `pimcord-0.7.0-py3-none-any.whl` gerada; E2EE MLS/DAVE real ausente.

## Referências

[1]: https://docs.discord.com/developers/reference
[2]: https://docs.discord.com/developers/change-log

- [Documentação oficial — API Reference][1]
- [Documentação oficial — Change Log][2]

## Mudanças oficiais que exigem acompanhamento

A documentação oficial consultada informa que a API v10 é a versão disponível atual e que IDs Discord são snowflakes serializados como strings. A paginação segue o padrão de identificadores e parâmetros `before`, `after` e `around` em várias rotas. Erros de formulário podem trazer `code`, `message` e uma árvore detalhada `errors`, portanto o cliente deve preservar status, código, rota, método e detalhes.

O changelog de 12/08/2026 anunciou obfuscação de canais para usuários e bots. Em HTTP, `GET /guilds/{guild.id}/channels` passará a omitir canais sem `VIEW_CHANNEL` a partir de 16/11/2026; no Gateway, canais podem ter metadados obfuscados, a flag `CHANNEL_OBFUSCATED` e um overwrite negando `VIEW_CHANNEL`. O changelog de 05/08/2026 tornou `channel.application_id` anulável. Também foi documentado `file_types` em File Upload components/opções `ATTACHMENT`, e `app_permissions` em canais resolvidos de interações.

Esses itens devem orientar uma próxima rodada de modelos, cache e interações. Eles não são considerados implementados apenas por estarem documentados aqui.

## Matriz local já coberta

No código local já existem rotas para onboarding, Soundboard, role-connections metadata, Widget, prune, vanity URL, Voice States/Resource, SKUs, assinaturas, stickers multipart, paginação segura e webhooks por token. A matriz integral ainda está aberta.

Validação local no registro: 106 testes aprovados; wheel `pimcord-0.7.0-py3-none-any.whl` gerada; E2EE MLS/DAVE real ausente.

## Referências

[1]: https://docs.discord.com/developers/reference
[2]: https://docs.discord.com/developers/change-log

- [Documentação oficial — API Reference][1]
- [Documentação oficial — Change Log][2]

## Mudanças oficiais que exigem acompanhamento

A documentação oficial consultada informa que a API v10 é a versão disponível atual e que IDs Discord são snowflakes serializados como strings. A paginação segue o padrão de identificadores e parâmetros `before`, `after` e `around` em várias rotas. Erros de formulário podem trazer `code`, `message` e uma árvore detalhada `errors`, portanto o cliente deve preservar status, código, rota, método e detalhes.

O changelog de 12/08/2026 anunciou obfuscação de canais para usuários e bots. Em HTTP, `GET /guilds/{guild.id}/channels` passará a omitir canais sem `VIEW_CHANNEL` a partir de 16/11/2026; no Gateway, canais podem ter metadados obfuscados, a flag `CHANNEL_OBFUSCATED` e um overwrite negando `VIEW_CHANNEL`. O changelog de 05/08/2026 tornou `channel.application_id` anulável. Também foi documentado `file_types` em File Upload components/opções `ATTACHMENT`, e `app_permissions` em canais resolvidos de interações.

Esses itens devem orientar uma próxima rodada de modelos, cache e interações. Eles não são considerados implementados apenas por estarem documentados aqui.

## Matriz local já coberta

No código local já existem rotas para onboarding, Soundboard, role-connections metadata, Widget, prune, vanity URL, Voice States/Resource, SKUs, assinaturas, stickers multipart, paginação segura e webhooks por token. A matriz integral ainda está aberta.

Validação local no registro: 106 testes aprovados; wheel `pimcord-0.7.0-py3-none-any.whl` gerada; E2EE MLS/DAVE real ausente.

## Referências

[1]: https://docs.discord.com/developers/reference
[2]: https://docs.discord.com/developers/change-log

- [Documentação oficial — API Reference][1]
- [Documentação oficial — Change Log][2]

## Mudanças oficiais que exigem acompanhamento

A documentação oficial consultada informa que a API v10 é a versão disponível atual e que IDs Discord são snowflakes serializados como strings. A paginação segue o padrão de identificadores e parâmetros `before`, `after` e `around` em várias rotas. Erros de formulário podem trazer `code`, `message` e uma árvore detalhada `errors`, portanto o cliente deve preservar status, código, rota, método e detalhes.

O changelog de 12/08/2026 anunciou obfuscação de canais para usuários e bots. Em HTTP, `GET /guilds/{guild.id}/channels` passará a omitir canais sem `VIEW_CHANNEL` a partir de 16/11/2026; no Gateway, canais podem ter metadados obfuscados, a flag `CHANNEL_OBFUSCATED` e um overwrite negando `VIEW_CHANNEL`. O changelog de 05/08/2026 tornou `channel.application_id` anulável. Também foi documentado `file_types` em File Upload components/opções `ATTACHMENT`, e `app_permissions` em canais resolvidos de interações.

Esses itens devem orientar uma próxima rodada de modelos, cache e interações. Eles não são considerados implementados apenas por estarem documentados aqui.

## Matriz local já coberta

No código local já existem rotas para onboarding, Soundboard, role-connections metadata, Widget, prune, vanity URL, Voice States/Resource, SKUs, assinaturas, stickers multipart, paginação segura e webhooks por token. A matriz integral ainda está aberta.

Validação local no registro: 106 testes aprovados; wheel `pimcord-0.7.0-py3-none-any.whl` gerada; E2EE MLS/DAVE real ausente.

## Referências

[1]: https://docs.discord.com/developers/reference
[2]: https://docs.discord.com/developers/change-log

- [Documentação oficial — API Reference][1]
- [Documentação oficial — Change Log][2]

## Mudanças oficiais que exigem acompanhamento

A documentação oficial consultada informa que a API v10 é a versão disponível atual e que IDs Discord são snowflakes serializados como strings. A paginação segue o padrão de identificadores e parâmetros `before`, `after` e `around` em várias rotas. Erros de formulário podem trazer `code`, `message` e uma árvore detalhada `errors`, portanto o cliente deve preservar status, código, rota, método e detalhes.

O changelog de 12/08/2026 anunciou obfuscação de canais para usuários e bots. Em HTTP, `GET /guilds/{guild.id}/channels` passará a omitir canais sem `VIEW_CHANNEL` a partir de 16/11/2026; no Gateway, canais podem ter metadados obfuscados, a flag `CHANNEL_OBFUSCATED` e um overwrite negando `VIEW_CHANNEL`. O changelog de 05/08/2026 tornou `channel.application_id` anulável. Também foi documentado `file_types` em File Upload components/opções `ATTACHMENT`, e `app_permissions` em canais resolvidos de interações.

Esses itens devem orientar uma próxima rodada de modelos, cache e interações. Eles não são considerados implementados apenas por estarem documentados aqui.

## Matriz local já coberta

No código local já existem rotas para onboarding, Soundboard, role-connections metadata, Widget, prune, vanity URL, Voice States/Resource, SKUs, assinaturas, stickers multipart, paginação segura e webhooks por token. A matriz integral ainda está aberta.

Validação local no registro: 106 testes aprovados; wheel `pimcord-0.7.0-py3-none-any.whl` gerada; E2EE MLS/DAVE real ausente.

## Referências

[1]: https://docs.discord.com/developers/reference
[2]: https://docs.discord.com/developers/change-log

- [Documentação oficial — API Reference][1]
- [Documentação oficial — Change Log][2]

## Mudanças oficiais que exigem acompanhamento

A documentação oficial consultada informa que a API v10 é a versão disponível atual e que IDs Discord são snowflakes serializados como strings. A paginação segue o padrão de identificadores e parâmetros `before`, `after` e `around` em várias rotas. Erros de formulário podem trazer `code`, `message` e uma árvore detalhada `errors`, portanto o cliente deve preservar status, código, rota, método e detalhes.

O changelog de 12/08/2026 anunciou obfuscação de canais para usuários e bots. Em HTTP, `GET /guilds/{guild.id}/channels` passará a omitir canais sem `VIEW_CHANNEL` a partir de 16/11/2026; no Gateway, canais podem ter metadados obfuscados, a flag `CHANNEL_OBFUSCATED` e um overwrite negando `VIEW_CHANNEL`. O changelog de 05/08/2026 tornou `channel.application_id` anulável. Também foi documentado `file_types` em File Upload components/opções `ATTACHMENT`, e `app_permissions` em canais resolvidos de interações.

Esses itens devem orientar uma próxima rodada de modelos, cache e interações. Eles não são considerados implementados apenas por estarem documentados aqui.

## Matriz local já coberta

No código local já existem rotas para onboarding, Soundboard, role-connections metadata, Widget, prune, vanity URL, Voice States/Resource, SKUs, assinaturas, stickers multipart, paginação segura e webhooks por token. A matriz integral ainda está aberta.

Validação local no registro: 106 testes aprovados; wheel `pimcord-0.7.0-py3-none-any.whl` gerada; E2EE MLS/DAVE real ausente.

## Referências

[1]: https://docs.discord.com/developers/reference
[2]: https://docs.discord.com/developers/change-log

- [Documentação oficial — API Reference][1]
- [Documentação oficial — Change Log][2]

## Mudanças oficiais que exigem acompanhamento

A documentação oficial consultada informa que a API v10 é a versão disponível atual e que IDs Discord são snowflakes serializados como strings. A paginação segue o padrão de identificadores e parâmetros `before`, `after` e `around` em várias rotas. Erros de formulário podem trazer `code`, `message` e uma árvore detalhada `errors`, portanto o cliente deve preservar status, código, rota, método e detalhes.

O changelog de 12/08/2026 anunciou obfuscação de canais para usuários e bots. Em HTTP, `GET /guilds/{guild.id}/channels` passará a omitir canais sem `VIEW_CHANNEL` a partir de 16/11/2026; no Gateway, canais podem ter metadados obfuscados, a flag `CHANNEL_OBFUSCATED` e um overwrite negando `VIEW_CHANNEL`. O changelog de 05/08/2026 tornou `channel.application_id` anulável. Também foi documentado `file_types` em File Upload components/opções `ATTACHMENT`, e `app_permissions` em canais resolvidos de interações.

Esses itens devem orientar uma próxima rodada de modelos, cache e interações. Eles não são considerados implementados apenas por estarem documentados aqui.

## Matriz local já coberta

No código local já existem rotas para onboarding, Soundboard, role-connections metadata, Widget, prune, vanity URL, Voice States/Resource, SKUs, assinaturas, stickers multipart, paginação segura e webhooks por token. A matriz integral ainda está aberta.

Validação local no registro: 106 testes aprovados; wheel `pimcord-0.7.0-py3-none-any.whl` gerada; E2EE MLS/DAVE real ausente.

## Referências

[1]: https://docs.discord.com/developers/reference
[2]: https://docs.discord.com/developers/change-log

- [Documentação oficial — API Reference][1]
- [Documentação oficial — Change Log][2]

## Mudanças oficiais que exigem acompanhamento

A documentação oficial consultada informa que a API v10 é a versão disponível atual e que IDs Discord são snowflakes serializados como strings. A paginação segue o padrão de identificadores e parâmetros `before`, `after` e `around` em várias rotas. Erros de formulário podem trazer `code`, `message` e uma árvore detalhada `errors`, portanto o cliente deve preservar status, código, rota, método e detalhes.

O changelog de 12/08/2026 anunciou obfuscação de canais para usuários e bots. Em HTTP, `GET /guilds/{guild.id}/channels` passará a omitir canais sem `VIEW_CHANNEL` a partir de 16/11/2026; no Gateway, canais podem ter metadados obfuscados, a flag `CHANNEL_OBFUSCATED` e um overwrite negando `VIEW_CHANNEL`. O changelog de 05/08/2026 tornou `channel.application_id` anulável. Também foi documentado `file_types` em File Upload components/opções `ATTACHMENT`, e `app_permissions` em canais resolvidos de interações.

Esses itens devem orientar uma próxima rodada de modelos, cache e interações. Eles não são considerados implementados apenas por estarem documentados aqui.

## Matriz local já coberta

No código local já existem rotas para onboarding, Soundboard, role-connections metadata, Widget, prune, vanity URL, Voice States/Resource, SKUs, assinaturas, stickers multipart, paginação segura e webhooks por token. A matriz integral ainda está aberta.

Validação local no registro: 106 testes aprovados; wheel `pimcord-0.7.0-py3-none-any.whl` gerada; E2EE MLS/DAVE real ausente.

## Referências

[1]: https://docs.discord.com/developers/reference
[2]: https://docs.discord.com/developers/change-log

- [Documentação oficial — API Reference][1]
- [Documentação oficial — Change Log][2]

## Mudanças oficiais que exigem acompanhamento

A documentação oficial consultada informa que a API v10 é a versão disponível atual e que IDs Discord são snowflakes serializados como strings. A paginação segue o padrão de identificadores e parâmetros `before`, `after` e `around` em várias rotas. Erros de formulário podem trazer `code`, `message` e uma árvore detalhada `errors`, portanto o cliente deve preservar status, código, rota, método e detalhes.

O changelog de 12/08/2026 anunciou obfuscação de canais para usuários e bots. Em HTTP, `GET /guilds/{guild.id}/channels` passará a omitir canais sem `VIEW_CHANNEL` a partir de 16/11/2026; no Gateway, canais podem ter metadados obfuscados, a flag `CHANNEL_OBFUSCATED` e um overwrite negando `VIEW_CHANNEL`. O changelog de 05/08/2026 tornou `channel.application_id` anulável. Também foi documentado `file_types` em File Upload components/opções `ATTACHMENT`, e `app_permissions` em canais resolvidos de interações.

Esses itens devem orientar uma próxima rodada de modelos, cache e interações. Eles não são considerados implementados apenas por estarem documentados aqui.

## Matriz local já coberta

No código local já existem rotas para onboarding, Soundboard, role-connections metadata, Widget, prune, vanity URL, Voice States/Resource, SKUs, assinaturas, stickers multipart, paginação segura e webhooks por token. A matriz integral ainda está aberta.

Validação local no registro: 106 testes aprovados; wheel `pimcord-0.7.0-py3-none-any.whl` gerada; E2EE MLS/DAVE real ausente.

## Referências

[1]: https://docs.discord.com/developers/reference
[2]: https://docs.discord.com/developers/change-log

- [Documentação oficial — API Reference][1]
- [Documentação oficial — Change Log][2]

## Mudanças oficiais que exigem acompanhamento

A documentação oficial consultada informa que a API v10 é a versão disponível atual e que IDs Discord são snowflakes serializados como strings. A paginação segue o padrão de identificadores e parâmetros `before`, `after` e `around` em várias rotas. Erros de formulário podem trazer `code`, `message` e uma árvore detalhada `errors`, portanto o cliente deve preservar status, código, rota, método e detalhes.

O changelog de 12/08/2026 anunciou obfuscação de canais para usuários e bots. Em HTTP, `GET /guilds/{guild.id}/channels` passará a omitir canais sem `VIEW_CHANNEL` a partir de 16/11/2026; no Gateway, canais podem ter metadados obfuscados, a flag `CHANNEL_OBFUSCATED` e um overwrite negando `VIEW_CHANNEL`. O changelog de 05/08/2026 tornou `channel.application_id` anulável. Também foi documentado `file_types` em File Upload components/opções `ATTACHMENT`, e `app_permissions` em canais resolvidos de interações.

Esses itens devem orientar uma próxima rodada de modelos, cache e interações. Eles não são considerados implementados apenas por estarem documentados aqui.

## Matriz local já coberta

No código local já existem rotas para onboarding, Soundboard, role-connections metadata, Widget, prune, vanity URL, Voice States/Resource, SKUs, assinaturas, stickers multipart, paginação segura e webhooks por token. A matriz integral ainda está aberta.

Validação local no registro: 106 testes aprovados; wheel `pimcord-0.7.0-py3-none-any.whl` gerada; E2EE MLS/DAVE real ausente.

## Referências

[1]: https://docs.discord.com/developers/reference
[2]: https://docs.discord.com/developers/change-log

- [Documentação oficial — API Reference][1]
- [Documentação oficial — Change Log][2]

## Mudanças oficiais que exigem acompanhamento

A documentação oficial consultada informa que a API v10 é a versão disponível atual e que IDs Discord são snowflakes serializados como strings. A paginação segue o padrão de identificadores e parâmetros `before`, `after` e `around` em várias rotas. Erros de formulário podem trazer `code`, `message` e uma árvore detalhada `errors`, portanto o cliente deve preservar status, código, rota, método e detalhes.

O changelog de 12/08/2026 anunciou obfuscação de canais para usuários e bots. Em HTTP, `GET /guilds/{guild.id}/channels` passará a omitir canais sem `VIEW_CHANNEL` a partir de 16/11/2026; no Gateway, canais podem ter metadados obfuscados, a flag `CHANNEL_OBFUSCATED` e um overwrite negando `VIEW_CHANNEL`. O changelog de 05/08/2026 tornou `channel.application_id` anulável. Também foi documentado `file_types` em File Upload components/opções `ATTACHMENT`, e `app_permissions` em canais resolvidos de interações.

Esses itens devem orientar uma próxima rodada de modelos, cache e interações. Eles não são considerados implementados apenas por estarem documentados aqui.

## Matriz local já coberta

No código local já existem rotas para onboarding, Soundboard, role-connections metadata, Widget, prune, vanity URL, Voice States/Resource, SKUs, assinaturas, stickers multipart, paginação segura e webhooks por token. A matriz integral ainda está aberta.

Validação local no registro: 106 testes aprovados; wheel `pimcord-0.7.0-py3-none-any.whl` gerada; E2EE MLS/DAVE real ausente.

## Referências

[1]: https://docs.discord.com/developers/reference
[2]: https://docs.discord.com/developers/change-log

- [Documentação oficial — API Reference][1]
- [Documentação oficial — Change Log][2]

## Mudanças oficiais que exigem acompanhamento

A documentação oficial consultada informa que a API v10 é a versão disponível atual e que IDs Discord são snowflakes serializados como strings. A paginação segue o padrão de identificadores e parâmetros `before`, `after` e `around` em várias rotas. Erros de formulário podem trazer `code`, `message` e uma árvore detalhada `errors`, portanto o cliente deve preservar status, código, rota, método e detalhes.

O changelog de 12/08/2026 anunciou obfuscação de canais para usuários e bots. Em HTTP, `GET /guilds/{guild.id}/channels` passará a omitir canais sem `VIEW_CHANNEL` a partir de 16/11/2026; no Gateway, canais podem ter metadados obfuscados, a flag `CHANNEL_OBFUSCATED` e um overwrite negando `VIEW_CHANNEL`. O changelog de 05/08/2026 tornou `channel.application_id` anulável. Também foi documentado `file_types` em File Upload components/opções `ATTACHMENT`, e `app_permissions` em canais resolvidos de interações.

Esses itens devem orientar uma próxima rodada de modelos, cache e interações. Eles não são considerados implementados apenas por estarem documentados aqui.

## Matriz local já coberta

No código local já existem rotas para onboarding, Soundboard, role-connections metadata, Widget, prune, vanity URL, Voice States/Resource, SKUs, assinaturas, stickers multipart, paginação segura e webhooks por token. A matriz integral ainda está aberta.

Validação local no registro: 106 testes aprovados; wheel `pimcord-0.7.0-py3-none-any.whl` gerada; E2EE MLS/DAVE real ausente.

## Referências

[1]: https://docs.discord.com/developers/reference
[2]: https://docs.discord.com/developers/change-log

- [Documentação oficial — API Reference][1]
- [Documentação oficial — Change Log][2]

## Mudanças oficiais que exigem acompanhamento

A documentação oficial consultada informa que a API v10 é a versão disponível atual e que IDs Discord são snowflakes serializados como strings. A paginação segue o padrão de identificadores e parâmetros `before`, `after` e `around` em várias rotas. Erros de formulário podem trazer `code`, `message` e uma árvore detalhada `errors`, portanto o cliente deve preservar status, código, rota, método e detalhes.

O changelog de 12/08/2026 anunciou obfuscação de canais para usuários e bots. Em HTTP, `GET /guilds/{guild.id}/channels` passará a omitir canais sem `VIEW_CHANNEL` a partir de 16/11/2026; no Gateway, canais podem ter metadados obfuscados, a flag `CHANNEL_OBFUSCATED` e um overwrite negando `VIEW_CHANNEL`. O changelog de 05/08/2026 tornou `channel.application_id` anulável. Também foi documentado `file_types` em File Upload components/opções `ATTACHMENT`, e `app_permissions` em canais resolvidos de interações.

Esses itens devem orientar uma próxima rodada de modelos, cache e interações. Eles não são considerados implementados apenas por estarem documentados aqui.

## Matriz local já coberta

No código local já existem rotas para onboarding, Soundboard, role-connections metadata, Widget, prune, vanity URL, Voice States/Resource, SKUs, assinaturas, stickers multipart, paginação segura e webhooks por token. A matriz integral ainda está aberta.

Validação local no registro: 106 testes aprovados; wheel `pimcord-0.7.0-py3-none-any.whl` gerada; E2EE MLS/DAVE real ausente.

## Referências

[1]: https://docs.discord.com/developers/reference
[2]: https://docs.discord.com/developers/change-log

- [Documentação oficial — API Reference][1]
- [Documentação oficial — Change Log][2]

## Mudanças oficiais que exigem acompanhamento

A documentação oficial consultada informa que a API v10 é a versão disponível atual e que IDs Discord são snowflakes serializados como strings. A paginação segue o padrão de identificadores e parâmetros `before`, `after` e `around` em várias rotas. Erros de formulário podem trazer `code`, `message` e uma árvore detalhada `errors`, portanto o cliente deve preservar status, código, rota, método e detalhes.

O changelog de 12/08/2026 anunciou obfuscação de canais para usuários e bots. Em HTTP, `GET /guilds/{guild.id}/channels` passará a omitir canais sem `VIEW_CHANNEL` a partir de 16/11/2026; no Gateway, canais podem ter metadados obfuscados, a flag `CHANNEL_OBFUSCATED` e um overwrite negando `VIEW_CHANNEL`. O changelog de 05/08/2026 tornou `channel.application_id` anulável. Também foi documentado `file_types` em File Upload components/opções `ATTACHMENT`, e `app_permissions` em canais resolvidos de interações.

Esses itens devem orientar uma próxima rodada de modelos, cache e interações. Eles não são considerados implementados apenas por estarem documentados aqui.

## Matriz local já coberta

No código local já existem rotas para onboarding, Soundboard, role-connections metadata, Widget, prune, vanity URL, Voice States/Resource, SKUs, assinaturas, stickers multipart, paginação segura e webhooks por token. A matriz integral ainda está aberta.

Validação local no registro: 106 testes aprovados; wheel `pimcord-0.7.0-py3-none-any.whl` gerada; E2EE MLS/DAVE real ausente.

## Referências

[1]: https://docs.discord.com/developers/reference
[2]: https://docs.discord.com/developers/change-log

- [Documentação oficial — API Reference][1]
- [Documentação oficial — Change Log][2]

## Mudanças oficiais que exigem acompanhamento

A documentação oficial consultada informa que a API v10 é a versão disponível atual e que IDs Discord são snowflakes serializados como strings. A paginação segue o padrão de identificadores e parâmetros `before`, `after` e `around` em várias rotas. Erros de formulário podem trazer `code`, `message` e uma árvore detalhada `errors`, portanto o cliente deve preservar status, código, rota, método e detalhes.

O changelog de 12/08/2026 anunciou obfuscação de canais para usuários e bots. Em HTTP, `GET /guilds/{guild.id}/channels` passará a omitir canais sem `VIEW_CHANNEL` a partir de 16/11/2026; no Gateway, canais podem ter metadados obfuscados, a flag `CHANNEL_OBFUSCATED` e um overwrite negando `VIEW_CHANNEL`. O changelog de 05/08/2026 tornou `channel.application_id` anulável. Também foi documentado `file_types` em File Upload components/opções `ATTACHMENT`, e `app_permissions` em canais resolvidos de interações.

Esses itens devem orientar uma próxima rodada de modelos, cache e interações. Eles não são considerados implementados apenas por estarem documentados aqui.

## Matriz local já coberta

No código local já existem rotas para onboarding, Soundboard, role-connections metadata, Widget, prune, vanity URL, Voice States/Resource, SKUs, assinaturas, stickers multipart, paginação segura e webhooks por token. A matriz integral ainda está aberta.

Validação local no registro: 106 testes aprovados; wheel `pimcord-0.7.0-py3-none-any.whl` gerada; E2EE MLS/DAVE real ausente.

## Referências

[1]: https://docs.discord.com/developers/reference
[2]: https://docs.discord.com/developers/change-log

- [Documentação oficial — API Reference][1]
- [Documentação oficial — Change Log][2]

## Mudanças oficiais que exigem acompanhamento

A documentação oficial consultada informa que a API v10 é a versão disponível atual e que IDs Discord são snowflakes serializados como strings. A paginação segue o padrão de identificadores e parâmetros `before`, `after` e `around` em várias rotas. Erros de formulário podem trazer `code`, `message` e uma árvore detalhada `errors`, portanto o cliente deve preservar status, código, rota, método e detalhes.

O changelog de 12/08/2026 anunciou obfuscação de canais para usuários e bots. Em HTTP, `GET /guilds/{guild.id}/channels` passará a omitir canais sem `VIEW_CHANNEL` a partir de 16/11/2026; no Gateway, canais podem ter metadados obfuscados, a flag `CHANNEL_OBFUSCATED` e um overwrite negando `VIEW_CHANNEL`. O changelog de 05/08/2026 tornou `channel.application_id` anulável. Também foi documentado `file_types` em File Upload components/opções `ATTACHMENT`, e `app_permissions` em canais resolvidos de interações.

Esses itens devem orientar uma próxima rodada de modelos, cache e interações. Eles não são considerados implementados apenas por estarem documentados aqui.

## Matriz local já coberta

No código local já existem rotas para onboarding, Soundboard, role-connections metadata, Widget, prune, vanity URL, Voice States/Resource, SKUs, assinaturas, stickers multipart, paginação segura e webhooks por token. A matriz integral ainda está aberta.

Validação local no registro: 106 testes aprovados; wheel `pimcord-0.7.0-py3-none-any.whl` gerada; E2EE MLS/DAVE real ausente.

## Referências

[1]: https://docs.discord.com/developers/reference
[2]: https://docs.discord.com/developers/change-log

- [Documentação oficial — API Reference][1]
- [Documentação oficial — Change Log][2]

## Mudanças oficiais que exigem acompanhamento

A documentação oficial consultada informa que a API v10 é a versão disponível atual e que IDs Discord são snowflakes serializados como strings. A paginação segue o padrão de identificadores e parâmetros `before`, `after` e `around` em várias rotas. Erros de formulário podem trazer `code`, `message` e uma árvore detalhada `errors`, portanto o cliente deve preservar status, código, rota, método e detalhes.

O changelog de 12/08/2026 anunciou obfuscação de canais para usuários e bots. Em HTTP, `GET /guilds/{guild.id}/channels` passará a omitir canais sem `VIEW_CHANNEL` a partir de 16/11/2026; no Gateway, canais podem ter metadados obfuscados, a flag `CHANNEL_OBFUSCATED` e um overwrite negando `VIEW_CHANNEL`. O changelog de 05/08/2026 tornou `channel.application_id` anulável. Também foi documentado `file_types` em File Upload components/opções `ATTACHMENT`, e `app_permissions` em canais resolvidos de interações.

Esses itens devem orientar uma próxima rodada de modelos, cache e interações. Eles não são considerados implementados apenas por estarem documentados aqui.

## Matriz local já coberta

No código local já existem rotas para onboarding, Soundboard, role-connections metadata, Widget, prune, vanity URL, Voice States/Resource, SKUs, assinaturas, stickers multipart, paginação segura e webhooks por token. A matriz integral ainda está aberta.

Validação local no registro: 106 testes aprovados; wheel `pimcord-0.7.0-py3-none-any.whl` gerada; E2EE MLS/DAVE real ausente.

## Referências

[1]: https://docs.discord.com/developers/reference
[2]: https://docs.discord.com/developers/change-log

- [Documentação oficial — API Reference][1]
- [Documentação oficial — Change Log][2]

## Mudanças oficiais que exigem acompanhamento

A documentação oficial consultada informa que a API v10 é a versão disponível atual e que IDs Discord são snowflakes serializados como strings. A paginação segue o padrão de identificadores e parâmetros `before`, `after` e `around` em várias rotas. Erros de formulário podem trazer `code`, `message` e uma árvore detalhada `errors`, portanto o cliente deve preservar status, código, rota, método e detalhes.

O changelog de 12/08/2026 anunciou obfuscação de canais para usuários e bots. Em HTTP, `GET /guilds/{guild.id}/channels` passará a omitir canais sem `VIEW_CHANNEL` a partir de 16/11/2026; no Gateway, canais podem ter metadados obfuscados, a flag `CHANNEL_OBFUSCATED` e um overwrite negando `VIEW_CHANNEL`. O changelog de 05/08/2026 tornou `channel.application_id` anulável. Também foi documentado `file_types` em File Upload components/opções `ATTACHMENT`, e `app_permissions` em canais resolvidos de interações.

Esses itens devem orientar uma próxima rodada de modelos, cache e interações. Eles não são considerados implementados apenas por estarem documentados aqui.

## Matriz local já coberta

No código local já existem rotas para onboarding, Soundboard, role-connections metadata, Widget, prune, vanity URL, Voice States/Resource, SKUs, assinaturas, stickers multipart, paginação segura e webhooks por token. A matriz integral ainda está aberta.

Validação local no registro: 106 testes aprovados; wheel `pimcord-0.7.0-py3-none-any.whl` gerada; E2EE MLS/DAVE real ausente.

## Referências

[1]: https://docs.discord.com/developers/reference
[2]: https://docs.discord.com/developers/change-log

- [Documentação oficial — API Reference][1]
- [Documentação oficial — Change Log][2]

## Mudanças oficiais que exigem acompanhamento

A documentação oficial consultada informa que a API v10 é a versão disponível atual e que IDs Discord são snowflakes serializados como strings. A paginação segue o padrão de identificadores e parâmetros `before`, `after` e `around` em várias rotas. Erros de formulário podem trazer `code`, `message` e uma árvore detalhada `errors`, portanto o cliente deve preservar status, código, rota, método e detalhes.

O changelog de 12/08/2026 anunciou obfuscação de canais para usuários e bots. Em HTTP, `GET /guilds/{guild.id}/channels` passará a omitir canais sem `VIEW_CHANNEL` a partir de 16/11/2026; no Gateway, canais podem ter metadados obfuscados, a flag `CHANNEL_OBFUSCATED` e um overwrite negando `VIEW_CHANNEL`. O changelog de 05/08/2026 tornou `channel.application_id` anulável. Também foi documentado `file_types` em File Upload components/opções `ATTACHMENT`, e `app_permissions` em canais resolvidos de interações.

Esses itens devem orientar uma próxima rodada de modelos, cache e interações. Eles não são considerados implementados apenas por estarem documentados aqui.

## Matriz local já coberta

No código local já existem rotas para onboarding, Soundboard, role-connections metadata, Widget, prune, vanity URL, Voice States/Resource, SKUs, assinaturas, stickers multipart, paginação segura e webhooks por token. A matriz integral ainda está aberta.

Validação local no registro: 106 testes aprovados; wheel `pimcord-0.7.0-py3-none-any.whl` gerada; E2EE MLS/DAVE real ausente.

## Referências

[1]: https://docs.discord.com/developers/reference
[2]: https://docs.discord.com/developers/change-log

- [Documentação oficial — API Reference][1]
- [Documentação oficial — Change Log][2]

## Mudanças oficiais que exigem acompanhamento

A documentação oficial consultada informa que a API v10 é a versão disponível atual e que IDs Discord são snowflakes serializados como strings. A paginação segue o padrão de identificadores e parâmetros `before`, `after` e `around` em várias rotas. Erros de formulário podem trazer `code`, `message` e uma árvore detalhada `errors`, portanto o cliente deve preservar status, código, rota, método e detalhes.

O changelog de 12/08/2026 anunciou obfuscação de canais para usuários e bots. Em HTTP, `GET /guilds/{guild.id}/channels` passará a omitir canais sem `VIEW_CHANNEL` a partir de 16/11/2026; no Gateway, canais podem ter metadados obfuscados, a flag `CHANNEL_OBFUSCATED` e um overwrite negando `VIEW_CHANNEL`. O changelog de 05/08/2026 tornou `channel.application_id` anulável. Também foi documentado `file_types` em File Upload components/opções `ATTACHMENT`, e `app_permissions` em canais resolvidos de interações.

Esses itens devem orientar uma próxima rodada de modelos, cache e interações. Eles não são considerados implementados apenas por estarem documentados aqui.

## Matriz local já coberta

No código local já existem rotas para onboarding, Soundboard, role-connections metadata, Widget, prune, vanity URL, Voice States/Resource, SKUs, assinaturas, stickers multipart, paginação segura e webhooks por token. A matriz integral ainda está aberta.

Validação local no registro: 106 testes aprovados; wheel `pimcord-0.7.0-py3-none-any.whl` gerada; E2EE MLS/DAVE real ausente.

## Referências

[1]: https://docs.discord.com/developers/reference
[2]: https://docs.discord.com/developers/change-log

- [Documentação oficial — API Reference][1]
- [Documentação oficial — Change Log][2]

## Mudanças oficiais que exigem acompanhamento

A documentação oficial consultada informa que a API v10 é a versão disponível atual e que IDs Discord são snowflakes serializados como strings. A paginação segue o padrão de identificadores e parâmetros `before`, `after` e `around` em várias rotas. Erros de formulário podem trazer `code`, `message` e uma árvore detalhada `errors`, portanto o cliente deve preservar status, código, rota, método e detalhes.

O changelog de 12/08/2026 anunciou obfuscação de canais para usuários e bots. Em HTTP, `GET /guilds/{guild.id}/channels` passará a omitir canais sem `VIEW_CHANNEL` a partir de 16/11/2026; no Gateway, canais podem ter metadados obfuscados, a flag `CHANNEL_OBFUSCATED` e um overwrite negando `VIEW_CHANNEL`. O changelog de 05/08/2026 tornou `channel.application_id` anulável. Também foi documentado `file_types` em File Upload components/opções `ATTACHMENT`, e `app_permissions` em canais resolvidos de interações.

Esses itens devem orientar uma próxima rodada de modelos, cache e interações. Eles não são considerados implementados apenas por estarem documentados aqui.

## Matriz local já coberta

No código local já existem rotas para onboarding, Soundboard, role-connections metadata, Widget, prune, vanity URL, Voice States/Resource, SKUs, assinaturas, stickers multipart, paginação segura e webhooks por token. A matriz integral ainda está aberta.

Validação local no registro: 106 testes aprovados; wheel `pimcord-0.7.0-py3-none-any.whl` gerada; E2EE MLS/DAVE real ausente.

## Referências

[1]: https://docs.discord.com/developers/reference
[2]: https://docs.discord.com/developers/change-log

- [Documentação oficial — API Reference][1]
- [Documentação oficial — Change Log][2]

## Mudanças oficiais que exigem acompanhamento

A documentação oficial consultada informa que a API v10 é a versão disponível atual e que IDs Discord são snowflakes serializados como strings. A paginação segue o padrão de identificadores e parâmetros `before`, `after` e `around` em várias rotas. Erros de formulário podem trazer `code`, `message` e uma árvore detalhada `errors`, portanto o cliente deve preservar status, código, rota, método e detalhes.

O changelog de 12/08/2026 anunciou obfuscação de canais para usuários e bots. Em HTTP, `GET /guilds/{guild.id}/channels` passará a omitir canais sem `VIEW_CHANNEL` a partir de 16/11/2026; no Gateway, canais podem ter metadados obfuscados, a flag `CHANNEL_OBFUSCATED` e um overwrite negando `VIEW_CHANNEL`. O changelog de 05/08/2026 tornou `channel.application_id` anulável. Também foi documentado `file_types` em File Upload components/opções `ATTACHMENT`, e `app_permissions` em canais resolvidos de interações.

Esses itens devem orientar uma próxima rodada de modelos, cache e interações. Eles não são considerados implementados apenas por estarem documentados aqui.

## Matriz local já coberta

No código local já existem rotas para onboarding, Soundboard, role-connections metadata, Widget, prune, vanity URL, Voice States/Resource, SKUs, assinaturas, stickers multipart, paginação segura e webhooks por token. A matriz integral ainda está aberta.

Validação local no registro: 106 testes aprovados; wheel `pimcord-0.7.0-py3-none-any.whl` gerada; E2EE MLS/DAVE real ausente.

## Referências

[1]: https://docs.discord.com/developers/reference
[2]: https://docs.discord.com/developers/change-log

- [Documentação oficial — API Reference][1]
- [Documentação oficial — Change Log][2]

## Mudanças oficiais que exigem acompanhamento

A documentação oficial consultada informa que a API v10 é a versão disponível atual e que IDs Discord são snowflakes serializados como strings. A paginação segue o padrão de identificadores e parâmetros `before`, `after` e `around` em várias rotas. Erros de formulário podem trazer `code`, `message` e uma árvore detalhada `errors`, portanto o cliente deve preservar status, código, rota, método e detalhes.

O changelog de 12/08/2026 anunciou obfuscação de canais para usuários e bots. Em HTTP, `GET /guilds/{guild.id}/channels` passará a omitir canais sem `VIEW_CHANNEL` a partir de 16/11/2026; no Gateway, canais podem ter metadados obfuscados, a flag `CHANNEL_OBFUSCATED` e um overwrite negando `VIEW_CHANNEL`. O changelog de 05/08/2026 tornou `channel.application_id` anulável. Também foi documentado `file_types` em File Upload components/opções `ATTACHMENT`, e `app_permissions` em canais resolvidos de interações.

Esses itens devem orientar uma próxima rodada de modelos, cache e interações. Eles não são considerados implementados apenas por estarem documentados aqui.

## Matriz local já coberta

No código local já existem rotas para onboarding, Soundboard, role-connections metadata, Widget, prune, vanity URL, Voice States/Resource, SKUs, assinaturas, stickers multipart, paginação segura e webhooks por token. A matriz integral ainda está aberta.

Validação local no registro: 106 testes aprovados; wheel `pimcord-0.7.0-py3-none-any.whl` gerada; E2EE MLS/DAVE real ausente.

## Referências

[1]: https://docs.discord.com/developers/reference
[2]: https://docs.discord.com/developers/change-log

- [Documentação oficial — API Reference][1]
- [Documentação oficial — Change Log][2]

## Mudanças oficiais que exigem acompanhamento

A documentação oficial consultada informa que a API v10 é a versão disponível atual e que IDs Discord são snowflakes serializados como strings. A paginação segue o padrão de identificadores e parâmetros `before`, `after` e `around` em várias rotas. Erros de formulário podem trazer `code`, `message` e uma árvore detalhada `errors`, portanto o cliente deve preservar status, código, rota, método e detalhes.

O changelog de 12/08/2026 anunciou obfuscação de canais para usuários e bots. Em HTTP, `GET /guilds/{guild.id}/channels` passará a omitir canais sem `VIEW_CHANNEL` a partir de 16/11/2026; no Gateway, canais podem ter metadados obfuscados, a flag `CHANNEL_OBFUSCATED` e um overwrite negando `VIEW_CHANNEL`. O changelog de 05/08/2026 tornou `channel.application_id` anulável. Também foi documentado `file_types` em File Upload components/opções `ATTACHMENT`, e `app_permissions` em canais resolvidos de interações.

Esses itens devem orientar uma próxima rodada de modelos, cache e interações. Eles não são considerados implementados apenas por estarem documentados aqui.

## Matriz local já coberta

No código local já existem rotas para onboarding, Soundboard, role-connections metadata, Widget, prune, vanity URL, Voice States/Resource, SKUs, assinaturas, stickers multipart, paginação segura e webhooks por token. A matriz integral ainda está aberta.

Validação local no registro: 106 testes aprovados; wheel `pimcord-0.7.0-py3-none-any.whl` gerada; E2EE MLS/DAVE real ausente.

## Referências

[1]: https://docs.discord.com/developers/reference
[2]: https://docs.discord.com/developers/change-log

- [Documentação oficial — API Reference][1]
- [Documentação oficial — Change Log][2]

## Mudanças oficiais que exigem acompanhamento

A documentação oficial consultada informa que a API v10 é a versão disponível atual e que IDs Discord são snowflakes serializados como strings. A paginação segue o padrão de identificadores e parâmetros `before`, `after` e `around` em várias rotas. Erros de formulário podem trazer `code`, `message` e uma árvore detalhada `errors`, portanto o cliente deve preservar status, código, rota, método e detalhes.

O changelog de 12/08/2026 anunciou obfuscação de canais para usuários e bots. Em HTTP, `GET /guilds/{guild.id}/channels` passará a omitir canais sem `VIEW_CHANNEL` a partir de 16/11/2026; no Gateway, canais podem ter metadados obfuscados, a flag `CHANNEL_OBFUSCATED` e um overwrite negando `VIEW_CHANNEL`. O changelog de 05/08/2026 tornou `channel.application_id` anulável. Também foi documentado `file_types` em File Upload components/opções `ATTACHMENT`, e `app_permissions` em canais resolvidos de interações.

Esses itens devem orientar uma próxima rodada de modelos, cache e interações. Eles não são considerados implementados apenas por estarem documentados aqui.

## Matriz local já coberta

No código local já existem rotas para onboarding, Soundboard, role-connections metadata, Widget, prune, vanity URL, Voice States/Resource, SKUs, assinaturas, stickers multipart, paginação segura e webhooks por token. A matriz integral ainda está aberta.

Validação local no registro: 106 testes aprovados; wheel `pimcord-0.7.0-py3-none-any.whl` gerada; E2EE MLS/DAVE real ausente.

## Referências

[1]: https://docs.discord.com/developers/reference
[2]: https://docs.discord.com/developers/change-log

- [Documentação oficial — API Reference][1]
- [Documentação oficial — Change Log][2]

## Mudanças oficiais que exigem acompanhamento

A documentação oficial consultada informa que a API v10 é a versão disponível atual e que IDs Discord são snowflakes serializados como strings. A paginação segue o padrão de identificadores e parâmetros `before`, `after` e `around` em várias rotas. Erros de formulário podem trazer `code`, `message` e uma árvore detalhada `errors`, portanto o cliente deve preservar status, código, rota, método e detalhes.

O changelog de 12/08/2026 anunciou obfuscação de canais para usuários e bots. Em HTTP, `GET /guilds/{guild.id}/channels` passará a omitir canais sem `VIEW_CHANNEL` a partir de 16/11/2026; no Gateway, canais podem ter metadados obfuscados, a flag `CHANNEL_OBFUSCATED` e um overwrite negando `VIEW_CHANNEL`. O changelog de 05/08/2026 tornou `channel.application_id` anulável. Também foi documentado `file_types` em File Upload components/opções `ATTACHMENT`, e `app_permissions` em canais resolvidos de interações.

Esses itens devem orientar uma próxima rodada de modelos, cache e interações. Eles não são considerados implementados apenas por estarem documentados aqui.

## Matriz local já coberta

No código local já existem rotas para onboarding, Soundboard, role-connections metadata, Widget, prune, vanity URL, Voice States/Resource, SKUs, assinaturas, stickers multipart, paginação segura e webhooks por token. A matriz integral ainda está aberta.

Validação local no registro: 106 testes aprovados; wheel `pimcord-0.7.0-py3-none-any.whl` gerada; E2EE MLS/DAVE real ausente.

## Referências

[1]: https://docs.discord.com/developers/reference
[2]: https://docs.discord.com/developers/change-log

- [Documentação oficial — API Reference][1]
- [Documentação oficial — Change Log][2]

## Mudanças oficiais que exigem acompanhamento

A documentação oficial consultada informa que a API v10 é a versão disponível atual e que IDs Discord são snowflakes serializados como strings. A paginação segue o padrão de identificadores e parâmetros `before`, `after` e `around` em várias rotas. Erros de formulário podem trazer `code`, `message` e uma árvore detalhada `errors`, portanto o cliente deve preservar status, código, rota, método e detalhes.

O changelog de 12/08/2026 anunciou obfuscação de canais para usuários e bots. Em HTTP, `GET /guilds/{guild.id}/channels` passará a omitir canais sem `VIEW_CHANNEL` a partir de 16/11/2026; no Gateway, canais podem ter metadados obfuscados, a flag `CHANNEL_OBFUSCATED` e um overwrite negando `VIEW_CHANNEL`. O changelog de 05/08/2026 tornou `channel.application_id` anulável. Também foi documentado `file_types` em File Upload components/opções `ATTACHMENT`, e `app_permissions` em canais resolvidos de interações.

Esses itens devem orientar uma próxima rodada de modelos, cache e interações. Eles não são considerados implementados apenas por estarem documentados aqui.

## Matriz local já coberta

No código local já existem rotas para onboarding, Soundboard, role-connections metadata, Widget, prune, vanity URL, Voice States/Resource, SKUs, assinaturas, stickers multipart, paginação segura e webhooks por token. A matriz integral ainda está aberta.

Validação local no registro: 106 testes aprovados; wheel `pimcord-0.7.0-py3-none-any.whl` gerada; E2EE MLS/DAVE real ausente.

## Referências

[1]: https://docs.discord.com/developers/reference
[2]: https://docs.discord.com/developers/change-log

- [Documentação oficial — API Reference][1]
- [Documentação oficial — Change Log][2]

## Mudanças oficiais que exigem acompanhamento

A documentação oficial consultada informa que a API v10 é a versão disponível atual e que IDs Discord são snowflakes serializados como strings. A paginação segue o padrão de identificadores e parâmetros `before`, `after` e `around` em várias rotas. Erros de formulário podem trazer `code`, `message` e uma árvore detalhada `errors`, portanto o cliente deve preservar status, código, rota, método e detalhes.

O changelog de 12/08/2026 anunciou obfuscação de canais para usuários e bots. Em HTTP, `GET /guilds/{guild.id}/channels` passará a omitir canais sem `VIEW_CHANNEL` a partir de 16/11/2026; no Gateway, canais podem ter metadados obfuscados, a flag `CHANNEL_OBFUSCATED` e um overwrite negando `VIEW_CHANNEL`. O changelog de 05/08/2026 tornou `channel.application_id` anulável. Também foi documentado `file_types` em File Upload components/opções `ATTACHMENT`, e `app_permissions` em canais resolvidos de interações.

Esses itens devem orientar uma próxima rodada de modelos, cache e interações. Eles não são considerados implementados apenas por estarem documentados aqui.

## Matriz local já coberta

No código local já existem rotas para onboarding, Soundboard, role-connections metadata, Widget, prune, vanity URL, Voice States/Resource, SKUs, assinaturas, stickers multipart, paginação segura e webhooks por token. A matriz integral ainda está aberta.

Validação local no registro: 106 testes aprovados; wheel `pimcord-0.7.0-py3-none-any.whl` gerada; E2EE MLS/DAVE real ausente.

## Referências

[1]: https://docs.discord.com/developers/reference
[2]: https://docs.discord.com/developers/change-log

- [Documentação oficial — API Reference][1]
- [Documentação oficial — Change Log][2]

## Mudanças oficiais que exigem acompanhamento

A documentação oficial consultada informa que a API v10 é a versão disponível atual e que IDs Discord são snowflakes serializados como strings. A paginação segue o padrão de identificadores e parâmetros `before`, `after` e `around` em várias rotas. Erros de formulário podem trazer `code`, `message` e uma árvore detalhada `errors`, portanto o cliente deve preservar status, código, rota, método e detalhes.

O changelog de 12/08/2026 anunciou obfuscação de canais para usuários e bots. Em HTTP, `GET /guilds/{guild.id}/channels` passará a omitir canais sem `VIEW_CHANNEL` a partir de 16/11/2026; no Gateway, canais podem ter metadados obfuscados, a flag `CHANNEL_OBFUSCATED` e um overwrite negando `VIEW_CHANNEL`. O changelog de 05/08/2026 tornou `channel.application_id` anulável. Também foi documentado `file_types` em File Upload components/opções `ATTACHMENT`, e `app_permissions` em canais resolvidos de interações.

Esses itens devem orientar uma próxima rodada de modelos, cache e interações. Eles não são considerados implementados apenas por estarem documentados aqui.

## Matriz local já coberta

No código local já existem rotas para onboarding, Soundboard, role-connections metadata, Widget, prune, vanity URL, Voice States/Resource, SKUs, assinaturas, stickers multipart, paginação segura e webhooks por token. A matriz integral ainda está aberta.

Validação local no registro: 106 testes aprovados; wheel `pimcord-0.7.0-py3-none-any.whl` gerada; E2EE MLS/DAVE real ausente.

## Referências

[1]: https://docs.discord.com/developers/reference
[2]: https://docs.discord.com/developers/change-log

- [Documentação oficial — API Reference][1]
- [Documentação oficial — Change Log][2]

## Mudanças oficiais que exigem acompanhamento

A documentação oficial consultada informa que a API v10 é a versão disponível atual e que IDs Discord são snowflakes serializados como strings. A paginação segue o padrão de identificadores e parâmetros `before`, `after` e `around` em várias rotas. Erros de formulário podem trazer `code`, `message` e uma árvore detalhada `errors`, portanto o cliente deve preservar status, código, rota, método e detalhes.

O changelog de 12/08/2026 anunciou obfuscação de canais para usuários e bots. Em HTTP, `GET /guilds/{guild.id}/channels` passará a omitir canais sem `VIEW_CHANNEL` a partir de 16/11/2026; no Gateway, canais podem ter metadados obfuscados, a flag `CHANNEL_OBFUSCATED` e um overwrite negando `VIEW_CHANNEL`. O changelog de 05/08/2026 tornou `channel.application_id` anulável. Também foi documentado `file_types` em File Upload components/opções `ATTACHMENT`, e `app_permissions` em canais resolvidos de interações.

Esses itens devem orientar uma próxima rodada de modelos, cache e interações. Eles não são considerados implementados apenas por estarem documentados aqui.

## Matriz local já coberta

No código local já existem rotas para onboarding, Soundboard, role-connections metadata, Widget, prune, vanity URL, Voice States/Resource, SKUs, assinaturas, stickers multipart, paginação segura e webhooks por token. A matriz integral ainda está aberta.

Validação local no registro: 106 testes aprovados; wheel `pimcord-0.7.0-py3-none-any.whl` gerada; E2EE MLS/DAVE real ausente.

## Referências

[1]: https://docs.discord.com/developers/reference
[2]: https://docs.discord.com/developers/change-log

- [Documentação oficial — API Reference][1]
- [Documentação oficial — Change Log][2]

## Mudanças oficiais que exigem acompanhamento

A documentação oficial consultada informa que a API v10 é a versão disponível atual e que IDs Discord são snowflakes serializados como strings. A paginação segue o padrão de identificadores e parâmetros `before`, `after` e `around` em várias rotas. Erros de formulário podem trazer `code`, `message` e uma árvore detalhada `errors`, portanto o cliente deve preservar status, código, rota, método e detalhes.

O changelog de 12/08/2026 anunciou obfuscação de canais para usuários e bots. Em HTTP, `GET /guilds/{guild.id}/channels` passará a omitir canais sem `VIEW_CHANNEL` a partir de 16/11/2026; no Gateway, canais podem ter metadados obfuscados, a flag `CHANNEL_OBFUSCATED` e um overwrite negando `VIEW_CHANNEL`. O changelog de 05/08/2026 tornou `channel.application_id` anulável. Também foi documentado `file_types` em File Upload components/opções `ATTACHMENT`, e `app_permissions` em canais resolvidos de interações.

Esses itens devem orientar uma próxima rodada de modelos, cache e interações. Eles não são considerados implementados apenas por estarem documentados aqui.

## Matriz local já coberta

No código local já existem rotas para onboarding, Soundboard, role-connections metadata, Widget, prune, vanity URL, Voice States/Resource, SKUs, assinaturas, stickers multipart, paginação segura e webhooks por token. A matriz integral ainda está aberta.

Validação local no registro: 106 testes aprovados; wheel `pimcord-0.7.0-py3-none-any.whl` gerada; E2EE MLS/DAVE real ausente.

## Referências

[1]: https://docs.discord.com/developers/reference
[2]: https://docs.discord.com/developers/change-log

- [Documentação oficial — API Reference][1]
- [Documentação oficial — Change Log][2]

## Mudanças oficiais que exigem acompanhamento

A documentação oficial consultada informa que a API v10 é a versão disponível atual e que IDs Discord são snowflakes serializados como strings. A paginação segue o padrão de identificadores e parâmetros `before`, `after` e `around` em várias rotas. Erros de formulário podem trazer `code`, `message` e uma árvore detalhada `errors`, portanto o cliente deve preservar status, código, rota, método e detalhes.

O changelog de 12/08/2026 anunciou obfuscação de canais para usuários e bots. Em HTTP, `GET /guilds/{guild.id}/channels` passará a omitir canais sem `VIEW_CHANNEL` a partir de 16/11/2026; no Gateway, canais podem ter metadados obfuscados, a flag `CHANNEL_OBFUSCATED` e um overwrite negando `VIEW_CHANNEL`. O changelog de 05/08/2026 tornou `channel.application_id` anulável. Também foi documentado `file_types` em File Upload components/opções `ATTACHMENT`, e `app_permissions` em canais resolvidos de interações.

Esses itens devem orientar uma próxima rodada de modelos, cache e interações. Eles não são considerados implementados apenas por estarem documentados aqui.

## Matriz local já coberta

No código local já existem rotas para onboarding, Soundboard, role-connections metadata, Widget, prune, vanity URL, Voice States/Resource, SKUs, assinaturas, stickers multipart, paginação segura e webhooks por token. A matriz integral ainda está aberta.

Validação local no registro: 106 testes aprovados; wheel `pimcord-0.7.0-py3-none-any.whl` gerada; E2EE MLS/DAVE real ausente.

## Referências

[1]: https://docs.discord.com/developers/reference
[2]: https://docs.discord.com/developers/change-log

- [Documentação oficial — API Reference][1]
- [Documentação oficial — Change Log][2]

## Mudanças oficiais que exigem acompanhamento

A documentação oficial consultada informa que a API v10 é a versão disponível atual e que IDs Discord são snowflakes serializados como strings. A paginação segue o padrão de identificadores e parâmetros `before`, `after` e `around` em várias rotas. Erros de formulário podem trazer `code`, `message` e uma árvore detalhada `errors`, portanto o cliente deve preservar status, código, rota, método e detalhes.

O changelog de 12/08/2026 anunciou obfuscação de canais para usuários e bots. Em HTTP, `GET /guilds/{guild.id}/channels` passará a omitir canais sem `VIEW_CHANNEL` a partir de 16/11/2026; no Gateway, canais podem ter metadados obfuscados, a flag `CHANNEL_OBFUSCATED` e um overwrite negando `VIEW_CHANNEL`. O changelog de 05/08/2026 tornou `channel.application_id` anulável. Também foi documentado `file_types` em File Upload components/opções `ATTACHMENT`, e `app_permissions` em canais resolvidos de interações.

Esses itens devem orientar uma próxima rodada de modelos, cache e interações. Eles não são considerados implementados apenas por estarem documentados aqui.

## Matriz local já coberta

No código local já existem rotas para onboarding, Soundboard, role-connections metadata, Widget, prune, vanity URL, Voice States/Resource, SKUs, assinaturas, stickers multipart, paginação segura e webhooks por token. A matriz integral ainda está aberta.

Validação local no registro: 106 testes aprovados; wheel `pimcord-0.7.0-py3-none-any.whl` gerada; E2EE MLS/DAVE real ausente.

## Referências

[1]: https://docs.discord.com/developers/reference
[2]: https://docs.discord.com/developers/change-log

- [Documentação oficial — API Reference][1]
- [Documentação oficial — Change Log][2]

## Mudanças oficiais que exigem acompanhamento

A documentação oficial consultada informa que a API v10 é a versão disponível atual e que IDs Discord são snowflakes serializados como strings. A paginação segue o padrão de identificadores e parâmetros `before`, `after` e `around` em várias rotas. Erros de formulário podem trazer `code`, `message` e uma árvore detalhada `errors`, portanto o cliente deve preservar status, código, rota, método e detalhes.

O changelog de 12/08/2026 anunciou obfuscação de canais para usuários e bots. Em HTTP, `GET /guilds/{guild.id}/channels` passará a omitir canais sem `VIEW_CHANNEL` a partir de 16/11/2026; no Gateway, canais podem ter metadados obfuscados, a flag `CHANNEL_OBFUSCATED` e um overwrite negando `VIEW_CHANNEL`. O changelog de 05/08/2026 tornou `channel.application_id` anulável. Também foi documentado `file_types` em File Upload components/opções `ATTACHMENT`, e `app_permissions` em canais resolvidos de interações.

Esses itens devem orientar uma próxima rodada de modelos, cache e interações. Eles não são considerados implementados apenas por estarem documentados aqui.

## Matriz local já coberta

No código local já existem rotas para onboarding, Soundboard, role-connections metadata, Widget, prune, vanity URL, Voice States/Resource, SKUs, assinaturas, stickers multipart, paginação segura e webhooks por token. A matriz integral ainda está aberta.

Validação local no registro: 106 testes aprovados; wheel `pimcord-0.7.0-py3-none-any.whl` gerada; E2EE MLS/DAVE real ausente.

## Referências

[1]: https://docs.discord.com/developers/reference
[2]: https://docs.discord.com/developers/change-log

- [Documentação oficial — API Reference][1]
- [Documentação oficial — Change Log][2]

## Mudanças oficiais que exigem acompanhamento

A documentação oficial consultada informa que a API v10 é a versão disponível atual e que IDs Discord são snowflakes serializados como strings. A paginação segue o padrão de identificadores e parâmetros `before`, `after` e `around` em várias rotas. Erros de formulário podem trazer `code`, `message` e uma árvore detalhada `errors`, portanto o cliente deve preservar status, código, rota, método e detalhes.

O changelog de 12/08/2026 anunciou obfuscação de canais para usuários e bots. Em HTTP, `GET /guilds/{guild.id}/channels` passará a omitir canais sem `VIEW_CHANNEL` a partir de 16/11/2026; no Gateway, canais podem ter metadados obfuscados, a flag `CHANNEL_OBFUSCATED` e um overwrite negando `VIEW_CHANNEL`. O changelog de 05/08/2026 tornou `channel.application_id` anulável. Também foi documentado `file_types` em File Upload components/opções `ATTACHMENT`, e `app_permissions` em canais resolvidos de interações.

Esses itens devem orientar uma próxima rodada de modelos, cache e interações. Eles não são considerados implementados apenas por estarem documentados aqui.

## Matriz local já coberta

No código local já existem rotas para onboarding, Soundboard, role-connections metadata, Widget, prune, vanity URL, Voice States/Resource, SKUs, assinaturas, stickers multipart, paginação segura e webhooks por token. A matriz integral ainda está aberta.

Validação local no registro: 106 testes aprovados; wheel `pimcord-0.7.0-py3-none-any.whl` gerada; E2EE MLS/DAVE real ausente.

## Referências

[1]: https://docs.discord.com/developers/reference
[2]: https://docs.discord.com/developers/change-log

- [Documentação oficial — API Reference][1]
- [Documentação oficial — Change Log][2]

## Mudanças oficiais que exigem acompanhamento

A documentação oficial consultada informa que a API v10 é a versão disponível atual e que IDs Discord são snowflakes serializados como strings. A paginação segue o padrão de identificadores e parâmetros `before`, `after` e `around` em várias rotas. Erros de formulário podem trazer `code`, `message` e uma árvore detalhada `errors`, portanto o cliente deve preservar status, código, rota, método e detalhes.

O changelog de 12/08/2026 anunciou obfuscação de canais para usuários e bots. Em HTTP, `GET /guilds/{guild.id}/channels` passará a omitir canais sem `VIEW_CHANNEL` a partir de 16/11/2026; no Gateway, canais podem ter metadados obfuscados, a flag `CHANNEL_OBFUSCATED` e um overwrite negando `VIEW_CHANNEL`. O changelog de 05/08/2026 tornou `channel.application_id` anulável. Também foi documentado `file_types` em File Upload components/opções `ATTACHMENT`, e `app_permissions` em canais resolvidos de interações.

Esses itens devem orientar uma próxima rodada de modelos, cache e interações. Eles não são considerados implementados apenas por estarem documentados aqui.

## Matriz local já coberta

No código local já existem rotas para onboarding, Soundboard, role-connections metadata, Widget, prune, vanity URL, Voice States/Resource, SKUs, assinaturas, stickers multipart, paginação segura e webhooks por token. A matriz integral ainda está aberta.

Validação local no registro: 106 testes aprovados; wheel `pimcord-0.7.0-py3-none-any.whl` gerada; E2EE MLS/DAVE real ausente.

## Referências

[1]: https://docs.discord.com/developers/reference
[2]: https://docs.discord.com/developers/change-log

- [Documentação oficial — API Reference][1]
- [Documentação oficial — Change Log][2]

## Mudanças oficiais que exigem acompanhamento

A documentação oficial consultada informa que a API v10 é a versão disponível atual e que IDs Discord são snowflakes serializados como strings. A paginação segue o padrão de identificadores e parâmetros `before`, `after` e `around` em várias rotas. Erros de formulário podem trazer `code`, `message` e uma árvore detalhada `errors`, portanto o cliente deve preservar status, código, rota, método e detalhes.

O changelog de 12/08/2026 anunciou obfuscação de canais para usuários e bots. Em HTTP, `GET /guilds/{guild.id}/channels` passará a omitir canais sem `VIEW_CHANNEL` a partir de 16/11/2026; no Gateway, canais podem ter metadados obfuscados, a flag `CHANNEL_OBFUSCATED` e um overwrite negando `VIEW_CHANNEL`. O changelog de 05/08/2026 tornou `channel.application_id` anulável. Também foi documentado `file_types` em File Upload components/opções `ATTACHMENT`, e `app_permissions` em canais resolvidos de interações.

Esses itens devem orientar uma próxima rodada de modelos, cache e interações. Eles
