from __future__ import annotations

import asyncio
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from pimcord import CoordenaçãoSQLite


async def trabalhador_a(caminho: str, rodada: int) -> None:
    coordenador = CoordenaçãoSQLite(caminho)
    lease = await coordenador.adquirir("shard:prolongado", f"worker-a-{rodada}", duração=0.5)
    if lease is None:
        raise SystemExit(10)
    Path(f"{caminho}.{rodada}.pronto").write_text(str(lease.época), encoding="utf-8")
    os._exit(17)


async def trabalhador_b(caminho: str, rodada: int) -> None:
    pronto = Path(f"{caminho}.{rodada}.pronto")
    while not pronto.exists():
        await asyncio.sleep(0.002)
    coordenador = CoordenaçãoSQLite(caminho)
    bloqueado = await coordenador.adquirir("shard:prolongado", f"worker-b-{rodada}", duração=0.5)
    if bloqueado is not None:
        raise SystemExit(11)
    await asyncio.sleep(0.6)
    retomado = await coordenador.adquirir("shard:prolongado", f"worker-b-{rodada}", duração=0.5)
    if retomado is None or retomado.época <= rodada:
        raise SystemExit(12)
    print(f"rodada={rodada} epoca={retomado.época}")


def principal() -> None:
    with tempfile.TemporaryDirectory() as pasta:
        caminho = str(Path(pasta) / "coord.sqlite3")
        for rodada in range(1, 21):
            processo_a = subprocess.run([sys.executable, __file__, "a", caminho, str(rodada)], check=False)
            if processo_a.returncode != 17:
                raise SystemExit(f"worker-a falhou na rodada {rodada}: {processo_a.returncode}")
            subprocess.run([sys.executable, __file__, "b", caminho, str(rodada)], check=True)
            time.sleep(0.55)
        print("crash_prolongado=20_rodadas_recuperadas")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "a":
        asyncio.run(trabalhador_a(sys.argv[2], int(sys.argv[3])))
    elif len(sys.argv) > 1 and sys.argv[1] == "b":
        asyncio.run(trabalhador_b(sys.argv[2], int(sys.argv[3])))
    else:
        principal()
