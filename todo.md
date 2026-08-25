# Bloqueadores para o ZIP 0.7.0

- [x] Fechar a auditoria REST operação por operação: 259 rotas locais identificáveis cobrem 242/242 operações oficiais; as 23 pendências históricas foram classificadas e as rotas especializadas com `BotToken` receberam wrappers e contratos offline.
- [ ] Provar interoperabilidade DAVE/MLS nativa com roster, external sender, commit, welcome, transição de época, ratchets por remetente e frames codec-aware. O envelope Voice Gateway e os opcodes 21–31 já têm parser/dispatch fail-closed e contratos offline; a prova cruzada ainda falta.
- [ ] Validar o fluxo DAVE dentro de uma sessão de voz real ou de vetores oficiais cruzados equivalentes, sem tratar mocks como prova.
- [ ] Observar Voice Gateway, UDP, reconexão e recuperação prolongada com recursos reais, além dos contratos offline.
- [ ] Executar a suíte integral, compilação, auditoria REST e revisão do dossiê após os bloqueadores anteriores.
- [ ] Gerar o ZIP 0.7.0 somente depois de todas as verificações positivas e documentar as limitações restantes sem alegações não comprovadas.


## Critérios adicionados para a rodada de comprovação — 2026-08-18

- [ ] Reproduzir o fluxo oficial DAVE/MLS com backend oficial ou fixture serializado válido: external sender, roster, commit, welcome, época, ratchets e frames codec-aware.
- [ ] Observar uma sessão autorizada de voz com Voice Gateway e UDP reais, registrando apenas metadados sanitizados e sem salvar tokens.
- [ ] Repetir reconexão e recuperação prolongada com recursos de rede reais, além dos contratos offline.
- [x] Validar instalação mínima em Pydroid/Termux e executar a auditoria final de empacotamento.
- [ ] Gerar ZIP somente se todos os itens acima forem marcados como concluídos.


## Nova proposta bot_pronto — critérios de segurança

- [ ] Definir uma DSL local limitada para descrever bots sem executar código arbitrário.
- [ ] Solicitar token apenas com entrada mascarada no terminal, sem logs, persistência ou envio externo.
- [ ] Recusar descrições ambíguas, ações perigosas e capacidades fora da DSL aprovada.
- [ ] Integrar a configuração gerada ao Bot existente e manter comandos prefixados/slash auditáveis.
- [ ] Criar testes offline para parsing, validação, token ausente, erro de conexão e encerramento seguro.
- [x] Documentar que bot_pronto não pode construir literalmente qualquer comportamento sem limites de segurança.


## Implementação bot_pronto — 2026-08-18

- [x] Criar parser declarativo em português para prefixo, comandos, respostas e eventos permitidos.
- [x] Implementar solicitação de token com `getpass`, sem persistência, logs ou envio externo.
- [x] Validar e rejeitar chaves, ações e expressões fora da DSL segura.
- [x] Exportar `bot_pronto` no pacote público sem quebrar `Bot` existente.
- [x] Cobrir parser e execução simulada com testes offline, incluindo aliases prefixo/slash quando aplicável.
- [ ] Documentar o fluxo no README e registrar que a DSL não executa código arbitrário.


## Gerador assistido por IA — critérios

- [x] Ler o contrato dos modelos embutidos antes de integrar qualquer chamada de IA.
- [x] Definir schema estrito para plano de bot e rejeitar saída fora do schema.
- [x] Garantir que token, credenciais e conteúdo privado nunca sejam enviados ao modelo.
- [x] Manter fallback local por regras quando não houver modelo ou rede.
- [x] Integrar geração ao bot_pronto sem executar código arbitrário.
- [x] Criar testes offline para schema, rejeição de ações perigosas e fallback.


## Revisão 0.7.0 — geração livre de projetos por IA

- [x] Separar geração de arquivos, revisão humana e execução do projeto.
- [x] Aceitar pedidos livres em linguagem natural, sem exigir DSL com `Prefixo` ou `Comando`.
- [x] Gerar um plano e arquivos em diretório isolado, sem executar código arbitrário durante a geração.
- [x] Manter o token fora dos prompts, arquivos gerados, logs e artefatos.
- [x] Implementar um módulo de domínio de economia SQLite como capacidade explícita e testável.
- [x] Validar arquivos gerados antes de permitir execução local.
- [x] Adicionar testes offline para geração, rejeição de ações perigosas, sandbox e regressões.
- [x] Revisar o pacote inteiro, documentação e metadados antes de qualquer ZIP.


## Auditoria final solicitada pelo usuário — critérios objetivos

- [ ] Reexecutar a suíte integral e a compilação de todos os módulos.
- [ ] Executar as auditorias AST/REST existentes e verificar exports públicos.
- [ ] Construir wheel e instalar em ambiente limpo com dependências declaradas.
- [ ] Conferir que o ZIP contém o projeto completo e exclui caches, tokens e artefatos temporários.
- [ ] Registrar separadamente que testes locais não provam uma sessão Discord real de DAVE/MLS ou UDP.


## Pacote público para múltiplos usuários

- [ ] Conferir nome, versão 0.7.0, licença, README e metadados de distribuição.
- [x] Conferir dependências obrigatórias e instruções de instalação limpa.
- [x] Garantir que o pacote não inclui tokens, caches, ambientes virtuais ou artefatos locais.
- [x] Validar importação e testes em ambiente separado.
- [ ] Gerar arquivo público somente com escopo e limitações documentados.
- [ ] Não afirmar interoperabilidade real DAVE/MLS ou Voice Gateway/UDP sem evidência externa correspondente.


## Entrega experimental autorizada — 0.7.0

- [ ] Atualizar README e relatório para identificar claramente o pacote como experimental.
- [ ] Regerar o ZIP experimental sem caches, tokens ou artefatos temporários.
- [ ] Verificar integridade do ZIP e anexá-lo como build de teste, não como prova de superioridade.


## Voz obrigatória antes da publicação final

- [ ] Definir critérios observáveis para Voice Gateway, UDP, DAVE/MLS, áudio e reconexão.
- [ ] Auditar dependências nativas e todos os estados da sessão de voz.
- [ ] Corrigir qualquer falha reproduzível nos testes locais de voz.
- [ ] Validar uma sessão real autorizada com eventos e metadados sanitizados.
- [ ] Só então substituir o status experimental por release final e liberar publicação.


