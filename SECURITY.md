# Segurança

Não publique tokens de bot, credenciais, cookies ou arquivos `.env` em issues, pull requests ou logs. Se um token aparecer em um repositório, revogue-o imediatamente no Discord Developer Portal e gere outro.

Para relatar uma vulnerabilidade que possa expor credenciais, permitir acesso indevido ou comprometer o cliente REST/Gateway, não publique detalhes exploráveis em uma issue pública. Abra um contato privado com os mantenedores do projeto e inclua uma descrição mínima, a versão afetada, o comportamento esperado e uma forma segura de reproduzir o problema.

O Pimcord não registra tokens deliberadamente. Aplicações que usam a biblioteca devem evitar imprimir headers, URLs com tokens de interação e payloads completos em logs de produção.
