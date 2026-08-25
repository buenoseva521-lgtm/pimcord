# Fontes candidatas para o corpus

A PimcordIA não deve tratar “código público” como sinônimo de “código livre para treinamento”. Cada projeto precisa ser verificado individualmente, com licença, aviso de copyright, origem e política de uso registrados no manifesto.

| Fonte | Uso possível | Risco e decisão |
| --- | --- | --- |
| Documentação e exemplos próprios da Pimcord | Conhecimento específico da biblioteca | Prioridade máxima; manter autoria e licença do projeto |
| Projetos Python próprios com licença permissiva | Python geral, asyncio, SQLite e testes | Aceitar somente após confirmar licença e remover segredos |
| The Stack / The Stack v2 | Pré-treinamento amplo de código | Não importar indiscriminadamente: a composição inclui licenças variadas e exige filtragem por projeto e termos |
| Datasets do Hugging Face | Distribuição e versionamento de conjuntos selecionados | O card do dataset e a licença do conteúdo precisam ser lidos separadamente; não confiar apenas no rótulo da plataforma |

Referências para auditoria: [Hugging Face — Licenses](https://huggingface.co/docs/hub/en/repositories-licenses), [Hugging Face — Dataset Cards](https://huggingface.co/docs/hub/en/datasets-cards), [BigCode — The Stack](https://www.bigcode-project.org/docs/about/the-stack/), [The Stack v2](https://huggingface.co/datasets/bigcode/the-stack-v2) e [StarCoder 2 and The Stack v2](https://arxiv.org/abs/2402.19173).

O pipeline da Pimcord aceita somente as licenças configuradas em `preparar_dataset.py` e grava a fonte por exemplo. Essa lista é um filtro inicial, não uma autorização automática: o responsável pelo corpus deve revisar os termos de cada projeto antes do uso.
