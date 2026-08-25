from pimcord import BufferJitter, PacoteRTP


def pacote(numero: int) -> PacoteRTP:
    return PacoteRTP(numero, numero * 960, 7, bytes([numero & 255]))


def test_rtp_serializa_e_desserializa():
    original = PacoteRTP(12, 960, 99, b"opus", tipo_carga=111, marcador=True)
    recebido = PacoteRTP.desserializar(original.serializar())
    assert recebido.sequencia == 12
    assert recebido.timestamp == 960
    assert recebido.ssrc == 99
    assert recebido.carga == b"opus"
    assert recebido.tipo_carga == 111
    assert recebido.marcador is True


def test_buffer_jitter_libera_pacotes_em_ordem_e_descarta_duplicata():
    buffer = BufferJitter(capacidade=4)
    assert [item.sequencia for item in buffer.inserir(pacote(10))] == [10]
    assert buffer.inserir(pacote(12)) == []
    assert [item.sequencia for item in buffer.inserir(pacote(11))] == [11, 12]
    assert buffer.inserir(pacote(11)) == []
    assert buffer.descartados == 1


def test_buffer_jitter_avanca_lacuna_sem_fabricar_audio():
    buffer = BufferJitter()
    assert buffer.inserir(pacote(10))
    assert buffer.inserir(pacote(12)) == []
    assert buffer.avançar_sequencia(12) == 1
    assert [item.sequencia for item in buffer.inserir(pacote(13))] == [12, 13]
    assert buffer.descartados == 1


def test_buffer_jitter_respeita_wrap_de_sequencia():
    buffer = BufferJitter(capacidade=4)
    assert [item.sequencia for item in buffer.inserir(pacote(65535))] == [65535]
    assert [item.sequencia for item in buffer.inserir(pacote(0))] == [0]
