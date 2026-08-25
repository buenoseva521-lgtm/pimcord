import struct

import pimcord


def amostras(*valores: int) -> bytes:
    return struct.pack("<" + "h" * len(valores), *valores)


def ler(dados: bytes) -> tuple[int, ...]:
    return struct.unpack("<" + "h" * (len(dados) // 2), dados)


class Gravador:
    def __init__(self) -> None:
        self.quadros: list[bytes] = []

    def escrever(self, dados: bytes) -> None:
        self.quadros.append(dados)


def test_processador_preserva_frames_sem_decidir_perdas() -> None:
    processador = pimcord.ProcessadorPCMRecebido()
    quadros = [amostras(1), amostras(2)]
    assert processador.processar(quadros) == quadros


def test_processador_mistura_somente_quando_solicitado() -> None:
    processador = pimcord.ProcessadorPCMRecebido()
    assert ler(processador.processar([amostras(100), amostras(300)], misturar=True)[0]) == (200,)


def test_processador_preenche_lacuna_apenas_por_chamada_explicita() -> None:
    processador = pimcord.ProcessadorPCMRecebido()
    assert ler(processador.preencher_lacuna(amostras(0), amostras(1000), passo=1, total_passos=2)) == (500,)


def test_processador_entrega_ao_gravador_na_ordem() -> None:
    gravador = Gravador()
    processador = pimcord.ProcessadorPCMRecebido()
    quadros = [amostras(1), amostras(2)]
    assert processador.processar(quadros, gravador=gravador) == quadros
    assert gravador.quadros == quadros


def test_processador_e_exportado_pelo_pacote() -> None:
    assert "ProcessadorPCMRecebido" in pimcord.__all__
