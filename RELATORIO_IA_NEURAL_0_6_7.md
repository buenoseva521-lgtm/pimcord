# Relatório da PimcordIA Neural — versão 0.6.7

## Estado real da entrega

A versão 0.6.7 permanece estável e offline. A biblioteca não passou a fingir que um modelo GPT-2 pequeno já conhece Python inteiro: foi adicionada uma base neural treinável, um adaptador de checkpoint local e um agente de revisão com limite de tentativas. Sem pesos treinados no diretório `modelos/`, o comportamento padrão continua sendo o fallback local determinístico.

| Área | Resultado verificado |
| --- | --- |
| Suíte Pimcord | 253 testes aprovados em 1,65 s |
| Preparação de dataset | AST, licenças permitidas, segredo, deduplicação e manifesto |
| Separação de dados | Splits por fonte/projeto para reduzir vazamento |
| Treino | Tokenizer, configuração causal, seed, retomada e métricas |
| Inferência | Apenas checkpoint local; sem rede e sem chave externa |
| Catálogo runtime | 285 linhas de símbolos, assinaturas e métodos públicos da instalação |
| Agente | JSON, AST, caminhos, chamadas perigosas, compilação e até oito tentativas |
| Corpus próprio | 33 módulos encontrados; 31 exemplos aceitos após normalização |
| Benchmark público do fallback | 4 de 5 tarefas aprovadas; 80% e gate público aprovado |
| Benchmark retido do fallback | 0 de 4 tarefas aprovadas; gate retido reprovado |
| Gate global atual | Reprovado, como esperado antes da especialização neural |
| Modelo especialista | Ainda não comprovado; depende de dataset, treino e benchmark neural |

## Arquivos novos

`treinamento/ARQUITETURA.md` define o contrato de qualidade e os gates de integração. `treinamento/preparar_dataset.py` prepara exemplos instrucionais licenciados com splits por fonte e fallback determinístico sinalizado para corpora pequenos. `treinamento/gerar_corpus_proprio.py` coleta sementes do código próprio com origem e licença. `treinamento/treinar.py` cria checkpoints experimentais com métricas e recusa datasets pequenos por padrão. `treinamento/benchmark.py` mede tarefas observáveis. `pimcord/catalogo.py` cria a memória runtime da API. `pimcord/modelo_neural.py` carrega um checkpoint local offline e executa revisão iterativa sem executar o código gerado.

## Como validar

A suíte offline pode ser executada com `python3 -m pytest -q testes treinamento`. O benchmark determinístico pode ser executado com `PYTHONPATH=. python3 treinamento/benchmark.py --conjunto todos --saida benchmark.json`. Ele separa tarefas públicas de tarefas retidas e exige pelo menos 80% em cada conjunto. O fallback atual passa no público (4/5), mas reprova no retido (0/4), portanto não é uma super IA. Para um modelo neural real, prepare primeiro o dataset licenciado, treine em hardware adequado e execute `PYTHONPATH=. python3 treinamento/benchmark.py --modelo modelos/pimcordia/modelo`.

## Decisão de integração

O modelo neural **não foi conectado como padrão ao `bot_pronto`**, porque não há checkpoint treinado e aprovado neste ambiente. Essa decisão preserva a estabilidade e impede que um modelo sem evidência substitua uma implementação que já passa pela suíte. A integração automática será segura quando a taxa de tarefas aprovadas do modelo superar o fallback em um conjunto de avaliação não usado no treino, com ausência de violações de segurança.
