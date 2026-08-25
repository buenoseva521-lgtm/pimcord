# Matriz operacional Pimcord 0.7.0

Esta matriz é o contrato de trabalho do release. `Existente` significa que há código executável; `Expandir` significa que a base existe, mas não cobre o domínio inteiro; `Projetar` significa que ainda exige implementação e testes antes de aparecer como API estável.

| Área | Estado auditado | Entrega 0.7.0 | Testes obrigatórios |
|---|---|---|---|
| Instalação e CLI | Existente | Corrigir scaffolding, diagnóstico, versão e comandos de manutenção | Instalação limpa, CLI em subprocesso, help e erros |
| Bot e lifecycle | Existente | Context manager, cancelamento, shutdown ordenado e hooks completos | Ciclo normal, falha de conexão, cancelamento |
| Eventos | Existente/Expandir | Catálogo de 71 dispatches, listeners, tipos e aliases idiomáticos | Dispatcher, ordem, exceções e payloads |
| Intents | Existente | Cobrir todos os flags, serialização e validação de privilegiados | Bitmask, `all`, `todos`, configuração inválida |
| REST | Existente/Expandir | Métodos de recursos Discord, paginação, multipart, arquivos, audit reason, retries e erro estruturado | Servidor falso, 429, 5xx, timeout e cancelamento |
| Gateway | Expandir | Máquina de estados completa, Resume e close codes | Heartbeat, ACK, reconnect, invalid session e Resume |
| Modelos | Existente/Expandir | Entidades ampliadas, payloads tolerantes, conversores, bruto preservado e objetos parciais | Cada payload fixture, campos ausentes e round-trip |
| Mensagens | Existente/Expandir | Histórico, edição, exclusão, bulk, reactions, pins, referências e upload multipart | Rotas, permissões, limites e paginação |
| Canais | Existente/Expandir | Texto, voz, categoria, thread, fórum, tags, permissões e overwrites | Criação, edição, exclusão e serialização |
| Membros e cargos | Existente/Expandir | Busca, edição, nick, roles, ban, kick, auditoria e integração OAuth | Permissões, payloads e erros |
| Comandos prefixados | Existente | Conversores, flags, help, erro, cooldown, checks e grupos completos | Parsing, quotes, tipos, erros e concorrência |
| Slash commands | Expandir | Opções, choices, grupos, subcomandos, autocomplete e sync | Payload de registro, dispatch e resposta |
| Híbridos | Projetar | Callback único com Contexto normalizado para prefixo e slash | Invocação dupla e diferenças de resposta |
| Interações | Expandir | Defer, followup, ephemeral, edição, exclusão e expiração | Token, acknowledgement, 3s, followup e flags |
| Views | Expandir | Persistent registry, reidratação, timeout, checks e estado | Restart simulado, custom_id, concorrência e expiração |
| Modais e selects | Expandir | Validação, parsing, autocomplete e erros de usuário | Payload, callback e cancelamento |
| Webhooks | Expandir | Execução, edição, exclusão, arquivos e followups | Token inválido, rate limit e payload |
| Extensões | Existente | Cogs, listeners, teardown, reload e dependências | Carregamento, rollback e ordem |
| Tarefas | Existente | Loop robusto, backoff, locks, filas e jobs persistentes | Cancelamento, falha e reinício |
| Banco/cache | Existente | Interfaces, migração, transações e cache configurável | SQLite, concorrência e recuperação |
| Voz | Projetar | Voice Gateway, UDP, criptografia, fontes e player | Fixtures de protocolo, sem áudio externo obrigatório |
| Sharding | Base | Supervisor, workers, saúde, distribuição e backoff | Falha de worker, heartbeat e coordenação |
| Observabilidade | Existente | Logs estruturados, eventos de diagnóstico, métricas e tracing local | Snapshot, níveis e erros |
| Documentação | Expandir | Guia conceitual, referência automática, exemplos e troubleshooting | Links, snippets compiláveis e build offline |

## Regra de aceite

Uma linha só pode ser marcada como estável quando possuir implementação, export público, docstring, exemplo executável, teste de contrato e uma seção de limitações. Sem os seis itens, o artigo deve exibir o estado correto e encaminhar para o roadmap.
