# Changelog

## [0.6.9] — Voz modular, áudio e automação resiliente
- Voice Gateway ganhou loop cooperativo, reconexão exponencial e processamento de mensagens.
- Voz ganhou IP Discovery, fontes WAV/PCM/silêncio, fila de áudio limitada, gravador WAV e adaptadores opcionais de Opus/criptografia.
- `Agendador`, `TarefaAgendada`, `PoliticaRetentativa` e `FilaAssincrona` adicionados com backoff, jitter, cancelamento e consumidores concorrentes.
- Gerenciador de extensões ganhou dependências, carregamento em lote, rollback e diagnóstico.
- Autocomplete em português foi adicionado com `autocomplete(...)`, `responder_autocomplete()` e resposta limitada a 25 sugestões.
- A suíte de contratos offline alcançou 44 testes aprovados.
- Criptografia opcional de voz passou a suportar AES-256-GCM e XSalsa20-Poly1305 quando os backends estão instalados; XChaCha20/DAVE continuam exigindo adaptador compatível real.
- `SessaoVoz.construir_audio()` e `enviar_audio()` aceitam criptografador opcional e preservam o cabeçalho RTP durante a cifragem da carga.
- Gateway passou a tratar close codes 4004, 4007, 4009, 4011, 4013 e 4014 com diagnóstico em português, limpeza de sessão ou encerramento controlado.
- `GerenciadorDeShards` foi ampliado para supervisionar shards com estado, health check, reinício exponencial, limite de tentativas e encerramento cooperativo; coordenação distribuída externa continua exigindo um adaptador de transporte.
- A suíte de contratos offline alcançou 51 testes aprovados.
- Gateway passou a negociar `compress=zlib-stream` e decodificar pacotes binários zlib, com teste offline do fluxo compactado.
- A suíte de contratos offline alcançou 52 testes aprovados.
- Coordenação distribuída offline-first adicionada com `Lease`, `TransporteCoordenação` e `CoordenaçãoLocal`, incluindo exclusividade, épocas monotônicas, renovação, expiração e publicação de estado.
- O pacote passou a incluir `py.typed` conforme PEP 561; o wheel 0.6.9 foi validado com o marcador presente.
- A suíte de contratos offline alcançou 64 testes aprovados.
- Supervisor de shards passou a aceitar transporte de coordenação com lease por shard, publicação de estado e espera cooperativa por posse.
- Adicionados `FiltroSegredos`, `token_redigido` e marcador `py.typed` para segurança e suporte a verificadores estáticos.
- Auditoria ganhou alterações/opções tipadas; entitlements e assinaturas de aplicações ganharam modelos e métodos REST modelados.
- A suíte de contratos offline alcançou 68 testes aprovados.
- Carga local validada com 100 shards concorrentes, 100 leases e 100 estados publicados.
- Disputa entre dois supervisores validada com exclusividade de posse em 8 shards; nenhum shard foi processado por dois donos.
- Adicionado `CodecOpus` real via `libopus` com encode/decode, bitrate configurável e fallback explícito para `opuslib`; o adaptador `CodificadorOpus` preserva a API em português.
- A suíte de contratos offline alcançou 69 testes aprovados, incluindo round-trip de um frame Opus quando o backend nativo está disponível.
- RTP ganhou desserialização validada, suporte a CSRC/extensões e `BufferJitter` com retenção fora de ordem, wrap-around e descarte de duplicatas.
- A suíte de contratos offline alcançou 72 testes aprovados após os contratos de recepção RTP.
- `SessaoVoz.receber_audio()` passou a integrar desserialização RTP, `BufferJitter` e decodificação opcional, mantendo interpolação e mixagem explicitamente fora do escopo atual.
- A suíte de contratos offline alcançou 73 testes aprovados.
- Adicionada a camada explícita de negociação DAVE com `OpcodeDAVE`, `MensagemDAVE` e `EstadoDAVE`: versões, épocas, key packages delegados e transições binárias são modelados sem apresentar um backend MLS fictício como E2EE.
- A suíte de contratos offline alcançou 76 testes aprovados.
- Cliente REST ganhou onboarding de servidores, sons padrão do Soundboard e metadados de conexões de cargo da aplicação, com contratos sem rede.
- A suíte de contratos offline alcançou 77 testes aprovados.
- `SessaoVoz.receber_audio()` passou a aceitar um gravador injetável para persistir frames decodificados em ordem; interpolação, mixagem e política de perdas continuam fora do escopo.
- O contrato offline do `GravadorWAV` valida cabeçalho e persistência PCM usando apenas a biblioteca padrão.
- A suíte de contratos offline alcançou 78 testes aprovados.
- Auditoria da referência oficial adicionou `obter_som_servidor()` e `enviar_som()`, cobrindo Soundboard individual e envio para canal com servidor de origem opcional.
- Cliente REST ganhou `obter_url_personalizada()`, `obter_estado_voz()` e `alterar_estado_voz()` conforme a referência oficial de Guild/Voice Resource.
- O payload de voz foi alinhado aos campos oficiais `suppress` e `request_to_speak_timestamp`, e `alterar_estado_voz_usuario()` cobre o PATCH de estado de outro usuário.
- `ferramentas/gerar_referencia.py` gera `docs/API.md` offline por AST; o contrato confirma saída determinística e assinaturas públicas em português.
- Coordenação ganhou contratos para duração inválida e rejeição de trabalhador obsoleto; a suíte alcançou 80 testes aprovados.
- Cliente REST ganhou configuração de Widget e operações oficiais de prune com parâmetros de dias, contagem e inclusão de cargos; contratos permanecem offline.
- Métodos de prune rejeitam localmente `dias` fora de 1–30, preservando os limites oficiais antes do transporte; a suíte alcançou 81 testes aprovados.
- Cenário de carga cobre 12 shards concorrentes com duas falhas transitórias por worker e recuperação completa; a suíte alcançou 82 testes aprovados.
- EstadoDAVE rejeita épocas antigas/conflitantes, encaminha mensagens MLS ao backend injetado e só exporta chaves após transição estabelecida; a suíte alcançou 84 testes aprovados. O backend MLS criptográfico real continua não incluso.
- Validação cruzada executada em CPython 3.11.15 e 3.13.14: 83 testes aprovados e 1 ignorado em cada versão porque `libopus` não estava disponível no ambiente; o fallback continua explícito.
- `BufferJitter.avançar_sequencia()` permite descartar lacunas após timeout controlado pelo aplicativo e contabiliza perdas sem fabricar PCM; a suíte alcançou 85 testes aprovados. Interpolação e mixagem continuam fora do escopo.

