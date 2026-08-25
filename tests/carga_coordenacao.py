import asyncio

from pimcord import CoordenaçãoLocal, GerenciadorDeShards


async def principal() -> None:
    coordenador = CoordenaçãoLocal()
    donos: dict[int, set[str]] = {}

    def iniciar_para(nome: str):
        async def iniciar(shard):
            donos.setdefault(shard.id, set()).add(nome)
            await asyncio.sleep(0.01)
            return 0.01
        return iniciar

    primeiro = GerenciadorDeShards(8, iniciar_shard=iniciar_para("a"), coordenador=coordenador, trabalhador="a", duração_lease=1)
    segundo = GerenciadorDeShards(8, iniciar_shard=iniciar_para("b"), coordenador=coordenador, trabalhador="b", duração_lease=1)
    await asyncio.gather(primeiro.iniciar(), segundo.iniciar())
    assert await primeiro.aguardar_saude(2) or await segundo.aguardar_saude(2)
    await asyncio.gather(primeiro.parar(), segundo.parar())
    assert all(len(trabalhadores) <= 1 for trabalhadores in donos.values())
    print(f"shards_observados={len(donos)} exclusividade={all(len(x) <= 1 for x in donos.values())}")


if __name__ == "__main__":
    asyncio.run(principal())