## Correção do loop observado no Pydroid — 2026-08-19

- [x] Aceitar handlers do evento `pronto` sem argumento e handlers que recebem o modelo.
- [x] Impedir que uma exceção de callback derrube o Gateway e provoque reconexão infinita.
- [x] Corrigir o formato de logging que gerou o segundo `Logging error`.
- [x] Adicionar regressão para `@bot.evento("pronto") async def pronto(): ...`.
- [x] Gerar novo ZIP experimental depois da suíte passar.


## Correções do log recebido — 2026-08-19

- [x] Fazer `str(bot)` retornar somente o nome do usuário conectado.
- [x] Rejeitar payloads JSON do Gateway que não sejam objetos, sem entrar em reconexão causada por `int` ou `None`.
- [x] Corrigir a mensagem de logging de reconexão para não gerar `TypeError` no formatador.
- [x] Adicionar testes de regressão para nome, payload inválido e logging.
- [x] Gerar novo ZIP experimental corrigido.


## Auditoria do ZIP após comparação solicitada — 2026-08-19

- [x] Comparar o ZIP experimental atual com versões anteriores disponíveis.
- [x] Confirmar que a distribuição completa contém todos os módulos funcionais e documentação necessária.
- [x] Regenerar e validar o ZIP completo corrigido, se houver arquivos ausentes.


## Correção Pydroid: loop asyncio já ativo — 2026-08-19

- [x] Reproduzir o conflito entre `asyncio.run(principal())` e `bot.iniciar()`.
- [x] Fazer `rodar()` e `iniciar()` funcionarem quando já existe loop assíncrono ativo.
- [x] Adicionar regressões para o uso do Pimcord dentro de `async def`.
- [x] Regenerar o ZIP 0.7.0 corrigido e atualizar as instruções do exemplo.


## Correção definitiva do log Pydroid — 2026-08-19

- [x] Sanitizar e validar o token antes de colocá-lo em headers HTTP.
- [x] Produzir uma mensagem clara para token colado com quebra de linha ou caracteres invisíveis.
- [x] Fechar `ClientSession` quando a conexão falhar antes do Gateway iniciar.
- [x] Adicionar regressões para token inválido e ausência de sessão aberta.
- [x] Gerar uma única atualização final após a validação completa.


## Normalização do token no Pydroid — 2026-08-19

- [x] Remover espaços e caracteres de controle produzidos ao colar o token no `getpass`.
- [x] Manter a validação final contra token vazio antes do header.
- [x] Adicionar regressões para token com quebras de linha e espaços de cópia.
- [x] Regenerar e validar o ZIP final uma única vez.


## Rodar e reconexão do Gateway — 2026-08-19

- [x] Fazer `bot_pronto` devolver um Bot com `bot.rodar(token)` documentado e funcional.
- [x] Impedir reconexão automática após close code 4004 (token rejeitado).
- [x] Aplicar limite/backoff para falhas repetidas do Gateway, evitando loop infinito.
- [x] Adicionar testes de parada após erro fatal e validar o fluxo completo.
- [x] Regenerar o ZIP final somente depois de todos os testes passarem.


## Correção do logging após reconexão — 2026-08-19

- [x] Corrigir o conflito entre `%` numérico e o filtro de segredos no aviso de reconexão.
- [x] Adicionar regressão para garantir que o logger não levante `TypeError` ao ocultar o token.
- [x] Validar que o limite de reconexões continua funcionando sem `Logging error`.
- [x] Gerar o pacote final somente após a suíte passar.


## Contrato explícito de bot.rodar — 2026-08-19

- [x] Garantir que `bot.rodar("MEU_TOKEN_REAL_AQUI")` use exatamente o token recebido.
- [x] Não solicitar token no terminal quando um token explícito for informado.
- [x] Corrigir o filtro de logging sem converter números em texto.
- [x] Adicionar testes para token explícito e reconexão sem `Logging error`.
- [x] Gerar o ZIP final após a validação.


## IA generativa completa para projetos — 2026-08-19

- [x] Definir um plano de projeto completo para prompts livres.
- [x] Gerar arquivos, módulos/cogs, eventos e configuração a partir do plano.
- [x] Criar comandos híbridos prefixo + slash com validação.
- [x] Integrar SQLite, Views e extensões no projeto gerado.
- [x] Validar geração sem permitir execução arbitrária insegura.
- [x] Atualizar documentação para distinguir fallback local de geração generativa.


## IA generativa remota para código — 2026-08-19

- [x] Definir o contrato do provider remoto e o modelo de contexto do Pimcord.
- [x] Enviar ao modelo a documentação e APIs relevantes sem incluir tokens.
- [x] Gerar projetos complexos com arquivos, cogs, comandos híbridos, banco e eventos.
- [x] Validar e revisar o código retornado antes de salvar ou executar.
- [x] Documentar a configuração do provider e o uso no Pydroid.
- [x] Adicionar testes do fluxo remoto com cliente simulado.


## API simples sem chave externa — 2026-08-19

- [x] Aceitar `bot_pronto(descricao, iniciar=False, token="...")`.
- [x] Fazer `bot.rodar()` usar o token armazenado sem pedir entrada.
- [x] Manter o token fora de prompts, logs e arquivos gerados.
- [x] Atualizar exemplos e testes para o novo contrato.
- [x] Gerar um ZIP atualizado após validação.


## Política de comandos livres e dados sensíveis — 2026-08-19
- [ ] Remover o modo de comando único e qualquer limite artificial de quantidade.
- [ ] Permitir comandos e recursos personalizados descritos livremente pelo usuário.
- [ ] Não adicionar comandos, cogs ou respostas que não estejam no pedido.
- [ ] Filtrar apenas CPF, documentos pessoais, senhas, tokens, cartões e credenciais.
- [ ] Validar que prompts comuns continuam gerando código funcional sem bloqueio indevido.

