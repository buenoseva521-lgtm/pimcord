from __future__ import annotations

import asyncio

from pimcord import CoordenaçãoSQLite


def test_coordenacao_sqlite_compartilha_lease_e_estado(tmp_path):
    caminho = tmp_path / "coordenação.sqlite3"
    primeiro = CoordenaçãoSQLite(caminho)
    segundo = CoordenaçãoSQLite(caminho)

    async def cenário():
        lease = await primeiro.adquirir("shard:1", "worker-a", duração=1)
        assert lease is not None
        assert await segundo.adquirir("shard:1", "worker-b", duração=1) is None
        renovado = await segundo.renovar(lease, duração=1)
        assert renovado is not None
        await primeiro.publicar("shard:1", {"conectado": True, "reinicios": 2})
        assert await segundo.estados() == {"shard:1": {"conectado": True, "reinicios": 2}}
        assert await segundo.liberar(renovado) is True
        assert await primeiro.adquirir("shard:1", "worker-b", duração=1) is not None

    asyncio.run(cenário())


def test_coordenacao_sqlite_expira_lease(tmp_path):
    coordenador = CoordenaçãoSQLite(tmp_path / "coordenação.sqlite3")

    async def cenário():
        assert await coordenador.adquirir("shard:2", "worker-a", duração=0.01) is not None
        await asyncio.sleep(0.03)
        assert await coordenador.adquirir("shard:2", "worker-b", duração=1) is not None

    asyncio.run(cenário())
