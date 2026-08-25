"""Adaptador opcional para o binding nativo ``dave.py``/``libdave``.

O módulo não é importado pelo núcleo por padrão. A integração só é habilitada
quando o wheel nativo está instalado e quando o chamador fornece o contexto de
mídia (tipo, SSRC e codec). Não há fallback criptográfico neste adaptador.
"""
from __future__ import annotations

import importlib
from collections.abc import Iterable
from datetime import timedelta
from typing import Any

from .dave import BackendDAVEReal, MensagemMLSDAVE, TipoMensagemMLS


class AdaptadorDAVEPy:
    """Implementa o contrato Pimcord sobre ``dave.py`` sem esconder limitações."""

    e2ee_real = True

    def __init__(self, modulo: Any | None = None, *, callback_falha: Any = None):
        self.modulo = modulo or self._importar_modulo()
        maximo = getattr(self.modulo, "get_max_supported_protocol_version", None)
        if not callable(maximo):
            raise TypeError("dave.py sem get_max_supported_protocol_version")
        self.versao_maxima = int(maximo())
        if self.versao_maxima < 1:
            raise RuntimeError("dave.py não anuncia uma versão DAVE utilizável")
        classe_sessao = getattr(self.modulo, "Session", None)
        classe_encryptor = getattr(self.modulo, "Encryptor", None)
        classe_decryptor = getattr(self.modulo, "Decryptor", None)
        if not all(callable(item) for item in (classe_sessao, classe_encryptor, classe_decryptor)):
            raise TypeError("dave.py incompleto: Session, Encryptor e Decryptor são obrigatórios")
        self.sessao = classe_sessao(callback_falha)
        self.encryptor = classe_encryptor()
        self.decryptor = classe_decryptor()
        self.versao = 0
        self.grupo_id: int | None = None
        self.usuario_id: str | None = None
        self.epoca = 0
        self._usuarios_reconhecidos: set[str] = set()
        self._ssrc: int | None = None
        self._tipo_midia: Any | None = None
        self._codec: Any | None = None
        self._ratchet_remetente: str | None = None
        self._chave_transitoria: Any | None = None
        self._ultima_resposta_mls: bytes | None = None

    @staticmethod
    def _importar_modulo() -> Any:
        try:
            return importlib.import_module("dave")
        except ImportError as erro:
            raise RuntimeError(
                "O backend DAVE real não está instalado; instale dave.py "
                "em uma plataforma 64-bit compatível"
            ) from erro

    def inicializar(
        self,
        *,
        versao: int,
        grupo_id: int,
        usuario_id: str,
        chave_transitoria: Any | None = None,
    ) -> None:
        if not 1 <= versao <= self.versao_maxima:
            raise ValueError("versão DAVE fora do intervalo anunciado pelo backend")
        if not usuario_id or not str(usuario_id).isdigit():
            raise ValueError("usuario_id deve ser um ID numérico do Discord")
        if chave_transitoria is None:
            classe_chave = getattr(self.modulo, "SignatureKeyPair", None)
            gerar_chave = getattr(classe_chave, "generate", None) if classe_chave else None
            if not callable(gerar_chave):
                raise RuntimeError(
                    "dave.py não expõe SignatureKeyPair.generate; "
                    "não é possível criar um KeyPackage real"
                )
            chave_transitoria = gerar_chave(int(versao))
        self.sessao.init(versao, int(grupo_id), str(usuario_id), chave_transitoria)
        self._chave_transitoria = chave_transitoria
        self.versao = int(versao)
        self.grupo_id = int(grupo_id)
        self.usuario_id = str(usuario_id)
        self.epoca = 0
        self._ratchet_remetente = None

    def definir_usuarios_reconhecidos(self, usuarios: Iterable[str]) -> None:
        reconhecidos = {str(usuario) for usuario in usuarios if str(usuario)}
        if any(not usuario.isdigit() for usuario in reconhecidos):
            raise ValueError("usuarios_reconhecidos deve conter IDs numéricos do Discord")
        self._usuarios_reconhecidos = reconhecidos

    def definir_external_sender(self, pacote: bytes) -> None:
        if not pacote:
            raise ValueError("external sender package não pode ser vazio")
        metodo = getattr(self.sessao, "set_external_sender", None)
        if not callable(metodo):
            raise RuntimeError("dave.py não expõe set_external_sender")
        metodo(bytes(pacote))

    def processar_remetente_externo(self, pacote: bytes) -> None:
        """Alias semântico usado pelo dispatch binário do Voice Gateway."""
        self.definir_external_sender(pacote)

    def gerar_key_package(self) -> bytes:
        pacote = self.sessao.get_marshalled_key_package()
        if not pacote:
            raise RuntimeError("Session ainda não foi inicializada para gerar KeyPackage")
        return bytes(pacote)

    def processar_mensagem_mls(self, dados: bytes) -> None:
        raise TypeError(
            "AdaptadorDAVEPy exige MensagemMLSDAVE tipada; use EstadoDAVE.receber_mensagem_mls_tipada"
        )

    def processar_propostas(self, dados: bytes) -> bytes | None:
        resultado = self.sessao.process_proposals(bytes(dados), set(self._usuarios_reconhecidos))
        self._ultima_resposta_mls = bytes(resultado) if resultado else None
        return self._ultima_resposta_mls

    def processar_commit(self, dados: bytes) -> None:
        resultado = self.sessao.process_commit(bytes(dados))
        nome = getattr(resultado, "name", None)
        if nome == "failed":
            raise RuntimeError("libdave rejeitou o commit MLS")
        if isinstance(resultado, dict):
            self._atualizar_epoca()

    def processar_welcome(self, dados: bytes) -> None:
        resultado = self.sessao.process_welcome(bytes(dados), set(self._usuarios_reconhecidos))
        if resultado is not None:
            self._atualizar_epoca()

    def consumir_resposta_mls(self) -> bytes | None:
        resposta = self._ultima_resposta_mls
        self._ultima_resposta_mls = None
        return resposta

    def processar_mensagem_tipada(self, mensagem: MensagemMLSDAVE) -> None:
        self.definir_usuarios_reconhecidos(mensagem.usuarios_reconhecidos)
        if mensagem.tipo is TipoMensagemMLS.PROPOSTAS:
            self.processar_propostas(mensagem.dados)
        elif mensagem.tipo is TipoMensagemMLS.COMMIT:
            self.processar_commit(mensagem.dados)
        elif mensagem.tipo is TipoMensagemMLS.WELCOME:
            self.processar_welcome(mensagem.dados)
        else:
            raise ValueError(f"tipo MLS não suportado: {mensagem.tipo!r}")

    def preparar_epoca(self, epoca: int) -> None:
        if epoca < 1:
            raise ValueError("época DAVE deve ser positiva")
        self.epoca = int(epoca)
        if epoca == 1 and self.versao:
            self.sessao.reset()
            self.sessao.init(
                self.versao,
                int(self.grupo_id or 0),
                str(self.usuario_id or ""),
                self._chave_transitoria,
            )
        elif hasattr(self.sessao, "set_protocol_version") and self.versao:
            self.sessao.set_protocol_version(self.versao)

    def _atualizar_epoca(self) -> None:
        self.epoca = max(self.epoca, 1)

    def obter_ratchet_remetente(self, remetente_id: str) -> Any:
        """Obtém o handle opaco do libdave sem expor material secreto bruto."""
        if not self.sessao.has_established_group():
            raise RuntimeError("grupo MLS ainda não estabelecido")
        ratchet = self.sessao.get_key_ratchet(str(remetente_id))
        if ratchet is None:
            raise KeyError(f"nenhum ratchet para o remetente {remetente_id}")
        self._ratchet_remetente = str(remetente_id)
        return ratchet

    def exportar_chave_remetente(self, remetente_id: str) -> bytes:
        raise RuntimeError(
            "libdave mantém o ratchet opaco; use obter_ratchet_remetente "
            "ou cifrar_frame/decifrar_frame"
        )

    def preparar_ratchets(self) -> dict[str, Any]:
        if not self.sessao.has_established_group():
            raise RuntimeError("grupo MLS ainda não estabelecido")
        ids = set(self._usuarios_reconhecidos)
        if self.usuario_id:
            ids.add(self.usuario_id)
        ratchets: dict[str, Any] = {}
        for usuario_id in ids:
            ratchet = self.sessao.get_key_ratchet(usuario_id)
            if ratchet is None:
                raise RuntimeError(f"ratchet MLS ausente para o usuário {usuario_id}")
            ratchets[usuario_id] = ratchet
        return ratchets

    def configurar_midia(self, *, tipo: str, ssrc: int, codec: str) -> None:
        tipos = getattr(self.modulo, "MediaType", None)
        codecs = getattr(self.modulo, "Codec", None)
        if tipos is None or codecs is None:
            raise TypeError("dave.py não expõe MediaType e Codec")
        nome_tipo = "audio" if tipo.lower() == "audio" else "video" if tipo.lower() == "video" else None
        nome_codec = codec.lower()
        if nome_tipo is None or not hasattr(tipos, nome_tipo):
            raise ValueError("tipo de mídia DAVE deve ser audio ou video")
        if not hasattr(codecs, nome_codec):
            raise ValueError(f"codec DAVE não suportado pelo binding: {codec}")
        self._tipo_midia = getattr(tipos, nome_tipo)
        self._codec = getattr(codecs, nome_codec)
        self._ssrc = int(ssrc)
        self.encryptor.assign_ssrc_to_codec(self._ssrc, self._codec)

    def _exigir_contexto_midia(self) -> tuple[Any, int]:
        if self._tipo_midia is None or self._ssrc is None:
            raise RuntimeError("configure_midia deve ser chamado antes da transformação DAVE")
        return self._tipo_midia, self._ssrc

    def cifrar_frame(self, remetente_id: str, frame: bytes) -> bytes:
        tipo, ssrc = self._exigir_contexto_midia()
        ratchet = self.obter_ratchet_remetente(remetente_id)
        self.encryptor.set_key_ratchet(ratchet)
        resultado = self.encryptor.encrypt(tipo, ssrc, bytes(frame))
        if resultado is None:
            raise RuntimeError("libdave recusou a cifragem do frame")
        self._ratchet_remetente = str(remetente_id)
        return bytes(resultado)

    def decifrar_frame(self, remetente_id: str, frame: bytes) -> bytes:
        tipo, _ = self._exigir_contexto_midia()
        ratchet = self.obter_ratchet_remetente(remetente_id)
        self.decryptor.transition_to_key_ratchet(ratchet, timedelta(seconds=10))
        resultado = self.decryptor.decrypt(tipo, bytes(frame))
        if resultado is None:
            raise RuntimeError("libdave recusou a decifragem do frame")
        return bytes(resultado)

    def autenticador_epoca(self, epoca: int, dados: bytes) -> bytes:
        autenticador = self.sessao.get_last_epoch_authenticator()
        if int(epoca) != self.epoca or not autenticador:
            raise RuntimeError("autenticador da época não está disponível")
        return bytes(autenticador)


__all__ = ["AdaptadorDAVEPy"]

# O binding nativo não é importado no carregamento do módulo.
