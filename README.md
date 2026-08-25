# Pimcord

[![Python](https://img.shields.io/badge/Python-%3E%3D3.11-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-0B3D2E.svg)](LICENSE)
[![GitHub](https://img.shields.io/badge/GitHub-reposit%C3%B3rio%20open%20source-181717?logo=github&logoColor=white)](https://github.com/<SEU_USUARIO>/pimcord)
[![PyPI](https://img.shields.io/badge/PyPI-a%20publicar-lightgrey.svg)](https://pypi.org/project/pimcord/)
[![Status](https://img.shields.io/badge/status-em%20desenvolvimento-D97706.svg)](CHANGELOG.md)

**Pimcord** é uma biblioteca Python assíncrona para criação de bots Discord, com uma API em português e uma arquitetura composta por gateway, cliente REST, comandos, interações, modelos de recursos, voz, tarefas, persistência, segurança e diagnóstico.

O projeto prioriza contratos explícitos, testes offline e uma experiência de desenvolvimento em português. A implementação existente é preservada neste repositório; esta publicação organiza o código, a documentação e os exemplos para facilitar revisão e contribuição.

> **Status atual:** o `pyproject.toml` declara a versão `0.6.9`, Python `>=3.11` e dependência de runtime `aiohttp>=3.9,<4`. O changelog contém notas de evolução da linha `0.7.0`; qualquer mudança de versão deve ser feita como uma decisão de release, não inferida automaticamente.

## Recursos principais

A superfície pública inclui o ciclo de vida de `Bot`, comandos prefixados, slash e híbridos, checks e cooldowns, eventos do gateway, cliente REST, modelos Discord, interações efêmeras, Views e componentes, OAuth2, webhooks, automoderação offline-first, cache local, SQLite, coordenação de workers, sharding, métricas, diagnóstico de saúde, segurança de segredos, tarefas assíncronas e áudio/voz com codecs opcionais.

O pacote também contém áreas experimentais e especializadas. Elas permanecem no código original para não remover funcionalidades importantes, mas devem ser avaliadas separadamente antes de uma promessa de estabilidade ou publicação no PyPI.

## Instalação local

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[testes]"
```

A instalação de runtime pode ser feita sem as dependências de teste:

```bash
python -m pip install -e .
```

A distribuição PyPI ainda não foi confirmada neste repositório. Quando o pacote for publicado, substitua este trecho pelo comando de instalação validado e remova o badge temporário de PyPI.

## Primeiro bot

```python
import os
import pimcord

intents = pimcord.Intents(
    servidores=True,
    mensagens=True,
    conteudo_mensagens=True,
)

bot = pimcord.Bot(prefixo="!", intents=intents)

@bot.comando("ola", aliases=["oi"])
async def ola(ctx):
    await ctx.responder("Olá, mundo!")

@bot.evento("pronto")
async def pronto():
    print("Bot conectado ao Discord")

bot.iniciar(os.environ["DISCORD_TOKEN"])
```

Mantenha o token em uma variável de ambiente e nunca o coloque em arquivos versionados, argumentos de shell, issues ou logs.

## Exemplos

Os exemplos funcionais estão em [`examples/`](examples/):

| Arquivo | Conteúdo |
| --- | --- |
| [`bot_basico.py`](examples/bot_basico.py) | Bot mínimo com comando prefixado e evento `pronto`. |
| [`bot_completo.py`](examples/bot_completo.py) | Comandos híbridos, slash, aliases e purga limitada. |
| [`comandos_slash.py`](examples/comandos_slash.py) | Configuração de aplicação e sincronização de comandos slash. |
| [`interacoes.py`](examples/interacoes.py) | View com botão, adiamento e follow-up efêmero. |

Cada exemplo deve continuar compatível com a API real presente no pacote. Nenhum exemplo deve conter tokens reais.

## Documentação

A documentação oficial navegável está em [pimcorddocs-pvmazbtg.manus.space](https://pimcorddocs-pvmazbtg.manus.space). Ela possui índice completo da API, páginas por módulo, assinaturas e docstrings extraídas do pacote, guias de primeiro bot, comandos, interações, segurança e voz, busca semântica e changelog.

O material fonte existente também está em [`docs/`](docs/), além dos documentos históricos na raiz. Não remova relatórios, matrizes ou evidências sem revisar suas dependências e seu valor de auditoria.

A documentação específica de funcionalidades assistidas por IA continua em [`docs/IA_E_BOT_PRONTO.md`](docs/IA_E_BOT_PRONTO.md). O site público de referência acima foi deliberadamente mantido fora desse escopo editorial.

## Testes e qualidade

Para instalar as dependências de desenvolvimento e executar a suíte offline:

```bash
python -m pip install -e ".[testes]"
python -m pytest -q
python -m build
```

A suíte inclui contratos para núcleo, eventos, gateway, REST, interações, segurança, sharding, tarefas, voz, SQLite e regressões. Alguns cenários dependem de bibliotecas opcionais ou de capacidades externas; o resultado deve ser reportado sem transformar testes offline em prova de interoperabilidade completa com o Discord.

## Contribuindo

Leia [`CONTRIBUTING.md`](CONTRIBUTING.md), [`SECURITY.md`](SECURITY.md) e a documentação antes de propor mudanças. Pull requests devem preservar a API existente quando possível, incluir testes determinísticos sem rede, atualizar a documentação em português e explicar qualquer mudança de contrato. Nunca inclua tokens, senhas, chaves, dumps privados ou arquivos de ambiente.

Para relatar um bug, use o template de issue e informe a versão, o menor caso reproduzível, o comportamento esperado e o traceback sem dados sensíveis. Para propor um recurso, explique primeiro o problema, depois a API e o impacto arquitetural.

## Licença

O Pimcord é distribuído sob a licença [MIT](LICENSE).

## Links de publicação

| Recurso | Estado |
| --- | --- |
| Repositório GitHub | Placeholder até a criação/autorização do repositório: `https://github.com/<SEU_USUARIO>/pimcord`. |
| Documentação oficial | [pimcorddocs-pvmazbtg.manus.space](https://pimcorddocs-pvmazbtg.manus.space). |
| PyPI | Ainda não confirmado; não trate o link como prova de publicação. |
