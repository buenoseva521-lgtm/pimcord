# Contribuindo com o Pimcord 0.6.9

O Pimcord é uma biblioteca assíncrona para bots Discord com API pública em português brasileiro. Contribuições devem preservar a clareza da sintaxe, a compatibilidade com Python 3.11 ou superior e a separação entre transporte, modelos, roteamento e regras da aplicação.

## Antes de abrir uma alteração

Leia `ARQUITETURA_0.7.0.md`, `MATRIZ_0.7.0.md` e o README. Esses dois arquivos preservam registros históricos da linha 0.7.0; a matriz distingue recursos implementados, parciais e planejados, e uma proposta não deve apresentar uma área planejada como pronta para a versão atual 0.6.9.

## Desenvolvimento local

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[testes]"
python -m pytest -q
python -m build
```

O núcleo dos testes deve funcionar sem token, sem Gateway real e sem requisições externas. Use clientes falsos, payloads determinísticos e testes de contrato para endpoints. Testes que exigirem um servidor Discord devem ser explicitamente separados e nunca devem rodar por padrão.

## Regras de API

Novos recursos públicos precisam de nomes em português, docstring, teste e exemplo. Quando um alias em inglês for útil para compatibilidade, ele deve apontar para uma única implementação e ser documentado. Não altere silenciosamente a assinatura de um método existente; prefira uma extensão compatível ou registre a mudança no changelog.

Toda operação de rede deve ser assíncrona. O cliente REST é responsável por autenticação, rate limit e transporte; modelos não devem criar sessões HTTP próprias. Dados brutos importantes devem permanecer acessíveis para diagnóstico.

## Pull requests

Descreva o problema, a solução, os contratos novos, os limites conhecidos e os testes executados. Alterações de documentação devem apontar para APIs existentes no código. Antes de enviar, execute `python -m pytest -q`, `python -m build` e, quando modificar o site, `pnpm check && pnpm run build` dentro de `pimcord-docs`.

## Commits

Prefira mensagens curtas e objetivas, como `feat: adicionar follow-up de interação`, `fix: corrigir conversão de opção slash` e `docs: explicar comandos híbridos`.
