# IA e `bot_pronto`

O Pimcord oferece um gerador assistido por IA para transformar uma descrição em linguagem natural em um **plano estruturado de bot**. O gerador não escreve nem executa Python, SQL ou comandos do sistema. Ele produz apenas prefixo, intents e comandos com respostas literais; o Pimcord valida o plano antes de registrar os comandos híbridos.

## Uso direto com prompt livre

A forma principal agora é uma chamada direta em linguagem natural. O usuário não importa OpenAI, não cria um cliente e não precisa escrever uma DSL:

```python
import pimcord

bot = pimcord.bot_pronto("crie um bot de economia completo", iniciar=False)
print(bot.obter_comando("saldo"))
```

O `bot_pronto` usa `IAIntegradaPimcord`. Sem configuração adicional, ele funciona offline com um fallback seguro para intenções comuns. Em um ambiente com um endpoint Chat Completions, configure `PIMCORD_IA_URL`, `PIMCORD_IA_CHAVE` e, opcionalmente, `PIMCORD_IA_MODELO`. O padrão do gerador remoto é `gpt-5`, mas você pode escolher um modelo de código mais forte disponível no seu provider, como `claude-sonnet-4-6` ou outro catálogo compatível. O pacote faz a chamada HTTP internamente e não exige SDK de terceiros.

## Geração de projeto com arquivos e cogs

Quando o objetivo é criar um projeto completo, passe `diretorio`. O Pimcord salva `bot.py`, extensões em `cogs/`, comandos híbridos de prefixo e slash, configuração, README e o módulo SQLite de economia quando o pedido mencionar economia:

```python
import pimcord

bot = pimcord.bot_pronto(
    "crie um bot de economia completo",
    iniciar=False,
    diretorio="./meu_bot",
)
bot.rodar("SEU_TOKEN_REAL")
```

Esse caminho gera arquivos, mas não executa código arbitrário produzido pelo texto. O validador bloqueia traversal, imports perigosos, chamadas dinâmicas e segredos literais. O fallback local é rápido porque usa templates e regras seguras; para a IA de programação realmente generativa, configure o endpoint HTTP e a chave do seu provider. O Pimcord envia o prompt e o contexto da API, mas nunca envia o token do Discord.

## Compatibilidade com o interpretador local

O caminho declarativo continua disponível para projetos que precisam de uma configuração determinística:

```python
import pimcord

bot = pimcord.bot_pronto("""
Prefixo: !
Intents: basicos
Comando: ola
Resposta: Olá, mundo!
Aliases: oi
""", iniciar=False)
```

`iniciar=False` é útil para testes. Para uma execução real, omita esse argumento; o Pimcord solicitará o token com entrada mascarada no terminal. O token não é colocado na descrição, não é enviado ao gerador e não é persistido pelo `bot_pronto`.

## Uso com um cliente LLM avançado

`GeradorPlanoIA` continua disponível para quem já possui um cliente OpenAI-compatible e quer controlar o provedor. Ele é um caminho avançado e opcional; não é necessário para usar `bot_pronto`. O token do Discord nunca deve ser incluído na chamada.

```python
import os
from openai import OpenAI
import pimcord

cliente = OpenAI()
gerador = pimcord.GeradorPlanoIA(cliente, modelo="gpt-5-mini")

bot = pimcord.bot_pronto(
    "Crie um bot de saudação com os comandos ola e ajuda.",
    gerador=gerador,
    iniciar=False,
)

# Depois de revisar o plano localmente:
bot.iniciar(os.environ["DISCORD_TOKEN"])
```

A resposta esperada do modelo é validada com JSON Schema estrito. O contrato contém apenas:

| Campo | Regra |
| --- | --- |
| `prefixo` | De um a três caracteres, sem espaços. |
| `intents` | `basicos` ou `todos`. |
| `comandos` | No máximo 50 comandos. |
| `nome` | Uma palavra com até 32 caracteres. |
| `resposta` | Texto literal com até 2.000 caracteres. |
| `aliases` | Até dez aliases por comando. |

