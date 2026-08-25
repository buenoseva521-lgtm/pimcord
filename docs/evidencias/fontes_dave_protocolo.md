# Fontes externas sobre DAVE

## Fontes consultadas

1. Discord DAVE Protocol: https://daveprotocol.com/
2. Repositório oficial do protocolo: https://github.com/discord/dave-protocol/blob/main/protocol.md
3. Binding Python `dave.py`: https://github.com/DisnakeDev/dave.py

## Evidências relevantes

A especificação oficial descreve DAVE como MLS facilitado pelo Voice Gateway. A criação inicial do grupo depende de KeyPackages, propostas, commit e welcome; quando a lista de participantes muda, ocorre transição de época e novos ratchets por remetente. O protocolo também exige preparação/execução de transições e retenção temporária de chaves durante a transição.

A especificação confirma que a transformação de mídia ocorre sobre frames codificados antes/depois do RTP, com chaves ratcheted por remetente. Portanto, inicialização de `Session`, geração de KeyPackage, `set_external_sender` e rejeição fail-closed não constituem prova completa de interoperabilidade.

O repositório `dave.py` informa que os bindings são para `libdave`, disponibiliza a API Python e aponta a implementação de referência TypeScript `DaveSessionManager.ts`; não fornece, na página consultada, um vetor completo público de sessão Discord pronto para uso offline.

## Conclusão operacional

O Pimcord possui evidência positiva de inicialização nativa isolada, mas ainda precisa de vetores oficiais de commit/welcome ou uma sessão real para comprovar interoperabilidade cruzada. Nenhum payload MLS será inventado com base apenas na descrição da API.

## Implementação de referência do libdave

Fonte: https://github.com/discord/libdave/blob/main/samples/typescript/DaveSessionManager.ts

A referência pública confirma a ordem operacional: `PREPARE_EPOCH` com época 1 inicializa a sessão e envia KeyPackage; `MLS_EXTERNAL_SENDER_PACKAGE` configura o external sender; `MLS_PROPOSALS` chama `ProcessProposals` e envia o resultado como `MLS_COMMIT_WELCOME`; `MLS_PREPARE_COMMIT_TRANSITION` processa commit e prepara ratchets; `MLS_WELCOME` processa welcome e prepara ratchets; depois o cliente sinaliza readiness e executa a transição. A própria amostra deixa o envio ao Voice Gateway como TODO e não inclui payloads Discord reais, portanto ela orienta a máquina de estados, mas não constitui um vetor interoperável pronto.

Conclusão: podemos validar a ordem e as invariantes localmente, mas não marcar DAVE como interoperável sem um commit/welcome produzido por uma negociação real ou por vetores oficiais equivalentes.

## Busca de fixtures públicos

A consulta ao repositório `discord/libdave` confirmou as bibliotecas C++/JS e os exemplos TypeScript, mas não revelou na página pública consultada um diretório de testes com fixtures de commit/welcome exportáveis. A busca não será convertida em payloads inventados. O bloqueador de interoperabilidade permanece válido.

## Inspeção dos testes públicos de `dave.py`

O repositório público `DisnakeDev/dave.py` contém `test_basic.py`, que verifica a versão máxima, `test_python.py`, que cobre apenas geração de código exibível, e `test_leaks.py`, que verifica coleta de ciclo de referência. Não há nesses testes um vetor de negociação MLS com commit/welcome, roster estabelecido ou transformação de frame. Essa ausência confirma que o smoke nativo local não pode ser promovido, por si só, a prova de interoperabilidade Discord.

## Voice Gateway e opcodes DAVE confirmados

A documentação oficial de Voice Connections e o protocolo DAVE confirmam que o Identify de voz inclui `max_dave_protocol_version`. O protocolo usa, entre outros, `dave_protocol_execute_transition` (22), `dave_protocol_ready_for_transition` (23) e `dave_protocol_prepare_epoch` (24). Algumas mensagens DAVE são binárias e seguem o envelope de número de sequência opcional big-endian uint16, opcode uint8 e payload variável. A implementação atual de `pimcord/gateway/cliente.py` trata somente o Gateway geral em JSON e não possui um Voice Gateway/UDP DAVE transport; portanto, não deve fingir que o fluxo já está ligado ao transporte real.

Fontes: https://docs.discord.com/developers/topics/voice-connections e https://github.com/discord/dave-protocol/blob/main/protocol.md.