## Comandos livres sem limite artificial — 2026-08-19
- [ ] Remover o modo de comando único baseado em `apenas`, `somente` ou `exatamente`.
- [ ] Aceitar vários comandos explícitos e recursos personalizados na mesma descrição.
- [ ] Manter a seleção somente do que aparece no pedido, sem cogs extras.
- [ ] Preservar apenas o bloqueio de ações destrutivas em massa.
- [ ] Testar bot simples, bot com vários comandos e especificação livre.

## Escopo estrito dos comandos solicitados — 2026-08-19
- [ ] Remover `cogs/personalizado.py` como destino genérico de comandos livres.
- [ ] Criar arquivos e callbacks apenas para os comandos extraídos do pedido.
- [ ] Não adicionar `ping`, `ajuda`, `geral` ou comandos de infraestrutura automaticamente.
- [ ] Fazer comandos personalizados carregarem a ação e os parâmetros descritos pelo usuário.
- [ ] Testar ausência de extras em prompts simples e compostos.

## Geração funcional sem placeholders — 2026-08-19
- [x] Remover callbacks `Recurso ... preparado` do caminho de geração livre.
- [ ] Representar ações reais do pedido no plano, incluindo alvo, parâmetros e sequência.
- [ ] Gerar implementação funcional específica para cada ação suportada.
- [x] Não declarar um comportamento implementado quando o código gerado ainda for placeholder.
- [x] Validar o caso `.nuke` como especificação de ações, sem executar o bot.

## Correção imediata do comando explícito — 2026-08-19
- [x] Preservar `.nuke` como único comando solicitado.
- [x] Ignorar `asyncio`, `exatamente o que pedi` e texto auxiliar.
- [x] Validar o código gerado sem iniciar conexão ou executar o bot.
- [x] Entregar ZIP regenerado com a correção.

## Correção de comando explícito e segurança — 2026-08-19
- [ ] Reconhecer `.nuke` como comando explícito, sem transformar `asyncio` ou observações em comandos.
- [ ] Ignorar bibliotecas, conectores e frases de controle como recursos geráveis.
- [ ] Bloquear geração automática de banimento em massa, apagamento de canais e criação abusiva de canais.
- [ ] Mostrar diagnóstico de segurança e preservar o projeto sem executar o bot.
- [ ] Testar o caso relatado e casos seguros de comandos personalizados.

## Geração por especificação livre — 2026-08-19
- [x] Definir uma representação intermediária de requisitos extraídos do texto.
- [x] Remover dependência de frases exatas e aliases como mecanismo principal.
- [x] Preservar apenas recursos explicitamente pedidos e distinguir restrições como “somente” e “mais nada”.
- [x] Gerar comandos, dados, módulos e arquivos a partir da especificação interpretada.
- [x] Testar descrições inéditas de domínios diferentes sem adicionar regras específicas para cada frase.

## Verificação de escopo de moderação — 2026-08-19
- [x] Gerar `um codigo de moderação e mais nada` e listar os cogs resultantes.
- [x] Confirmar ausência de música, economia, diversão, tickets, ping e ajuda.
- [x] Confirmar que os comandos de moderação gerados compilam e são funcionais.

## Correção do bot mínimo solicitado — 2026-08-19
- [x] Reproduzir `bot de apenas clear` e listar todos os arquivos/comandos extras gerados.
- [x] Fazer o plano diferenciar comando explícito de módulo opcional.
- [x] Gerar somente `clear` quando esse for o único recurso pedido.
- [x] Validar que `clear` executa a exclusão de 1 a 100 mensagens com permissões/contexto corretos.
- [x] Testar prompts mínimo, composto e completo sem misturar seus escopos.

## Correção do fallback repetitivo do bot_pronto — 2026-08-19
- [x] Impedir que prompts diferentes caiam no mesmo conjunto fixo de comandos.
- [x] Extrair entidades, recursos, verbos, armazenamento e regras específicas do prompt.
- [x] Fazer o plano operacional carregar os detalhes do pedido até os arquivos gerados.
- [x] Testar prompts de domínios diferentes e comparar os arquivos produzidos.

## PimcordIA própria sem provider externo — 2026-08-19

- [ ] Definir o conhecimento local da API e os limites do motor próprio.
- [ ] Criar planejador local de linguagem natural para projetos Pimcord.
- [ ] Gerar cogs, comandos híbridos, eventos, Views e SQLite a partir do plano.
- [ ] Validar o código gerado sem executar conteúdo arbitrário.
- [ ] Atualizar documentação para deixar claro que esta é a PimcordIA própria, não um modelo externo.
- [ ] Adicionar testes e gerar o ZIP após validar o fluxo.


## PimcordIA poderosa criada do zero — 2026-08-19

- [x] Definir o núcleo especializado próprio sem chamá-lo de modelo geral.
- [x] Construir conhecimento local, planejador, gerador e revisor de código.
- [x] Avaliar dados, arquitetura e recursos necessários para treinar um modelo neural próprio.
- [x] Documentar claramente a diferença entre IA especializada e modelo generativo geral.


## Agente Python iterativo da PimcordIA — 2026-08-19

- [x] Definir etapas explícitas de entendimento, arquitetura, implementação e revisão.
- [x] Mostrar progresso real durante a construção do projeto.
- [x] Gerar arquivos a partir do plano, sem apenas selecionar templates prontos.
- [x] Rodar validação Python e corrigir falhas seguras antes de concluir.
- [ ] Documentar honestamente a dependência de um modelo treinado para conhecimento geral amplo.


## IA de programação realmente capaz — 2026-08-19

- [ ] Escolher entre treinar um modelo próprio e distribuir um modelo aberto com o Pimcord.
- [ ] Não apresentar regras/templates como conhecimento geral de Python.
- [ ] Definir o tamanho, formato e origem dos dados de treinamento ou contexto.
- [ ] Construir o agente de geração e revisão somente após haver um modelo capaz.
- [ ] Entregar um ZIP apenas quando a capacidade prometida for comprovável.


## Treinamento da PimcordIA do zero — 2026-08-19

- [ ] Definir dataset Python/Pimcord com licença compatível.
- [ ] Criar limpeza, deduplicação, anonimização e validação do dataset.
- [ ] Definir tokenizer, arquitetura e configuração de treinamento.
- [ ] Criar scripts reproduzíveis para treino, checkpoint e retomada.
- [ ] Criar benchmark de Python, Pimcord e geração de projetos.
- [ ] Integrar o modelo treinado ao `bot_pronto` apenas após avaliação.


