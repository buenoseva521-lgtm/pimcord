# Validação de superioridade do Pimcord

> Documento interno de prova. A versão 0.7.0 **não deve ser declarada superior ao discord.py** enquanto os bloqueadores marcados como abertos não forem encerrados com evidência executável.

## Critério de prova

A comparação não pode depender de quantidade de classes, slogans ou testes que nunca tocam os caminhos críticos. Para cada domínio, a prova exige uma combinação de superfície pública em português, contrato offline determinístico, comportamento de falha, documentação reproduzível e, quando o recurso depende de serviço externo ou criptografia, interoperabilidade real.

| Domínio | Evidência Pimcord | Situação | O que ainda impede uma conclusão final |
|---|---|---|---|
| API pública em português | 250 métodos públicos únicos no `ClienteHTTP`, APIs de comandos/eventos, aliases portugueses e documentação AST | Comprovado offline | Comparação semântica completa com todos os recursos que o discord.py cobre |
| REST | 196 contratos aprovados; 208 operações literais identificáveis contra 242 no OpenAPI v10 | Parcial | Revisão operação a operação, separação de endpoints fora do escopo de bots e cobertura das 45 lacunas conservadoras |
| Gateway e sharding | Simulações de recuperação, checkpoints atômicos, coordenação SQLite entre processos e 20 rodadas prolongadas com épocas 2–40 | Parcialmente comprovado | Observação prolongada com recursos nativos, falhas de transporte reais, múltiplas arquiteturas e carga real |
| Voz | RTP, jitter, Opus, PCM e integração arquitetural DAVE com SSRC/codec | Parcialmente comprovado | Sessão Voice real, transições de época, frames protegidos e interoperabilidade DAVE |
| DAVE/MLS | Wheel nativo inicializado, KeyPackage real, external sender detectado, fail-closed para bytes inválidos | Não concluído | Roster, propostas, commit, welcome, ratchets e vetores cruzados válidos |
| Automoderação | Motor offline-first com regras, ações, logs e tickets | Comprovado offline | Comparação de cobertura e comportamento com eventos/limites atuais do Discord |
| Views e interações | Views persistentes, despacho de componentes, follow-up, ephemeral, modais e upload tipo 19 | Comprovado offline | Auditoria de componentes, modais e limites atuais em referência oficial |
| Mobile/offline | Núcleo sem dependência nativa obrigatória e contratos sem rede | Comprovado por desenho | Validação em Pydroid/Termux e matriz real de wheels/arquiteturas |
| Resiliência | Smoke externo comprova lease ativo, crash por `os._exit` e retomada na época 2 | Comprovado no cenário reproduzido | Teste prolongado com gateway/voz e recursos nativos reais |

## Evidências reproduzíveis

A suíte principal é executada com:

```bash
python -m pytest -q
python -m compileall -q pimcord ferramentas
python ferramentas/auditar_openapi_rest.py
python ferramentas/contar_metodos_cliente.py
python ferramentas/smoke_coordenacao_processos.py
```

A evidência nativa DAVE é isolada para não tornar o pacote obrigatório para Pydroid/Termux:

```bash
PYTHONPATH=/home/ubuntu/Pimcord /tmp/pimcord-dave-venv/bin/python ferramentas/smoke_adaptador_dave_real.py
PYTHONPATH=/home/ubuntu/Pimcord /tmp/pimcord-dave-venv/bin/python ferramentas/smoke_dave_rejeicao.py
```

Os smokes nativos comprovam apenas inicialização, geração de KeyPackage, associação de mídia e rejeição fail-closed no estado pré-grupo. Eles não são tratados como prova de interoperabilidade.

## Regra de lançamento

A entrega final só pode ocorrer quando os itens abertos em `ROADMAP_TODO.md` forem convertidos em evidência positiva: DAVE/MLS válido e cruzado, matriz REST auditada operação a operação e teste prolongado de resiliência com recursos nativos. Até lá, qualquer afirmação de que o Pimcord é maior que o discord.py seria tecnicamente indefensável.


