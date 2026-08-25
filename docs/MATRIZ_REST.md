# Matriz de paridade REST do Pimcord

> Esta matriz é um instrumento de validação, não uma declaração de paridade completa. Uma família só pode ser marcada como concluída quando a operação HTTP, parâmetros, limites, paginação, erros e modelo correspondente tiverem contrato offline e comparação com a referência oficial vigente.

## Critério de classificação

| Estado | Significado |
|---|---|
| Coberto | Há método público, rota e contrato offline representativo. |
| Parcial | A rota principal existe, mas ainda falta parâmetro, modelo, paginação ou evento relacionado. |
| Auditoria | A superfície local existe, mas a comparação operação a operação ainda não foi encerrada. |
| Fora do escopo | Recurso não pertence à API de bots que o Pimcord promete suportar; deve permanecer documentado para evitar falsa equivalência. |

## Matriz por família

| Família oficial | Superfície local identificada | Estado | Lacuna verificável |
|---|---|---|---|
| Canais e mensagens | Mensagens, reações, pins, threads, permissões, histórico e exclusão em lote | Auditoria | Confirmar todos os filtros, limites, obfuscação e campos opcionais do parser. |
| Servidores | CRUD, membros, cargos, banimentos, podar, preview, convites, templates e canais | Auditoria | Comparar paginação, limites e parâmetros de cada operação; validar campos novos do recurso Guild. |
| Auditoria | Consulta e conversão tipada de entradas, usuários, integrações, comandos, automoderação, eventos agendados, threads e webhooks | Auditoria | Comparar todos os mapas de recursos referenciados e detalhes de alterações com a referência oficial vigente. |
| Aplicações | Aplicação, comandos globais/servidor, permissões, emojis, SKUs, assinaturas e entitlements | Auditoria | Auditar payloads, modelos e eventos de lifecycle de assinatura/entitlement. |
| OAuth2 | URL, troca, renovação, revogação e transporte injetável form-urlencoded | Parcial | Validar instalação/consentimento e fluxos reais; não misturar com autenticação Bot. |
| Interações | Callback, contexto, entitlements, proprietários autorizadores, limite de anexos, follow-up original e follow-up por ID | Auditoria | Comparar tipos de resposta, componentes/modais e limites atuais com a referência vigente; limites locais de botão, select, input e modal já são validados. |
| Webhooks | CRUD por aplicação/canal/servidor, token e execução | Auditoria | Confirmar operação por operação os parâmetros de edição, permissões, resposta 204, modelos tipados e eventos Webhooks Update; payload, `wait`, threads, poll, aliases portugueses e multipart já têm contratos locais. |
| Automoderação | CRUD de regras e motor offline-first próprio | Auditoria | Comparar campos e ações oficiais, além de manter o motor nativo mais rígido que a API. |
| Eventos agendados | CRUD, inscritos, paginação e modelos | Auditoria | Comparar entidade, contagem, campos opcionais e limites de inscritos. |
| Voz | Regiões, estado de voz e Voice Resource | Parcial | Confirmar ciclo completo de Voice State/Server Update e integração criptográfica DAVE/MLS. |
| Soundboard | Sons de servidor, som padrão, CRUD e modelos | Auditoria | Confirmar multipart, permissões, limites e mudanças futuras do recurso. |
| Stickers e emojis | Listagem, CRUD e multipart de stickers | Auditoria | Comparar formatos, limites de upload, campos opcionais e mensagens de erro. |
| Role Connections | Metadados e atualização da conexão de cargo | Auditoria | Validar tipos de metadado, OAuth2 e resposta modelada em todos os fluxos. |
| Onboarding e Discovery | `obter_onboarding` e `editar_onboarding`; campos de descoberta preservados no modelo de servidor | Auditoria | Comparar payload/limites do onboarding e confirmar se rotas de Discovery pertencem à API de bots suportada. |
| Templates e invites | `listar_templates`, `obter_template`, `criar_template`, `editar_template`, `excluir_template`, `sincronizar_template`; convites de canal/servidor e CRUD de convite | Auditoria | Confirmar todos os parâmetros, permissões, expiração, limites e resposta modelada operação a operação. |
| Gateway e intents | Gateway Bot, sharding e intents locais | Auditoria | Comparar eventos e payloads oficiais; não tratar REST como substituto do Gateway. |
| Social SDK | Não é assumido pelo cliente de bots | Fora do escopo | Documentar explicitamente a separação para não prometer suporte indevido. |

## Gaps prioritários para fechar o bloqueador

Primeiro, concluir a auditoria de `Audit Log` comparando todos os mapas de recursos referenciados e detalhes de alterações; os principais mapas, incluindo comandos de aplicação, já possuem preservação/tipagem local. Segundo, concluir a comparação oficial de Webhooks operação a operação; `wait`, threads, multipart e poll já têm contratos locais. Terceiro, concluir a comparação oficial da matriz de Interações/Componentes/Modais e seus follow-ups; limites locais e multipart já estão cobertos. Quarto, inventariar Onboarding, Discovery e Templates operação a operação. Quinto, validar eventos de monetização e o ciclo Voice/DAVE/MLS em conjunto.

## Evidência local atual

Marco histórico anterior: a auditoria AST local registrava **247 métodos públicos únicos**, a suíte offline **191 testes aprovados** e a auditoria OpenAPI conservadora **205 chamadas literais locais contra 242 operações oficiais**, com 48 sem correspondência literal. O marco atual está no relatório `docs/AUDITORIA_OPENAPI_LOCAL.md` e no histórico mais recente de `docs/NOTAS_REST_PARIDADE.md`: **250 métodos públicos únicos no ClienteHTTP**, **196 testes aprovados** e **208 operações literais**, com 45 lacunas conservadoras. O endpoint `modificar_acoes_incidente` cobre `PUT /guilds/{servidor_id}/incident-actions` com os campos oficiais de suspensão de convites e DMs, e o auditor literal passou a reconhecer essa chamada após a regeneração da auditoria. O suporte OAuth2 `criar_anexo_atividade` é documentado separadamente por usar bearer/multipart de Activities e não altera a contagem do ClienteHTTP. Esses números demonstram consistência interna e orientam a revisão, mas não substituem a comparação oficial completa exigida pelo `ROADMAP_TODO.md`.

Fontes primárias usadas no dossiê: [referência da API](https://docs.discord.com/developers/reference), [Canais](https://docs.discord.com/developers/resources/channel), [Servidores](https://docs.discord.com/developers/resources/guild), [Aplicações](https://docs.discord.com/developers/resources/application), [Webhooks](https://docs.discord.com/developers/resources/webhook), [Interações](https://docs.discord.com/developers/interactions/receiving-and-responding), [OAuth2](https://docs.discord.com/developers/topics/oauth2) e [índice oficial](https://docs.discord.com/llms.txt).
