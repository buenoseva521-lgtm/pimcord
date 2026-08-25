import struct

import pimcord
import pytest


def amostras(*valores: int) -> bytes:
    return struct.pack("<" + "h" * len(valores), *valores)


def ler(dados: bytes) -> tuple[int, ...]:
    return struct.unpack("<" + "h" * (len(dados) // 2), dados)


def test_misturador_faz_media_das_amostras() -> None:
    misturador = pimcord.MisturadorPCM()
    assert ler(misturador.misturar([amostras(1000, -1000), amostras(3000, 1000)])) == (2000, 0)


def test_misturador_satura_sem_estourar_pcm() -> None:
    misturador = pimcord.MisturadorPCM()
    assert ler(misturador.misturar([amostras(32767), amostras(32767)])) == (32767,)
    assert ler(misturador.misturar([amostras(-32768), amostras(-32768)])) == (-32768,)


def test_misturador_rejeita_quadros_incompativeis() -> None:
    misturador = pimcord.MisturadorPCM()
    with pytest.raises(ValueError, match="mesmo tamanho"):
        misturador.misturar([amostras(1), amostras(1, 2)])
    with pytest.raises(ValueError, match="amostras completas"):
        misturador.misturar([b"\x00"])


def test_misturador_nao_fabrica_quadro_ausente() -> None:
    misturador = pimcord.MisturadorPCM()
    assert misturador.misturar([]) == b""


def test_misturador_e_exportado_pelo_pacote() -> None:
    assert "MisturadorPCM" in pimcord.__all__
