import importlib.util

import pytest

from pimcord import CodificadorOpus


def test_opus_real_codifica_e_decodifica_frame():
    if importlib.util.find_spec("opuslib") is None:
        try:
            codec = CodificadorOpus(backend="nativo")
        except Exception as erro:
            if "indisponível" in str(erro).lower() or "não encontrou" in str(erro).lower():
                pytest.skip("libopus não disponível neste ambiente")
            raise
    else:
        codec = CodificadorOpus(backend="nativo")
    pcm = b"\x00\x00" * (960 * 2)
    try:
        pacote = codec.codificar(pcm)
        decodificado = codec.decodificar(pacote)
        assert pacote
        assert len(decodificado) > 0
        assert len(decodificado) <= len(pcm)
    finally:
        codec.fechar()
