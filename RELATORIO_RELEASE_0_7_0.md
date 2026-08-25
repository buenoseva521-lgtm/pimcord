# Relatório da release Pimcord 0.7.0

## Escopo comprovado offline

A suíte local foi executada com **246 testes aprovados**. Também foram compilados os módulos Python de `pimcord/` e `treinamento/`, e a distribuição foi construída com wheel e sdist.

| Área | Status | Evidência local |
|---|---|---|
| API pública em português | Aprovada offline | Importação, modelos, comandos, eventos e contratos testados |
| REST Discord v10 | Aprovada offline | Auditorias e testes de rotas sem rede real |
| Gateway | Aprovado por contrato offline | READY único, application_id automático, sincronização slash, MESSAGE_CREATE, heartbeat, timeout, backoff e códigos fatais testados |
| `bot_pronto` | Aprovado offline | Prompt local, DSL, token normalizado e geração de plano |
| Persistência do token | Aprovada localmente | `.env` com permissão restrita e `.gitignore` atualizado; token normalizado antes de HTTP e Gateway |
| IA local | Especializada e determinística | Domínios Pimcord, cogs específicos, comandos híbridos compatíveis com slash, eventos oficiais e SQLite |
| Segurança | Aprovada nos testes locais | AST, caminhos, imports e chamadas perigosas bloqueados |
| Voz/UDP | Experimental | Componentes e contratos offline; sessão Discord real não comprovada |
| DAVE/MLS | Experimental | Parsers/envelopes e fail-closed; interoperabilidade oficial não comprovada |
| IA neural | Experimental | Pipeline de treinamento criado; modelo treinado não incluído |

## Limitações honestas

Os testes offline não comprovam uma sessão autorizada real no Discord, nem a interoperabilidade completa de Voice Gateway, UDP, DAVE/MLS ou um modelo neural geral. Esses domínios permanecem identificados como experimentais para não confundir contratos locais com prova de produção.

## Instalação

```bash
python -m pip install pimcord-0.7.0-py3-none-any.whl
```

Para uso móvel, a instalação deve ser feita no Pydroid ou Termux com Python 3.11+ e `aiohttp` disponível. O projeto gerado por `bot_pronto` salva o token somente no `.env` do diretório escolhido e adiciona `.env` ao `.gitignore`.

## Exemplo mínimo

```python
import pimcord

bot = pimcord.bot_pronto(
    "crie um bot de moderação com ping e comandos híbridos",
    iniciar=False,
)
bot.rodar("SEU_TOKEN_REAL")
```

Nunca publique um token, não o envie para o modelo de IA e regenere-o imediatamente se ele for exposto.


## Revisão ampla de qualidade — 19/08/2026

Nesta rodada, o bootstrap dos projetos gerados passou a carregar automaticamente o `.env` local, enquanto `Bot.rodar()` também procura `DISCORD_TOKEN` no `.env` do diretório atual sem sobrescrever variáveis de ambiente já definidas. O template deixou de imprimir uma segunda mensagem redundante de conexão; o status de conexão permanece no logger da biblioteca. O `Contexto` recebeu `autor_id` e `canal_atual`, tornando comandos híbridos mais consistentes entre prefixo e slash.

Foi gerado e compilado um projeto completo com economia, tickets, moderação, boas-vindas e diversão. A suíte permaneceu com **246 testes aprovados** e a compilação de `pimcord/`, `treinamento/` e do projeto gerado foi concluída sem erro.

Essas melhorias aumentam a robustez local, mas não transformam os componentes de voz, DAVE/MLS ou IA neural em recursos comprovados de produção. A validação real ainda depende de uma conta Discord autorizada, permissões corretas no Developer Portal e condições de rede externas.


## Renumeração para 0.6.5

A distribuição corrente foi renumerada para **0.6.5** conforme solicitado. O conteúdo técnico e os limites experimentais permanecem os mesmos; somente os metadados e as referências da release corrente foram atualizados.


## Correção da PimcordIA e comandos híbridos — 2026-08-19

A API de comandos híbridos foi fortalecida. Quando `opcoes` não é fornecido, os parâmetros tipados da assinatura do callback agora são convertidos automaticamente em opções slash com nome, tipo, descrição e obrigatoriedade. A interação slash monta os argumentos pelo nome da opção, e não pela ordem incidental do dicionário recebido.

Comandos slash e híbridos também aceitam `permissoes`, serializadas como `default_member_permissions` na sincronização. O template de moderação da PimcordIA agora gera `limpar` com descrição, permissão de gerenciar mensagens, limite de 1 a 100 e chamada real a `canal.purge`, respondendo com a quantidade apagada. A suíte desta revisão passou com **252 testes**, além de compilação da biblioteca e do pipeline de treinamento.
