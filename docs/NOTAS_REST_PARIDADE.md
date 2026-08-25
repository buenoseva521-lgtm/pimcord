# Notas de paridade REST — 17/08/2026

## Audit Logs

A documentação oficial atual confirma `GET /guilds/{guild.id}/audit-logs`, retenção de 45 dias e os campos `application_commands`, `audit_log_entries`, `auto_moderation_rules`, `guild_scheduled_events`, `integrations`, `threads`, `users` e `webhooks` no objeto de auditoria. O modelo atual já tipa entradas, usuários e integrações, mas ainda deve modelar ou preservar explicitamente comandos de aplicação, regras de automoderação, eventos agendados, threads e webhooks referenciados.

## Assinaturas e entitlements

A documentação de monetização reforça que assinaturas são ciclo de relatório/lifecycle, enquanto a presença de entitlement é a fonte de verdade para acesso premium. O cliente já cobre listagem/consulta/cancelamento de assinaturas e entitlements, mas eventos Gateway `SUBSCRIPTION_CREATE`, `SUBSCRIPTION_UPDATE`, `ENTITLEMENT_CREATE`, `ENTITLEMENT_UPDATE` e `ENTITLEMENT_DELETE` devem ser auditados na família de eventos e modelos.

## Obfuscação de canais

A documentação atual do recurso de canais contém campos opcionais e uma mudança futura de obfuscação para canais que o bot não pode visualizar. O Pimcord já preserva `obfuscado` e `permissoes_aplicacao` em `CanalCompleto`; a auditoria deve confirmar aliases, semântica de campos ausentes e comportamento fail-closed no parser quando um canal vier obfuscado.

