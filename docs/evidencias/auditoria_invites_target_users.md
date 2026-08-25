# Evidência REST — Convites com usuários-alvo

Fonte oficial: https://docs.discord.com/developers/resources/invite
Fonte complementar: https://docs.discord.com/developers/tutorials/using-community-invites

A documentação oficial confirma três operações distintas:

| Operação | Rota | Contrato |
|---|---|---|
| Obter usuários-alvo | `GET /invites/{invite.code}/target-users` | Resposta CSV com cabeçalho `user_id`; exige ser criador do convite, `MANAGE_GUILD` ou `VIEW_AUDIT_LOG`. |
| Atualizar usuários-alvo | `PUT /invites/{invite.code}/target-users` | Multipart com campo `target_users_file`, CSV de uma coluna de IDs; IDs inválidos retornam erro 400 detalhado. Exige ser criador ou `MANAGE_GUILD`. |
| Ver status do processamento | `GET /invites/{invite.code}/target-users/job-status` | Processamento assíncrono; resposta contém `status`, `total_users`, `processed_users`, `created_at`, `completed_at` e `error_message`. |

A fonte complementar confirma que `target_users_file` também pode ser enviado na criação do convite em multipart, junto a `payload_json`, e que a funcionalidade é destinada a bots/aplicações com permissões adequadas. Esta evidência não prova que qualquer lacuna local seja realmente ausente: a implementação deve ser inspecionada para distinguir rota literal, composição interna e suporte multipart antes de alterar o cliente.
