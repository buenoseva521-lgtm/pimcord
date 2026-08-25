"""Carga offline repetível para falhas de processo, leases e Voice Gateway."""
from __future__ import annotations

import asyncio

from pimcord import Bot, ClienteGatewayVoz, CoordenaçãoLocal, GerenciadorDeShards, SessaoVoz


class WSFechando:
    def __aiter__(self):
        return self

    async def __anext__(self):
        raise StopAsyncIteration

    async def close(self):
        return None


async def rodada(numero: int) -> tuple[int, int]:
    coordenador = CoordenaçãoLocal()
    chamadas = 0

    async def iniciar(shard):
        nonlocal chamadas
        chamadas += 1
        if chamadas == 1:
            raise RuntimeError(f"queda de processo na rodada {numero}")
        await asyncio.sleep(0)
        return 0.01

    gerente = GerenciadorDeShards(2, iniciar, coordenador=coordenador, trabalhador=f"worker-{numero}", duração_lease=0.03, atraso_inicial=0.0001, atraso_maximo=0.0002)
    await gerente.iniciar()
    saudavel = await gerente.aguardar_saude(0.5)
    if not saudavel:
        raise AssertionError(f"shards não recuperaram na rodada {numero}: {gerente.estado()}")
    estados = await coordenador.estados()
    assert all(item["conectado"] for item in estados.values())
    await gerente.parar()

    sessao = SessaoVoz(Bot(), "10", "20")
    cliente = ClienteGatewayVoz(sessao)
    tentativas = 0

    async def conectar():
        nonlocal tentativas
        tentativas += 1
        if tentativas == 1:
            raise ConnectionError("queda de processo de voz")
        cliente.ws = WSFechando()
        sessao._parar.set()

    cliente.conectar = conectar
    original_sleep = asyncio.sleep

    async def sleep_curto(_duracao):
        await original_sleep(0)

    import pimcord.voz as modulo_voz
    antigo = modulo_voz.asyncio.sleep
    modulo_voz.asyncio.sleep = sleep_curto
    try:
        await cliente.executar(maximo_tentativas=3)
    finally:
        modulo_voz.asyncio.sleep = antigo
    assert tentativas == 2
    return chamadas, tentativas


async def principal() -> None:
    resultados = [await rodada(numero) for numero in range(1, 21)]
    assert all(chamadas == 3 and tentativas == 2 for chamadas, tentativas in resultados)
    print(f"rodadas={len(resultados)} shards_recuperados={sum(item[0] for item in resultados)} reconexoes_voz={sum(item[1] for item in resultados)}")


if __name__ == "__main__":
    asyncio.run(principal())
