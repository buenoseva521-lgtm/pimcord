# Pimcord 0.7.0 — Arquitetura de superprojeto

## Propósito

O Pimcord 0.7.0 será uma biblioteca assíncrona para bots Discord com API nativa em português brasileiro, contratos explícitos, transporte real isolado da camada de domínio e uma documentação local que não depende de requisições externas para ser construída ou consultada.

A meta não é copiar a implementação de outra biblioteca. A meta é cobrir uma superfície funcional ampla com arquitetura própria, nomes previsíveis, testes de contrato e compatibilidade consciente entre versões.

## Princípios não negociáveis

| Princípio | Decisão de arquitetura |
|---|---|
| Português primeiro | Decorators, modelos, exceções, parâmetros e documentação usam nomes em português; aliases em inglês só existem quando ajudam migração. |
| Async-first | Toda operação de rede, persistência potencialmente bloqueante, áudio e callback de usuário possui caminho assíncrono. |
| Transporte separado | Gateway, REST, Voice Gateway e UDP não vazam detalhes de protocolo para comandos e modelos. |
| Sem promessas falsas | A documentação identifica cada símbolo como estável, experimental, base ou roadmap. |
| Testável sem token | Fixtures, servidor falso, payloads locais e transportes injetáveis cobrem o comportamento sem conectar a uma conta real. |
| Offline-first na documentação | O site usa conteúdo versionado localmente; busca, exemplos e referência não dependem de API externa. |
| Compatibilidade progressiva | A superfície pública ganha contratos versionados e avisos de depreciação antes de mudanças incompatíveis. |

## Camadas

```text
Aplicação do usuário
    ↓
API pública em português
    ├── Bot, comandos, híbridos, listeners e lifecycle
    ├── Interações, Views, modais, follow-ups e webhooks
    ├── Modelos: servidores, canais, mensagens, membros, cargos e permissões
    └── Extensões, tarefas, cache, banco, métricas e CLI
    ↓
Orquestração
    ├── Dispatcher de eventos
    ├── Registro de componentes persistentes
    ├── Sincronizador de comandos
    ├── Supervisor de shards
    └── Políticas de retry, timeout e cancelamento
    ↓
Transportes
    ├── REST com buckets, paginação, uploads e rate limits
    ├── Gateway WebSocket com heartbeat, ACK, Resume e reconexão
    ├── Voice Gateway + UDP + player de áudio
    └── Webhook transport
    ↓
Infraestrutura
    ├── Serialização e desserialização
    ├── Persistência SQLite e adaptadores
    ├── Observabilidade, logs, métricas e diagnóstico
    └── Fixtures e servidores falsos
```

## Domínios do release

| Domínio | Superfície prevista | Critério de pronto |
|---|---|---|
| Núcleo | `Bot`, configuração, intents, lifecycle, eventos e erros | Ciclo de vida determinístico, cancelamento seguro e diagnóstico reproduzível. |
| REST | Mensagens, canais, cargos, membros, threads, fóruns, auditoria, uploads e paginação | Rotas tipadas, rate limits por bucket/global, retries seguros e payloads testados. |
| Gateway | Hello, Identify, heartbeat, ACK, Resume, invalid session, close codes e reconexão | Máquina de estados testada com servidor falso e backoff controlado. |
| Comandos | Prefixo, slash, híbridos, grupos, opções, conversores, checks, cooldowns e help | Um callback compartilhado pode ser invocado pelos transportes suportados. |
| Interações | Resposta inicial, defer, follow-up, ephemeral, edição/exclusão, componentes e modais | Tokens, expiração, acknowledgement e erros possuem contratos explícitos. |
| Views | Botões, selects, modais, IDs, timeout, persistência e reidratação | Restart simulado recupera componentes registrados sem código repetido do usuário. |
| Discord | Modelos, eventos, permissões, intents e cache | Payloads conhecidos preservam campos brutos e não quebram atributos existentes. |
| Plataforma | Extensões, tarefas, filas, locks, SQLite, webhooks e métricas | Falhas e encerramento não deixam tarefas órfãs nem sessões abertas. |
| Voz | Voice Gateway, UDP, criptografia, fontes e player | Transporte isolado e testes sem exigir dependência de áudio no núcleo. |
| Sharding | Cálculo, workers, supervisão, saúde e distribuição | Falhas de worker, heartbeat e configuração são observáveis e recuperáveis. |
| Ferramentas | CLI, scaffolding, diagnóstico, docs locais e empacotamento | Projeto novo instala, testa e executa sem copiar arquivos manualmente. |

## Contrato público

A API pública deve ser reexportada por `pimcord` quando for estável. Cada recurso deve possuir uma docstring em português, exemplo mínimo, exemplo de produção, comportamento de erro e teste de contrato. Módulos internos não devem ser necessários para o uso normal.

Os decorators principais devem aceitar duas formas quando isso não gerar ambiguidade:

```python
@bot.evento("pronto")
async def pronto():
    ...

@bot.evento
async def ao_ligar():
    ...
```

Comandos híbridos devem declarar uma única função de domínio:

```python
@bot.hibrido("perfil", descricao="Mostra o perfil")
async def perfil(ctx):
    await ctx.responder("Perfil carregado")
```

## Política de versão

O release `0.7.0` será considerado um marco de expansão de superfície, não uma promessa de que todas as capacidades do Discord estão finalizadas. Recursos sem testes de contrato permanecem marcados como experimentais. Mudanças posteriores devem preservar aliases, emitir avisos de depreciação e atualizar a documentação no mesmo commit.

## Regra de documentação

Nenhuma página pode descrever uma função que não exista no pacote. Cada artigo deve conter: o problema resolvido, o modelo mental, o fluxo interno, o exemplo mínimo, um exemplo completo, limites, permissões Discord necessárias, erros esperados e links para testes locais. A referência automática deve ser derivada dos exports e das assinaturas efetivamente presentes no código.