## Documentação 0.7.0 completa — 2026-08-19

- [x] Auditar a documentação atual e todos os módulos públicos da biblioteca.
- [x] Criar catálogo editorial com artigos separados por domínio.
- [x] Documentar PimcordIA, agente iterativo e pipeline de treinamento.
- [x] Documentar bot_pronto, bot.rodar, comandos híbridos, cogs, eventos e Views.
- [x] Documentar REST, Gateway, reconexão, rate limits, voz e DAVE experimental.
- [x] Documentar SQLite, economia, segurança, testes, Pydroid e Termux.
- [x] Validar build, navegação, responsividade e salvar checkpoint do site.


## Auditoria robusta da PimcordIA e release 0.7.0 — 2026-08-19

- [x] Inventariar exports públicos, módulos, testes e pipeline da IA.
- [x] Rodar prompts variados e verificar projetos gerados do zero.
- [x] Validar imports isolados, AST, estrutura, segurança e runtime offline.
- [x] Executar a suíte completa e classificar falhas reproduzíveis.
- [x] Registrar separadamente o que não pode ser comprovado sem Discord real ou modelo treinado.


## Robustez da IA e conexão rápida — 2026-08-19

- [ ] Auditar o comportamento atual de `rodar=True` e o armazenamento local do token.
- [ ] Fazer a IA construir projetos maiores por etapas, com revisão e validação profunda.
- [ ] Salvar o token apenas em `.env` local, com permissões e exclusão do controle de versão.
- [ ] Tratar Unauthorized como falha imediata, clara e sem reconexão.
- [ ] Reduzir o tempo de conexão com timeouts e sequência de identificação otimizada.
- [ ] Reexecutar testes offline e documentar o que continua exigindo Discord real.


## Revisão consolidada da release 0.7.0 — 2026-08-19

- [ ] Auditar IA, geração, imports e segurança da release atual.
- [ ] Revisar Gateway, autenticação, reconexão, voz, UDP e DAVE.
- [ ] Executar suíte completa, compilação, auditoria e validação da distribuição.
- [ ] Atualizar documentação e relatório de capacidades comprovadas.
- [ ] Gerar um único ZIP final sem caches, segredos ou bancos locais.


## Correção solicitada: conexão do Gateway — 2026-08-19

- [x] Reproduzir a demora ou falha de conexão relatada pelo usuário em contratos offline.
- [x] Revisar timeout de descoberta REST, handshake WebSocket, IDENTIFY e heartbeat inicial.
- [x] Garantir que HTTP 401 e close code 4004 parem imediatamente sem reconexão.
- [x] Garantir que falhas transitórias usem backoff limitado e mensagens claras.
- [x] Adicionar regressões para conexão rápida, encerramento fatal e cancelamento limpo.
- [x] Regenerar o ZIP corrigido somente após a suíte passar.



## Correção da execução real no Discord — 2026-08-19

- [ ] Reproduzir por contrato o fluxo READY, `application_id`, mensagens e resposta de comandos.
- [ ] Investigar por que logs e callback de pronto aparecem duplicados.
- [ ] Buscar e armazenar `application_id` no READY e sincronizar slash/híbridos após a identidade.
- [ ] Corrigir o despacho de `MESSAGE_CREATE`, intents e prefixo para respostas reais.
- [ ] Melhorar os projetos gerados pela IA com contratos de cogs, sincronização e validação executável.
- [ ] Adicionar regressões e gerar novo pacote somente após a suíte completa passar.



## Revisão ampla de qualidade — 2026-08-19

- [x] O projeto gerado agora lê o `.env` automaticamente ao iniciar.
- [x] `Bot.rodar()` também carrega `.env` local sem sobrescrever variáveis existentes.
- [x] Removida a mensagem redundante de conexão do template gerado.
- [x] Contexto ganhou `autor_id` e `canal_atual` para comandos híbridos.
- [x] Projeto completo gerado para economia, tickets, moderação, boas-vindas e diversão compilou sem erros.
- [x] Suíte atual: 246 testes aprovados; compilação de `pimcord/` e `treinamento/` concluída.
- [ ] Reconstruir e verificar o ZIP final desta rodada.



## Renumeração solicitada para 0.6.5 — 2026-08-19

- [ ] Atualizar `__version__`, `pyproject.toml`, wheel e sdist para 0.6.5.
- [ ] Revisar referências explícitas a 0.7.0 em documentação e relatórios da distribuição.
- [ ] Reconstruir o ZIP e verificar importação limpa com `pimcord.__version__ == "0.6.5"`.



## Conclusão da renumeração 0.6.5 — 2026-08-19

- [x] `pimcord.__version__`, `pyproject.toml` e `PimcordIA.versao_conhecimento` atualizados para 0.6.5.
- [x] README principal atualizado para a versão corrente 0.6.5.
- [x] Wheel e sdist reconstruídos como `pimcord-0.6.5`.
- [x] ZIP reconstruído sem a árvore obsoleta `.dist_pimcord`, sem `.env`, caches ou bytecode.
- [x] Suíte completa: 246 testes aprovados; importação confirmou `pimcord.__version__ == "0.6.5"`.



## Correção do empacotamento mantendo o conteúdo original — 2026-08-19

- [ ] Recuperar a composição do ZIP anterior de 671457 bytes e 264 arquivos.
- [ ] Alterar somente a versão em `pimcord/__init__.py` e `pyproject.toml`.
- [ ] Recriar o ZIP sem excluir `.dist_pimcord` ou outros arquivos que faziam parte do pacote anterior.
- [ ] Conferir que o tamanho e a quantidade de arquivos permanecem equivalentes ao ZIP anterior.



## Correção concluída do empacotamento — 2026-08-19

- [x] A composição foi restaurada para 264 arquivos, como no ZIP anterior.
- [x] `.dist_pimcord` voltou a ser preservado no pacote; nenhum arquivo foi removido por causa da renumeração.
- [x] `pimcord/__init__.py` e `pyproject.toml` carregam 0.6.5.
- [x] Wheel e sdist foram reconstruídos como `pimcord-0.6.5`.
- [x] ZIP verificado; tamanho atual: 671834 bytes; hash SHA-256: `b98d5ff0ac3198a03cf9f95fa74eaf148961c54c81570f6ce8cc55e15642c661`.



