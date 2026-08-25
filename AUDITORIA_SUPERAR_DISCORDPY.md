# Auditoria para superar o discord.py — Pimcord 0.7.0

## Resumo executivo

A versão 0.7.0 possui uma base funcional real: 23 arquivos Python, 52 classes identificadas, 3 arquivos de testes e 21 testes passando em ambiente local, sem conexão externa. Há Bot assíncrono, Gateway básico, REST com controle de rota, comandos prefixados, slash e híbridos, conversão tipada inicial, intents, eventos, embeds, componentes, Views, follow-ups, respostas efêmeras, canais, overwrites, histórico, purge, cache, SQLite, extensões, tarefas, métricas, webhooks, CLI e cálculo básico de shards.

Isso ainda **não é maior que discord.py**. O maior bloqueio é de cobertura: existe uma boa fundação, mas várias áreas são apenas básicas, parciais ou ausentes. A auditoria encontrou um `NotImplementedError` explícito para uploads de arquivos, nenhum módulo de voz/áudio, sharding sem supervisor distribuído, ausência de uma superfície completa de modelos/eventos Discord e apenas 21 testes locais. O release deve ser tratado como uma fundação 0.7.0, não como paridade concluída.

## Estado observado

| Domínio | Estado real | Evidência | Prioridade |
|---|---|---|---:|
| Bot e ciclo de vida | Implementado, mas precisa endurecimento | `Bot`, conexão, fechamento e despacho presentes | Alta |
| Gateway | Base funcional | Cliente, heartbeat, ACK, Identify e reconexão básica | Crítica |
| REST | Base funcional | Cliente HTTP, rotas e rate limit por rota | Crítica |
| Comandos prefixados | Implementado em nível inicial | Prefixo, aliases, conversão e checks básicos | Alta |
| Slash commands | Parcial | Registro, opções tipadas iniciais e callbacks | Crítica |
| Comandos híbridos | Parcial/implementado no primeiro contrato | Callback compartilhado e Contexto normalizado | Crítica |
| Grupos e subcomandos | Não comprovados como completos | Não devem ser anunciados como paridade | Crítica |
| Autocomplete e transformers | Ausentes ou incompletos | Não há cobertura comprovada equivalente | Alta |
| Follow-up e ephemeral | Implementados no contrato inicial | Métodos de Interacao e payloads locais | Alta |
| Views persistentes | Implementadas para classes importáveis | Registro/reidratação local e `custom_id` | Crítica |
| Uploads/anexos | Ausentes | `NotImplementedError` em `Mensagem.enviar_arquivo` | Crítica |
| Canais e permissões | Parcialmente implementados | Criar/listar/editar, overwrites e purge | Alta |
| Modelos Discord | Incompletos | Usuário, membro, cargo, canal, servidor, mensagem e anexo básicos | Crítica |
| Eventos | Incompletos | Mensagens e eventos essenciais, não cobertura integral | Crítica |
| Voz e áudio | Ausentes | Não existe módulo `voz`, `voice` ou `audio` | Crítica |
| Sharding | Básico | `ShardInfo` e gerenciador local, sem supervisor distribuído | Alta |
| Cache | Básico | Cache em memória, sem políticas avançadas/caches especializados | Alta |
| Persistência | Básica | SQLite presente, sem camada robusta de migração/concorrência | Média |
| Extensões/Cogs | Base presente | Precisa hooks, lifecycle, dependências e isolamento | Alta |
| Tarefas | Base presente | Precisa cancelamento, backoff, jitter e observabilidade | Média |
| Webhooks | Presente, mas isolado | Usa sessão própria e não compartilha toda a infraestrutura REST | Média |
| Testes | Insuficientes para uma biblioteca maior que discord.py | 21 testes, sem matriz extensa de eventos/transportes | Crítica |
| Tipagem | Insuficiente | Não há garantia de stubs, mypy/pyright ou contratos completos | Alta |
| Docs de referência | Parcial | Há guias, mas não geração automática de API | Alta |
| Ferramentas | Base | CLI, CI e exemplos presentes; faltam lint, typecheck e release automatizado | Média |

## Lacunas críticas de funcionalidade

### 1. API Discord e modelos

O Pimcord precisa cobrir todos os objetos que um bot de produção encontra: guilds completas, canais de texto/voz/categoria/fórum/stage, threads, membros, cargos, emojis, stickers, scheduled events, invites, templates, automod, bans, timeouts, audit log, welcome screen, integrations, interactions, entitlements, subscriptions, soundboard e recursos de aplicação. Cada modelo precisa de conversão segura, `fetch`, `edit`, `delete`, igualdade por ID, cache coerente e tratamento de dados parciais.

### 2. Eventos e Gateway

A camada de eventos precisa representar os dispatches de criação, atualização e remoção de mensagens, membros, cargos, canais, threads, reações, presença, typing, voz, integrações, automod, polls, scheduled events e interações. O Gateway deve incluir heartbeat com medição de latência, reconnect com backoff e jitter, resume robusto, invalid session, sequence tracking, rate limits de Identify, múltiplos shards, sessão observável e shutdown seguro.

