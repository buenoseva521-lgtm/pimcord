import struct

import pytest

from pimcord import EstadoDAVE, MensagemDAVE, OpcodeDAVE, validar_backend_dave


class Backend:
    versao_maxima = 1

    def __init__(self):
        self.key_package = b"key-package"
        self.epocas = []
        self.mensagens = []

    def gerar_key_package(self) -> bytes:
        return self.key_package

    def processar_mensagem_mls(self, dados: bytes) -> None:
        self.mensagens.append(dados)

    def preparar_epoca(self, epoca: int) -> None:
        self.epocas.append(epoca)

    def exportar_chave_remetente(self, remetente_id: str) -> bytes:
        return b"chave-" + remetente_id.encode()


def test_validador_dave_aceita_backend_completo_e_rejeita_incompleto():
    assert validar_backend_dave(Backend()).versao_maxima == 1
    with pytest.raises(TypeError, match="versao_maxima"):
        validar_backend_dave(object())


class BackendSemOperacao:
    versao_maxima = 1


def test_validador_dave_rejeita_metodo_ausente():
    with pytest.raises(TypeError, match="processar_mensagem_mls"):
        validar_backend_dave(BackendSemOperacao())


def test_mensagem_dave_binaria_com_sequencia():
    original = MensagemDAVE(OpcodeDAVE.PRONTO_PARA_TRANSICAO, b"abc", 9)
    recebido = MensagemDAVE.desserializar(original.serializar(), tem_sequencia=True)
    assert recebido == original


def test_estado_dave_prepara_key_package_e_transicao():
    backend = Backend()
    estado = EstadoDAVE(backend)
    assert estado.identificar() == {"max_dave_protocol_version": 1}
    assert estado.receber_preparacao(versao=1, epoca=1, transicao_id=4) == b"key-package"
    pronto = estado.marcar_pronto()
    assert pronto.opcode == OpcodeDAVE.PRONTO_PARA_TRANSICAO
    assert pronto.payload == struct.pack(">I", 4)
    estado.executar(transicao_id=4)
    assert estado.em_transicao is False


def test_estado_dave_encaminha_mls_e_exporta_chave_apos_transicao():
    backend = Backend()
    estado = EstadoDAVE(backend)
    estado.receber_preparacao(versao=1, epoca=1, transicao_id=4)
    estado.marcar_pronto()
    estado.executar(transicao_id=4)
    estado.receber_mensagem_mls(b"mensagem-mls")
    assert backend.mensagens == [b"mensagem-mls"]
    assert estado.exportar_chave_remetente("42") == b"chave-42"
    with pytest.raises(ValueError):
        estado.receber_mensagem_mls(b"")


def test_estado_dave_rejeita_versao_ou_transicao_invalida():
    estado = EstadoDAVE(Backend())
    with pytest.raises(ValueError):
        estado.receber_preparacao(versao=2, epoca=1, transicao_id=1)
    with pytest.raises(RuntimeError):
        estado.marcar_pronto()


def test_estado_dave_rejeita_epoca_antiga_e_conflito_atual():
    estado = EstadoDAVE(Backend())
    estado.receber_preparacao(versao=1, epoca=1, transicao_id=1)
    with pytest.raises(ValueError):
        estado.receber_preparacao(versao=1, epoca=1, transicao_id=2)
    estado.marcar_pronto()
    estado.executar(transicao_id=1)
    with pytest.raises(ValueError):
        estado.receber_preparacao(versao=1, epoca=0, transicao_id=3)


def test_exigencia_dave_real_rejeita_backend_de_teste():
    from pimcord import exigir_backend_dave_real
    with pytest.raises(TypeError, match="E2EE real"):
        exigir_backend_dave_real(Backend())


class BackendRealDeclarado(Backend):
    e2ee_real = True

    def cifrar_frame(self, frame: bytes, remetente_id: str) -> bytes:
        return frame

    def decifrar_frame(self, frame: bytes, remetente_id: str) -> bytes:
        return frame

    def autenticador_epoca(self) -> bytes:
        return b"autenticador"

    def processar_propostas(self, dados: bytes) -> None:
        self.mensagens.append(b"propostas:" + dados)

    def processar_commit(self, dados: bytes) -> None:
        self.mensagens.append(b"commit:" + dados)

    def processar_welcome(self, dados: bytes) -> None:
        self.mensagens.append(b"welcome:" + dados)


def test_exigencia_dave_real_exige_superficie_criptografica_explicita():
    from pimcord import exigir_backend_dave_real
    assert exigir_backend_dave_real(BackendRealDeclarado()).e2ee_real is True


