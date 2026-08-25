# Notas de pesquisa DAVE/MLS

## Fontes primárias

1. [DAVE protocol v1.1 — discord/dave-protocol](https://github.com/discord/dave-protocol/blob/main/protocol.md)
2. [Discord Voice Connections](https://docs.discord.com/developers/topics/voice-connections)
3. [Meet DAVE: Discord's New End-to-End Encryption for Audio & Video](https://discord.com/blog/meet-dave-e2ee-for-audio-video)

## Fatos técnicos extraídos

O protocolo DAVE documentado no repositório oficial está na versão 1.1. Ele usa MLS como troca de chaves em grupo; cada época MLS produz chaves simétricas ratcheadas por remetente. Mudanças de participantes alteram a época e as chaves: novos participantes não devem decifrar mídia anterior e participantes que saem não devem decifrar mídia futura.

A negociação de versão ocorre no Voice Gateway. O cliente anuncia a maior versão suportada no Identify; o gateway informa a versão inicial no Select Protocol ACK. Mudanças podem usar `dave_protocol_prepare_epoch` opcode 24, `dave_protocol_ready_for_transition` opcode 23 e `dave_protocol_execute_transition` opcode 22. Durante a transição, chaves de épocas anteriores podem ser mantidas por até dez segundos para mídia em trânsito.

A documentação de voz recomenda a versão 8 do Voice Gateway. O Identify de voz inclui `max_dave_protocol_version`. O gateway informa Ready com SSRC, IP, porta e modos. A documentação destaca que o `heartbeat_interval` correto vem do Hello, não do Ready. O DAVE adiciona mensagens binárias com sequência opcional big-endian uint16, opcode de um byte e payload variável.

O Discord mantém uma biblioteca aberta chamada `libdave`, indicada pela documentação como possível referência de implementação. O DAVE usa uma chave de identidade ECDSA P-256 por participante/dispositivo e códigos de verificação; a autenticação da época pode ser comparada fora de banda. A camada de mídia aplica transformação depois do encode e antes do packetizer/depacketizer, com tratamento específico por codec.

## Consequências para o Pimcord

Não é correto implementar DAVE/MLS como um simples modo de `AESGCM` ou `XSalsa20`: é necessário modelar negociação de versão, key packages, grupo MLS, épocas, commits, transições, ratchet por remetente, verificação e mensagens binárias. A implementação atual deve permanecer declaradamente incompleta até existir backend compatível real ou integração validada com uma biblioteca MLS/DAVE auditável. 

## libdave oficial

O repositório oficial `discord/libdave` contém bibliotecas JS e C++ usadas pelos clientes nativos. O README JS documenta o pacote `@discordapp/libdave`, usado para verificações fora de banda dos membros DAVE e do autenticador da época MLS, com dependências JS `@noble/hashes` e `base64-js`. As fontes oficiais consultadas não oferecem um binding Python oficial nem um wheel multiplataforma. Portanto, o caminho seguro para o Pimcord é criar uma interface de backend DAVE/MLS injetável e um adaptador nativo opcional documentado, não uma implementação Python parcial apresentada como E2EE completo.