### 3. REST de produção

O cliente precisa de uma tabela completa de rotas, serialização centralizada, paginação, retry com classificação de erros, limite global, buckets compartilhados, `Retry-After`, `X-RateLimit-*`, idempotência, uploads multipart, downloads, anexos, allowed mentions, proxy, timeout configurável, tracing, métricas e exceções com corpo estruturado. O `NotImplementedError` de upload impede declarar a camada REST completa.

### 4. Comandos e interações

Para superar discord.py, o Pimcord precisa fechar o contrato de comandos: grupos, subcomandos, comandos híbridos com schema único, converters assíncronos, flags, choices, transformers, autocomplete, checks por árvore, cooldowns por usuário/canal/guild/global, hooks antes/depois, error handlers, help command, prefixo dinâmico, `wait_for`, context menus, message commands, localization, permissões padrão e sincronização diferencial. Interações devem suportar todos os tipos de resposta, edição/exclusão de respostas, follow-ups, attachments, modais completos, DynamicItem e layouts.

### 5. Voz e áudio

A ausência total de módulo de voz é uma lacuna crítica. É necessário implementar Voice Gateway, UDP discovery, IP discovery, encryption modes, SSRC, heartbeat, reconnect, voice state, player assíncrono, fila, pause/resume/seek, volume, fontes PCM/Opus, FFmpeg opcional, transcodificação, eventos de fim/erro e suporte a múltiplas guilds. Para ser maior que discord.py, a API de áudio precisa ser modular, testável e amigável para mobile.

### 6. Persistência, extensões e operação

Views persistentes não podem depender somente da importação de classes: devem ter versionamento, validação de schema, migração, conflito de `custom_id`, recuperação após falha e armazenamento opcional. Cogs/extensões precisam lifecycle completo, dependências, reload seguro, rollback e isolamento de erro. Tarefas precisam política de retry, backoff, jitter, locks distribuídos e shutdown cooperativo. O sistema de observabilidade precisa logs estruturados, métricas do Gateway/REST, tracing e health checks.

## O que pode tornar o Pimcord maior, não apenas equivalente

| Diferencial | Proposta |
|---|---|
| API portuguesa consistente | Nomes portugueses com aliases explícitos, documentação de migração e validação de conflitos |
| Arquitetura offline-first | Fixtures oficiais, simuladores locais de Gateway/REST e testes sem rede |
| Schema único | Um callback e uma definição de parâmetros gerando prefixo, slash e híbrido |
| Tipagem de verdade | Protocols, generics, overloads, py.typed, mypy/pyright e modelos imutáveis opcionais |
| Observabilidade nativa | Eventos de diagnóstico, métricas, tracing, health checks e exportadores sem acoplamento |
| Resiliência | Supervisor de reconexão, circuit breaker REST, filas, backpressure e degradação controlada |
| Ferramentas | CLI para scaffold, validação de intents, inspeção de comandos, geração de documentação e diagnóstico |
| Mobile-first | Dependências opcionais, compatibilidade com Pydroid/Termux, SQLite local, baixo consumo e exemplos sem FFmpeg obrigatório |
| Segurança | Redação automática de tokens, allowed mentions segura, validação de permissões e prevenção de logs sensíveis |
| Docs executáveis | Referência gerada do código, exemplos testados no CI, simulador local e matrizes de compatibilidade |
| Migração | Ferramenta que converte padrões comuns de discord.py para a sintaxe do Pimcord e aponta diferenças |
| Compatibilidade | Camada opcional de aliases, sem copiar implementação externa, para reduzir custo de migração |

## Critérios para declarar um módulo completo

Um módulo só deve ser marcado como **estável** quando possuir implementação executável, export público, docstrings, tipos, exemplos executáveis, testes unitários e de integração simulada, tratamento de erros, métricas mínimas, documentação de limites e compatibilidade mobile. A existência de uma classe ou um endpoint isolado não é suficiente.

## Ordem técnica recomendada

1. Fechar REST, uploads, paginação, erros, rate limits e modelos base.
2. Fechar Gateway, intents, eventos, reconexão e supervisor de shards.
3. Completar comandos híbridos, grupos, autocomplete, converters e sincronização.
4. Completar interações, Views persistentes, modais, anexos e context menus.
5. Implementar voz e áudio como subsistema independente.
6. Expandir modelos, moderação, threads, fóruns e eventos de plataforma.
7. Construir testes de contrato, simuladores locais, tipagem e benchmarks.
8. Gerar documentação API automaticamente e só então declarar os módulos estáveis.

## Conclusão

O Pimcord 0.7.0 é uma base promissora e já possui vários recursos reais, mas ainda não supera nem iguala integralmente o discord.py. As lacunas mais importantes são voz, uploads, cobertura de modelos/eventos, grupos/autocomplete slash, robustez de Gateway/REST, sharding distribuído, tipagem e testes. O caminho para ser maior é combinar cobertura funcional ampla com diferenciais de API portuguesa, schema único, operação offline-first, observabilidade, resiliência, tooling e suporte mobile.
