# Pimcord 0.7.0 — revisão de geração por IA

A revisão adiciona geração de projeto a partir de linguagem natural. Um pedido como “crie um bot de economia completo com saldo, diária, ranking e SQLite local” pode ser enviado a um cliente LLM compatível, que retorna arquivos estruturados em JSON. O Pimcord valida caminhos, sintaxe Python, imports sensíveis, chamadas dinâmicas e possíveis segredos antes de salvar o projeto.

A geração não executa automaticamente o resultado. O fluxo é gerar, validar, salvar, revisar e executar explicitamente. Quando a execução explícita é solicitada sem token, o Pimcord pede o token mascarado no terminal e o fornece apenas ao processo do bot; o segredo não entra no prompt, nos arquivos ou nos logs do gerador.

Também foi adicionado `EconomiaSQLite`, com saldo, recompensa diária, cooldown, transferência e ranking. O recurso usa SQLite parametrizado e não aceita SQL proveniente da descrição do usuário.

A validação local terminou com **219 testes aprovados**, compilação Python, referência AST atualizada e construção bem-sucedida do wheel `pimcord-0.7.0-py3-none-any.whl`. O smoke test do wheel funcionou em ambiente temporário com a dependência declarada `aiohttp` disponível.

Esta revisão não prova interoperabilidade DAVE/MLS com uma sessão real do Discord nem observação real prolongada de Voice Gateway/UDP. Portanto, não é uma autorização para alegar superioridade total sobre `discord.py`, publicar no PyPI ou entregar um ZIP de distribuição final enquanto esses bloqueadores históricos permanecerem abertos.
