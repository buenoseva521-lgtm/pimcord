# Auditoria objetiva do Pimcord 0.7.0

## Resultado executivo

A distribuição importa como `0.7.0`, o `pyproject.toml` declara `0.7.0` e existem 21 testes coletados. Os recursos de comandos híbridos, opções slash tipadas, follow-ups, respostas efêmeras, Views persistentes importáveis, canais, overwrites, histórico, purge, extensões, tarefas básicas, cache/métricas e cálculo de sharding possuem código e cobertura local parcial.

A versão não deve ser descrita como paridade total com discord.py. A auditoria encontrou lacunas concretas: o User-Agent REST ainda dizia `Pimcord/0.6.2`; uploads de arquivos continuam com `NotImplementedError`; o módulo de voz/áudio completo não existe; sharding é um gerenciador local básico, não um supervisor distribuído; cache e tarefas são mínimos; e vários modelos, eventos, grupos slash, subcomandos, autocomplete, threads, fóruns, cargos avançados, auditoria e APIs completas de voz continuam parciais ou ausentes.

## Cobertura observada

| Área | Estado observado | Evidência |
|---|---|---|
| Importação e empacotamento | Implementado | `__version__ = "0.7.0"`, `pyproject.toml`, wheel e sdist |
| Gateway | Base funcional | WebSocket, heartbeat, ACK e eventos básicos |
| REST | Base funcional | cliente assíncrono, retries e rate limit por rota |
| Comandos prefixados | Implementado em parte | aliases, conversão, checks e cooldowns |
| Comandos híbridos | Implementado em parte | callback compartilhado entre prefixo e slash |
| Slash tipado | Implementado em parte | `OpcaoSlash`, schema e valores nomeados |
| Follow-up/ephemeral | Implementado em parte | resposta, follow-up, edição e exclusão de resposta |
| Views persistentes | Implementado em parte | registro/reidratação de classes importáveis |
| Canais e permissões | Implementado em parte | criação, categoria e overwrites |
| Moderação | Implementado em parte | delete, histórico e purge |
| Voz/áudio | Ausente ou placeholder | não há transporte UDP/player completo |
| Sharding | Base | cálculo e tarefas locais, sem supervisão distribuída |
| Uploads | Ausente | `NotImplementedError` em `discord/modelos.py` |
| Modelos/eventos Discord | Parcial | superfície ainda menor que a API completa |
| Documentação no repositório | Presente | guias Markdown locais; o site React fica fora deste ZIP |

## Correção aplicada nesta auditoria

O User-Agent REST foi alinhado de `Pimcord/0.6.2` para `Pimcord/0.7.0`. A suíte local passou com 21 testes, todos os arquivos Python foram compilados, a importação confirmou `0.7.0` e wheel/sdist foram reconstruídos. O ZIP final conterá somente o repositório da biblioteca, sem `pimcord-docs`, caches ou dependências instaladas.

## Critério de entrega

O pacote será entregue como uma versão auditada e testada do marco 0.7.0, não como uma alegação de que todas as APIs do Discord já estão completas. As lacunas ficam registradas para impedir que a documentação prometa funcionalidades inexistentes.
