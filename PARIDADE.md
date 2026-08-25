# Matriz de paridade do Pimcord

O Pimcord será uma biblioteca própria, escrita em português brasileiro, com cobertura progressiva da API de bots Discord. A meta é alcançar uma superfície comparável à de bibliotecas maduras sem copiar implementação de terceiros. Cada recurso só deve aparecer como disponível na documentação depois de possuir código, teste e exemplo verificáveis.

## Princípios de compatibilidade

A API pública prioriza nomes em português, métodos assíncronos e objetos que representam entidades do Discord. O transporte continua isolado no cliente HTTP e no Gateway, permitindo que modelos de alto nível serializem dados sem espalhar detalhes de endpoint pelo código do usuário. Recursos novos devem possuir uma rota de prefixo e, quando aplicável, uma rota slash equivalente.

Views devem ser persistentes por padrão: `View()` usa `timeout=None`, gera componentes com `custom_id` e o `Bot` roteia interações pelo identificador registrado. Persistência entre processos exige que a aplicação recrie e registre a View na inicialização, porque callbacks Python não podem ser recuperados automaticamente apenas a partir do Discord.

## Estado atual por domínio

| Domínio | Estado | Próximo marco |
|---|---|---|
| Ciclo de vida do Bot | Implementado | Melhorar encerramento e reconexão |
| Gateway e heartbeat | Parcial funcional | Eventos completos e reconexão distribuída |
| Cliente REST e rate limits | Parcial funcional | Cabeçalhos de auditoria, paginação e helpers |
| Comandos de prefixo | Implementado | Conversão avançada e erros estruturados |
| Slash commands | Base funcional | Opções tipadas, grupos e autocomplete |
| Views, Buttons e Selects | Base com roteamento | Registro persistente, modais e checks por componente |
| Canais | Alto nível inicial | Categorias, fóruns, threads e edição tipada |
| Permission overwrites | Abstração inicial | Resolver permissões efetivas e cargos |
| Modelos Discord | Base | Completar entidades e conversores |
| Extensões e tarefas | Implementado | Ciclo de vida e observabilidade |
| Banco SQLite | Implementado | Migrações e transações assíncronas |
| Voz | Planejado | Gateway de voz, UDP e reprodução |
| Sharding | Base de cálculo | Supervisor distribuído |

## Contrato da primeira entrega

A primeira entrega desta expansão inclui `Servidor.criar_canal`, `Servidor.buscar_canais`, `SobrescritaPermissao.cargo`, `SobrescritaPermissao.usuario`, roteamento de Buttons e Selects pelo `custom_id` e `View.persistente`. Esses recursos estão acompanhados por testes automatizados. O restante continua marcado como parcial ou planejado até receber implementação equivalente.

## Ordem de expansão

A ordem de engenharia será: modelos e permissões; canais, categorias e threads; interações e Views; eventos e comandos; Gateway e REST; voz; sharding; documentação gerada a partir da API. Essa ordem reduz acoplamento e evita publicar exemplos que dependam de recursos ausentes.
