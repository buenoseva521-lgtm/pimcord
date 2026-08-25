import asyncio
from types import SimpleNamespace

from pimcord.pronto import DefinicaoBot, DefinicaoComando, _construir_definicao


class CanalFalso:
    def __init__(self):
        self.limites = []

    async def purge(self, *, limite):
        self.limites.append(limite)
        return [object() for _ in range(limite)]


class ContextoFalso:
    def __init__(self, canal):
        self.canal_atual = canal
        self.respostas = []

    async def responder(self, texto):
        self.respostas.append(texto)


async def principal():
    bot = _construir_definicao(
        DefinicaoBot(
            prefixo="!",
            intents="todos",
            comandos=[DefinicaoComando("limpar", "resposta antiga", ())],
        )
    )
    comando = bot.comandos["limpar"]
    canal = CanalFalso()
    contexto = ContextoFalso(canal)
    await comando.callback(contexto, 8)
    assert canal.limites == [8], canal.limites
    assert contexto.respostas == ["Apaguei 8 mensagem(ns)."], contexto.respostas
    assert "resposta antiga" not in contexto.respostas
    assert bot.comandos_slash["limpar"].descricao == "Apaga de 1 a 100 mensagens deste canal"
    print("callback limpar funcional: OK")


if __name__ == "__main__":
    asyncio.run(principal())
