# Arquitetura da PimcordIA Neural

## Objetivo

A PimcordIA Neural deve ser um modelo local de geração de código Python e Pimcord, com capacidade de interpretar requisitos, planejar arquivos, escrever código, revisar a própria saída e corrigir erros observados em compilação e testes. O motor neural não deve ser confundido com o interpretador local atual: regras e templates são fallback determinístico, não prova de inteligência geral.

## Contrato de uma super IA

Para este projeto, “super IA” não significa apenas produzir texto que parece código. A PimcordIA deverá receber uma descrição aberta em português e entregar um projeto coerente com múltiplos arquivos, comandos prefixo e slash, Views, cogs, eventos, persistência, permissões, tratamento de erros e testes quando esses requisitos fizerem parte do pedido. Ela deverá saber dizer quando a API não oferece um recurso, pedir esclarecimentos quando o pedido for incompleto e nunca preencher lacunas com métodos inventados.

A qualidade será medida por tarefas inéditas. Uma tarefa só é aprovada quando os arquivos compilam, os testes de contrato passam, as APIs usadas existem no catálogo da versão, as permissões fazem sentido, os efeitos solicitados são realmente implementados e nenhuma regra de segurança é violada. Código apenas sintaticamente válido ou resposta que repete argumentos não conta.

## Limite técnico importante

Um modelo GPT-2 inicializado do zero não conhece Python, asyncio, HTTP ou Pimcord antes de receber treinamento suficiente. Portanto, a existência do script de treino não autoriza declarar que a biblioteca já possui uma IA especialista. A integração só poderá substituir o fallback depois de um checkpoint treinado e aprovado pelos benchmarks. Uma super IA exigirá corpus amplo, treinamento real, memória recuperável da API, agente de ferramentas e avaliação contínua; esses componentes não podem ser substituídos por templates fixos.

## Camadas

| Camada | Responsabilidade | Critério de aceite |
| --- | --- | --- |
| Catálogo | Extrair símbolos, assinaturas, docstrings e exemplos da instalação real | Catálogo versionado e reproduzível |
| Dataset | Converter exemplos licenciados em instruções, contexto e respostas | Deduplicação, licença, split sem vazamento |
| Modelo | Predizer planos, arquivos e correções | Perda de validação menor que a de treino e benchmark crescente |
| Agente | Orquestrar planejar, gerar, compilar, testar e corrigir | Limite de iterações, logs e artefatos auditáveis |
| Segurança | Validar AST, caminhos, imports e ações proibidas | Nenhuma saída insegura passa ao executor |
| Integração | Usar o modelo apenas quando houver checkpoint válido | Ausência de checkpoint gera diagnóstico claro |

## Formato de exemplo

Cada linha do dataset deve conter JSON com `id`, `instrucao`, `contexto`, `resposta`, `arquivos`, `testes`, `fonte` e `licenca`. A resposta deve ser código ou uma operação estruturada; pedidos sem informação suficiente devem resultar em perguntas de esclarecimento, não em comandos fictícios.

## Treinamento

O pipeline deve produzir tokenizer e modelo em diretórios versionados, separar treino e validação por projeto, registrar configuração, quantidade de tokens, perda e seed, e permitir retomada de checkpoint. O corpus deve combinar Python geral, asyncio, SQLite, HTTP assíncrono, testes e a API pública do Pimcord. Exemplos sintéticos podem complementar o corpus, mas não devem ser apresentados como conhecimento extraído de projetos reais.

## Agente iterativo

1. Interpretar a solicitação em JSON estruturado.
2. Consultar o catálogo real da versão instalada.
3. Planejar arquivos, dependências, permissões e testes.
4. Gerar a menor versão completa que satisfaça o contrato.
5. Executar apenas compilação e validações permitidas em diretório temporário.
6. Coletar erros determinísticos.
7. Pedir ao modelo uma correção localizada, preservando partes válidas.
8. Repetir até o limite configurado.
9. Entregar somente artefatos que passaram por segurança e compilação; testes falhos permanecem explicitamente reportados.

## Gates antes da integração

A integração padrão exige um corpus instrucional licenciado e deduplicado, split por projeto, validação de sintaxe acima de 99%, cobertura dos contratos principais do Pimcord, benchmark com tarefas nunca vistas, zero passagem de chamadas proibidas no validador e taxa de correção superior ao fallback local. Para a denominação “super IA”, acrescenta-se a aprovação em Python geral, asyncio, SQLite, REST, Gateway, comandos híbridos, Views, cogs, permissões, moderação, economia, tickets, tratamento de erros e segurança.

Sem esses números e sem um checkpoint distribuível, o modelo deve permanecer experimental e não ser vendido como especialista. O modo estável do Pimcord continuará usando o fallback local até que a evidência justifique a troca.

## Benchmarks

O conjunto de avaliação deve conter tarefas de Python geral, asyncio, SQLite, REST, Gateway, comandos híbridos, slash commands, Views persistentes, tratamento de erros, migração e segurança. Cada tarefa deve ser avaliada por compilação, testes, aderência estrutural, uso correto da API e ausência de ações perigosas. A métrica principal é `taxa_de_tarefas_aprovadas`, não apenas a similaridade textual.
