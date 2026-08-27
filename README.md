# Pimcord

[![CI](https://github.com/buenoseva521-lgtm/pimcord/actions/workflows/ci.yml/badge.svg)](https://github.com/buenoseva521-lgtm/pimcord/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/Python-%3E%3D3.11-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![PyPI](https://img.shields.io/pypi/v/pimcord.svg)](https://pypi.org/project/pimcord/)
[![License: MIT](https://img.shields.io/badge/license-MIT-0B3D2E.svg)](LICENSE)

**Pimcord** é uma biblioteca Python assíncrona para criar bots Discord com uma API em português. A versão publicada atualmente é **0.6.9**.

O projeto reúne ciclo de vida de bot, Gateway, cliente REST, comandos prefixados, slash e híbridos, eventos, modelos Discord, interações, Views e componentes, permissões, tarefas, persistência, segurança, diagnóstico, sharding, métricas e recursos experimentais de voz. A lista pública deve ser interpretada junto com o código e a referência da API; roadmaps e relatórios históricos não representam automaticamente funcionalidades disponíveis.

## Comece aqui

O caminho mais curto para criar um bot é:

| Etapa | O que fazer |
| --- | --- |
| Entender | Leia o [guia de início](https://pimcorddocs-pvmazbtg.manus.space/comecar). |
| Instalar | Use `pip install pimcord` em um ambiente virtual. |
| Configurar | Guarde o token em `DISCORD_TOKEN` e ative somente os intents necessários. |
| Construir | Comece pelo [primeiro bot](https://pimcorddocs-pvmazbtg.manus.space/guias/primeiro-bot). |
| Consultar | Pesquise classes, funções e métodos no [catálogo da API](https://pimcorddocs-pvmazbtg.manus.space/api). |
| Continuar | Escolha um [guia](https://pimcorddocs-pvmazbtg.manus.space/guias/comandos), uma [receita](https://pimcorddocs-pvmazbtg.manus.space/receitas/criar-comando) ou a [migração do discord.py](https://pimcorddocs-pvmazbtg.manus.space/migrar). |

## Instalação

A instalação recomendada para usuários é feita pelo PyPI:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install pimcord
```

O pacote requer **Python 3.11 ou superior**. Para confirmar a versão instalada:

```bash
python -c "import pimcord; print(pimcord.__version__)"
```

Para atualizar uma instalação existente:

```bash
python -m pip install --upgrade pimcord
```

Clone e instalação editável são caminhos para contribuidores e ficam descritos na documentação de desenvolvimento, não substituem a instalação normal pelo PyPI.

## Primeiro bot

O exemplo abaixo usa apenas APIs públicas confirmadas no pacote:

```python
import os
import pimcord

bot = pimcord.Bot(prefixo="!")

@bot.comando("ola")
async def ola(ctx):
    await ctx.responder("Olá!")

@bot.evento("pronto")
async def pronto():
    print("Bot conectado")

bot.iniciar(os.environ["DISCORD_TOKEN"])
```

Configure o segredo antes de executar:

```bash
export DISCORD_TOKEN="seu-token"
python bot.py
```

Nunca publique o token no GitHub, em prints, issues, logs, argumentos de shell ou arquivos versionados. Se o valor vazar, revogue-o no portal do Discord e gere outro.

## O que a biblioteca oferece

A documentação oficial classifica os recursos conforme o que pode ser confirmado no código e nos metadados atuais:

| Status | Interpretação |
| --- | --- |
| **Estável** | API pública coberta pelo contrato atual do pacote e pelos testes disponíveis. |
| **Experimental** | API existente que pode depender do ambiente, de bibliotecas nativas ou de validação adicional. Voz e áudio entram nesta categoria. |
| **Planejado** | Intenção registrada em roadmap ou relatório; não deve ser usada como API disponível. |
| **Não disponível** | Recurso que não deve ser anunciado como completo sem implementação e integração correspondentes. |

## Documentação oficial

A referência completa está em **[pimcorddocs-pvmazbtg.manus.space](https://pimcorddocs-pvmazbtg.manus.space/)**. Ela foi organizada para seguir o fluxo **Descobrir → Entender → Copiar → Executar → Aprender**:

| Área | Conteúdo |
| --- | --- |
| [Comece aqui](https://pimcorddocs-pvmazbtg.manus.space/comecar) | Introdução, instalação, primeiro bot e próximos passos. |
| [Guias](https://pimcorddocs-pvmazbtg.manus.space/guias/comandos) | Comandos, eventos, mensagens, interações, segurança, configuração e voz. |
| [Receitas](https://pimcorddocs-pvmazbtg.manus.space/receitas/criar-comando) | Soluções pequenas para tarefas reais, com código copiável. |
| [API](https://pimcorddocs-pvmazbtg.manus.space/api) | Classes, funções, métodos, assinaturas, heranças e docstrings extraídas do código. |
| [Migração](https://pimcorddocs-pvmazbtg.manus.space/migrar) | Comparação factual com discord.py, sem prometer compatibilidade drop-in. |
| [FAQ](https://pimcorddocs-pvmazbtg.manus.space/faq) | Respostas verificadas para instalação, token, intents, erros e versão. |
| [Desenvolvimento](https://pimcorddocs-pvmazbtg.manus.space/desenvolvimento) | Arquitetura, limites, contribuição e separação entre uso e planejamento. |

A documentação fonte e os relatórios técnicos estão em [`docs/`](docs/). Arquivos que mencionam 0.7.0 ou outras versões futuras são históricos ou de desenvolvimento e estão marcados para não confundirem a versão publicada 0.6.9.

## Exemplos

Os exemplos funcionais estão em [`examples/`](examples/). Eles não contêm tokens reais e devem ser lidos junto com a referência da API:

| Arquivo | Demonstra |
| --- | --- |
| [`bot_basico.py`](examples/bot_basico.py) | Bot mínimo, comando prefixado e evento `pronto`. |
| [`bot_completo.py`](examples/bot_completo.py) | Comandos híbridos, slash, aliases e purga limitada. |
| [`comandos_slash.py`](examples/comandos_slash.py) | Configuração e sincronização de comandos slash. |
| [`interacoes.py`](examples/interacoes.py) | View com botão, adiamento e follow-up efêmero. |

## Para quem vem do discord.py

Pimcord possui conceitos semelhantes, mas não é uma substituição drop-in. Os nomes e contratos devem ser consultados no catálogo antes de portar um handler. A [área de migração](https://pimcorddocs-pvmazbtg.manus.space/migrar) cobre equivalências confirmadas para Bot, comandos, eventos, contexto, interações, intents e transporte.

## Desenvolvimento e contribuição

Leia [`CONTRIBUTING.md`](CONTRIBUTING.md), [`SECURITY.md`](SECURITY.md) e [`docs/README.md`](docs/README.md) antes de abrir uma alteração. Mudanças devem preservar a API existente quando possível, incluir testes determinísticos sem rede, atualizar a documentação em português e explicar qualquer alteração de contrato.

Para trabalhar no código localmente:

```bash
git clone https://github.com/buenoseva521-lgtm/pimcord.git
cd pimcord
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[testes]"
python -m pytest -q
python -m build
```

Nunca inclua tokens, senhas, chaves, dumps privados, `.env` ou credenciais em um commit. Para bugs, informe a versão, o menor caso reproduzível, o comportamento esperado e um traceback sem dados sensíveis.

## Qualidade

O CI executa a suíte offline, valida empacotamento e confirma a importação e a versão do pacote em Python 3.11, 3.12 e 3.13. Testes offline comprovam contratos locais; não devem ser tratados como prova de interoperabilidade completa com todos os serviços externos do Discord.

## Links oficiais

- [Documentação oficial](https://pimcorddocs-pvmazbtg.manus.space/)
- [PyPI — pimcord 0.6.9](https://pypi.org/project/pimcord/)
- [Repositório GitHub](https://github.com/buenoseva521-lgtm/pimcord)
- [Changelog](CHANGELOG.md)
- [Licença MIT](LICENSE)

## Licença

O Pimcord é distribuído sob a licença [MIT](LICENSE).
