

## Fontes oficiais consultadas em 2026-08-18

A documentação oficial do Discord confirma que o Voice Gateway deve usar `?v=8`; o handshake começa com Opcode 4 no Gateway principal, aguarda simultaneamente `VOICE_STATE_UPDATE` e `VOICE_SERVER_UPDATE`, depois usa Opcode 0 Identify com `max_dave_protocol_version`. O Opcode 2 Ready fornece SSRC, IP, porta e modos; o `heartbeat_interval` do Ready deve ser ignorado, pois o intervalo correto vem do Opcode 8 Hello. O cliente executa IP Discovery por UDP, envia Opcode 1 Select Protocol e só então inicia mídia. Fonte: https://docs.discord.com/developers/topics/voice-connections

A mesma documentação descreve DAVE como MLS para troca de chaves, com mensagens binárias contendo sequência opcional uint16, opcode uint8 e payload; o protocolo oficial está em https://github.com/discord/dave-protocol/blob/main/protocol.md. O protocolo exige negociação de versão, mudanças de época e ratchets de mídia por remetente. Fonte adicional: https://discord.com/blog/every-voice-and-video-call-on-discord-is-now-end-to-end-encrypted

Critério derivado: testes offline de parser não provam interoperabilidade. É necessário observar uma sessão autorizada real ou executar fixtures oficiais compatíveis para validar handshake, UDP, Select Protocol, DAVE/MLS e mídia.
