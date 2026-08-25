# Auditoria de versionamento — Pimcord 0.6.9

**Data:** 25 de agosto de 2026  
**Escopo:** referências de versão no código, metadados, documentação, exemplos, testes, workflows e artefatos de distribuição.

## Resultado executivo

A versão oficial atual do Pimcord é **0.6.9**. O código-fonte já expunha `pimcord.__version__ = "0.6.9"` e o `pyproject.toml` já declarava `version = "0.6.9"`. A auditoria encontrou referências atuais inconsistentes a 0.7.0 no User-Agent HTTP, nos cabeçalhos de dois exemplos, no changelog, no template de issue e no texto de status do README. Essas referências foram corrigidas sem alteração da API ou da implementação funcional.

## Arquivos corrigidos

| Arquivo | Correção |
| --- | --- |
| `pimcord/http/cliente.py` | User-Agent alinhado para `Pimcord/0.6.9`. |
| `examples/bot_completo.py` | Cabeçalho do exemplo alinhado para 0.6.9. |
| `examples/interacoes.py` | Cabeçalho do exemplo alinhado para 0.6.9. |
| `CHANGELOG.md` | Release corrente convertida para `## [0.6.9]`; subseções mantidas; referência ao wheel corrigida. |
| `README.md` | Status atual passou a declarar 0.6.9 e o changelog como histórico. |
| `CONTRIBUTING.md` | Cabeçalho alinhado para 0.6.9 e documentos 0.7.0 contextualizados como históricos. |
| `.github/ISSUE_TEMPLATE/bug.yml` | Placeholder da versão atualizado para 0.6.9. |
| `docs/README.md` | Regra explícita para interpretar arquivos 0.7.0 como histórico. |
| `docs/VALIDACAO_SUPERIORIDADE.md` | Documento identificado como histórico da linha 0.7.0. |

## Fontes de verdade verificadas

`pimcord.__version__`, `pyproject.toml`, a versão do wheel, a versão do sdist, o workflow de CI e os testes de importação reconhecem **0.6.9**. Não há `setup.py`, `setup.cfg` ou arquivo separado `_version.py` competindo com essas fontes.

## Referências históricas preservadas

Foram mantidos os relatórios, matrizes, planos e notas que registram a evolução de linhas anteriores, incluindo arquivos nomeados com `0.7.0`, referências a 0.6.7 na documentação histórica da PimcordIA e a matriz histórica de paridade 0.5.0. Esses textos não foram reescritos artificialmente. O `docs/README.md` agora explica que tais documentos são históricos e não representam a versão atual.

A variável `versao_conhecimento = "0.6.7"` em `pimcord/ia.py` também foi mantida: ela identifica o estado de conhecimento do componente de IA, não a versão de distribuição do pacote. A área de IA permanece fora do índice público da documentação navegável.

## Testes e build

A suíte executada após as correções terminou com **252 testes aprovados e 1 ignorado**. O build foi executado com `python -m build` após a limpeza do diretório `dist/` e gerou somente:

- `pimcord-0.6.9-py3-none-any.whl`
- `pimcord-0.6.9.tar.gz`

O `METADATA` do wheel e o `PKG-INFO` do sdist foram conferidos e ambos informam `Version: 0.6.9`.

## Busca final

A busca final não encontrou referências atuais de 0.7.0 em código, metadados, exemplos, testes ou workflow. As ocorrências restantes de 0.7.0 estão em relatórios, planos, matrizes e notas históricas, além das referências de contexto que explicitamente as identificam como históricas. Nenhuma release nova foi criada ou publicada durante esta auditoria.