## Marco de validação integral — 2026-08-18

A execução integral deste ciclo passou com **193 testes**, compilação do pacote, auditoria de **242 operações oficiais**, **207 operações literais identificáveis** e **249 métodos públicos únicos**. A coordenação SQLite completou **20 rodadas reais entre subprocessos**, observando bloqueio durante lease ativo, expiração e retomada em épocas 2–40. O wheel nativo `dave.py` inicializou, gerou KeyPackage de 392 bytes e configurou áudio/SSRC/Opus; propostas e welcome sem grupo foram rejeitados sem efeito, e commit inválido produziu `RuntimeError`.

Esse marco fortalece as provas offline, de recuperação externa e de fail-closed, mas não fecha os bloqueadores: ainda faltam roster/commit/welcome válidos, ratchets e frames DAVE interoperáveis; auditoria REST operação a operação e revisão das 45 lacunas conservadoras; além de observação prolongada com gateway, voz e recursos nativos reais. A versão permanece **não liberada** para qualquer declaração de superioridade.


## Marco de validação pós-OAuth2 — 2026-08-18

A validação integral posterior ao suporte de anexo efêmero de Activity e a Incident Actions passou com **196 testes**, compilação de `pimcord` e `ferramentas`, auditoria REST em **242 operações oficiais, 208 correspondências literais e 45 lacunas conservadoras**, além de **250 métodos públicos únicos** no `ClienteHTTP`. O smoke prolongado entre subprocessos recuperou 20 rodadas, avançando as épocas de 2 até 40. O smoke nativo DAVE confirmou inicialização, KeyPackage e contexto de mídia, mas também confirmou que o grupo MLS ainda não está estabelecido: propostas e welcome inválidos são rejeitados sem efeito e commit inválido falha fechado.

Este marco não autoriza lançamento. Permanecem abertos: interoperabilidade DAVE/MLS com roster, commit, welcome, épocas e frames codec-aware reais; auditoria REST completa contra a especificação; e resiliência prolongada com Voice Gateway, UDP e recursos nativos reais.

## Marco de revalidação nativa e coordenação — 2026-08-18

A reexecução pós-auditoria confirmou **196 testes**, compilação limpa, **250 métodos públicos únicos**, auditoria REST em **208 de 242 operações literais** e **45 lacunas conservadoras**. A coordenação SQLite recuperou 20 rodadas entre subprocessos, avançando épocas de 2 a 40. No wheel nativo DAVE, o adaptador confirmou contexto de mídia, KeyPackage de 391 bytes e época 0; propostas e welcome inválidos foram rejeitados sem efeito e commit inválido produziu `RuntimeError`.

Essas evidências confirmam recuperação externa e fail-closed pré-grupo, mas não provam interoperabilidade: ainda faltam roster, commit, welcome, ratchets e frames codec-aware válidos, além de Voice Gateway/UDP reais e a revisão REST operação a operação. O Pimcord permanece não liberado para qualquer declaração de superioridade.

## Marco REST de convites direcionados — 2026-08-18

A auditoria semântica confirmou, na documentação oficial do Discord, as operações `GET /invites/{code}/target-users`, `PUT /invites/{code}/target-users` e `GET /invites/{code}/target-users/job-status`. O cliente recebeu as APIs portuguesas `obter_usuarios_alvo_convite`, `atualizar_usuarios_alvo_convite` e `obter_status_usuarios_alvo_convite`, com retorno CSV bruto em bytes, upload multipart pelo campo `target_users_file` e consulta do processamento assíncrono. A evidência local foi registrada em `docs/evidencias/auditoria_invites_target_users.md`.