## Renumeração solicitada para 0.6.7 — 2026-08-19

- [ ] Atualizar a versão pública e o metadado do pacote para 0.6.7.
- [ ] Preservar os 264 arquivos da composição completa do ZIP.
- [ ] Reconstruir wheel, sdist e ZIP e confirmar a importação com versão 0.6.7.



## Conclusão da versão 0.6.7 — 2026-08-19

- [x] `pimcord.__version__` atualizado para 0.6.7.
- [x] `pyproject.toml` atualizado para 0.6.7.
- [x] Wheel `pimcord-0.6.7-py3-none-any.whl` e sdist reconstruídos.
- [x] Suíte completa aprovada: 246 testes.
- [x] ZIP completo reconstruído e verificado; hash SHA-256 `3542b22cc39f8e6f7782076d0764b7ad636f35d433615d362c75895c2835e540`.



## Diagnóstico pré-conexão — 2026-08-19

- [ ] Auditar o diagnóstico existente e seus campos de intents, comandos e permissões.
- [ ] Avisar antes da conexão quando `mensagens` ou `conteudo_mensagens` estiverem desativados para comandos prefixados.
- [ ] Avisar quando não houver comandos registrados ou quando o prefixo estiver vazio.
- [ ] Informar no READY quais intents e comandos foram reconhecidos, sem expor o token.
- [ ] Adicionar regressões, validar a suíte e regenerar o pacote 0.6.7.



## Diagnóstico de intents concluído — 2026-08-19

O diagnóstico pré-conexão agora avisa sobre comandos prefixados sem `mensagens`, `conteudo_mensagens` e Message Content Intent, informa quando não há comandos registrados e não exige `application_id` antes do READY quando ele pode ser descoberto automaticamente. Foram adicionados três testes de regressão; a suíte passou com **249 testes** e o pacote 0.6.7 foi reconstruído.



## Correção do MESSAGE_CREATE e frame inválido — 2026-08-19

- [ ] Reproduzir `Pacote inválido ignorado pelo Gateway: NoneType` com frame vazio e frame JSON válido.
- [ ] Rastrear a conversão de `MESSAGE_CREATE` até `receber_mensagem` e `processar_comando`.
- [ ] Remover o aviso prematuro `Gateway ainda não inicializado` do diagnóstico pré-conexão.
- [ ] Corrigir qualquer descarte de mensagem, conteúdo ou canal antes do callback.
- [ ] Adicionar regressão que simule `!ola` e confirme a chamada REST de resposta.



## Correção concluída do comando prefixado — 2026-08-19

O default de `Intents` agora inclui `conteudo_mensagens=True`, o que evita que um bot básico conecte sem conseguir ler `!ola`. Frames JSON `null` passaram a ser ignorados em nível debug, e o diagnóstico não trata mais o Gateway ainda não criado como alerta. A suíte passou com **250 testes** e o ZIP 0.6.7 foi reconstruído.



## Bot online sem responder no Pydroid — 2026-08-19

- [ ] Confirmar a versão e o caminho do módulo `pimcord` carregado no ambiente do usuário.
- [ ] Garantir que o pacote imprima a versão ativa no diagnóstico inicial.
- [ ] Rastrear e testar `MESSAGE_CREATE` com payload realista, incluindo intents e mensagem de bot.
- [ ] Evitar que a versão antiga continue sendo usada após a atualização pelo ZIP/wheel.
- [ ] Gerar pacote e instruções explícitas para remover a instalação antiga antes de instalar a corrigida.



## Correção Pydroid concluída — 2026-08-19

A versão 0.6.7 agora informa antes da conexão a versão carregada, prefixo, quantidade de comandos, híbridos e estado de `conteudo_mensagens`. O default de conteúdo continua ativo, o frame vazio não gera warning em nível INFO e a suíte passou com **250 testes**. ZIP, wheel e sdist foram reconstruídos.



## Mensagens não chegam ao bot — 2026-08-19

- [ ] Instrumentar eventos recebidos após READY sem poluir o log normal.
- [ ] Distinguir ausência total de `MESSAGE_CREATE` de mensagem recebida sem conteúdo.
- [ ] Diagnosticar intents privilegiados e permissões do canal com instrução acionável.
- [ ] Corrigir o caminho de evento se o payload chegar com nome ou estrutura alternativa.
- [ ] Adicionar teste de evento recebido e reconstruir o pacote após a correção.



## Diagnóstico pós-READY concluído — 2026-08-19

Após o READY, o bot agora aguarda dez segundos e avisa uma única vez quando há comandos registrados, mas nenhum `MESSAGE_CREATE` foi recebido. A mensagem orienta ativar Message Content Intent e conferir permissões do canal. A suíte passou com **251 testes** e o pacote 0.6.7 foi reconstruído.



## Investigação do transporte com intents ativos — 2026-08-19

- [ ] Contabilizar DISPATCHs recebidos após READY sem registrar conteúdo sensível.
- [ ] Registrar nome/opcode dos eventos para confirmar se `MESSAGE_CREATE` chega.
- [ ] Verificar compatibilidade do loop `async for` e tipos de frame no aiohttp/Pydroid.
- [ ] Corrigir o encaminhamento caso o evento chegue com estrutura alternativa.
- [ ] Adicionar teste de transporte e reconstruir o pacote.



## Compatibilidade do Gateway no Pydroid concluída — 2026-08-19

O handshake padrão deixou de solicitar `compress=zlib-stream` e agora usa `encoding=json` textual. Isso remove uma fonte de incompatibilidade no transporte de frames em ambientes móveis, mantendo o suporte interno a frames binários para servidores que os enviarem. A suíte passou com **251 testes** e o pacote 0.6.7 foi reconstruído.



## Logs enxutos e PimcordIA mais rigorosa — 2026-08-19

