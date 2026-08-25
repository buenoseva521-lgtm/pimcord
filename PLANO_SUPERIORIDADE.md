# Plano mestre de superioridade do Pimcord

## Requisitos confirmados do Gateway

A documentação oficial do Discord exige que o cliente respeite o intervalo de heartbeat recebido no Hello, aplique jitter no primeiro heartbeat, envie a última sequência recebida, processe ACKs e feche conexões zumbis para tentar Resume. O Identify é limitado por `max_concurrency`, e a documentação também descreve limite global de chamadas Identify, Ready, Resume, intents, compressão, rastreamento de estado, disponibilidade de servidores e sharding.

Fontes consultadas:

- Gateway: https://docs.discord.com/developers/events/gateway
- Gateway Events: https://docs.discord.com/developers/events/gateway-events
- API Reference: https://docs.discord.com/developers/reference
- Rate Limits: https://docs.discord.com/developers/topics/rate-limits
- discord.py API Reference: https://discordpy.readthedocs.io/en/latest/api.html

## Critério de conclusão

O Pimcord só poderá ser declarado superior quando cada domínio tiver implementação real, contrato offline, teste de falha e documentação executável. Diferenciais de ergonomia brasileira, simulador offline, diagnóstico e observabilidade contam como superioridade adicional, mas não substituem voz, Gateway, REST, sharding e confiabilidade.

## Domínios

| Domínio | Critério mínimo | Diferencial Pimcord |
|---|---|---|
| Gateway | Hello, jitter, heartbeat, ACK, Identify, Resume, close codes, compressão, intents, estado e sharding | Diagnóstico de sessão e simulador offline |
| REST | Endpoints completos, multipart, paginação, rate limits globais e erros tipados | Cliente declarativo e replay offline |
| Voz | Voice Gateway, UDP, criptografia, Opus, reprodução, gravação e reconexão | Pipeline português de áudio e testes sem Discord |
| Comandos | Prefixo, slash, híbridos, grupos, autocomplete, context menus, checks, cooldowns e sync | Um schema gera todas as formas |
| Interações | Componentes, modais, follow-ups, ephemeral, Views persistentes e concorrência | Reidratação local e diagnóstico de estado |
| Cache | Usuários, membros, servidores, canais, mensagens, presença e voz com invalidação | Cache observável e políticas configuráveis |
| Sharding | Supervisor, workers, health checks, redistribuição e recuperação | Operação distribuída com métricas por shard |
| Qualidade | Tipagem, testes, benchmarks, segurança, CI e versões Python | Compatibilidade Pydroid/Termux e modo offline |
| Ecossistema | CLI, plugins, migração, documentação gerada e exemplos testados | Ferramentas totalmente em português |

## Requisitos confirmados de voz

A conexão de voz exige enviar Voice State Update e aguardar tanto `VOICE_STATE_UPDATE` quanto `VOICE_SERVER_UPDATE`. Depois são necessários `session_id`, token e endpoint para abrir o Voice WebSocket, enviar Identify e processar Ready com SSRC, IP, porta, modos e intervalo de heartbeat. O cliente precisa manter heartbeat com nonce e `seq_ack`, abrir UDP, fazer IP Discovery quando necessário e enviar Select Protocol. A documentação atual também descreve modos AEAD modernos, compatibilidade legada e DAVE/MLS para chamadas com E2EE; a implementação não pode assumir que XSalsa20 é a única opção.

Fonte: https://docs.discord.com/developers/topics/voice-connections

## Estado do marco de voz

Implementado nesta rodada: `SessaoVoz`, `ClienteGatewayVoz`, Voice Identify/Ready/Heartbeat, `seq_ack`, seleção de modo, `TransporteUDP`, pacote RTP, fontes PCM/WAV/silêncio, `FilaAudio`, gravador WAV e integração do Bot em português.

Ainda não concluído: codec Opus real, criptografia AEAD/XSalsa20, DAVE/MLS, IP Discovery automático completo, recepção e interpolação de áudio, reconexão de Voice Gateway, gravação de áudio recebido e reprodução integrada com arquivo/stream. Portanto, a camada está preparada e testada offline, mas ainda não deve ser anunciada como voz completa de produção.

## Checkpoint técnico — 16/08/2026

A suíte offline passou com 40 testes. O pacote de checkpoint contém 86 arquivos e foi validado por listagem e SHA-256: `372381c063de034063247ace0aa2200b002d070dc362bea2bd38afc683602075`.

## Estado revisado do marco de voz e automação

- Voice Gateway: handshake, heartbeat, sequência, reconnect cooperativo e sinalização de fala implementados.
- UDP: transporte injetável, RTP e IP Discovery implementados para contratos e integração progressiva.
- Áudio: PCM, silêncio, WAV, gravador WAV, fila limitada e codec de identidade implementados sem dependências nativas.
- Codecs/segurança: adaptadores opcionais com mensagens mobile; XChaCha20/DAVE não são simulados e continuam exigindo implementação compatível real.
- Automação: agendador com retry/backoff/jitter, fila assíncrona e extensões com dependências/rollback integrados ao Bot.
- Validação: 40 testes passando após a última correção.

- Correção adicional: IP Discovery agora procura o terminador NUL real no pacote UDP e extrai endereço/porta corretamente.
- Validação atual: 42 testes aprovados após a correção.


## Atualização técnica — validação de 17/08/2026

A suíte offline alcançou 68 testes aprovados. A compilação em Python 3.12.3 foi concluída e o wheel 0.7.0 contém `py.typed`, coordenação e segurança. O supervisor de shards foi exercitado com 100 shards concorrentes, 100 leases e 100 estados publicados; dois supervisores disputando oito shards também foram validados sem dupla posse.

A coordenação agora possui `Lease`, `TransporteCoordenação` e `CoordenaçãoLocal`, com época monotônica, renovação, expiração, liberação e publicação de estado. O Gateway e o cliente REST instalam redaction automática nos próprios loggers. Auditoria recebeu objetos tipados para alterações e opções; entitlements e assinaturas de aplicação receberam modelos e métodos REST modelados.

A superioridade total ainda não está demonstrada. Permanecem bloqueadores explícitos: codec Opus real, recepção/interpolação de áudio, DAVE/MLS compatível com a especificação vigente, cobertura integral de endpoints REST, execução comprovada em Python 3.11 e 3.13 e uma matriz de falhas/carga mais longa. Nenhum desses pontos deve ser substituído por mock ou alegação documental.
