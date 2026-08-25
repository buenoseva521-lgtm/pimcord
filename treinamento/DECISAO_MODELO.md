# Decisão de modelo-base da PimcordIA

## Decisão

A arquitetura recomendada é **modelo aberto pré-treinado + especialização Pimcord + catálogo runtime + agente seguro**, em vez de treinar um modelo do zero. Isso entrega mais capacidade de Python com um custo e um corpus viáveis, mantendo o uso local sem chave de provedor.

## Comparação auditada

| Modelo | Licença indicada na ficha | Pontos fortes | Riscos/limites |
|---|---|---|---|
| Qwen2.5-Coder-7B-Instruct | Apache-2.0 | É instrucional, tem geração, raciocínio e correção de código; ficha informa 7,61B parâmetros e contexto até 131.072 tokens | O peso completo é grande para Pydroid/Termux; precisa de quantização e licença dos dados especializados |
| StarCoder2-7B | BigCode OpenRAIL-M v1 | Treinado em código com transparência e possui versões quantizadas | A ficha informa que não é modelo instrucional; exige prompt/adapter adicional e tem obrigações de atribuição e busca de origem |
| DeepSeek-Coder-6.7B-Instruct | Licença própria DeepSeek | Instrucional, voltado a código e com versões de 1B a 33B | A licença do modelo é separada do repositório MIT e precisa ser revisada antes da redistribuição; a ficha recomenda `trust_remote_code` |

## Escolha inicial

O candidato inicial é **Qwen2.5-Coder-7B-Instruct**, por combinar uma licença permissiva indicada na ficha, ajuste instrucional e recursos de geração/correção. A distribuição final não deve embutir o peso de 7B diretamente no pacote Python. A Pimcord deve oferecer um comando de preparação de modelo, suporte a diretório local e quantização compatível com o dispositivo.

Para celulares muito limitados, o plano deve permitir uma variante menor da mesma família, desde que passe no benchmark Pimcord. A variante não pode ser chamada de especialista apenas por carregar o mesmo nome.

## Fontes

[1]: https://huggingface.co/Qwen/Qwen2.5-Coder-7B-Instruct "Qwen2.5-Coder-7B-Instruct — ficha oficial"
[2]: https://huggingface.co/bigcode/starcoder2-7b "StarCoder2-7B — ficha oficial"
[3]: https://huggingface.co/deepseek-ai/deepseek-coder-6.7b-instruct "DeepSeek-Coder-6.7B-Instruct — ficha oficial"
[4]: https://www.bigcode-project.org/docs/about/models/ "BigCode — modelos e governança"
