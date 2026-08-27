# Documentação do Pimcord

A documentação oficial navegável está em [pimcorddocs-pvmazbtg.manus.space](https://pimcorddocs-pvmazbtg.manus.space/). Ela é a porta de entrada para instalar o pacote publicado, criar o primeiro bot, aprender recursos e consultar a API.

## Caminho recomendado para usuários

| Ordem | Página | Objetivo |
| --- | --- | --- |
| 1 | [Comece aqui](https://pimcorddocs-pvmazbtg.manus.space/comecar) | Entender o projeto, instalar e executar o primeiro bot. |
| 2 | [Instalação](https://pimcorddocs-pvmazbtg.manus.space/instalacao) | Conferir Python, PyPI, atualização e problemas comuns. |
| 3 | [Guias](https://pimcorddocs-pvmazbtg.manus.space/guias/comandos) | Aprender comandos, eventos, mensagens, interações e segurança. |
| 4 | [Receitas](https://pimcorddocs-pvmazbtg.manus.space/receitas/criar-comando) | Resolver tarefas pequenas com exemplos copiáveis. |
| 5 | [API completa](https://pimcorddocs-pvmazbtg.manus.space/api) | Consultar classes, funções, métodos, assinaturas e docstrings. |
| 6 | [Migração do discord.py](https://pimcorddocs-pvmazbtg.manus.space/migrar) | Comparar apenas conceitos e equivalências confirmadas. |

## Guias fonte

| Documento | Uso |
| --- | --- |
| [`GUIA_USUARIO.md`](GUIA_USUARIO.md) | Caminho de instalação, primeiro bot, token e próximos passos. |
| [`FAQ.md`](FAQ.md) | Respostas verificadas para dúvidas recorrentes. |
| [`MIGRACAO_DISCORD_PY.md`](MIGRACAO_DISCORD_PY.md) | Comparação factual e limites para quem vem do discord.py. |
| [`API.md`](API.md) | Referência textual principal do contrato público. |

## Fonte de verdade

O código em [`pimcord/`](../pimcord/) é a fonte de verdade para nomes, assinaturas e comportamento. O pacote publicado no PyPI é [`pimcord 0.6.9`](https://pypi.org/project/pimcord/), e a instalação normal deve usar `pip install pimcord`.

A referência textual [`API.md`](API.md) e a referência navegável devem ser corrigidas quando divergirem do código. Quando uma informação não puder ser confirmada na implementação ou nos metadados, ela não deve ser inventada.

## Organização para contribuidores

Relatórios, auditorias, matrizes, roadmaps, notas de arquitetura e evidências ficam neste diretório e na raiz por razões históricas. Eles não compõem o caminho principal do usuário. Documentos cujo nome ou conteúdo menciona `0.7.0` ou outra linha futura devem ser lidos como registros de desenvolvimento, não como prova de que uma API está disponível em 0.6.9.

> **Aviso de desenvolvimento:** este documento descreve materiais internos, históricos ou de planejamento e pode não representar a API atualmente publicada.

Para contribuir, leia [`CONTRIBUTING.md`](../CONTRIBUTING.md), [`SECURITY.md`](../SECURITY.md) e o [guia de desenvolvimento no site](https://pimcorddocs-pvmazbtg.manus.space/desenvolvimento). A área de desenvolvimento deve preservar testes offline, contratos públicos e documentação em português.

A documentação específica de funcionalidades assistidas por IA está em [`IA_E_BOT_PRONTO.md`](IA_E_BOT_PRONTO.md) e permanece separada do índice público principal.
