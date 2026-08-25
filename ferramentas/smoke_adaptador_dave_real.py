from __future__ import annotations

import json

import dave

from pimcord.adaptador_dave import AdaptadorDAVEPy


def principal() -> None:
    adaptador = AdaptadorDAVEPy(dave)
    adaptador.inicializar(versao=1, grupo_id=123, usuario_id="123456789")
    pacote = adaptador.gerar_key_package()
    adaptador.configurar_midia(tipo="audio", ssrc=42, codec="opus")
    print(json.dumps({
        "versao": adaptador.versao,
        "grupo_id": adaptador.grupo_id,
        "key_package_bytes": len(pacote),
        "epoca": adaptador.epoca,
        "contexto_midia": True,
        "grupo_estabelecido": bool(adaptador.sessao.has_established_group()),
        "transformacao_disponivel": False,
        "motivo_transformacao": "aguarda commit/welcome MLS interoperável",
    }, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    principal()
