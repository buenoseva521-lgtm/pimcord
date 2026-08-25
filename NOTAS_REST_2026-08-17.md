# Auditoria REST oficial — 17/08/2026

Fontes consultadas:
- [Guild Resource](https://docs.discord.com/developers/resources/guild)
- [Application Resource](https://docs.discord.com/developers/resources/application)
- [Application Role Connection Metadata](https://docs.discord.com/developers/resources/application-role-connection-metadata)
- [Soundboard Resource](https://docs.discord.com/developers/resources/soundboard)

A documentação oficial confirma `GET/PUT /applications/{application.id}/role-connections/metadata`, `GET /soundboard-default-sounds` e as rotas de Soundboard de guild. Também confirma o limite de cinco registros de metadata de role connection e o endpoint `POST /channels/{channel.id}/send-soundboard-sound`, ainda ausente do cliente Pimcord. O recurso Guild documenta onboarding e objetos de guild; a auditoria completa de rotas precisa continuar comparando a referência inteira, incluindo permissões, paginação e formatos de resposta.

A busca na referência oficial confirmou que Guild Resource documenta Get Guild Vanity URL e que o changelog oficial registra endpoints HTTP para voz. A página oficial de Voice Resource é `https://docs.discord.com/developers/resources/voice`; a implementação deve conferir os métodos Get Guild Voice State, Get Current User Voice State e Modify Current User Voice State antes de adicionar contratos.

A referência oficial de Application Commands confirma que `default_member_permissions`, `contexts`, `integration_types` e `handler` pertencem ao objeto do comando; a documentação de permissões descreve permissões de comandos, mas a auditoria não encontrou nas páginas consultadas uma nova rota REST necessária além das já mapeadas. Não será adicionada uma rota de permissões sem confirmação de endpoint oficial atual.

A documentação oficial de Guild Resource confirma Get Guild Widget Settings, Modify Guild Widget, Get Guild Prune Count e Begin Guild Prune; o changelog oficial também registra que prune exige MANAGE_GUILD além de KICK_MEMBERS. Implementar apenas os métodos e contratos dessas rotas, com parâmetros oficiais e sem extrapolar permissões.
