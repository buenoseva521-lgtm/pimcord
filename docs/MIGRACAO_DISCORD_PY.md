# Migração de discord.py para Pimcord

Pimcord não é uma substituição drop-in de discord.py. O objetivo desta página é orientar a leitura e apontar conceitos comparáveis; cada assinatura deve ser conferida no código e na [referência da API](https://pimcorddocs-pvmazbtg.manus.space/api).

| Conceito | discord.py | Pimcord | Observação |
| --- | --- | --- | --- |
| Fachada principal | `Bot` | `Bot` | O ciclo de vida e os argumentos devem ser conferidos individualmente. |
| Comando prefixado | `@bot.command` | `@bot.comando` | Decorator em português para o contrato do Pimcord. |
| Evento | `@bot.event` | `@bot.evento` | O dispatcher usa nomes de evento do Pimcord. |
| Contexto | `Context` | `Contexto` | Consulte o conteúdo e a assinatura antes de portar handlers. |
| Interação | `Interaction` | `Interacao` | Respostas, adiamento e follow-ups possuem contrato próprio. |
| Intents | `Intents` | `Intents` | O nome é compartilhado; defaults e máscara devem ser validados. |
| Transporte | cliente interno | `Gateway` + `ClienteHTTP` | Pimcord separa transporte e modelos de domínio explicitamente. |

## Ordem segura de migração

Primeiro reescreva a inicialização com `pimcord.Bot` e `pimcord.Configuracao`. Depois porte um comando simples com `@bot.comando` e `ctx.responder`. Em seguida, migre eventos e interações um por vez, conferindo as assinaturas na referência. Por fim, revise permissões, tratamento de erros, intents e dependências opcionais.

Não copie imports internos de discord.py para Pimcord, não assuma equivalências por nomes parecidos e não considere um teste offline como prova de interoperabilidade completa com o Discord.