Campos extras, Python, SQL, shell, URLs, credenciais, pagamentos e ações livres são rejeitados. Uma descrição ambígua deve produzir um erro ou um plano mínimo, não executar uma interpretação perigosa.

## Arquitetura

> Descrição → modelo LLM ou regras locais → JSON Schema → validador Pimcord → comandos híbridos → execução do `Bot`.

`IAIntegradaPimcord` e `GeradorPlanoIA` estão em `pimcord/ia.py`. O parser local, a entrada mascarada de token e a integração com o `Bot` estão em `pimcord/pronto.py`. A IA nativa não depende de SDK externo; sem URL e chave configuradas, o fallback local continua funcionando sem rede.

## Segurança

Nunca coloque o token no prompt, no código publicado, no ZIP, no log ou em uma descrição. Use uma variável de ambiente ou solicite o token localmente com `getpass`. O modelo pode produzir texto incorreto; por isso, sua saída nunca é uma autorização para executar uma ferramenta arbitrária. Recursos complexos, como economia com SQLite, moderação ou pagamentos, precisam de módulos Pimcord previamente implementados e de um plano específico, não de código gerado livremente.

## Testes

A suíte offline cobre JSON estrito, rejeição de campos perigosos, integração com comandos prefixados e slash e fallback local:

```bash
python -m pytest tests/test_ia_pronto.py
```

Essa funcionalidade agora possui duas camadas: o modo rápido configura um Bot em memória, enquanto o modo com `diretorio` gera uma árvore de projeto com extensões/cogs, comandos híbridos, eventos, configuração e módulos persistentes disponíveis. Voz, DAVE/MLS e moderação avançada continuam sujeitos a validação e testes específicos.


## Geração livre de projeto

Para pedidos como “crie um bot de economia completo”, use `GeradorProjetoIA`. Diferentemente de `GeradorPlanoIA`, ele retorna um conjunto de arquivos de projeto, e não apenas comandos declarativos:

```python
from openai import OpenAI
import pimcord

cliente = OpenAI()
projeto = pimcord.criar_projeto_ia(
    "Crie um bot de economia completo com saldo, diária, ranking e SQLite local.",
    cliente,
    "./economia_bot",
)

print(projeto.nome)
print(projeto.caminhos())
```

A geração e o salvamento não iniciam o bot. O código deve ser revisado pelo usuário. Somente depois da revisão é possível solicitar a execução explicitamente:

```python
projeto.executar("./economia_bot", token=os.environ["DISCORD_TOKEN"])
```

A validação bloqueia traversal de diretórios, Python inválido, `eval`, `exec`, imports perigosos e segredos literais. A variável de ambiente do token é passada apenas ao processo executado; nunca é adicionada ao prompt ou aos arquivos gerados.

Essa arquitetura permite que a IA escreva um bot de domínio completo quando o modelo produzir os arquivos necessários, mas mantém o Pimcord no controle do ciclo de vida: **gerar, validar, revisar, salvar e somente então executar**. O Pimcord não afirma que um texto livre sempre resultará em um projeto correto; a saída do modelo continua sujeita a revisão e aos testes do projeto.


## Recurso de economia incluído

O pacote agora inclui `EconomiaSQLite`, uma camada de domínio local que pode ser usada por um projeto gerado:

```python
import pimcord

economia = pimcord.EconomiaSQLite("economia.sqlite3", saldo_inicial=0, diaria=100)

saldo = economia.saldo(str(ctx.autor.id))
novo_saldo = economia.diaria(str(ctx.autor.id))
remetente, destinatario = economia.transferir(str(ctx.autor.id), str(outro.id), 25)
ranking = economia.ranking(10)
```

O módulo usa consultas parametrizadas, cooldown da recompensa diária e validação de valores. Ele é uma capacidade do Pimcord, não código arbitrário produzido pela IA. Um projeto gerado pode registrá-lo nos comandos `saldo`, `diaria`, `pagar` e `ranking`, mas ainda deve ser revisado e testado pelo autor antes da execução real.
