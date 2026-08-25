# Classificação inicial das operações REST abertas

A inspeção offline de `/tmp/discord-openapi.json` confirmou que grande parte das 23 não correspondências reportadas pertence a superfícies especiais: `lobbies`, `partner-sdk` e integrações de webhook GitHub/Slack. Essas rotas não devem ser implementadas automaticamente sem contrato de modelo próprio, mas a classificação não pode descartá-las como fora da superfície de bots: o OpenAPI local declara `BotToken` em várias operações de Lobbies e Partner SDK. Elas devem permanecer como lacunas especializadas do cliente enquanto payloads, escopo e comportamento não forem auditados.

## Superfícies especiais identificadas

| Família | Operações abertas | Tratamento inicial |
|---|---:|---|
| Lobbies | 16 | Superfície especializada que aceita `BotToken` em várias rotas; exige investigação e API própria antes de implementação. |
| Partner SDK | 5 | Superfície especializada; parte aceita `BotToken`, portanto permanece pendência potencial de bots até revisão de contrato. |
| Webhook GitHub/Slack | 2 | Avaliar como integrações específicas de webhook, separadas do CRUD de webhooks já implementado. |

A lista atual de pendências reportadas também contém operações de comandos da aplicação e exceções de eventos agendados, que devem ser comparadas com métodos compostos existentes antes de qualquer implementação duplicada. Após o auditor passar a resolver variáveis, condicionais, concatenações e defaults como `@me`, a contagem reportada foi reduzida para 23. As pendências atuais incluem 16 operações de Lobbies, 5 de Partner SDK e 2 de webhooks GitHub/Slack. O upload de anexo de aplicação e as operações de metadata/moderação estão contidos nessas superfícies especiais; não há, nesta lista, uma lacuna comum de bot confirmada apenas pela ausência literal. A classificação não fecha o bloqueador REST: a matriz ainda precisa de revisão operação a operação e documentação das decisões de escopo.


## Classificação operação por operação

| Operação | Classificação | Decisão |
|---|---|---|
| `DELETE /lobbies/{id}` | Lobby | Fora da paridade comum de bots; exige superfície Lobby própria. |
| `DELETE /lobbies/{id}/members/@me` | Lobby | Fora da paridade comum de bots; exige superfície Lobby própria. |
| `DELETE /lobbies/{id}/members/{user_id}` | Lobby | Fora da paridade comum de bots; exige superfície Lobby própria. |
| `GET /lobbies/{id}` | Lobby | Fora da paridade comum de bots; exige superfície Lobby própria. |
| `GET /lobbies/{id}/messages` | Lobby | Fora da paridade comum de bots; exige superfície Lobby própria. |
| `PATCH /lobbies/{id}` | Lobby | Fora da paridade comum de bots; exige superfície Lobby própria. |
| `PATCH /lobbies/{id}/channel-linking` | Lobby | Fora da paridade comum de bots; exige superfície Lobby própria. |
| `POST /lobbies` | Lobby | Fora da paridade comum de bots; exige superfície Lobby própria. |
| `POST /lobbies/{id}/members/@me/invites` | Lobby | Fora da paridade comum de bots; exige superfície Lobby própria. |
| `POST /lobbies/{id}/members/bulk` | Lobby | Fora da paridade comum de bots; exige superfície Lobby própria. |
| `POST /lobbies/{id}/members/{user_id}/invites` | Lobby | Fora da paridade comum de bots; exige superfície Lobby própria. |
| `POST /lobbies/{id}/messages` | Lobby | Fora da paridade comum de bots; exige superfície Lobby própria. |
| `PUT /lobbies` | Lobby | Fora da paridade comum de bots; exige superfície Lobby própria. |
| `PUT /lobbies/{id}/members/{user_id}` | Lobby | Fora da paridade comum de bots; exige superfície Lobby própria. |
| `PUT /lobbies/{id}/messages/{message_id}/moderation-metadata` | Lobby/metadata | Fora da paridade comum de bots; metadata pertence à superfície Lobby. |
| `POST /partner-sdk/provisional-accounts/unmerge` | Partner SDK | Fora do cliente comum de bots; exige credenciais e contrato Partner SDK. |
| `POST /partner-sdk/provisional-accounts/unmerge/bot` | Partner SDK | Fora do cliente comum de bots; exige credenciais e contrato Partner SDK. |
| `POST /partner-sdk/token` | Partner SDK | Fora do cliente comum de bots; token próprio de integração. |
| `POST /partner-sdk/token/bot` | Partner SDK | Fora do cliente comum de bots; token próprio de integração. |
| `PUT /partner-sdk/dms/{id}/{id}/messages/{id}/moderation-metadata` | Partner SDK/metadata | Fora do cliente comum de bots; metadata pertence à superfície Partner SDK. |
| `POST /webhooks/{id}/{token}/github` | Webhook GitHub | Integração específica; não é CRUD comum de webhook de bot. |
| `POST /webhooks/{id}/{token}/slack` | Webhook Slack | Integração específica; não é CRUD comum de webhook de bot. |
| `POST /applications/{id}/attachment` | Activities/anexo | Superfície de anexo de aplicação; não implementar como endpoint comum sem contrato de Activities validado. |

Essa tabela fecha apenas a classificação preliminar por família das 23 pendências reportadas. A inspeção de segurança mostrou que várias rotas de Lobbies, Partner SDK e webhooks aceitam `BotToken` ou autenticação alternativa; portanto elas não podem ser excluídas da paridade de bots apenas por pertencerem a uma superfície especializada. Elas permanecem bloqueadoras até revisão oficial de payloads, escopo e testes offline. A matriz REST continua marcada como bloqueador até uma revisão final de autenticação, payloads e escopo para cada família.