def test_estado_dave_encaminha_envelope_mls_sem_adivinhar_bytes():
    from pimcord import MensagemMLSDAVE, TipoMensagemMLS

    backend = BackendRealDeclarado()
    estado = EstadoDAVE(backend)
    estado.receber_mensagem_mls_tipada(
        MensagemMLSDAVE(TipoMensagemMLS.COMMIT, b"commit", frozenset({"42"}))
    )
    assert backend.mensagens == [b"commit:commit"]


def test_estado_dave_recusa_backend_sem_dispatch_semantico():
    from pimcord import MensagemMLSDAVE, TipoMensagemMLS

    with pytest.raises(TypeError, match="processador semântico"):
        EstadoDAVE(Backend()).receber_mensagem_mls_tipada(
            MensagemMLSDAVE(TipoMensagemMLS.WELCOME, b"welcome")
        )


def test_backend_dave_real_e_exportado_como_contrato_tipado():
    import pimcord
    from pimcord import BackendDAVEReal

    assert BackendDAVEReal is pimcord.BackendDAVEReal
    assert "BackendDAVEReal" in pimcord.__all__



def test_envelope_mls_tipado_exige_tipo_e_dados():
    from pimcord import MensagemMLSDAVE, TipoMensagemMLS

    mensagem = MensagemMLSDAVE(
        TipoMensagemMLS.COMMIT,
        b"commit-binario",
        frozenset({"usuario-1"}),
    )
    assert mensagem.tipo is TipoMensagemMLS.COMMIT
    assert mensagem.dados == b"commit-binario"
    assert mensagem.usuarios_reconhecidos == frozenset({"usuario-1"})

    with pytest.raises(ValueError, match="vazia"):
        MensagemMLSDAVE(TipoMensagemMLS.WELCOME, b"")


def test_envelope_mls_rejeita_usuario_reconhecido_invalido():
    from pimcord import MensagemMLSDAVE, TipoMensagemMLS

    with pytest.raises(ValueError, match="IDs não vazios"):
        MensagemMLSDAVE(TipoMensagemMLS.PROPOSTAS, b"proposta", frozenset({""}))


def test_envelope_mls_e_exportado_publicamente():
    import pimcord
    from pimcord import MensagemMLSDAVE, TipoMensagemMLS

    assert pimcord.MensagemMLSDAVE is MensagemMLSDAVE
    assert pimcord.TipoMensagemMLS is TipoMensagemMLS
    assert "MensagemMLSDAVE" in pimcord.__all__
    assert "TipoMensagemMLS" in pimcord.__all__


def test_adaptador_dave_py_mapeia_sessao_mls_e_midia():
    from enum import IntEnum
    from types import SimpleNamespace
    from pimcord import AdaptadorDAVEPy, MensagemMLSDAVE, TipoMensagemMLS

    class TipoMidia(IntEnum):
        audio = 0
        video = 1

    class Codec(IntEnum):
        opus = 1
        vp8 = 2

    class SignatureKeyPair:
        @staticmethod
        def generate(versao):
            return ("chave", versao)

    class SessaoFake:
        def __init__(self, callback=None):
            self.callback = callback
            self.inicializada = None
            self.mensagens = []

        def init(self, versao, grupo, usuario, chave):
            self.inicializada = (versao, grupo, usuario, chave)

        def get_marshalled_key_package(self):
            return b"key-package-real"

        def set_external_sender(self, pacote):
            self.external_sender = pacote

        def process_proposals(self, dados, usuarios):
            self.mensagens.append(("propostas", dados, usuarios))
            return b"commit-welcome"

        def process_commit(self, dados):
            self.mensagens.append(("commit", dados))
            return {}

        def process_welcome(self, dados, usuarios):
            self.mensagens.append(("welcome", dados, usuarios))
            return {}

        def has_established_group(self):
            return True

        def get_key_ratchet(self, usuario):
            return "ratchet:" + usuario

        def get_last_epoch_authenticator(self):
            return b"auth"

        def reset(self):
            pass

        def set_protocol_version(self, versao):
            pass

    class EncryptorFake:
        def __init__(self):
            self.codec = None
            self.ratchet = None

        def assign_ssrc_to_codec(self, ssrc, codec):
            self.codec = (ssrc, codec)

        def set_key_ratchet(self, ratchet):
            self.ratchet = ratchet

        def encrypt(self, tipo, ssrc, frame):
            return b"cifrado:" + frame

    class DecryptorFake:
        def transition_to_key_ratchet(self, ratchet, validade):
            self.ratchet = ratchet

        def decrypt(self, tipo, frame):
            return frame.removeprefix(b"cifrado:")

    modulo = SimpleNamespace(
        MediaType=TipoMidia,
        Codec=Codec,
        SignatureKeyPair=SignatureKeyPair,
        Session=SessaoFake,
        Encryptor=EncryptorFake,
        Decryptor=DecryptorFake,
        get_max_supported_protocol_version=lambda: 1,
    )
    adaptador = AdaptadorDAVEPy(modulo)
    adaptador.inicializar(versao=1, grupo_id=9, usuario_id="10")
    assert adaptador.gerar_key_package() == b"key-package-real"
    adaptador.definir_external_sender(b"external-sender")
    adaptador.processar_mensagem_tipada(
        MensagemMLSDAVE(TipoMensagemMLS.PROPOSTAS, b"propostas", frozenset({"11"}))
    )
    assert adaptador.consumir_resposta_mls() == b"commit-welcome"
    adaptador.processar_mensagem_tipada(
        MensagemMLSDAVE(TipoMensagemMLS.COMMIT, b"commit", frozenset({"11"}))
    )
    assert set(adaptador.preparar_ratchets()) == {"10", "11"}
    adaptador.configurar_midia(tipo="audio", ssrc=123, codec="opus")
    cifrado = adaptador.cifrar_frame("11", b"frame")
    assert cifrado == b"cifrado:frame"
    assert adaptador.decifrar_frame("11", cifrado) == b"frame"
    assert adaptador.autenticador_epoca(1, b"") == b"auth"


