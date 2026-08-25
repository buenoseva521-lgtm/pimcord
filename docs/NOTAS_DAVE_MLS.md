# Notas técnicas para DAVE/MLS

Estas notas orientam a implementação; não representam ainda uma implementação criptográfica completa.

## Fontes normativas

O DAVE usa o MLS como protocolo de troca de chaves em grupo e exporta chaves simétricas por remetente para proteger frames de áudio/vídeo por época. A especificação também descreve mudanças de época quando participantes entram ou saem, verificação por autenticador da época e negociação de versões.

- [Whitepaper oficial do DAVE](https://daveprotocol.com/)
- [Anúncio técnico do Discord](https://discord.com/blog/meet-dave-e2ee-for-audio-video)
- [RFC 9420 — Messaging Layer Security](https://datatracker.ietf.org/doc/rfc9420/)
- [Repositório oficial do protocolo](https://github.com/discord/dave-protocol)
- [Biblioteca de referência libdave](https://github.com/discord/libdave)

## Requisitos que não podem ser simulados

A máquina de estados existente não deve ser chamada de E2EE real. Um backend legítimo precisa validar credenciais MLS, KeyPackages, assinaturas, árvore ratchet, commits, épocas, exporters e a Secret Tree, além de usar uma suíte MLS compatível e AEAD para frames. O transporte do Discord continua sendo um serviço de entrega/coordenação; ele não deve receber as chaves de mídia.

O DAVE também exige cuidado com os frames codificados: o transformador é codec-aware, mantém metadados necessários ao packetizer fora da cifra, valida sequências reservadas e aplica a chave ratcheada por remetente. Portanto, um simples `AES-GCM( pacote_RTP )` não é equivalente ao DAVE.

## Decisões para o Pimcord

O backend será injetável, offline-testável e fail-closed. Na ausência de uma implementação MLS compatível, a sessão deve recusar o modo E2EE em vez de anunciar proteção falsa. A integração com dependência nativa deverá ser opcional e explicitamente identificada; o núcleo não conterá primitivas criptográficas caseiras.

Antes de declarar o bloqueador concluído, serão exigidos vetores de interoperabilidade ou uma biblioteca de referência compatível, testes de round-trip entre participantes, mudança de época após entrada/saída, rejeição de replay, autenticação de credenciais, apagamento de segredos antigos e validação do frame transformado.

## Resultado da auditoria de dependências

A biblioteca oficial [libdave](https://github.com/discord/libdave) fornece implementações em **C++ e JavaScript**, não um pacote Python puro pronto para o Pimcord. O projeto atual possui `cryptography`, mas isso não implementa MLS: primitivas isoladas não substituem a árvore ratchet, o formato wire, validação de KeyPackages, commits, exporters e o transformador codec-aware do DAVE.

Consequentemente, o bloqueador permanece aberto. As opções tecnicamente honestas são um binding nativo opcional para libdave, uma implementação MLS completa baseada em uma biblioteca compatível auditada, ou manter o modo DAVE explicitamente desabilitado até existir backend real. Não será adicionado um adaptador que apenas derive chaves locais e se anuncie como interoperável.

A documentação de build do `libdave` confirma que o núcleo C++ depende de `mlspp` e de OpenSSL ou BoringSSL; o pacote JavaScript serve principalmente à verificação fora de banda e ao autenticador da época. Isso reforça que `cryptography` isolado não é uma implementação DAVE/MLS. Uma integração futura deverá ser um adaptador nativo opcional, com detecção de biblioteca, testes de interoperabilidade e falha fechada quando o artefato não estiver disponível.

## Alternativas Python encontradas em 17/08/2026

Foi encontrado o projeto [`dave.py`](https://github.com/DisnakeDev/dave.py), publicado no PyPI como [`dave.py 1.0.0`](https://pypi.org/project/dave.py/). Ele fornece bindings Python para a implementação C++ oficial `libdave`, com wheels pré-compiladas para muitas plataformas 64-bit, mas não oferece suporte a arquiteturas 32-bit e depende de artefatos nativos. Não deve ser incluído automaticamente no núcleo, porque isso prejudicaria a compatibilidade Pydroid/Termux e exigiria validar a matriz de wheels, ABI e API pública.

Também foi encontrado [`rfc9420 1.0.0`](https://pypi.org/project/rfc9420/), uma implementação Python de MLS que declara suporte a grupos, ratchet tree, commits, Welcome, ciphersuites e vetores RFC. Ela implementa MLS genérico, não DAVE; portanto ainda faltariam o perfil DAVE, integração com o Voice Gateway, autenticador de época, exportação de chaves por remetente e transformadores codec-aware. Antes de adicionar uma dependência de segurança, o Pimcord deve fixar versão, verificar licença, rodar vetores RFC/interoperabilidade e revisar o código. Até essa auditoria, o bloqueador permanece aberto.

A auditoria local do sdist `rfc9420==1.0.0` confirmou licença Apache-2.0, `Development Status :: 3 - Alpha` e dependências `cryptography>=42`, `certifi>=2024.7.4` e `rfc9180>=0.3.0`. O hash SHA-256 do arquivo analisado é `1aea139a4792a5d6176b5184fd93d2424b55a3d2d1d0c2084edca73a2ac2cf9a`. A licença é compatível em princípio, mas o status Alpha e a ausência de um perfil DAVE completo impedem incorporá-lo diretamente como backend de produção nesta versão.

A suíte isolada do sdist `rfc9420==1.0.0` passou com **26 testes aprovados e 2 ignorados** após instalar `pytest` e o extra opcional `aiosqlite` apenas no ambiente temporário. Isso é evidência positiva de consistência interna do pacote MLS, mas não prova interoperabilidade DAVE: ainda faltam o perfil/transformadores DAVE, o binding do Voice Gateway, o autenticador de época e vetores cruzados com libdave/OpenMLS/Discord.

## Auditoria de superfície do núcleo

A ferramenta AST de auditoria não encontrou métodos de produção marcados com `NotImplementedError`. Os caminhos que recusam execução sem backend são intencionais: `CriptografiaVozOpcional` falha quando o modo requer adaptador não injetado, e o contrato DAVE rejeita backend estrutural sem marcador E2EE real. Isso evita transformar fallback ou máquina de negociação em falsa criptografia de produção; a integração libdave/DAVE completa continua pendente.

A verificação do ambiente do Pimcord em 17/08/2026 confirmou que o módulo `dave`/`dave.py` não está instalado. Nenhuma dependência nativa foi adicionada automaticamente; isso preserva a compatibilidade offline e móvel, enquanto o modo E2EE continua recusando execução sem backend real.


## Atualização de disponibilidade em 2026

A página oficial de releases registra `libdave v1.1.1` como release C mais recente consultado, com correção de gerenciamento de memória no C API: [releases do libdave](https://github.com/discord/libdave/releases). O projeto [dave.py](https://github.com/DisnakeDev/dave.py) fornece bindings Python para libdave sob MIT e informa wheels para muitas plataformas 64-bit; arquiteturas 32-bit não são suportadas e o build de origem exige VCPKG_ROOT/vcpkg. A existência desses artefatos torna viável estudar um adaptador nativo opcional, mas não prova que o Pimcord esteja interoperável: ainda são necessários testes de API, Voice Gateway, época, exportação por remetente, transformadores de áudio/vídeo e vetores cruzados. O núcleo móvel não deve instalar a dependência por padrão.

A comunicação técnica do Discord também afirma que clientes sem DAVE deixariam de participar de chamadas a partir de 1º de março de 2026 e descreve a separação entre negociação MLS e workers de transformação de frames; isso aumenta a urgência do bloqueador, mas não autoriza copiar uma cifra ou declarar suporte sem a integração completa: [Bringing DAVE to All Discord Platforms](https://discord.com/blog/bringing-dave-to-all-discord-platforms).


## Auditoria do wheel `dave.py` 1.0.0

O wheel publicado expõe `Session`, `Encryptor` e `Decryptor`, além de `MediaType`, `Codec`, `SignatureKeyPair` e `get_max_supported_protocol_version()`. A sessão não recebe uma mensagem MLS genérica única: ela separa `process_proposals`, `process_commit` e `process_welcome`, e exige `init(version, group_id, self_user_id, transient_key)` antes do uso. O `Encryptor` requer `MediaType`, SSRC, frame e associação de codec; o `Decryptor` requer transição para `IKeyRatchet`. Portanto, o contrato atual `processar_mensagem_mls(dados: bytes)` é deliberadamente insuficiente para um adaptador real. O Pimcord já introduziu e exportou `TipoMensagemMLS`/`MensagemMLSDAVE` para propostas/commit/welcome, com validação de dados e IDs reconhecidos; ainda faltam mapear grupo/usuário/versão no adaptador `dave.py`, integrar SSRC/codec no fluxo de voz e provar época/interoperabilidade. Não será implementado um dispatcher que adivinhe o tipo por bytes, pois isso poderia aceitar mensagens erradas e mascarar falhas de interoperabilidade.

## Registro de validação — dispatch semântico

A máquina `EstadoDAVE` agora oferece `receber_mensagem_mls_tipada(MensagemMLSDAVE)`. O método encaminha exclusivamente por `TipoMensagemMLS` para `processar_propostas`, `processar_commit` ou `processar_welcome`; não interpreta bytes para adivinhar o tipo. O contrato `BackendDAVEEnvelope` foi exportado publicamente, e `exigir_backend_dave_real` passou a exigir esses três processadores além dos marcadores de cifra e autenticador de época.

A suíte offline foi ampliada para cobrir encaminhamento de `COMMIT` e rejeição de backend sem processador semântico: **158 testes passaram**. A verificação do ambiente continua indicando `dave` e `libdave` indisponíveis localmente. Portanto, este marco endurece a fronteira do adaptador, mas não fecha o bloqueador de interoperabilidade DAVE/MLS real; ainda faltam o binding nativo opcional, mapeamento de `Session.init`, grupos/usuários/versões, SSRC/codec e vetores cruzados.

O núcleo continua deliberadamente sem dependência nativa obrigatória para preservar o uso offline e em Pydroid/Termux. Nenhum fallback estrutural deve anunciar E2EE.

## Evidência externa revisada em 18/08/2026

A documentação pública atual do repositório `DisnakeDev/dave.py` confirma que ele é um binding Python para o `libdave` oficial, distribuído como `dave.py`, com wheels pré-compiladas para plataformas 64-bit e ausência de suporte 32-bit; o README não oferece uma API de alto nível estável e remete aos exemplos TypeScript do `libdave`. O repositório oficial `discord/libdave` confirma que as implementações oficiais são C++ e JavaScript.

O protocolo DAVE 1.1 descreve a negociação de versão no Voice Gateway, criação e transição de grupos MLS, exportação de chave simétrica por remetente e transformação de frames codificados antes do packetizer RTP. A comunicação técnica do Discord também confirma que o SSRC identifica o fluxo e que a camada MLS deve ficar separada do worker de transformação. Assim, um adaptador Pimcord válido precisa transportar grupo, usuário, versão, épocas, processadores separados de propostas/commit/welcome e o contexto SSRC/codec; um adaptador que apenas encaminhe bytes ou aplique AEAD sobre o pacote RTP não é equivalente.

Fontes consultadas:
- https://github.com/DisnakeDev/dave.py
- https://github.com/discord/libdave
- https://github.com/discord/dave-protocol/blob/main/protocol.md
- https://discord.com/blog/bringing-dave-to-all-discord-platforms

## Evidência adicional — sequência de sessão nativa

O exemplo oficial `DaveSessionManager.ts` do `libdave` confirma que a sessão nativa é inicializada no preparo de uma nova época com `Init(protocolVersion, groupId, selfUserId, privateKey)`, mas a administração dos usuários reconhecidos e dos ratchets é uma etapa separada. O exemplo chama `GetMarshalledKeyPackage()` para enviar o pacote, processa propostas com a lista de usuários reconhecidos, processa commit/welcome em opcodes distintos, e cria/atualiza um ratchet para cada usuário, inclusive o próprio usuário na transição inicial. A integração de referência também mantém transições por `transitionId` e trata `Reset` quando o protocolo é desabilitado.

O smoke test do wheel `dave.py==1.0.0` em CPython 3.12 confirmou que `SignatureKeyPair.generate(1)` pode ser criado e que `Session`, `Encryptor` e `Decryptor` existem; porém a chamada direta a `Session.init` seguida de `get_marshalled_key_package()` ainda retornou `None` fora do fluxo completo de external sender/negociação, com aviso de leaf node ausente. Isso evidencia que gerar uma chave transitória não basta para declarar grupo MLS estabelecido. O adaptador deve permanecer fail-closed até implementar e testar o fluxo de external sender, propostas, commit/welcome, roster e transições.

Fontes:
- https://github.com/discord/libdave/blob/main/samples/typescript/DaveSessionManager.ts
- https://github.com/DisnakeDev/disnake/pull/1492
- https://github.com/discord/libdave/blob/main/js/README.md

## Evidência nativa corrigida

O smoke test do wheel `dave.py==1.0.0` em CPython 3.12 foi repetido com um ID Discord numérico (`123456789`). Nesse formato, `SignatureKeyPair.generate(1)` + `Session.init(1, 123, "123456789", chave)` produziu um KeyPackage de 392 bytes. O teste anterior com `usuario-1` foi inválido para o domínio Discord e retornou `None`; o adaptador agora rejeita IDs não numéricos antes de chamar o binding.

O script reproduzível `ferramentas/smoke_dave_nativo.py`, executado em ambiente isolado com `dave.py==1.0.0`, confirmou: versão máxima anunciada `1`, símbolos `Session`/`Encryptor`/`Decryptor`/`SignatureKeyPair` presentes, KeyPackage de `392` bytes, external sender disponível, grupo MLS ainda não estabelecido e ratchet do usuário ainda indisponível antes da negociação. Portanto, a inicialização nativa funciona, mas o resultado também demonstra objetivamente por que não se deve anunciar E2EE antes de external sender, roster, commit/welcome, época e ratchets reais.

O `AdaptadorDAVEPy` foi validado contra o wheel real para inicialização e geração de KeyPackage. Ainda não foi declarado E2EE completo: external sender, roster real, commits/welcomes de uma chamada Discord, transições Voice Gateway e cifragem RTP interoperável continuam exigindo vetores reais e ligação no fluxo de voz.

## Integração com voz — contrato offline

`SessaoVoz.ativar_dave()` agora valida `BackendDAVEReal` antes de habilitar a camada protegida. Quando o SSRC chega no pacote READY do Voice Gateway, o adaptador recebe `tipo=audio`, SSRC e codec Opus. Frames outbound passam pelo `cifrar_frame` antes da serialização RTP; frames inbound exigem `remetente_id` explícito e passam pelo `decifrar_frame` antes do decoder. O caminho legado permanece inalterado quando DAVE não é ativado.

O contrato offline cobre ativação fail-closed, transformação RTP outbound e decifragem inbound. Isso prova a ligação arquitetural, mas não prova interoperabilidade com uma chamada Discord real: ainda faltam vetores reais de roster/commit/welcome, transições de Voice Gateway e validação cruzada de RTP protegido.


## Evidência nativa adicional — 2026-08-18

No venv isolado `/tmp/pimcord-dave-venv`, o wheel nativo expôs `Session`, `Encryptor`, `Decryptor` e `SignatureKeyPair`, anunciou a versão máxima 1, gerou KeyPackage de 392 bytes e informou `set_external_sender`; antes da negociação, o grupo e o ratchet permanecem indisponíveis.

O smoke `ferramentas/smoke_adaptador_dave_real.py` inicializou `AdaptadorDAVEPy` contra o módulo nativo real, gerou KeyPackage de 391 bytes e associou `audio`/SSRC 42 ao codec `opus`. O grupo ainda não estava estabelecido, portanto a transformação de frames não foi executada. Essa evidência confirma inicialização e configuração de mídia, mas **não** confirma commit/welcome interoperável, retenção de ratchets, cifragem/decifragem cruzada nem sessão real com Discord.


## Smoke nativo de rejeição — 2026-08-18

O script `ferramentas/smoke_dave_rejeicao.py` executado contra o wheel nativo `dave.py` 1.0.0 inicializa uma sessão real e envia bytes MLS inválidos para propostas, commit e welcome. O commit produz rejeição convertida pelo adaptador em `RuntimeError`; propostas e welcome retornam sem efeito enquanto não existe estado MLS local estabelecido. Resultado reproduzível: `{"commit": "RuntimeError", "propostas": "rejeitado-sem-efeito", "welcome": "rejeitado-sem-efeito"}`.

Essa evidência confirma comportamento fail-closed para entradas inválidas no estado pré-grupo. Ela **não** prova a geração, aceitação ou interoperabilidade de um commit/welcome válido, nem habilita transformação de frames; esses pontos continuam bloqueadores.


## Inventário nativo adicional — 2026-08-18

O inventário reproduzível de `dave.py` 1.0.0 confirmou que `Session` expõe `process_proposals`, `process_commit` e `process_welcome`, além de `get_key_ratchet`, `get_pairwise_fingerprint`, `get_last_epoch_authenticator` e `get_marshalled_key_package`. O wheel não expõe, nessa API pública, um construtor de commit ou welcome para gerar um vetor local de negociação. Portanto, não é tecnicamente válido fabricar bytes ou alegar uma sessão MLS interoperável a partir apenas do binding instalado. O próximo nível de prova exige vetores oficiais/reais de roster, commit e welcome ou uma sessão Discord controlada.


## Smoke de rejeição nativa corrigido — 2026-08-18

A primeira execução falhou somente porque o processo não tinha `/home/ubuntu/Pimcord` no `PYTHONPATH`. Com o caminho corrigido, `process_proposals` e `process_welcome` retornaram sem efeito por ausência de grupo/estado MLS, enquanto `process_commit` rejeitou o payload inválido com `RuntimeError`. O resultado confirma a política fail-closed pré-negociação, mas não constitui vetor de commit/welcome válido nem prova interoperabilidade.


## Revalidação pós-suporte OAuth2 — 2026-08-18

Os smokes nativos foram reexecutados após o suporte de anexos de Activities. A primeira tentativa falhou apenas por `PYTHONPATH=/home/ubuntu`, que não continha o pacote; com `PYTHONPATH=/home/ubuntu/Pimcord`, o adaptador real inicializou contexto de mídia, áudio/SSRC/Opus e KeyPackage de 393 bytes, mantendo `grupo_estabelecido=false`, época 0 e transformação indisponível enquanto não houver commit/welcome interoperável. O smoke de rejeição confirmou novamente propostas e welcome rejeitados sem efeito e commit inválido convertido em `RuntimeError`.


## Smoke nativo deste ciclo — 2026-08-18

Os 19 testes locais de `test_dave.py` e `test_recepcao_voz.py` passaram. Esses contratos cobrem a máquina fail-closed, envelopes semânticos e a integração arquitetural da sessão de voz, mas não constituem interoperabilidade externa. O smoke nativo executado no ambiente atual encontrou `dave_disponivel=False`; não há binding `dave.py` instalado neste ambiente para executar roster, commit, welcome, ratchets e frames codec-aware reais. Nenhum mock foi promovido a evidência de compatibilidade com Discord e o bloqueador permanece aberto.


## Diagnóstico nativo adicional — 2026-08-18

A verificação independente no ambiente atual retornou `dave_disponivel=False` com `ModuleNotFoundError: No module named 'dave'`. Assim, não foi possível executar neste ambiente roster, commit, welcome, ratchet ou frames codec-aware contra o binding nativo. As evidências históricas do wheel isolado permanecem registradas, mas os contratos offline continuam sendo apenas validação estrutural e fail-closed; o bloqueador de interoperabilidade com uma sessão Discord real permanece aberto.


## Smoke nativo reproduzido em venv isolado — 2026-08-18

Um venv temporário recebeu `dave.py==1.0.0`, `aiohttp`, `cryptography` e `pytest`, sem modificar as dependências do projeto. O smoke nativo confirmou `versao_maxima=1`, `external_sender_disponivel=true`, `key_package_bytes=390`, `grupo_estabelecido_antes_negociacao=false` e `ratchet_disponivel_antes_negociacao=false`. O smoke do `AdaptadorDAVEPy` confirmou contexto de mídia, grupo `123`, época `0`, versão `1` e KeyPackage de `394` bytes, mas `transformacao_disponivel=false` porque ainda aguarda commit/welcome MLS interoperável.

A suíte `tests/test_dave.py` executada nesse venv aprovou **16 testes**. Isso melhora a evidência de inicialização nativa e fail-closed, mas não fecha o bloqueador: ainda não houve roster Discord, external sender negociado, commit/welcome real, transição de época, ratchets por usuário ou frames codec-aware cruzados.


## Superfície nativa observada — 2026-08-18

A inspeção reproduzível do venv `dave.py==1.0.0` confirmou que `Session` expõe `init`, `set_external_sender`, `get_marshalled_key_package`, `process_proposals`, `process_commit`, `process_welcome`, `get_key_ratchet`, `get_last_epoch_authenticator`, `get_pairwise_fingerprint` e `reset`. `Encryptor` expõe associação de SSRC/codec, `set_key_ratchet` e `encrypt`; `Decryptor` expõe `transition_to_key_ratchet` e `decrypt`.

Essa superfície confirma que o caminho necessário existe no binding, mas não fornece por si só mensagens Discord válidas, roster, external sender negociado, commit/welcome, transição de época ou frames de uma sessão real. A implementação deve continuar fail-closed até esses vetores serem obtidos e executados de forma cruzada.

## Critério objetivo de fechamento após inspeção das fontes

A especificação oficial e a amostra `DaveSessionManager.ts` confirmam a ordem: `PREPARE_EPOCH`, KeyPackage, external sender, propostas, commit/welcome, ratchets e transição. Os testes públicos de `dave.py` não fornecem fixtures de commit/welcome ou grupo MLS.

Para marcar o bloqueador como concluído, será exigida uma execução positiva em que uma mensagem de propostas produza commit/welcome válido e ambos os lados aceitem a mudança de roster, estabeleçam época, obtenham ratchets por remetente e cifrem/decifrem um frame codec-aware; alternativamente, a mesma sequência deve ser registrada contra uma sessão real do Voice Gateway com logs sanitizados. Até isso ocorrer, a disponibilidade do binding nativo não será descrita como interoperabilidade.

## Marco de opcodes do Voice Gateway

O modelo agora reconhece os opcodes oficiais 21–31 do DAVE e o cliente Voice Gateway aceita mensagens binárias com sequência big-endian, encaminhando external sender, proposals, commit e welcome somente para métodos explícitos do backend. Payloads MLS permanecem opacos e opcodes sem handler falham fechado. Foram adicionados contratos offline para enumeração, serialização e dispatch semântico; a suíte integral passou com **206 testes**. Isso fecha a cobertura do envelope e do roteamento, mas não prova roster, commit/welcome ou ratchet interoperável contra uma sessão Discord real.


## Dispatch Voice Gateway — contrato local

O caminho `Voice Gateway type=2 → MensagemDAVE.desserializar → ClienteGatewayVoz.processar_binario → backend` agora possui contratos offline para external sender, propostas, welcome, eventos DAVE e rejeição sem backend ativo. A suíte específica DAVE passou com **20 testes** e a suíte do projeto chegou a **208 testes**. Esse resultado valida o roteamento e o fail-closed local; não constitui interoperabilidade MLS positiva nem substitui uma sessão Discord real.


## Limite da API pública nativa

A inspeção dos símbolos do wheel isolado não encontrou uma API pública adicional de criação de grupo, proposta, commit ou Welcome além dos processadores de mensagens recebidas e dos objetos de sessão/ratchet. Assim, o Pimcord pode validar o roteamento e o fail-closed, mas não deve fabricar um commit ou Welcome para simular interoperabilidade. A prova positiva continua dependendo de payloads oficiais cruzados ou de uma sessão Discord real.

## Auditoria do vetor oficial ExternalSender — 2026-08-18

A suíte oficial CAPI do repositório `discord/libdave` contém um fluxo positivo de duas sessões: KeyPackages, proposta Add, `process_proposals`, separação de commit/welcome, `process_commit`, `process_welcome`, roster, assinaturas e ratchets. Contudo, a API pública do wheel `dave.py==1.0.0` instalado no ambiente isolado expõe `Session`, `SignatureKeyPair`, `Encryptor` e `Decryptor`, mas não expõe a classe `ExternalSender` nem funções equivalentes para criar propostas/commit/welcome. O teste C oficial também depende de `mlspp` e de um wrapper C++, ausentes no ambiente do Pimcord.

Conclusão: existe agora um vetor oficial positivo identificável, mas ele ainda não foi reproduzido pelo binding Python nem cruzado com uma sessão Discord. Não será tratado como prova de interoperabilidade. O bloqueador DAVE/MLS permanece aberto até existir um adaptador oficial/nativo validado ou fixture oficial serializado que possa ser processado por `dave.py` e pelo Pimcord.

## Observação de rede pública — 2026-08-18

A conectividade pública foi verificada sem autenticação: `GET /api/v10/gateway` respondeu com a URL do Gateway principal; `GET /api/v10/voice/regions` respondeu HTTP 401 e `/api/v10/gateway/voice` respondeu 404. Esses resultados não constituem sessão de voz. Faltam credencial legítima, `VOICE_STATE_UPDATE`, `VOICE_SERVER_UPDATE`, endpoint de voz, SSRC e transporte UDP. Portanto, a observação live de Voice Gateway/UDP continua bloqueada por ausência de sessão autenticada, e não será simulada.