A suíte completa passou com **204 testes**, `compileall` terminou sem erros e a referência `docs/API.md` foi regenerada pela ferramenta AST. A superfície AST permanece em **268 métodos públicos únicos** após a adição dos wrappers de Lobbies, Partner SDK, anexo de aplicação e webhooks especializados. A auditoria OpenAPI local aprimorada resolve variáveis, condicionais, concatenações e defaults: identificou **259 rotas locais**, correspondendo a **242 de 242 operações oficiais**, sem operações oficiais restantes sem correspondência literal. O cliente também recebeu `listar_assinaturas_sku` e `obter_assinatura_sku`, distintos da superfície de assinaturas da aplicação, com filtros oficiais `before`, `after`, `limit` e `user_id`. A leitura global de permissões de comandos por servidor (`GET /applications/{application.id}/guilds/{guild.id}/commands/permissions`) também recebeu método próprio, distinto da leitura de permissões de um comando individual. Além das rotas compostas, foram confirmados `GET/PATCH /guilds/{guild.id}/requests` e o `POST /guilds/{guild.id}/scheduled-events/{event.id}/exceptions`; a assinatura histórica de exceção permanece apenas como compatibilidade explícita, enquanto o caminho oficial não usa ID de usuário. A correção de `excluir_integracao` também foi mantida na rota oficial `/guilds/{servidor}/integrations/{integration}`; a contagem ainda exige classificação semântica das rotas especiais e dos contratos fora do escopo de bots. A classificação inicial também identificou que parte das 23 não correspondências reportadas pertence a superfícies especiais de `lobbies`, `partner-sdk` e webhooks GitHub/Slack. As fontes oficiais do Lobby Resource, Social SDK e Webhook Resource foram registradas em `docs/evidencias/fontes_escopo_lobbies_sdk_webhooks.md`; a decisão de escopo é não tratar essas rotas como paridade comum de bot antes de contratos próprios. A classificação atual das 23 pendências separa 16 operações de Lobbies, 5 de Partner SDK e 2 de webhooks GitHub/Slack; o upload de anexo de aplicação e as operações de metadata/moderação estão contidos nessas superfícies especiais. Essa separação é conservadora; a evidência `docs/evidencias/classificacao_operacoes_rest_abertas.md` agora lista as 23 operações individualmente, com família e decisão preliminar de escopo. A inspeção do OpenAPI mostrou `BotToken` em várias rotas de Lobbies e Partner SDK, portanto essas superfícies continuam pendências potenciais de bots e não podem ser excluídas por categoria. A matriz REST foi fechada no nível de correspondência de rotas e contratos básicos, com os payloads especializados cobertos por contratos offline; a validação de sessão real e comportamento externo permanece separada nos bloqueadores DAVE/MLS e Voice Gateway/UDP. O marco reduz lacunas REST confirmadas, mas não autoriza lançamento. Neste ciclo, os 19 testes específicos de DAVE/MLS e recepção de voz passaram, enquanto o diagnóstico nativo atual encontrou `dave_disponivel=False` (`ModuleNotFoundError`); o venv isolado reproduziu o binding `dave.py==1.0.0`, com KeyPackage nativo, external sender disponível e 16 testes DAVE aprovados. A superfície observada inclui `process_proposals`, `process_commit`, `process_welcome`, `get_key_ratchet`, `Encryptor.encrypt` e `Decryptor.decrypt`; as evidências históricas e atuais confirmam inicialização/fail-closed, mas grupo, ratchet e transformação continuam indisponíveis sem mensagens Discord válidas, commit/welcome interoperável e roster, portanto isso ainda não prova interoperabilidade. Continuam abertos a revisão operação a operação das lacunas conservadoras restantes, a interoperabilidade DAVE/MLS com roster, commits, welcomes, ratchets e frames codec-aware reais, e a observação prolongada com Voice Gateway, UDP e recursos nativos reais. O smoke adicional de coordenação completou 20 rodadas entre subprocessos, com recuperação até a época 40; a cobertura específica de Gateway, voz, recepção, RTP/Jitter, sharding e falhas prolongadas aprovou 33 testes. Essa evidência confirma WAL/leases/retomada SQLite e contratos offline de transporte, mas não substitui o cenário de Voice Gateway/UDP externo, sessão Discord real, binding DAVE nativo ou múltiplas arquiteturas. A ferramenta adicional `validar_crash_externo.py` também retornou `crash_externo=aprovado`, `retomada=aprovada` e `checkpoint=validado`; essa prova permanece limitada ao processo/checkpoint local.


