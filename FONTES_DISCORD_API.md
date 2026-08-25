# Fontes oficiais usadas na expansão da API

A expansão de modelos, eventos e REST foi conferida contra a documentação oficial do Discord consultada em 16 de agosto de 2026.

| Referência | Uso no Pimcord |
|---|---|
| [API Reference](https://docs.discord.com/developers/reference) | Base URL, versionamento v10, autenticação, erros estruturados e snowflakes. |
| [Gateway Events](https://docs.discord.com/developers/events/gateway-events) | Estrutura de dispatches, eventos de envio/recebimento, Identify, Resume e eventos oficiais. |
| [Channels Resource](https://docs.discord.com/developers/resources/channel) | Canais, threads, fóruns, mensagens, pins, reações, permissões e anexos. |
| [Guild Resource](https://docs.discord.com/developers/resources/guild) | Servidores, membros, cargos, bans, auditoria, integrações, eventos agendados e configurações. |
| [Gateway](https://docs.discord.com/developers/events/gateway) | Ciclo de conexão, heartbeat, reconexão e retomada de sessão. |

A documentação oficial informa que o Discord utiliza a API REST versionada, que a versão 10 está disponível e que erros de formulário podem conter `code`, `message` e `errors`. Também define que eventos Gateway são encapsulados com `op`, `d`, `s` e `t`, e que os nomes práticos são maiúsculos com sublinhados. Esses contratos orientaram o cliente HTTP, as exceções estruturadas, o catálogo `EVENTOS_DISCORD` e os aliases portugueses.