### Voz modular e transporte RTP
- `SessaoVoz`, `InformacoesVoz`, `PacoteRTP` e `TransporteUDP` adicionados em português.
- Fluxo de Voice State Update, seleção de modo, heartbeat com `seq_ack`, SSRC e construção RTP preparado para codecs e criptografia injetáveis.
- Atalhos `Bot.entrar_em_voz()`, `Bot.voz_do_servidor()` e `Bot.sair_da_voz()` adicionados.
- Contratos offline de voz incluídos sem obrigar FFmpeg, Opus ou dependências nativas em ambientes móveis.

### Identidade brasileira e diferenciais próprios
- API principal priorizada em português; aliases em inglês permanecem apenas como compatibilidade opcional.
- `Simulador` para testar Gateway, mensagens e interações sem token, WebSocket ou rede externa.
- `diagnosticar()` e `bot.diagnostico_saude()` para validar configuração, intents, comandos, Views e saúde antes da conexão.
- `Bot.criar_simulador()` integrado ao fluxo natural do Bot.

### Ergonomia de produção do Bot
- Aliases `add_view`, `get_guild`, `get_channel`, `get_user`, `wait_for`, `setup_hook`, `start` e `run` adicionados ao lifecycle e ao cache.
- Logs automáticos de conexão, identificação, READY, reconexão, heartbeat, encerramento e erros.
- Propriedades públicas `bot.user`, `bot.usuario`, `bot.me`, `bot.id`, `bot.servidores`, `bot.guilds`, `bot.canais`, `bot.latencia`, `bot.latencia_ms`, `bot.conectado`, `bot.estado_conexao` e `bot.ws`.
- Cache local atualizado por READY, GUILD_CREATE/UPDATE/DELETE e CHANNEL_CREATE/UPDATE/DELETE.
- Aliases `close()` e `wait_until_ready()` para lifecycle compatível.

### Expansão REST, modelos e Gateway
- Cliente REST ampliado com mensagens, reações, pins, threads, fóruns, permissões, membros, cargos, bans, auditoria, convites, webhooks, emojis, stickers, integrações, eventos agendados, Stage, automoderação, templates, soundboard, comandos de aplicação, entitlements, DMs e uploads multipart.
- Modelos tolerantes e tipados para threads, tags de fórum, auditoria, convites, webhooks, eventos agendados, Stage, voz, presença, reações, automoderação, enquetes e conexões.
- Catálogo de 71 dispatches Gateway com aliases em português e normalização opcional em objetos modelados, preservando o payload bruto para compatibilidade.
- Erros REST passaram a carregar status, código Discord, erros de validação, rota, método e detalhes de rate limit.
- Testes offline de contrato adicionados para payloads, rotas, uploads e despacho de eventos.

### Marco de expansão
- Comandos híbridos com callback compartilhado entre prefixo e slash.
- Aliases `comando_slash` e `comando_hibrido` para a sintaxe portuguesa.
- Interações com opções estruturadas, `adiar()`, Views em respostas e Views em follow-ups.
- Follow-ups, respostas efêmeras, edição e exclusão da resposta original mantidos no contrato público.
- Suíte local ampliada para validar os contratos de interação sem rede externa.


## 0.6.2
- Atualização dos metadados de empacotamento e do User-Agent REST.
- Inclusão do alias `Mensagem.deletar()` para exclusão em português.
- Consolidação de intents completos, eventos automáticos, follow-ups e respostas efêmeras na linha de paridade.
- Documentação conceitual e guias de arquitetura revisados para o release.

## 0.2.0
- Gateway WebSocket real com Hello, heartbeat, Identify e eventos.
- Cliente REST real para obter Gateway e enviar mensagens.
- Comandos prefixados recebem MESSAGE_CREATE e respondem via ctx.responder().

## 0.1.0
- Núcleo inicial, eventos, cache, tarefas, embeds e SQLite.