def test_opcodes_dave_oficiais_sao_reconhecidos_sem_decodificar_payloads():
    assert [int(op) for op in OpcodeDAVE] == list(range(21, 32))
    mensagem = MensagemDAVE(OpcodeDAVE.WELCOME, b"welcome", 7)
    assert MensagemDAVE.desserializar(mensagem.serializar(), tem_sequencia=True) == mensagem


def test_estado_dave_encaminha_propostas_commit_e_welcome_explicitamente():
    class BackendMLS(Backend):
        def __init__(self):
            super().__init__()
            self.mls = []

        def processar_propostas(self, dados):
            self.mls.append(("propostas", dados))

        def processar_commit(self, dados):
            self.mls.append(("commit", dados))

        def processar_welcome(self, dados):
            self.mls.append(("welcome", dados))

    backend = BackendMLS()
    estado = EstadoDAVE(backend)
    estado.receber_propostas(b"p")
    estado.receber_commit(b"c")
    estado.receber_welcome(b"w")
    assert backend.mls == [("propostas", b"p"), ("commit", b"c"), ("welcome", b"w")]

    with pytest.raises(ValueError, match="vazio"):
        estado.receber_commit(b"")



def test_cliente_gateway_voz_encaminha_binario_dave_para_backend_sem_adivinhar_mls():
    import asyncio
    from pimcord import ClienteGatewayVoz, MensagemDAVE, OpcodeDAVE, SessaoVoz

    class BackendGateway(BackendRealDeclarado):
        def __init__(self):
            super().__init__()
            self.eventos = []

        def processar_remetente_externo(self, dados):
            self.eventos.append(("external_sender", dados))

        def processar_evento_dave(self, opcode, dados, sequencia):
            self.eventos.append((opcode, dados, sequencia))

    backend = BackendGateway()
    sessao = SessaoVoz(object(), "servidor", "usuario", "token")
    sessao.ativar_dave(backend)
    cliente = ClienteGatewayVoz(sessao)

    async def executar():
        await cliente.processar_binario(MensagemDAVE(OpcodeDAVE.REMETENTE_EXTERNO, b"sender", 3).serializar())
        await cliente.processar_binario(MensagemDAVE(OpcodeDAVE.PROPOSTAS, b"propostas", 4).serializar())
        await cliente.processar_binario(MensagemDAVE(OpcodeDAVE.WELCOME, b"welcome", 5).serializar())
        await cliente.processar_binario(MensagemDAVE(OpcodeDAVE.PRONTO_PARA_TRANSICAO, b"evento", 6).serializar())

    asyncio.run(executar())
    assert backend.eventos == [
        ("external_sender", b"sender"),
        (23, b"evento", 6),
    ]
    assert backend.mensagens == [b"propostas:propostas", b"welcome:welcome"]


def test_cliente_gateway_voz_recusa_binario_sem_backend_dave():
    import asyncio
    from pimcord import ClienteGatewayVoz, MensagemDAVE, OpcodeDAVE, SessaoVoz

    cliente = ClienteGatewayVoz(SessaoVoz(object(), "servidor", "usuario"))

    async def executar():
        with pytest.raises(RuntimeError, match="backend DAVE ativo"):
            await cliente.processar_binario(MensagemDAVE(OpcodeDAVE.WELCOME, b"welcome", 1).serializar())

    asyncio.run(executar())
