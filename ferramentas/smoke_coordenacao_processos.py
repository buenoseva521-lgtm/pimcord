from __future__ import annotations

import asyncio
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from pimcord import CoordenaçãoSQLite


async def trabalhador_a(caminho: str, pronto: str) -> None:
    coordenador = CoordenaçãoSQLite(caminho)
    lease = await coordenador.adquirir("shard:7", "worker-a", duração=2.0)
    if lease is None:
        raise SystemExit(2)
    Path(pronto).write_text("ocupado", encoding="utf-8")
    os._exit(17)


async def trabalhador_b(caminho: str, pronto: str) -> None:
    while not Path(pronto).exists():
        await asyncio.sleep(0.01)
    coordenador = CoordenaçãoSQLite(caminho)
    bloqueado = await coordenador.adquirir("shard:7", "worker-b", duração=1)
    if bloqueado is not None:
        raise SystemExit(3)
    await asyncio.sleep(2.1)
    retomado = await coordenador.adquirir("shard:7", "worker-b", duração=1)
    if retomado is None:
        raise SystemExit(4)
    print("crash_externo=recuperado epoca=%d" % retomado.época)


def principal() -> None:
    if len(sys.argv) > 1 and sys.argv[1] == "a":
        asyncio.run(trabalhador_a(sys.argv[2], sys.argv[3]))
        return
    if len(sys.argv) > 1 and sys.argv[1] == "b":
        asyncio.run(trabalhador_b(sys.argv[2], sys.argv[3]))
        return
    with tempfile.TemporaryDirectory() as pasta:
        caminho = str(Path(pasta) / "coord.sqlite3")
        pronto = str(Path(pasta) / "pronto")
        processo_a = subprocess.run([sys.executable, __file__, "a", caminho, pronto], check=False)
        if processo_a.returncode != 17:
            raise SystemExit(f"worker-a não simulou crash: {processo_a.returncode}")
        subprocess.run([sys.executable, __file__, "b", caminho, pronto], check=True)


if __name__ == "__main__":
    principal()
