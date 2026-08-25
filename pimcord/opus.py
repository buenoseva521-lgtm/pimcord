"""Adaptador opcional de Opus usando a biblioteca nativa libopus.

O módulo não é importado por padrão como dependência obrigatória. Em ambientes
sem libopus, a construção falha com uma mensagem clara para permitir o fallback
PCM já existente ou a instalação do pacote nativo apropriado.
"""
from __future__ import annotations

import ctypes
import ctypes.util
from typing import ClassVar


class OpusIndisponivel(RuntimeError):
    """Sinaliza que libopus não está instalada ou não pôde ser carregada."""


class CodecOpus:
    """Codificador/decodificador Opus real, adequado a frames de voz Discord."""

    APLICACAO_VOZ: ClassVar[int] = 2049  # OPUS_APPLICATION_VOIP
    _ERRO_OK: ClassVar[int] = 0

    def __init__(self, *, taxa: int = 48_000, canais: int = 2, frame_size: int = 960, bitrate: int | None = None, biblioteca: str | None = None):
        if taxa not in (8_000, 12_000, 16_000, 24_000, 48_000):
            raise ValueError("A taxa Opus deve ser 8000, 12000, 16000, 24000 ou 48000 Hz")
        if canais not in (1, 2):
            raise ValueError("Opus suporta apenas 1 ou 2 canais neste adaptador")
        if frame_size <= 0:
            raise ValueError("frame_size deve ser positivo")
        nome = biblioteca or ctypes.util.find_library("opus") or "libopus.so.0"
        try:
            self._lib = ctypes.CDLL(nome)
        except OSError as erro:
            raise OpusIndisponivel(f"libopus não encontrada ({nome!r}); instale o codec nativo para usar voz Opus") from erro
        self.taxa = taxa
        self.canais = canais
        self.frame_size = frame_size
        self._configurar_api()
        erro = ctypes.c_int()
        self._codificador = self._lib.opus_encoder_create(taxa, canais, self.APLICACAO_VOZ, ctypes.byref(erro))
        if erro.value != self._ERRO_OK or not self._codificador:
            raise OpusIndisponivel(f"libopus não criou o encoder (código {erro.value})")
        self._decodificador = self._lib.opus_decoder_create(taxa, canais, ctypes.byref(erro))
        if erro.value != self._ERRO_OK or not self._decodificador:
            self._lib.opus_encoder_destroy(self._codificador)
            raise OpusIndisponivel(f"libopus não criou o decoder (código {erro.value})")
        if bitrate is not None:
            self._configurar_bitrate(bitrate)

    def _configurar_api(self) -> None:
        ponteiro = ctypes.c_void_p
        self._lib.opus_encoder_create.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_int)]
        self._lib.opus_encoder_create.restype = ponteiro
        self._lib.opus_encoder_destroy.argtypes = [ponteiro]
        self._lib.opus_encoder_destroy.restype = None
        self._lib.opus_encode.argtypes = [ponteiro, ctypes.POINTER(ctypes.c_int16), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int32]
        self._lib.opus_encode.restype = ctypes.c_int32
        self._lib.opus_decoder_create.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_int)]
        self._lib.opus_decoder_create.restype = ponteiro
        self._lib.opus_decoder_destroy.argtypes = [ponteiro]
        self._lib.opus_decoder_destroy.restype = None
        self._lib.opus_decode.argtypes = [ponteiro, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int32, ctypes.POINTER(ctypes.c_int16), ctypes.c_int, ctypes.c_int]
        self._lib.opus_decode.restype = ctypes.c_int32
        self._lib.opus_encoder_ctl.argtypes = [ponteiro, ctypes.c_int, ctypes.c_int]
        self._lib.opus_encoder_ctl.restype = ctypes.c_int

    def _configurar_bitrate(self, bitrate: int) -> None:
        if bitrate <= 0:
            raise ValueError("bitrate deve ser positivo")
        resultado = self._lib.opus_encoder_ctl(self._codificador, 4002, int(bitrate))  # OPUS_SET_BITRATE_REQUEST
        if resultado != self._ERRO_OK:
            raise ValueError(f"libopus rejeitou bitrate (código {resultado})")

    def codificar(self, pcm: bytes) -> bytes:
        esperado = self.frame_size * self.canais * 2
        if len(pcm) != esperado:
            raise ValueError(f"um frame PCM deve conter {esperado} bytes; recebido {len(pcm)}")
        amostras = (ctypes.c_int16 * (self.frame_size * self.canais)).from_buffer_copy(pcm)
        saida = (ctypes.c_ubyte * 4000)()
        tamanho = self._lib.opus_encode(self._codificador, amostras, self.frame_size, saida, len(saida))
        if tamanho < 0:
            raise OpusIndisponivel(f"libopus falhou ao codificar (código {tamanho})")
        return bytes(saida[:tamanho])

    def decodificar(self, pacote: bytes, *, frame_size: int | None = None) -> bytes:
        if not pacote:
            raise ValueError("pacote Opus vazio")
        capacidade = frame_size or self.frame_size
        entrada = (ctypes.c_ubyte * len(pacote)).from_buffer_copy(pacote)
        saida = (ctypes.c_int16 * (capacidade * self.canais))()
        tamanho = self._lib.opus_decode(self._decodificador, entrada, len(pacote), saida, capacidade, 0)
        if tamanho < 0:
            raise OpusIndisponivel(f"libopus falhou ao decodificar (código {tamanho})")
        return ctypes.string_at(ctypes.addressof(saida), tamanho * self.canais * 2)

    def fechar(self) -> None:
        if getattr(self, "_codificador", None):
            self._lib.opus_encoder_destroy(self._codificador)
            self._codificador = None
        if getattr(self, "_decodificador", None):
            self._lib.opus_decoder_destroy(self._decodificador)
            self._decodificador = None

    def __enter__(self) -> "CodecOpus":
        return self

    def __exit__(self, *_: object) -> None:
        self.fechar()

    def __del__(self) -> None:
        try:
            self.fechar()
        except Exception:
            pass


__all__ = ["CodecOpus", "OpusIndisponivel"]
