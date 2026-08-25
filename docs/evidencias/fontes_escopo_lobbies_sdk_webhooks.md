# Fontes oficiais — escopo REST especial

## Lobbies

Fonte: https://docs.discord.com/developers/resources/lobby

A referência oficial descreve Lobbies como recursos de matchmaking associados ao Discord Social SDK. Ela documenta criação, ingresso, alteração, exclusão, membros, convites, mensagens e metadados de moderação. A própria fonte informa que clientes Discord Social SDK não conseguem ingressar ou sair de um lobby criado pela API HTTP da mesma forma que `Client::CreateOrJoinLobby`, indicando uma superfície distinta da API tradicional de bots.

## Discord Social SDK

Fonte: https://docs.discord.com/developers/discord-social-sdk/overview

O Social SDK é apresentado como uma plataforma para integrar recursos sociais do Discord diretamente em jogos, incluindo lobbies, convites, voz, contas provisórias e comunicação. Portanto, operações `/lobbies` devem ser auditadas como uma integração de escopo próprio, não automaticamente como lacunas de um cliente de bot compatível com discord.py.

## Webhooks

Fonte: https://docs.discord.com/developers/resources/webhook

A referência oficial distingue webhooks de entrada, de seguidores de canal e de aplicação. Ela confirma o CRUD e execução geral já cobertos pelo Pimcord; as rotas específicas GitHub/Slack devem ser tratadas como integrações de webhook separadas, não como ausência do CRUD ou da execução de webhook. A fonte também confirma que webhooks não exigem usuário bot ou autenticação para uso em determinados fluxos.

## Conclusão de escopo

Essas fontes sustentam uma classificação conservadora: lobbies e Partner/Social SDK não devem ser implementados ou contabilizados como paridade comum de bots sem autenticação, público-alvo e contratos específicos. GitHub/Slack também requerem uma decisão separada entre conveniência de integração e superfície HTTP central.