## Marco DAVE — envelope binário e opcodes oficiais

O cliente Voice Gateway passou a reconhecer o envelope binário DAVE com sequência e os opcodes oficiais 21–31. External sender, propostas, commit e welcome são encaminhados somente para métodos semânticos explícitos do backend; payloads MLS não são adivinhados, e opcodes sem handler falham fechado. Foram adicionados contratos offline para serialização, enumeração e dispatch, elevando a suíte integral para **206 testes aprovados**.

Este marco melhora a ligação arquitetural entre Voice Gateway e adaptador, mas **não prova interoperabilidade DAVE/MLS**. Ainda faltam roster/leaf nodes, commit/welcome produzidos por sessão cruzada, transição de época, ratchets por remetente e transformação codec-aware validados contra Discord/libdave real.


## Marco adicional — dispatch binário no Voice Gateway

O caminho de mensagens binárias `type=2` foi exercitado com o parser oficial de envelope e o dispatch para external sender, propostas, welcome e eventos DAVE. O backend sem capacidade explícita é rejeitado, e o contrato cobre também a ausência de backend ativo. A suíte específica passou com 20 testes e a suíte integral chegou a **208 testes aprovados**.

A evidência é de integração local entre transporte e adaptador. Ela não substitui a interoperabilidade DAVE/MLS com uma sessão Discord: continuam pendentes roster real, commit/welcome cruzados, transição de época, ratchets por remetente e frames codec-aware.


## Marco de vínculo Voice State/Server — 2026-08-18

O Gateway principal agora encaminha `VOICE_STATE_UPDATE` e `VOICE_SERVER_UPDATE` para a sessão própria do bot. A sessão guarda o `session_id`, valida a correspondência do servidor, prepara `InformacoesVoz` somente após receber endpoint/token e inicia uma única tarefa de `ClienteGatewayVoz`, com encerramento e cancelamento vinculados a `SessaoVoz.sair()`. O caminho foi coberto offline sem rede e a suíte integral chegou a **209 testes aprovados**, com compilação limpa.

Este marco fecha uma lacuna de ligação entre eventos oficiais e transporte local, mas não equivale a uma sessão Discord real. Permanecem abertos o handshake efetivo do Voice Gateway, UDP/RTP externo, negociação DAVE/MLS com roster, commit/welcome, transição de época, ratchets e frames codec-aware interoperáveis.

## Atualização de bloqueadores — auditoria ExternalSender

A inspeção do libdave oficial encontrou testes CAPI que cobrem commit/welcome e roster em duas sessões. A inspeção do wheel Python utilizado pelo adaptador mostrou que `ExternalSender` não está exposto na API Python. Como o teste C depende de mlspp e wrapper C++, não é tecnicamente correto converter essa descoberta em prova executada pelo Pimcord. O resultado é evidência de um caminho de referência, não evidência de interoperabilidade do pacote.

## Observação de rede pública — 2026-08-18

O endpoint público `GET /api/v10/gateway` respondeu com a URL do Gateway principal. Já `GET /api/v10/voice/regions` respondeu HTTP 401 neste ambiente, e `/api/v10/gateway/voice` não é um endpoint público de descoberta, retornando 404. Isso confirma conectividade externa, mas não fornece um `session_id`, `token`, `endpoint` de Voice Server Update, SSRC ou IP/porta UDP. Sem credencial de bot e sem uma chamada de voz legítima, não é possível observar DAVE/MLS, Voice Gateway de voz ou UDP real sem inventar uma prova.
