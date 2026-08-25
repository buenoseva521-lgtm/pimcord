# Treinamento da PimcordIA

Este diretório contém o pipeline para treinar uma PimcordIA própria especializada em Python e na API Pimcord. Ele não inclui pesos pré-treinados nem promete uma IA geral pronta: o modelo só passa a existir depois que o usuário fornece um dataset licenciado e executa o treinamento em hardware apropriado.

## Fluxo

O processo agora é dividido em preparação, treino, avaliação e integração. Primeiro, coloque exemplos autorizados em `dados/brutos/*.jsonl`, com um objeto por linha contendo `codigo`, `linguagem`, `fonte` e `licenca`. Exemplos instrucionais podem acrescentar `instrucao`, `contexto`, `arquivos` e `testes`; exemplos sem instrução são mantidos como continuação de código e não são tratados como respostas de especialista.

Depois execute `python -m treinamento.preparar_dataset --origem dados/brutos --destino dados/limpos.jsonl`. O script valida AST, remove segredos, deduplica por instrução/contexto/resposta e grava `dados/limpos.manifesto.json`. Os splits são separados por fonte/projeto, reduzindo vazamento entre treino e validação. Em seguida, treine com `python -m treinamento.treinar --dataset dados/limpos.jsonl --saida modelos/pimcordia --passos 1000`. O diretório final conterá tokenizer, checkpoints, modelo e `treino.json` com seed, configuração e métricas.

Por fim, rode os benchmarks de sintaxe Python e geração de projetos antes de conectar o modelo ao `bot_pronto`. Um checkpoint é experimental até demonstrar melhora sobre o fallback local em tarefas nunca vistas; perda de treino, tamanho do arquivo ou texto aparentemente elaborado não comprovam especialização.

O pipeline foi desenhado para não raspar código sem verificar licença. Não coloque tokens, dados pessoais, código proprietário ou arquivos cuja licença não permita treinamento. O dataset deve conter exemplos Python, testes, documentação e exemplos Pimcord com autorização compatível.

## Especialização recomendada com LoRA

A rota recomendada para a PimcordIA é adaptar um modelo de código aberto já pré-treinado, em vez de treinar um modelo geral do zero. A primeira configuração avaliada usa `Qwen2.5-Coder-7B-Instruct` em um diretório local, com `treinamento/adaptar.py`. O script é offline: não baixa pesos e exige `transformers`, `datasets`, `peft` e `torch` instalados no ambiente de treinamento. As dependências estão listadas em `treinamento/requirements.txt` e não fazem parte da instalação mínima do Pimcord.

```bash
python -m treinamento.adaptar \\
  --base modelos/Qwen2.5-Coder-7B-Instruct \\
  --dataset dados/limpos.jsonl \\
  --saida modelos/pimcordia-lora \\
  --passos 1000
```

O gate padrão recusa corpora pequenos. `--permitir-dataset-pequeno` existe somente para smoke test e nunca deve produzir um checkpoint divulgado como especialista. O adaptador gerado precisa passar pelo benchmark de tarefas inéditas antes de ser integrado ao `bot_pronto`.

## Diagnóstico automático

Antes de qualquer treinamento, execute:

```bash
python -m treinamento.diagnosticar
```

O diagnóstico não instala nada nem baixa pesos. Ele informa se há dependências e GPU suficientes. Quando não houver, a recomendação será não treinar naquele aparelho e usar posteriormente um checkpoint quantizado para inferência no Pydroid/Termux.

## Hardware e expectativas

Treinar do zero exige uma GPU com memória suficiente, armazenamento para checkpoints e tempo de treinamento. O Pydroid pode executar inferência de um modelo já treinado, mas não é um ambiente adequado para treinar um modelo de programação grande. A configuração inicial é deliberadamente pequena para validação do pipeline; ela não deve ser confundida com um modelo especialista de produção.

O contrato de qualidade está em `ARQUITETURA.md`: o modelo precisa gerar código compilável, respeitar a API instalada, passar validações de segurança e corrigir falhas observadas pelo agente. Enquanto esses gates não forem medidos, a PimcordIA deve permanecer em modo experimental e o fallback local não deve ser removido.

## Integração posterior

A integração com `bot_pronto` só deve ser ativada depois de o modelo passar pelos benchmarks. O modelo deve gerar uma representação estruturada de arquivos, ser validado com `ast`, ter imports e chamadas perigosas rejeitados, e nunca receber tokens do Discord no prompt.


## Modelo próprio inicializado do zero

A implementação `pimcord.modelo_proprio` oferece uma arquitetura Transformer causal com tokenizador byte-level próprio. Ela não usa pesos externos nem modelo-base. O treinamento exige PyTorch apenas no ambiente de treinamento; o `import pimcord` básico não depende dessa biblioteca.

Para montar o corpus real da árvore Pimcord e preparar divisões por fonte, use:

```bash
python3 treinamento/coletar_corpus_pimcord.py --raiz . --destino dados/brutos/pimcord_local.jsonl
python3 treinamento/preparar_dataset.py --origem dados/brutos --destino dados/limpos.jsonl --validacao 0.15 --teste 0.15
```

O coletor usa código Python real do projeto e blocos Python completos da documentação. Ele não inventa respostas. O preparador agora rejeita placeholders como “o comando foi executado com sucesso”, registra categoria, nível, dependências, tags, objetivo e critérios, além de gravar métricas no manifesto.

Para um primeiro experimento:

```bash
python3 -m pip install torch
python3 treinamento/treinar_proprio.py \
  --dataset dados/limpos.jsonl \
  --saida modelos/pimcordia-propria-v0 \
  --passos 1000 \
  --intervalo-checkpoint 250 \
  --camadas 4 \
  --dimensao 256 \
  --cabecas 8 \
  --contexto 2048 \
  --dispositivo cpu
```

O script grava checkpoints intermediários em `modelos/pimcordia-propria-v0/checkpoints/`, mede a perda no split de validação e salva `treinamento.json` com seed, configuração, perda de treino e perda de validação. Uma perda menor não garante que o modelo gere bots completos; os prompts retidos, compilação e testes continuam sendo o gate de qualidade.

No primeiro experimento local realizado durante o desenvolvimento, foram encontrados 139 exemplos brutos, 133 aceitos, 92 no treino, 21 na validação e 20 no teste, provenientes de 109 fontes de arquivo. Um smoke test de dois passos com arquitetura mínima gerou checkpoints e mostrou queda de perda de treino de 22,12 para 21,45 e de validação de 21,88 para 21,82. Isso confirma o pipeline, não a especialização final do modelo.