Fonte primária: [Discord Developer Documentation — Audit Logs](https://docs.discord.com/developers/resources/audit-log), [Implementing App Subscriptions](https://docs.discord.com/developers/monetization/implementing-app-subscriptions) e [Channels Resource](https://docs.discord.com/developers/resources/channel).

## Webhooks e interações

A documentação oficial de webhooks confirma as rotas já presentes para criar/listar/obter/editar/excluir e executar webhooks, mas destaca que execução pode usar `wait`, `thread_id`/`thread_name`, arquivos multipart e exige pelo menos um entre `content`, `embeds`, `components`, `file` ou `poll`. A execução com token é diferente de callback de interação.

A documentação oficial de interações confirma `POST /interactions/{interaction.id}/{interaction.token}/callback` como resposta inicial; o objeto de interação atual também contém `entitlements`, `authorizing_integration_owners`, `context` e `attachment_size_limit`, pontos que devem ser auditados no modelo de interação do Pimcord.

Fonte primária: [Webhook Resource](https://docs.discord.com/developers/resources/webhook) e [Receiving and Responding to Interactions](https://docs.discord.com/developers/interactions/receiving-and-responding).

## Índice oficial de superfície

O índice oficial de documentação consultado confirma famílias adicionais que precisam ser classificadas na matriz de paridade: OAuth2/instalações, application commands, componentes e modais, gerenciamento de servidores/canais, webhooks e eventos de webhook, monetização (SKUs, assinaturas, compras únicas), discovery, community invites, gateway/intents e recursos de voz. Recursos do Social SDK não devem ser confundidos com endpoints da API de bots; devem ser marcados como fora do escopo ou tratados separadamente.

Fonte primária: [índice oficial de documentação Discord](https://docs.discord.com/llms.txt).

## OAuth2 e escopo da matriz

A documentação oficial trata OAuth2 como uma superfície distinta da autenticação de bot: autorização usa `https://discord.com/oauth2/authorize`, troca usa `https://discord.com/api/oauth2/token` e revogação usa `https://discord.com/api/oauth2/token/revoke`; token e revogação exigem `application/x-www-form-urlencoded`, não JSON. O Pimcord agora possui `ClienteOAuth2` separado, com URL, formulários, troca, renovação, revogação e transporte injetável; continuam pendentes os fluxos completos de instalação, consentimento e interoperabilidade em ambiente real. OAuth2 não deve ser confundido com uma rota REST de recurso de servidor.

Fonte primária: [OAuth2](https://docs.discord.com/developers/topics/oauth2).

## Auditoria oficial iniciada — 18/08/2026

A referência oficial atual do Discord informa que a API base usa `https://discord.com/api`, que a versão 10 está disponível e é a versão disponível mais recente no quadro consultado, e que IDs Snowflake são retornados como strings no HTTP. A documentação também mantém erros estruturados com `code`, `message` e `errors`, o que deve ser preservado pelo cliente tipado do Pimcord.

A documentação oficial consultada separa pelo menos os recursos de Canais, Servidores/Guilds e Aplicações, além dos grupos indexados no `llms.txt`: OAuth2, Interações e Comandos, Componentes e Modais, Webhooks, monetização/SKUs/assinaturas, onboarding, Soundboard, role connections, templates, invites, audit logs e voz. A matriz local já cobre muitos desses grupos, mas o bloqueador permanece aberto até comparar cada operação HTTP, método, parâmetros, paginação, limite e modelo com a referência atual.

Fontes primárias:
- https://docs.discord.com/developers/reference
- https://docs.discord.com/developers/resources/channel
- https://docs.discord.com/developers/resources/guild
- https://docs.discord.com/developers/resources/application
- https://docs.discord.com/llms.txt

## Auditoria primária adicional — Webhooks, Interações e Canais

A referência oficial de Webhooks confirma tipos Incoming, Channel Follower e Application; `Execute Webhook` aceita `wait`, `thread_id` e `thread_name`, pode exigir multipart para anexos e exige pelo menos um entre `content`, `embeds`, `components`, `file` ou `poll`. O modelo também possui `application_id`, `source_guild`, `source_channel` e `url` opcionais. A referência de Interações confirma `entitlements`, `authorizing_integration_owners`, `context` e `attachment_size_limit`, além dos tipos de componente e modal. A página de Canais informa que, a partir de 16/11/2026, canais sem permissão de visualização serão obfuscados; o cliente deve preservar `obfuscated` e `app_permissions` e aceitar campos ausentes sem assumir que o canal é inexistente.

Fontes consultadas em 18/08/2026: [Webhook Resource](https://docs.discord.com/developers/resources/webhook), [Receiving and Responding to Interactions](https://docs.discord.com/developers/interactions/receiving-and-responding) e [Channels Resource](https://docs.discord.com/developers/resources/channel).


## Revalidação oficial — 18/08/2026

As páginas oficiais atuais confirmam que o Audit Log deve preservar mapas de `application_commands`, `audit_log_entries`, `auto_moderation_rules`, `guild_scheduled_events`, `integrations`, `threads`, `users` e `webhooks`. Também confirmam que `changes` é variável por evento e não deve ser reduzido a um conjunto fechado de chaves; o modelo genérico `AlteracaoAuditoria` mantém `key`, `old_value`, `new_value` e o valor bruto. O motivo de auditoria aceita de 1 a 512 caracteres codificados em UTF-8.

A referência de Interações confirma `guild`, `guild_id`, `channel`, `channel_id`, `member`/`user`, `token`, `version`, `message`, `app_permissions`, `locale`, `guild_locale`, `entitlements`, `authorizing_integration_owners`, `context` e `attachment_size_limit`. A referência OAuth2 confirma os três URLs oficiais e que token/revogação aceitam exclusivamente `application/x-www-form-urlencoded`; a superfície `ClienteOAuth2` permanece alinhada a esse transporte e agora também expõe parâmetros de instalação/consentimento.

Fontes: [Audit Logs](https://docs.discord.com/developers/resources/audit-log), [Receiving and Responding](https://docs.discord.com/developers/interactions/receiving-and-responding) e [OAuth2](https://docs.discord.com/developers/topics/oauth2).


## Auditoria OpenAPI oficial — 2026-08-17

A especificação oficial pública `discord/discord-api-spec` declara OpenAPI 3.1 para a API v10 e alerta que é uma prévia; a própria especificação recomenda seguir a documentação quando houver divergência. O arquivo estável `specs/openapi.json` foi baixado somente para inspeção estática em `/tmp/discord-openapi.json`: 150 caminhos e 242 operações HTTP foram contados. Fonte: https://github.com/discord/discord-api-spec . O repositório oficial de documentação também foi consultado: https://github.com/discord/discord-api-docs . Essa contagem não é uma prova de paridade do Pimcord; serve como referência para a matriz e inclui operações fora do escopo de bots.


A ferramenta `ferramentas/auditar_openapi_rest.py` foi criada para comparação estática. Após reconhecer f-strings, ela identificou 147 operações locais com rota recuperável contra 242 operações do OpenAPI; 235 não tiveram correspondência literal porque a normalização de parâmetros, composição de rotas e operações fora do escopo ainda exigem mapeamento semântico. Este resultado é um diagnóstico de trabalho, não uma medida de cobertura nem uma declaração de inferioridade/superioridade.


A comparação foi refinada para normalizar nomes de parâmetros (`{guild_id}`, `{channel_id}` etc.) para um placeholder comum. O diagnóstico passou a identificar 147 operações locais contra 242 oficiais, deixando 103 sem correspondência semântica fechada. Ainda é uma ferramenta conservadora: não resolve aliases, composição de rotas, métodos indiretos nem separação de escopo, portanto não é prova de paridade.


A superfície do `ClienteHTTP` foi ampliada com `obter_oauth2_atual`, `obter_aplicacao_oauth2_atual`, `obter_chaves_oauth2` e `obter_userinfo_oauth2`, cobrindo os caminhos oficiais de introspecção OAuth2. A auditoria normalizada passou a identificar 151 operações locais contra 242 do OpenAPI, com 99 sem correspondência literal; o relatório continua sendo diagnóstico conservador e não prova de paridade.


A auditoria agrupada foi corrigida: `ferramentas/auditar_superficie_rest.py` percorre a classe `ClienteHTTP`, deduplica nomes públicos e reescreve `docs/REST_AUDITORIA_LOCAL.txt`. O estado atual é 195 métodos públicos únicos e nenhum duplicado; o relatório OpenAPI continua separado, conservador e registra 154 operações locais identificáveis contra 242 oficiais.


A operação oficial de enquete `GET /channels/{channel.id}/polls/{message.id}/answers/{answer.id}` foi adicionada como `listar_votantes_enquete`, com `limit` validado entre 1 e 100 e paginação por `after`. O auditor local registra 196 métodos públicos únicos e o comparador OpenAPI identifica 155 operações locais contra 242 oficiais; a diferença permanece conservadora e exige análise semântica.


A auditoria encontrou duas famílias de pins no arquivo OpenAPI baixado: `/channels/{channel_id}/pins` e `/channels/{channel_id}/messages/pins`, ambas com operações. O cliente segue a rota documentada no endpoint de Pin Message (`/channels/{channel_id}/pins/{message_id}`); a segunda família foi mantida como discrepância da especificação para revisão manual, não como implementação especulativa.


## Marco de validação posterior — 2026-08-18

Marco histórico anterior: a superfície pública do `ClienteHTTP` estava em **243 métodos públicos únicos**, com **190 testes aprovados** e **201 chamadas literais locais contra 242 operações oficiais**. Esse comparador continua conservador e não interpreta todos os caminhos construídos por composição ou ramificações de escopo. O estado atual está registrado no marco mais recente abaixo.

Neste marco foram adicionados contratos e rotas para pins oficiais, reações explícitas, destinatários de DM, sticker específico de servidor, regiões do servidor, boas-vindas de novos membros, busca de mensagens no servidor, contagens de cargos, membro atual, remoção de conexão de cargo, mensagens de webhook por token, Gateway público, sticker packs, instância de atividade, entitlements do usuário, contagens de inscritos em eventos, seguidores de canal, bulk-ban e status de voz. A matriz REST permanece aberta até a comparação operação a operação e a revisão das famílias especializadas.


## Lote de eventos recorrentes e reações — 2026-08-18

Marco histórico anterior: foram adicionadas as operações oficiais de criar, editar e excluir exceções de usuários em eventos agendados recorrentes, além de um método explícito para remover todas as reações de uma mensagem. Os contratos offline cobriram rotas, verbos, payloads e rejeição de edição vazia. Naquele ponto, a suíte tinha **191 testes**, o contador AST **247 métodos públicos únicos** e a auditoria literal **205 de 242 operações**, mantendo 48 lacunas conservadoras para revisão semântica.


## Classificação das lacunas conservadoras — 2026-08-18

A lista OpenAPI ainda mostra chamadas sem correspondência literal que já possuem cobertura por composição, como listagem de comandos globais/por servidor, threads arquivadas e estado de voz `@me`; o auditor literal não resolve essas ramificações. As operações de Lobbies, Partner SDK e metadados de moderação de parceiros permanecem fora da promessa de uma biblioteca de bots e não devem ser implementadas por aparência de paridade. As lacunas que continuam exigindo revisão real incluem exceções agregadas de eventos recorrentes, solicitações de servidor, assinaturas de SKU, widget PNG, anexos de aplicação, ações de incidente e webhooks de integração GitHub/Slack; cada uma precisa de confirmação na referência oficial e contrato próprio antes de ser marcada como coberta.


## Widget PNG e respostas binárias — 2026-08-18

O `ClienteHTTP` passou a aceitar `bruto=True` em `requisitar`, preservando bytes sem tentar decodificação JSON. A operação portuguesa `obter_widget_png` cobre `GET /guilds/{guild.id}/widget.png` e recebeu contrato offline. O marco verificável passou a **248 métodos públicos únicos**, **206 operações literais identificáveis** e **192 testes aprovados**. A auditoria continua conservadora, com **47 operações oficiais sem correspondência literal**, incluindo famílias já cobertas por composição e recursos fora do escopo de bots.


## Marco de inscritos por ocorrência — 2026-08-18

Foi adicionada `listar_inscritos_excecao_evento`, correspondente a `GET /guilds/{servidor_id}/scheduled-events/{evento_id}/{excecao_id}/users`, com `limit` de 1 a 100, cursores `before`/`after`, `with_member` e rejeição local de ocorrência ausente ou cursores conflitantes. O contrato foi executado sem rede.

A auditoria posterior registrou 242 operações oficiais, 207 chamadas literais identificáveis, 46 lacunas conservadoras e 249 métodos públicos únicos no cliente REST. As lacunas incluem recursos fora do escopo de bots, rotas compostas já cobertas pela API e famílias ainda não implementadas; esse número não deve ser interpretado como ausência sem revisão semântica.

O bloqueador de REST continua aberto até a comparação operação a operação e a revisão das integrações oficiais. A validação não declara paridade total.


## Solicitações de servidor — revisão semântica

A consulta à referência oficial de Guilds não confirmou uma família pública de rotas `requests` para a API de bots. Por isso, as entradas conservadoras relacionadas a solicitações permanecem **não confirmadas**, e não serão transformadas em métodos Pimcord sem método, payload e resposta documentados. A decisão evita criar uma API que pareça completa, mas não seja interoperável com o Discord.


## Revisão de falsos positivos compostos — 2026-08-18

A inspeção direta do `ClienteHTTP` confirmou cobertura local para templates (`listar_templates`, `obter_template`, criação, edição, exclusão e sincronização), pins (`listar_pins` e operações por mensagem), convites de canal/servidor, widget JSON/PNG, preview de servidor, instância de atividade, sons padrão/por servidor e inscritos normais ou por ocorrência. O relatório OpenAPI continua literal e, portanto, pode listar essas rotas quando a composição dos parâmetros ou o nome português não é normalizado.

Essas confirmações reduzem o espaço de implementação segura; nenhuma rota não documentada foi criada apenas para diminuir o contador de lacunas.


## Anexo efêmero de Activity — marco OAuth2

`ClienteOAuth2.criar_anexo_atividade` foi adicionado com transporte injetável, bearer explícito, bytes, nome e MIME validados. O contrato offline confirma a rota `POST /applications/{application_id}/attachment` e a documentação AST foi regenerada. Como essa operação pertence ao fluxo de Activities com bearer/OAuth2, ela não altera a contagem de operações do `ClienteHTTP`: a métrica permanece em 207 operações literais e 249 métodos REST únicos; a suíte integral passou a 194 testes.


## Exceções agregadas de eventos recorrentes — decisão de escopo

A referência pública oficial de Guild Scheduled Events consultada descreve o objeto de exceção e a recorrência, mas não apresentou no conteúdo público extraído um contrato REST suficiente para o `POST /guilds/{servidor_id}/scheduled-events/{evento_id}/exceptions` — especialmente payload, permissões e resposta normativos. A documentação secundária foi usada apenas como pista e não como autoridade. O Pimcord mantém as operações individuais já confirmadas e não implementará a rota agregada por especulação. A entrada continua classificada como lacuna conservadora até existir contrato oficial completo.


## Incident Actions — marco atual — 2026-08-18

`ClienteHTTP.modificar_acoes_incidente` foi adicionado para `PUT /guilds/{servidor_id}/incident-actions`, usando os campos oficiais `invites_disabled_until` e `dms_disabled_until`. O método aceita timestamps ISO8601 ou `None`, rejeita campos desconhecidos, corpo vazio e tipos inválidos localmente, e possui contratos offline de rota, verbo e JSON. A suíte passou a **196 testes**, o contador AST confirmou **250 métodos públicos únicos** e a auditoria literal reconhece **208 de 242 operações oficiais**, mantendo **45 lacunas conservadoras**. Essa operação não encerra o bloqueador REST, que ainda exige comparação operação a operação.
