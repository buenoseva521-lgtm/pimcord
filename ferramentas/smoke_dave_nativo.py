from __future__ import annotations

import json

import dave


def executar() -> None:
    saida: dict[str, object] = {
        "versao_maxima": int(dave.get_max_supported_protocol_version()),
        "simbolos": all(hasattr(dave, nome) for nome in ("Session", "Encryptor", "Decryptor", "SignatureKeyPair")),
    }
    versao = 1
    grupo_id = 123
    usuario_id = "123456789"
    chave = dave.SignatureKeyPair.generate(versao)
    sessao = dave.Session(None)
    sessao.init(versao, grupo_id, usuario_id, chave)
    pacote = sessao.get_marshalled_key_package()
    saida["key_package_bytes"] = len(pacote) if pacote else 0
    saida["grupo_estabelecido_antes_negociacao"] = bool(sessao.has_established_group())
    saida["external_sender_disponivel"] = callable(getattr(sessao, "set_external_sender", None))
    saida["ratchet_disponivel_antes_negociacao"] = sessao.get_key_ratchet(usuario_id) is not None
    print(json.dumps(saida, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    executar()
