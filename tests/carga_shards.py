import asyncio

from pimcord import CoordenaçãoLocal, GerenciadorDeShards


async def principal() -> None:
    coordenador = CoordenaçãoLocal()
    chamadas: list[int] = []

    async def iniciar(shard):
        chamadas.append(shard.id)
        await asyncio.sleep(0)
        return 0.012

    gerente = GerenciadorDeShards(
        total=100,
        iniciar_shard=iniciar,
        coordenador=coordenador,
        trabalhador="carga-1",
        duração_lease=1.0,
    )
    await gerente.iniciar()
    assert await gerente.aguardar_saude(tempo_limite=3.0)
    estados = await coordenador.estados()
    assert len(chamadas) == 100
    assert len(estados) == 100
    assert all(item["conectado"] for item in estados.values())
    await gerente.parar()
    assert all(item["estado"] == "encerrado" for item in (await coordenador.estados()).values())
    print(f"shards={len(chamadas)} estados={len(estados)} saudavel={gerente.saudavel}")


if __name__ == "__main__":
    asyncio.run(principal())
