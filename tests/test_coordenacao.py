import asyncio

import pytest

from pimcord import CoordenaçãoLocal


@pytest.mark.asyncio
async def test_lease_exclusivo_e_renovavel():
    coordenador = CoordenaçãoLocal()
    primeiro = await coordenador.adquirir("shard:0", "worker-a", duração=0.1)
    assert primeiro is not None
    assert await coordenador.adquirir("shard:0", "worker-b", duração=0.1) is None

    renovado = await coordenador.renovar(primeiro, duração=0.2)
    assert renovado is not None
    assert renovado.época == primeiro.época
    assert renovado.trabalhador == "worker-a"


@pytest.mark.asyncio
async def test_lease_expira_e_pode_ser_reivindicado():
    coordenador = CoordenaçãoLocal()
    primeiro = await coordenador.adquirir("shard:1", "worker-a", duração=0.01)
    assert primeiro is not None
    await asyncio.sleep(0.02)
    assert await coordenador.renovar(primeiro, duração=0.1) is None
    segundo = await coordenador.adquirir("shard:1", "worker-b", duração=0.1)
    assert segundo is not None
    assert segundo.época > primeiro.época


@pytest.mark.asyncio
async def test_duracao_invalida_e_trabalhador_antigo_sao_rejeitados():
    coordenador = CoordenaçãoLocal()
    with pytest.raises(ValueError):
        await coordenador.adquirir("shard:falha", "worker-a", duração=0)
    lease = await coordenador.adquirir("shard:3", "worker-a", duração=0.1)
    assert lease is not None
    assert await coordenador.renovar(type(lease)(lease.chave, "worker-b", lease.época, lease.expira_em), duração=0.1) is None


@pytest.mark.asyncio
async def test_liberacao_e_publicacao_de_estado_sao_idempotentes_no_estado_atual():
    coordenador = CoordenaçãoLocal()
    lease = await coordenador.adquirir("shard:2", "worker-a")
    assert lease is not None
    assert await coordenador.liberar(lease) is True
    assert await coordenador.liberar(lease) is False

    await coordenador.publicar("shard:2", {"estado": "encerrado", "reinicios": 1})
    assert await coordenador.estados() == {"shard:2": {"estado": "encerrado", "reinicios": 1}}


@pytest.mark.asyncio
async def test_ciclos_prolongados_de_expiracao_e_recuperacao():
    coordenador = CoordenaçãoLocal()
    epocas = []
    for ciclo in range(40):
        chave = f"shard:prolongado:{ciclo}"
        primeiro = await coordenador.adquirir(chave, "worker-a", duração=0.001)
        assert primeiro is not None
        assert await coordenador.adquirir(chave, "worker-b", duração=0.001) is None
        await asyncio.sleep(0.002)
        assert await coordenador.renovar(primeiro, duração=0.001) is None
        segundo = await coordenador.adquirir(chave, "worker-b", duração=0.01)
        assert segundo is not None
        assert segundo.época > primeiro.época
        epocas.append(segundo.época)
        assert await coordenador.liberar(segundo) is True
    assert len(epocas) == 40
    assert all(epoca >= 2 for epoca in epocas)