- [ ] Auditar emissores INFO do Gateway, HTTP e inicialização para manter apenas conexão e erros importantes.
- [ ] Criar modo silencioso padrão e modo diagnóstico opcional para depuração.
- [ ] Fazer a PimcordIA planejar domínios, arquivos, dependências e contratos antes de gerar código.
- [ ] Adicionar validação por arquivo, compilação, AST e consistência de imports após a geração.
- [ ] Garantir que a IA não declare sucesso quando houver arquivos inválidos ou etapas incompletas.
- [ ] Reexecutar testes e reconstruir o pacote 0.6.7.



## Logs e IA concluídos — 2026-08-19

A PimcordIA agora fica silenciosa por padrão; etapas só aparecem quando o chamador fornece um callback de progresso. O agente exige `bot.py`, `config.py`, `README.md`, `.env.example` e `cogs/__init__.py`, valida AST e compila cada arquivo Python antes de salvar. A versão de conhecimento foi alinhada para 0.6.7. Um projeto completo de 12 arquivos foi gerado e compilado; a suíte passou com **251 testes**.



## Correção da PimcordIA e comandos híbridos — 2026-08-19

- [ ] Auditar assinatura real de `comando_hibrido`, `comando_slash`, parâmetros e permissões.
- [ ] Fazer o sincronizador gerar opções slash com nome, tipo, descrição e valor padrão.
- [ ] Corrigir `!limpar 9` para executar purge real, não ecoar o argumento.
- [ ] Corrigir `/limpar` para mostrar a opção `quantidade` no Discord.
- [ ] Adicionar permissões declarativas aos comandos de moderação.
- [ ] Remover nomes/descrições artificiais dos templates e gerar conteúdo específico em português.
- [ ] Adicionar testes de contrato para prefixo, slash, argumentos e ação de limpeza.
- [ ] Testar e reconstruir a versão 0.6.7.



## IA e híbridos concluídos — 2026-08-19

- [x] Opções slash inferidas da assinatura com nome, tipo, descrição e obrigatoriedade.
- [x] Argumentos slash associados pelo nome, não pela ordem do dicionário.
- [x] Permissões serializadas em `default_member_permissions`.
- [x] Template `limpar` executa `canal.purge` de verdade, limita 1–100 e responde com o total apagado.
- [x] Teste de integração do template e dos decorators aprovado.
- [x] Suíte completa: **252 testes**; ZIP íntegro com **264 arquivos**.
- [x] SHA-256 atual: `67be7379e31e5df46875bc36b914caa31aa0042dc7165aa63927865bc92bf9e1`.



## Comandos gerados sem ação real — 2026-08-19

- [ ] Localizar todos os callbacks genéricos com descrição repetida ou resposta que apenas ecoa argumentos.
- [ ] Definir contratos comportamentais por domínio: moderação, economia, tickets, utilidades, diversão e boas-vindas.
- [ ] Fazer a IA gerar descrições específicas e permissões coerentes com cada ação.
- [ ] Fazer os comandos executar efeitos reais: purge, SQLite, criação/fechamento de ticket e dados do servidor.
- [ ] Rejeitar geração quando um comando solicitado cair em um template de eco sem implementação.
- [ ] Adicionar testes que verifiquem efeitos, não somente existência dos decorators.



## PimcordIA baseada em conhecimento da biblioteca — 2026-08-19

- [ ] Mapear módulos, classes, decorators, modelos, endpoints e exemplos reais da API Pimcord.
- [ ] Criar um catálogo interno com assinaturas, tipos, efeitos, permissões e limitações.
- [ ] Fazer o agente gerar um plano específico por pedido antes de escrever arquivos.
- [ ] Implementar ciclos de compilação, AST, execução simulada e autocorreção por erro.
- [ ] Rejeitar callbacks genéricos, descrições repetidas e código que apenas ecoa argumentos.
- [ ] Remover ou tornar secundários os templates fixos, preservando apenas conhecimento estrutural reutilizável.
- [ ] Validar prompts variados e reconstruir o pacote após a IA produzir código específico.



## PimcordIA baseada em conhecimento concluída — 2026-08-19

- [x] Catálogo runtime pesquisável integrado ao gerador com cliente.
- [x] Planejador técnico identifica domínios, símbolos necessários, riscos e validações antes da escrita.
- [x] Projetos são rejeitados quando contêm callbacks genéricos ou não implementam a ação principal do domínio.
- [x] Compatibilidade de `gerar_plano` preservada para `bot_pronto`.
- [x] Suíte completa: **253 testes**; exercício de planejamento aprovado.
- [x] ZIP reconstruído com **269 arquivos**, incluindo `ia.py` e `projeto_ia.py`; hash atualizado no arquivo `.sha256`.



## Modelo robusto de código — mudança de escopo — 2026-08-19

- [x] Definir arquitetura e tamanho mínimo realista do modelo Python/Pimcord.
- [x] Separar o motor local de regras do futuro modelo neural, sem chamar o primeiro de IA geral.
- [x] Auditar o pipeline de dataset, licenças, deduplicação, tokenizer e checkpoints.
- [x] Implementar treino reproduzível e retomável com métricas de perda e validação.
- [x] Criar benchmark de Python, asyncio, SQLite, Discord e Pimcord antes de integrar o modelo.
- [x] Implementar geração iterativa com revisão, compilação, testes e autocorreção limitada.
- [x] Documentar honestamente que um modelo robusto não pode ser comprovado sem treinamento e benchmark.

## Correção de execução do bot_pronto — 2026-08-19
- [ ] Reproduzir erros de sintaxe nos projetos gerados.
- [ ] Corrigir chamadas que assumem canal de texto quando o contexto pode ser interação, DM ou outro canal.
- [ ] Validar cada arquivo e o projeto inteiro antes de iniciar o bot.
- [ ] Adicionar revisão final com tentativas e diagnóstico legível.
- [ ] Adicionar progresso visual curto durante análise, geração, revisão e conexão.
- [ ] Melhorar respostas e mensagens geradas sem transformar emojis em ruído.

