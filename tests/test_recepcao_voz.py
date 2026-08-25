from pimcord import InformacoesVoz, PacoteRTP, SessaoVoz


class Decodificador:
    def decodificar(self, dados: bytes) -> bytes:
        return b"pcm:" + dados


class Gravador:
    def __init__(self):
        self.frames = []

    def escrever(self, dados: bytes) -> None:
        self.frames.append(dados)


def test_sessao_voz_recebe_rtp_em_ordem():
    sessao = SessaoVoz(object(), "1", "2")
    primeiro = PacoteRTP(20, 0, 99, b"a").serializar()
    terceiro = PacoteRTP(22, 1920, 99, b"c").serializar()
    segundo = PacoteRTP(21, 960, 99, b"b").serializar()
    assert sessao.receber_audio(primeiro, decodificador=Decodificador()) == [b"pcm:a"]
    assert sessao.receber_audio(terceiro, decodificador=Decodificador()) == []
    gravador = Gravador()
    assert sessao.receber_audio(segundo, decodificador=Decodificador(), gravador=gravador) == [b"pcm:b", b"pcm:c"]
    assert gravador.frames == [b"pcm:b", b"pcm:c"]


def test_recepcao_entrega_frames_ao_processador_pcm():
    from pimcord import ProcessadorPCMRecebido

    sessao = SessaoVoz(object(), "1", "2")
    processador = ProcessadorPCMRecebido()
    primeiro = PacoteRTP(30, 0, 99, b"um").serializar()
    segundo = PacoteRTP(31, 960, 99, b"dois").serializar()

    assert sessao.receber_audio(primeiro, processador=processador) == [b"um"]
    assert sessao.receber_audio(segundo, processador=processador) == [b"dois"]


def test_sessao_voz_integra_dave_antes_do_rtp():
    class BackendDAVEFake:
        versao_maxima = 1
        e2ee_real = True

        def gerar_key_package(self):
            return b"kp"

        def processar_mensagem_mls(self, dados):
            return None

        def preparar_epoca(self, epoca):
            return None

        def exportar_chave_remetente(self, remetente_id):
            return b"chave"

        def processar_propostas(self, dados):
            return None

        def processar_commit(self, dados):
            return None

        def processar_welcome(self, dados):
            return None

        def cifrar_frame(self, remetente_id, frame):
            return b"dave:" + frame

        def decifrar_frame(self, remetente_id, frame):
            assert remetente_id == "2"
            return frame.removeprefix(b"dave:")

        def autenticador_epoca(self, epoca, dados):
            return b"auth"

    sessao = SessaoVoz(object(), "1", "2")
    sessao.informacoes = InformacoesVoz("1", "2", "sessao", "token", "endpoint", ssrc=99)
    backend = BackendDAVEFake()
    sessao.ativar_dave(backend)
    pacote = sessao.construir_audio(b"opus")
    assert PacoteRTP.desserializar(pacote).carga == b"dave:opus"
    recebido = PacoteRTP(1, 0, 99, b"dave:opus").serializar()
    assert sessao.receber_audio(recebido, remetente_id="2") == [b"opus"]
