import struct

import pimcord
import pytest


def amostras(*valores: int) -> bytes:
    return struct.pack("<" + "h" * len(valores), *valores)


def ler(dados: bytes) -> tuple[int, ...]:
    return struct.unpack("<" + "h" * (len(dados) // 2), dados)


def test_interpolador_lineariza_quadro_intermediario() -> None:
    interpolador = pimcord.InterpoladorPCM()
    assert ler(interpolador.interpolar(amostras(0, 1000), amostras(1000, 3000), passo=1, total_passos=2)) == (500, 2000)


def test_interpolador_satura_amostras() -> None:
    interpolador = pimcord.InterpoladorPCM()
    assert ler(interpolador.interpolar(amostras(32760), amostras(-32760), passo=1, total_passos=2)) == (0,)


def test_interpolador_rejeita_passo_fora_da_lacuna() -> None:
    interpolador = pimcord.InterpoladorPCM()
    with pytest.raises(ValueError, match="passo"):
        interpolador.interpolar(amostras(0), amostras(1), passo=0, total_passos=2)


def test_interpolador_rejeita_quadros_incompativeis() -> None:
    interpolador = pimcord.InterpoladorPCM()
    with pytest.raises(ValueError, match="mesmo tamanho"):
        interpolador.interpolar(amostras(0), amostras(1, 2), passo=1, total_passos=2)


def test_interpolador_e_exportado_pelo_pacote() -> None:
    assert "InterpoladorPCM" in pimcord.__all__
