import asyncio

import pytest

from pimcord.sharding import GerenciadorDeShards


@pytest.mark.asyncio
async def test_supervisor_reinicia_shard_apos_falha():
    chamadas = 0

    async def iniciar(shard):
        nonlocal chamadas
        chamadas += 1
        if chamadas == 1:
            raise RuntimeError("queda simulada")
        return 0.125

    gerenciador = GerenciadorDeShards(1, iniciar, atraso_inicial=0.001, atraso_maximo=0.002)
    await gerenciador.iniciar()
    assert await gerenciador.aguardar_saude(0.2)
    assert chamadas == 2
    assert gerenciador.shards[0].reinicios == 1
    assert gerenciador.shards[0].latencia == 0.125
    await gerenciador.parar()


@pytest.mark.asyncio
async def test_supervisor_respeita_limite_de_reinicios():
    async def iniciar(shard):
        raise RuntimeError("falha permanente")

    gerenciador = GerenciadorDeShards(1, iniciar, max_reinicios=1, atraso_inicial=0.001, atraso_maximo=0.002)
    await gerenciador.iniciar()
    await asyncio.sleep(0.02)
    assert gerenciador.shards[0].estado == "falhou"
    assert gerenciador.shards[0].reinicios == 2
    await gerenciador.parar()


@pytest.mark.asyncio
async def test_supervisor_recupera_multiplos_shards_com_falhas_transitorias():
    tentativas = {}

    async def iniciar(shard):
        tentativas[shard.id] = tentativas.get(shard.id, 0) + 1
        if tentativas[shard.id] <= 2:
            raise RuntimeError(f"falha transitória {shard.id}")
        return shard.id / 100

    gerenciador = GerenciadorDeShards(12, iniciar, atraso_inicial=0.001, atraso_maximo=0.004)
    await gerenciador.iniciar()
    assert await gerenciador.aguardar_saude(1.0)
    assert all(tentativas[shard_id] == 3 for shard_id in range(12))
    assert all(info.reinicios == 2 for info in gerenciador.shards.values())
    await gerenciador.parar()


@pytest.mark.asyncio
async def test_supervisor_mapeia_servidor_e_expoe_estado():
    async def iniciar(shard):
        return 0.05

    gerenciador = GerenciadorDeShards(2, iniciar)
    assert gerenciador.shard_de_servidor(str((3 << 22) + 42)).id == 1
    await gerenciador.iniciar()
    assert await gerenciador.aguardar_saude(0.2)
    assert gerenciador.saudavel is True
    assert gerenciador.estado()[0]["conectado"] is True
    await gerenciador.parar()


@pytest.mark.asyncio
async def test_supervisor_persiste_e_restaura_checkpoint(tmp_path):
    checkpoint = tmp_path / "shards.json"

    async def iniciar(shard):
        return 0.05

    primeiro = GerenciadorDeShards(2, iniciar, caminho_checkpoint=checkpoint)
    await primeiro.iniciar()
    assert await primeiro.aguardar_saude(0.2)
    await primeiro.parar()
    assert checkpoint.exists()

    segundo = GerenciadorDeShards(2, iniciar, caminho_checkpoint=checkpoint)
    assert all(info.estado == "retomando" for info in segundo.shards.values())
    assert all(info.conectado is False for info in segundo.shards.values())
    await segundo.iniciar()
    assert await segundo.aguardar_saude(0.2)
    await segundo.parar()