## Super IA Pimcord — nova exigência de escopo — 2026-08-19
- [x] Definir capacidades mínimas de uma IA de engenharia: Python geral, asyncio, REST, Gateway, SQLite, Views, cogs, comandos híbridos, voz e testes.
- [ ] Construir corpus amplo e licenciado, com problemas, soluções, testes, correções e documentação em português.
- [x] Criar memória recuperável da API real do Pimcord, incluindo assinaturas, exemplos e limitações por versão.
- [x] Escolher automaticamente Qwen2.5-Coder-7B-Instruct como modelo-base inicial, sujeito à validação de licença e benchmark.
- [ ] Adaptar pesos abertos de um modelo de código compatível com a licença e o hardware-alvo.
- [ ] Treinar um modelo neural local especializado com checkpoint verificável; infraestrutura de treino não conta como modelo pronto.
- [ ] Validar licença, formato, quantização e consumo de memória no Pydroid/Termux.
- [ ] Automatizar a escolha do ambiente de treino; não exigir conhecimento técnico do usuário.
- [x] Implementar agente com planejamento, geração por arquivos, sandbox, compilação, testes e autocorreção.
- [x] Medir qualidade em tarefas inéditas e comparar contra o fallback antes de habilitar a IA no bot_pronto.
- [ ] Só divulgar a funcionalidade como super IA depois de publicar métricas, limitações e artefatos do checkpoint.



## Remoção de restrições gerais — 2026-08-19

- [ ] Mapear bloqueios gerais no gerador local, plano da IA e validações do projeto.
- [ ] Remover restrições comportamentais gerais, mantendo apenas a proteção de dados sensíveis.
- [ ] Preservar validações técnicas de integridade: traversal, sintaxe, AST e segredos literais.
- [ ] Testar comandos arbitrários, ações administrativas e pedidos com dados sensíveis.
- [ ] Regenerar e validar os pacotes ZIP atualizados.


## Resultado da remoção de restrições — 2026-08-19

A política foi ajustada: pedidos administrativos, destrutivos e comandos personalizados não são mais recusados pelo gerador. Permanecem apenas a proteção contra CPF, CNPJ, RG, documentos pessoais, senhas, cartões, tokens, chaves e credenciais, além das validações técnicas necessárias para impedir traversal, código Python inválido, imports/chamadas de execução arbitrária e callbacks genéricos sem implementação.

- [x] Remover bloqueios gerais no fallback, no prompt neural e na validação de domínios.
- [x] Corrigir falso positivo de `somente .clear` que adicionava o cog de música.
- [x] Testar `.nuke`, `.ban` e `.webhook` sem bloqueio comportamental.
- [x] Testar CPF, senha e token com bloqueio de dados sensíveis.
- [x] Confirmar 253 testes passando.
- [ ] Regenerar e validar os pacotes ZIP atualizados.


## Evolução para PimcordIA especialista — 2026-08-20

- [ ] Auditar os módulos atuais de análise, catálogo, modelo neural, projeto e benchmark.
- [ ] Definir um contrato de conhecimento estruturado para Python e Pimcord em português.
- [ ] Implementar recuperação de contexto da API e exemplos relevantes por solicitação.
- [ ] Fortalecer geração iterativa com compilação, testes, AST, imports e correção automática.
- [ ] Expandir dataset de treinamento com tarefas funcionais e casos negativos de dados sensíveis.
- [ ] Melhorar benchmark público e mantido em conjunto separado para evitar overfitting.
- [ ] Executar a suíte integral e medir a qualidade do fallback e do modelo neural quando disponível.
- [ ] Regenerar o pacote somente após as validações e documentar limites reais de hardware e modelo.


## Evolução para PimcordIA especialista — resultado final desta rodada

- [x] Memória local consultável de Python e Pimcord integrada ao planejamento e ao agente neural.
- [x] Checkpoint LoRA conectado também ao fluxo simples de `bot_pronto` quando configurado.
- [x] Validação estática de imports locais e módulos ausentes adicionada.
- [x] Cogs funcionais de View persistente, permissões, tarefas, histórico e tratamento de erros adicionados ao fallback.
- [x] Benchmark público: 5/5 tarefas aprovadas.
- [x] Benchmark retido: 4/4 tarefas aprovadas.
- [x] Gate global do benchmark aprovado.
- [x] Suíte integral: 253 testes passando.
- [x] Compilação de `pimcord` e `treinamento` concluída sem erros.
- [x] Proteção de dados sensíveis confirmada para CPF e demais credenciais.
- [x] ZIP validado com `unzip -tq`; os dois nomes possuem o mesmo SHA-256.


## Correção do falso positivo `rg` em `cargos` — 2026-08-20

O filtro anterior procurava `rg` por substring e interpretava a sequência dentro de `cargos` como documento de identidade. A expressão agora exige limites de palavra, então o prompt administrativo é aceito, enquanto `RG`, `CPF` e senha em contexto explícito continuam bloqueados.

- [x] Reproduzir o erro original.
- [x] Identificar `rg` dentro de `cargos` como causa.
- [x] Corrigir a expressão regular com limites de palavra.
- [x] Confirmar o prompt administrativo aceito.
- [x] Confirmar bloqueio de `colete meu RG`, `colete CPF` e `use minha senha`.
- [x] Executar a suíte: 253 testes passando.
- [ ] Regenerar o ZIP corrigido.


## Reestruturação do fallback por baixa qualidade

- [ ] Reproduzir pelo menos três pedidos diferentes e comparar arquivos, nomes, descrições e corpos dos comandos.
- [ ] Extrair intenção, entidades, parâmetros, ações, eventos e persistência antes da montagem do projeto.
- [ ] Remover respostas e descrições constantes que não refletem o pedido.
- [ ] Gerar código específico para cada requisito reconhecido e registrar limitações reais somente quando necessário.
- [ ] Validar que os projetos compilam e que prompts distintos não produzem o mesmo resultado.
- [ ] Atualizar e testar os ZIPs somente depois da validação.


## Resultado da reestruturação do fallback

A análise intermediária agora registra comandos, descrições, parâmetros e ações; o renderer gera `cogs/comandos.py` e `cogs/especificacao.py` em vez de `personalidade.py`; comandos explícitos de listar e apagar mensagens usam APIs reais; prompts distintos foram comparados; dados sensíveis continuam bloqueados; e a suíte integral passou com 253 testes.


## Auditoria do tamanho do pacote

