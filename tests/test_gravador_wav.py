import wave

from pimcord import GravadorWAV


def test_gravador_wav_persiste_pcm(tmp_path):
    caminho = tmp_path / "recebido.wav"
    gravador = GravadorWAV(str(caminho), canais=1, amostragem=48000, bytes_amostra=2)
    gravador.escrever(b"\x00\x01" * 10)
    gravador.fechar()
    with wave.open(str(caminho), "rb") as arquivo:
        assert arquivo.getnchannels() == 1
        assert arquivo.getframerate() == 48000
        assert arquivo.getsampwidth() == 2
        assert arquivo.readframes(10) == b"\x00\x01" * 10
