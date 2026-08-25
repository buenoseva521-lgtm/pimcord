# Matriz de paridade do Pimcord

O Pimcord 0.5.0 possui uma API pública em português para criação de bots Discord. Esta matriz separa o que já está disponível do que ainda exige implementação adicional, para que a documentação não prometa recursos inexistentes.

## Disponível

| Área | Recursos |
|---|---|
| Bot | prefixo, lifecycle básico, eventos, tarefas e diagnóstico |
| Comandos | aliases, argumentos tipados, grupos, checks, cooldowns e hooks |
| Gateway | Hello, Identify, heartbeat, ACK, Resume básico, reconexão e eventos genéricos |
| REST | requisições assíncronas, mensagens, embeds, componentes, buckets e retries |
| Modelos | usuário, membro, cargo, anexo, canal, servidor e mensagem |
| Interações | slash command básico, resposta inicial e followup inicial |
| Componentes | View, botões, selects, opções e modais serializáveis |
| Plataforma | extensões, cache, tarefas, banco SQLite, métricas, webhooks e shards |
| Ferramentas | CLI de versão, diagnóstico e geração inicial de projeto |

## Em desenvolvimento

A implementação completa de autocomplete, permissões por comando, grupos de slash, componentes persistentes após reinício, edição de respostas de interação, paginação REST, uploads multipart, cache de membros e modelos de todas as entidades Discord deve ser acompanhada por testes de contrato.

A camada de voz exige um transporte próprio, UDP, codecs, criptografia e player. Ela deve permanecer opcional em `pimcord[voz]` e não deve ser anunciada como funcional até possuir testes com um servidor de voz real ou simulado.

Sharding possui o cálculo de distribuição e o lifecycle inicial no pacote, mas a coordenação entre processos, identificação por shard, rate limits distribuídos e supervisão de workers ainda precisam ser finalizados para operação em escala.

## Princípios de compatibilidade

A API pública deve usar nomes em português, manter aliases quando isso ajudar a migração e evitar expor módulos internos. Toda mudança incompatível deve aumentar a versão principal e entrar no changelog. Recursos experimentais devem estar identificados na documentação.

O token do Discord nunca pertence ao pacote. Cada usuário configura suas próprias credenciais por variável de ambiente ou provedor seguro de secrets.
