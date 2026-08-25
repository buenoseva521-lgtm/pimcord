# Fontes oficiais consultadas na validação REST

As páginas oficiais atuais consultadas foram:

- https://docs.discord.com/developers/resources/guild
- https://docs.discord.com/developers/interactions/application-commands
- https://docs.discord.com/developers/resources/channel
- https://docs.discord.com/developers/resources/user

A documentação oficial confirma que a API v10 possui operações separadas para obter/editar aplicação, comandos globais e por servidor, obter usuário atual, membro do servidor, busca de membros, threads, mensagens e pins. A referência de Application Commands confirma os tipos `CHAT_INPUT`, `USER`, `MESSAGE` e `PRIMARY_ENTRY_POINT`, limites de nome/descrição e opções de contexto/integração. A referência de Guild confirma `Search Guild Members`, `Get Guild Member`, `Modify Current User Nick` e operações de servidor como recursos distintos. A referência de Channels descreve mensagens, threads, pins e membros de thread como operações independentes.

Essas fontes foram usadas somente para confrontar a superfície local; não autorizam declarar paridade total enquanto o relatório operação a operação e os fluxos reais ainda estiverem incompletos.


## Revisão de lacunas conservadoras

A referência oficial atual também confirma Entitlements como operações de aplicação (`GET/POST/DELETE /applications/{application.id}/entitlements...`) e trata webhooks de integração como uma família distinta dos webhooks de mensagens. A lista conservadora inclui Lobbies e Partner SDK, que não pertencem à promessa de uma biblioteca de bots e permanecem fora do escopo. Composição local já cobre comandos globais/por servidor, threads arquivadas e estado de voz `@me`; a ausência literal nessas famílias exige normalização antes de ser classificada como ausência funcional.


## Eventos agendados recorrentes — fonte oficial

Fonte: https://docs.discord.com/developers/resources/guild-scheduled-event

A página oficial confirma o objeto de evento agendado, a regra de recorrência e os usuários inscritos. A extração disponível ainda não expôs o trecho completo das rotas de exceção agregadas; portanto, as operações individuais já implementadas não autorizam inferir o payload da rota agregada `POST /guilds/{guild.id}/scheduled-events/{guild_scheduled_event.id}/exceptions`. Essa operação continuará pendente até a confirmação explícita de método, corpo e resposta na referência completa.


## Revisão de solicitações de servidor — 2026-08-18

A referência oficial de [Guild Resource](https://docs.discord.com/developers/resources/guild) foi consultada para verificar a família `requests`. A página documenta Guilds como coleções isoladas de usuários e canais e mantém a referência normativa da API v10; a busca atual não apresentou uma seção pública de endpoints de solicitações de servidor equivalente às rotas conservadoras `GET/PATCH /guilds/{guild_id}/requests`. A família deve permanecer classificada como **não confirmada** até existir documentação oficial específica ou contrato público verificável, sem implementação especulativa.

A [API Reference](https://docs.discord.com/developers/reference) confirma que a API base é `https://discord.com/api`, que a v10 está disponível, que IDs Snowflake retornam como strings e que erros preservam `code`, `message` e `errors`. Esses fatos sustentam a validação do transporte, mas não comprovam as rotas de solicitações.


## Anexo efêmero de Activities — 2026-08-18

A página oficial [User Actions](https://docs.discord.com/developers/activities/development-guides/user-actions) confirma o endpoint `POST /applications/{application_id}/attachment` para criar uma URL CDN efêmera usada por `openShareMomentDialog`. O exemplo oficial envia `multipart/form-data` com o campo `file`, autentica com `Authorization: Bearer` e lê `attachment.url` na resposta. Esse recurso pertence ao fluxo de Activities/Embedded App, não ao token de bot comum; qualquer suporte no Pimcord precisa de uma API explicitamente separada para bearer/OAuth2 e multipart, sem fingir que é uma operação REST de bot.


## Webhooks compatíveis com GitHub/Slack — 2026-08-18

A referência oficial de Webhooks confirma que a execução por token não exige usuário de bot ou autenticação adicional e que uma mensagem precisa fornecer ao menos `content`, `embeds`, `components`, `file` ou `poll`. As variantes `/github` e `/slack` são formatos de integração compatíveis, mas o contrato detalhado de transformação não foi exposto de forma completa na referência pública extraída. O Pimcord mantém a execução genérica já validada e não adiciona aliases específicos sem payload normativo completo.
