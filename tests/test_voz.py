import asyncio

import pytest

from pimcord import Bot, InformacoesVoz, PacoteRTP, SessaoVoz


def test_pacote_rtp_tem_cabecalho_e_carga():
    pacote = PacoteRTP(1, 960, 42, b"audio")
    bruto = pacote.serializar()
    assert len(bruto) == 12 + 5
    assert bruto[-5:] == b"audio"
    assert bruto[0] == 0x80


def test_informacoes_e_selecao_de_modo():
    info = InformacoesVoz.de_pronto("1", "2", "sessao", "token", {"endpoint": "voz", "ssrc": 8, "ip": "127.0.0.1", "port": 9, "modes": ["aead_aes256_gcm_rtpsize"], "heartbeat_interval": 1000})
    assert info.intervalo_heartbeat == 1
    bot = Bot()
    sessao = SessaoVoz(bot, "1", "2")
    sessao.informacoes = info
    assert sessao.selecionar_modo() == "aead_aes256_gcm_rtpsize"
    assert sessao.construir_select_protocol(endereco="127.0.0.1", porta=9)["d"]["data"]["mode"] == "aead_aes256_gcm_rtpsize"


@pytest.mark.asyncio
async def test_heartbeat_de_voz_envia_seq_ack_e_para():
    bot = Bot()
    sessao = SessaoVoz(bot, "1", "2")
    sessao.informacoes = InformacoesVoz("1", "2", "s", "t", "voz", sequencia_ack=17)
    enviados = []
    await sessao.iniciar_heartbeat(enviados.append, intervalo=0.001)
    await asyncio.sleep(0.01)
    await sessao.sair()
    assert enviados
    assert enviados[0]["op"] == 3
    assert enviados[0]["d"]["seq_ack"] == 17


@pytest.mark.asyncio
async def test_fontes_e_fila_de_audio_sao_limitadas():
    from pimcord import FontePCM, FonteSilencio, FilaAudio
    fonte = FontePCM(b"abcdefgh", tamanho_quadro=3)
    assert await fonte.proximo_quadro() == b"abc"
    assert await fonte.proximo_quadro() == b"def"
    assert await fonte.proximo_quadro() == b"gh"
    silencio = FonteSilencio(quadros=1, tamanho_quadro=2)
    assert await silencio.proximo_quadro() == bytes(2)
    assert await silencio.proximo_quadro() is None
    fila = FilaAudio(limite=2)
    assert fila.limite == 2


@pytest.mark.asyncio
async def test_gravador_e_fonte_wav_sem_dependencias(tmp_path):
    from pimcord import FonteWAV, GravadorWAV
    caminho = tmp_path / "audio.wav"
    gravador = GravadorWAV(str(caminho), canais=1, amostragem=48000)
    gravador.escrever(bytes(3840))
    gravador.fechar()
    fonte = FonteWAV(str(caminho), tamanho_quadro=3840)
    assert fonte.amostragem == 48000
    assert fonte.canais == 1
    assert await fonte.proximo_quadro() == bytes(3840)
    fonte.fechar()


def test_criptografia_rejeita_modo_nao_implementado():
    from pimcord import CriptografiaVozOpcional
    with pytest.raises(RuntimeError, match="adaptador compatível"):
        CriptografiaVozOpcional("aead_xchacha20_poly1305_rtpsize", b"0" * 32)


def test_criptografia_aes_gcm_tem_chave_e_nonce_validos():
    from pimcord import CriptografiaVozOpcional
    pytest.importorskip("cryptography")
    cifra = CriptografiaVozOpcional("aead_aes256_gcm_rtpsize", b"1" * 32)
    resultado = cifra.cifrar_pacote(b"cabecalho-rtp", b"audio")
    assert resultado != b"audio"
    assert len(resultado) > len(b"audio")



def test_buffer_jitter_resiste_a_20_janelas_de_reordenacao_e_perda():
    from pimcord import BufferJitter

    buffer = BufferJitter(capacidade=16)
    liberados = []
    perdidos = 0
    for inicio in range(0, 200, 10):
        janela = [PacoteRTP(inicio, inicio * 960, 7, bytes([inicio & 0xFF]))]
        janela.extend(PacoteRTP(seq, seq * 960, 7, bytes([seq & 0xFF])) for seq in range(inicio + 2, inicio + 10))
        liberados.extend(buffer.inserir(janela[0]))
        for pacote in reversed(janela[1:]):
            liberados.extend(buffer.inserir(pacote))
        if inicio + 10 < 200:
            perdidos += buffer.avançar_sequencia(inicio + 10)
    assert len(liberados) == 20
    assert [pacote.sequencia for pacote in liberados] == list(range(0, 200, 10))
    assert perdidos == 171
    assert buffer.descartados == 171
    assert buffer.pendentes == 8


@pytest.mark.asyncio
async def test_eventos_de_voz_ligam_sessao_ao_gateway_sem_rede(monkeypatch):
    from pimcord.discord.modelos import Usuario
    from pimcord.voz import ClienteGatewayVoz

    bot = Bot()
    bot._usuario = Usuario("bot-1", "teste")
    sessao = SessaoVoz(bot, "guild-1", "bot-1")
    bot._sessoes_voz["guild-1"] = sessao
    executou = asyncio.Event()

    async def executar_sem_rede(self, maximo_tentativas=None):
        executou.set()

    monkeypatch.setattr(ClienteGatewayVoz, "executar", executar_sem_rede)
    await bot._processar_estado_voz({"guild_id": "guild-1", "user_id": "bot-1", "session_id": "sessao-1", "channel_id": "canal-1"})
    await bot._processar_servidor_voz({"guild_id": "guild-1", "endpoint": "voice.example", "token": "temporario"})
    await asyncio.wait_for(executou.wait(), timeout=1)
    assert sessao._sessao_gateway_id == "sessao-1"
    assert sessao.estado == "servidor_recebido"
    assert sessao.gateway_voz is not None
    await sessao.sair()


@pytest.mark.asyncio
async def test_session_description_registra_chave_e_modo():
    from pimcord.voz import ClienteGatewayVoz

    bot = Bot()
    sessao = SessaoVoz(bot, "guild-1", "bot-1")
    sessao.informacoes = InformacoesVoz("guild-1", "bot-1", "sessao", "token", "voice.example")
    cliente = ClienteGatewayVoz(sessao)
    await cliente.processar({"op": 4, "d": {"mode": "aead_aes256_gcm_rtpsize", "secret_key": [1] * 32}})
    assert sessao.informacoes.chave_secreta == bytes([1]) * 32
    assert sessao.modo_criptografia == "aead_aes256_gcm_rtpsize"
    assert sessao.estado == "conectada"


@pytest.mark.asyncio
async def test_session_description_sem_chave_e_rejeitada():
    from pimcord.voz import ClienteGatewayVoz

    bot = Bot()
    sessao = SessaoVoz(bot, "guild-1", "bot-1")
    sessao.informacoes = InformacoesVoz("guild-1", "bot-1", "sessao", "token", "voice.example")
    cliente = ClienteGatewayVoz(sessao)
    with pytest.raises(ValueError, match="secret_key"):
        await cliente.processar({"op": 4, "d": {"mode": "aead_aes256_gcm_rtpsize"}})
