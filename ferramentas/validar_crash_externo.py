"""Valida retomada externa após morte abrupta de um processo filho.

O cenário é local e determinístico: o primeiro processo persiste um checkpoint e
morre com ``os._exit``; o supervisor reinicia um segundo processo, que precisa
ler o checkpoint, validar o proprietário e registrar a retomada.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path


def filho(caminho: Path, geração: int) -> int:
    if geração == 1:
        caminho.write_text(json.dumps({"trabalhador": "worker-a", "época": 1, "shards": [0, 1]}), encoding="utf-8")
        os._exit(17)
    estado = json.loads(caminho.read_text(encoding="utf-8"))
    if estado != {"trabalhador": "worker-a", "época": 1, "shards": [0, 1]}:
        return 2
    caminho.write_text(json.dumps({**estado, "retomado": True, "época": 2}), encoding="utf-8")
    return 0


def principal() -> None:
    if len(sys.argv) == 3 and sys.argv[1] == "--filho":
        raise SystemExit(filho(Path(sys.argv[2]), int(os.environ["PIMCORD_GERACAO"])))
    with tempfile.TemporaryDirectory(prefix="pimcord-crash-") as pasta:
        checkpoint = Path(pasta) / "checkpoint.json"
        ambiente = dict(os.environ, PIMCORD_GERACAO="1")
        primeiro = subprocess.run([sys.executable, __file__, "--filho", str(checkpoint)], env=ambiente)
        assert primeiro.returncode == 17, primeiro.returncode
        assert checkpoint.exists()
        ambiente["PIMCORD_GERACAO"] = "2"
        segundo = subprocess.run([sys.executable, __file__, "--filho", str(checkpoint)], env=ambiente)
        assert segundo.returncode == 0, segundo.returncode
        resultado = json.loads(checkpoint.read_text(encoding="utf-8"))
        assert resultado["retomado"] is True
        assert resultado["época"] == 2
    print("crash_externo=aprovado retomada=aprovada checkpoint=validado")


if __name__ == "__main__":
    principal()