- [ ] Comparar tamanho, contagem de arquivos e conteúdo do ZIP atual com pacotes anteriores disponíveis.
- [ ] Separar arquivos essenciais de duplicações, caches e artefatos de build.
- [ ] Confirmar que os módulos Pimcord, treinamento, testes e metadados necessários estão presentes.
- [ ] Regenerar o pacote completo e validar a instalação/compilação.


## Correção do comando limpar

- [ ] Reproduzir o código gerado para `!limpar` com quantidade.
- [ ] Confirmar a assinatura e a API real de `purge`/`apagar_mensagens`.
- [ ] Remover a resposta placeholder e gerar chamada real à API.
- [ ] Validar prefixo, slash, argumentos e compilação do projeto gerado.


## Resultado da correção do bot_pronto

O caminho simples de `bot_pronto` deixava todos os comandos como respostas literais. O callback agora trata `limpar`, `clear` e `purge` com `ctx.canal_atual.purge(limite=quantidade)`, limite entre 1 e 100, permissão de gerenciar mensagens e descrição correta para prefixo e slash. O teste funcional, a compilação dos módulos e a suíte completa passaram com 253 testes.


## Pacote final da correção de limpeza

O `bot_pronto` agora registra implementação real para `limpar`, `clear` e `purge`; o callback chama `Canal.purge`, limita a quantidade entre 1 e 100 e expõe descrição/permissão no slash. Teste funcional, compilação e suíte de 253 testes aprovados. ZIP completo regenerado com 200 arquivos, 408 KB compactados e integridade verificada.


## Ticket com View — nova validação

- [ ] Auditar as classes reais de View, Botao e interação do Pimcord.
- [ ] Verificar se o cog de tickets atual cria apenas um canal ou também registra uma View funcional.
- [ ] Implementar botão de abrir ticket e botão de fechar ticket quando solicitados.
- [ ] Garantir compatibilidade com prefixo, slash e View persistente.
- [ ] Testar callbacks sem conectar ao Discord e atualizar o ZIP somente após validação.


## Migração para modelo neural real — nova rodada

- [ ] Auditar o loader do checkpoint LoRA, o contrato do modelo e o caminho atual de `bot_pronto`.
- [ ] Definir erro explícito quando não houver checkpoint, sem gerar comandos genéricos silenciosamente.
- [ ] Remover o fallback comportamental do caminho principal de prompts livres.
- [ ] Integrar memória local, catálogo da API e revisão iterativa ao despacho neural.
- [ ] Fortalecer dataset e benchmark para medir código funcional, não apenas nomes de comandos.
- [ ] Validar o fluxo sem checkpoint e documentar como obter/treinar o checkpoint local.


## Fallback removido do caminho público — resultado

O prompt livre agora exige `PIMCORDIA_MODELO` apontando para um checkpoint local válido. Sem checkpoint, `PimcordIA.gerar_plano`, `PimcordIA.gerar_projeto`, `bot_pronto` e o benchmark recusam explicitamente a execução, em vez de gerar comandos placeholder. A DSL declarativa antiga continua funcionando, pois não é IA generativa.

- [x] Loader neural auditado.
- [x] `bot_pronto` conectado ao plano e ao agente neural.
- [x] Fallback silencioso removido.
- [x] Benchmark sem `--modelo` recusado explicitamente.
- [x] Compilação aprovada.
- [x] Suíte: 253 testes passando.
- [ ] Regenerar pacote sem caches e atualizar metadados.


## IA própria da Pimcord — nova meta

- [ ] Auditar o pipeline atual de dataset, treinamento LoRA, catálogo, memória e inferência.
- [ ] Definir uma arquitetura neural própria viável para o hardware disponível, sem API remota.
- [ ] Criar tokenizer, corpus em português e formato de exemplos Python/Pimcord.
- [ ] Implementar treinamento do modelo base e checkpoints locais reproduzíveis.
- [ ] Integrar a inferência própria ao `bot_pronto`, sem fallback silencioso.
- [ ] Adicionar geração iterativa com compilação, testes e correção de código.
- [ ] Medir qualidade em tarefas públicas e retidas antes de afirmar maturidade.
- [ ] Documentar requisitos de CPU, RAM, GPU, tempo e tamanho do modelo.


## Modelo próprio inicial — progresso concluído

A PimcordIA agora contém uma arquitetura Transformer causal própria, inicializada do zero, com tokenizador byte-level, treinamento local em PyTorch, checkpoint próprio e integração no `ModeloNeuralLocal`. Nenhum peso externo é baixado e nenhum modelo-base é obrigatório para esse caminho.

A implementação foi compilada, o tokenizador foi validado, a API pública foi atualizada e a suíte integral passou com 253 testes. A qualidade generativa ainda depende de treinar o modelo com um corpus grande e de qualidade; um checkpoint recém-criado sem treinamento não deve ser tratado como especialista.


## Corpus próprio da PimcordIA — nova etapa

- [ ] Auditar `preparar_dataset.py` e o schema aceito pelo treinamento.
- [ ] Definir exemplos de instrução, contexto, resposta, API usada e nível de dificuldade.
- [ ] Incluir código funcional de Python/Pimcord e explicações em português.
- [ ] Incluir casos de correção de erros, imports, async, Views, REST, Gateway e permissões.
- [ ] Manter casos de dados sensíveis fora da geração de respostas perigosas.
- [ ] Deduplicar por conteúdo normalizado e dividir por tarefa, não apenas por linha.
- [ ] Criar conjunto retido de generalização que não seja usado no treinamento.
- [ ] Medir cobertura e preparar o primeiro treinamento próprio.


## Corpus e primeiro experimento — resultado

- [x] Preparador ampliado com categorias, níveis, dependências, tags, objetivos e critérios.
- [x] Placeholders genéricos rejeitados durante a preparação.
- [x] Coletor real da árvore Pimcord criado, sem respostas sintéticas.
- [x] Corpus bruto: 139 exemplos; corpus aceito: 133 exemplos.
- [x] Divisão por fonte: 92 treino, 21 validação e 20 teste; 109 fontes.
- [x] PyTorch instalado no ambiente de treinamento.
- [x] Smoke test do Transformer próprio concluído com checkpoints e perda de validação.
- [x] Suíte integral: 253 testes passando.
- [ ] Empacotar o corpus e a documentação atualizados.
