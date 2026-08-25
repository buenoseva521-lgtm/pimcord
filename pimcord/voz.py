"""Transporte e sessão de voz do Pimcord.

A camada é assíncrona, modular e testável sem rede. O codec e a criptografia são
injetáveis para permitir suporte opcional a Opus, AEAD e DAVE sem obrigar
FFmpeg ou dependências nativas em ambientes móveis.
"""
from __future__ import annotations

import asyncio
import json
import logging
import random
import struct
import time
import wave
from dataclasses import dataclass, field
from typing import Any, Protocol


class CodificadorAudio(Protocol):
    def codificar(self, pcm: bytes) -> bytes: ...


class CriptografadorVoz(Protocol):
    def cifrar(self, dados: bytes, nonce: bytes) -> bytes: ...


@dataclass(slots=True)
class InformacoesVoz:
    servidor_id: str
    usuario_id: str
    sessao_id: str
    token: str
    endpoint: str
    ssrc: int | None = None
    ip: str | None = None
    porta: int | None = None
    modos: list[str] = field(default_factory=list)
    intervalo_heartbeat: float = 5.0
    sequencia_ack: int = 0
    chave_secreta: bytes | None = None
    modo_selecionado: str | None = None

    @classmethod
    def de_pronto(cls, servidor_id: str, usuario_id: str, sessao_id: str, token: str, dados: dict[str, Any]) -> "InformacoesVoz":
        return cls(
            servidor_id=servidor_id,
            usuario_id=usuario_id,
            sessao_id=sessao_id,
            token=token,
            endpoint=str(dados.get("endpoint", "")),
            ssrc=dados.get("ssrc"),
            ip=dados.get("ip"),
            porta=dados.get("port", dados.get("porta")),
            modos=list(dados.get("modes", dados.get("modos", []))),
            intervalo_heartbeat=float(dados.get("heartbeat_interval", 5000)) / 1000,
        )


@dataclass(slots=True)
class PacoteRTP:
    sequencia: int
    timestamp: int
    ssrc: int
    carga: bytes
    tipo_carga: int = 120
    marcador: bool = False

    def serializar(self) -> bytes:
        primeiro = 0x80
        segundo = (0x80 if self.marcador else 0) | (self.tipo_carga & 0x7F)
        cabecalho = struct.pack(">BBHII", primeiro, segundo, self.sequencia & 0xFFFF, self.timestamp & 0xFFFFFFFF, self.ssrc & 0xFFFFFFFF)
        return cabecalho + self.carga

    @classmethod
    def desserializar(cls, dados: bytes) -> "PacoteRTP":
        if len(dados) < 12:
            raise ValueError("Pacote RTP menor que o cabeçalho mínimo")
        primeiro, segundo, sequencia, timestamp, ssrc = struct.unpack(">BBHII", dados[:12])
        if primeiro >> 6 != 2:
            raise ValueError("Versão RTP incompatível")
        csrc = primeiro & 0x0F
        extensao = bool(primeiro & 0x10)
        deslocamento = 12 + csrc * 4
        if len(dados) < deslocamento:
            raise ValueError("Pacote RTP truncado nos identificadores CSRC")
        if extensao:
            if len(dados) < deslocamento + 4:
                raise ValueError("Extensão RTP truncada")
            _, tamanho = struct.unpack(">HH", dados[deslocamento:deslocamento + 4])
            deslocamento += 4 + tamanho * 4
        if len(dados) < deslocamento:
            raise ValueError("Pacote RTP truncado na extensão")
        return cls(sequencia, timestamp, ssrc, dados[deslocamento:], segundo & 0x7F, bool(segundo & 0x80))


class BufferJitter:
    """Ordena pacotes RTP recebidos e descarta duplicatas fora da janela."""
    def __init__(self, *, capacidade: int = 64):
        if capacidade < 2:
            raise ValueError("capacidade do buffer deve ser pelo menos 2")
        self.capacidade = capacidade
        self._pacotes: dict[int, PacoteRTP] = {}
        self._proximo: int | None = None
        self.descartados = 0

    @property
    def pendentes(self) -> int:
        return len(self._pacotes)

    def inserir(self, pacote: PacoteRTP) -> list[PacoteRTP]:
        if self._proximo is None:
            self._proximo = pacote.sequencia
        if pacote.sequencia in self._pacotes or self._distancia(pacote.sequencia, self._proximo) >= 0x8000:
            self.descartados += 1
            return []
        self._pacotes[pacote.sequencia] = pacote
        liberados: list[PacoteRTP] = []
        while self._proximo in self._pacotes:
            liberados.append(self._pacotes.pop(self._proximo))
            self._proximo = (self._proximo + 1) & 0xFFFF
        while len(self._pacotes) > self.capacidade:
            mais_antigo = min(self._pacotes, key=lambda seq: self._distancia(seq, self._proximo or 0))
            self._pacotes.pop(mais_antigo)
            self.descartados += 1
        return liberados

    def avançar_sequencia(self, sequencia: int) -> int:
        """Descarta lacunas até ``sequencia`` e retorna quantos pacotes faltaram.

        O método é deliberadamente explícito: ele não cria PCM, não interpola e não
        altera o conteúdo de áudio. O pipeline pode chamá-lo após um timeout próprio.
        """
        sequencia &= 0xFFFF
        if self._proximo is None:
            self._proximo = sequencia
            return 0
        distancia = self._distancia(sequencia, self._proximo)
        if distancia >= 0x8000:
            return 0
        perdidos = distancia
        self._pacotes = {seq: pacote for seq, pacote in self._pacotes.items() if self._distancia(seq, sequencia) < 0x8000}
        self._proximo = sequencia
        self.descartados += perdidos
        return perdidos

    @staticmethod
    def _distancia(atual: int, base: int) -> int:
        return (atual - base) & 0xFFFF


class TransporteUDP(asyncio.DatagramProtocol):
    """Transporte UDP de voz com estado observável e injeção de socket."""

    def __init__(self, ao_receber: Any = None):
        self.ao_receber = ao_receber
        self.transporte: asyncio.DatagramTransport | None = None
        self.erro: Exception | None = None
        self.recebidos = 0

    def connection_made(self, transporte: asyncio.BaseTransport) -> None:
        self.transporte = transporte  # type: ignore[assignment]

    def datagram_received(self, dados: bytes, endereco: tuple[str, int]) -> None:
        self.recebidos += 1
        if self.ao_receber:
            resultado = self.ao_receber(dados, endereco)
            if asyncio.iscoroutine(resultado):
                asyncio.create_task(resultado)

    def error_received(self, erro: Exception) -> None:
        self.erro = erro

    def connection_lost(self, erro: Exception | None) -> None:
        if erro:
            self.erro = erro
        self.transporte = None

    def enviar(self, dados: bytes, endereco: tuple[str, int]) -> None:
        if not self.transporte:
            raise RuntimeError("Transporte UDP de voz não está conectado")
        self.transporte.sendto(dados, endereco)

    def fechar(self) -> None:
        if self.transporte:
            self.transporte.close()


class SessaoVoz:
    """Orquestra uma sessão de voz sem esconder estados de protocolo."""

    def __init__(self, bot: Any, servidor_id: str, usuario_id: str, token: str | None = None):
        self.bot = bot
        self.servidor_id = str(servidor_id)
        self.usuario_id = str(usuario_id)
        self.token = token or getattr(getattr(bot, "configuracao", None), "token", "")
        self.logger = logging.getLogger("pimcord.voz")
        self.estado = "desconectada"
        self.informacoes: InformacoesVoz | None = None
        self.transporte_udp: TransporteUDP | None = None
        self._heartbeat: asyncio.Task[None] | None = None
        self._parar = asyncio.Event()
        self._sequencia = random.randrange(0, 65536)
        self._timestamp = random.randrange(0, 2**32)
        self._modo: str | None = None
        self._endereco: tuple[str, int] | None = None
        self.buffer_jitter = BufferJitter()
        self._adaptador_dave: Any | None = None
        self._sessao_gateway_id: str | None = None
        self.gateway_voz: ClienteGatewayVoz | None = None
        self._tarefa_gateway_voz: asyncio.Task[None] | None = None

    def ativar_dave(self, backend: Any, *, codec: str = "opus") -> Any:
        """Ativa DAVE somente com um backend E2EE semanticamente validado."""
        from .dave import exigir_backend_dave_real

        self._adaptador_dave = exigir_backend_dave_real(backend)
        if self.informacoes and self.informacoes.ssrc is not None:
            configurar = getattr(self._adaptador_dave, "configurar_midia", None)
            if callable(configurar):
                configurar(tipo="audio", ssrc=int(self.informacoes.ssrc), codec=codec)
        return self._adaptador_dave

    @property
    def dave_ativo(self) -> bool:
        return self._adaptador_dave is not None

    @property
    def conectada(self) -> bool:
        return self.estado == "conectada"

    @property
    def modo_criptografia(self) -> str | None:
        return self._modo

    async def entrar(self, canal_id: str, *, auto_mudo: bool = False, auto_surdo: bool = False) -> None:
        """Solicita entrada no canal pelo Gateway principal."""
        gateway = getattr(self.bot, "gateway", None)
        if gateway is None or gateway.ws is None:
            raise RuntimeError("O Gateway principal precisa estar conectado antes de entrar em voz")
        self.estado = "solicitando"
        await gateway.ws.send_json({"op": 4, "d": {"guild_id": self.servidor_id, "channel_id": str(canal_id), "self_mute": auto_mudo, "self_deaf": auto_surdo}})
        self.logger.info("Solicitada entrada no canal de voz %s do servidor %s", canal_id, self.servidor_id)

    def preparar_servidor(self, dados: dict[str, Any], sessao_id: str) -> InformacoesVoz:
        endpoint = str(dados.get("endpoint", ""))
        if not endpoint:
            raise ValueError("VOICE_SERVER_UPDATE não contém endpoint")
        self.informacoes = InformacoesVoz.de_pronto(self.servidor_id, self.usuario_id, sessao_id, str(dados.get("token", self.token)), dados)
        self.estado = "servidor_recebido"
        return self.informacoes

    async def preparar_udp(self, *, ip: str, porta: int, loop: asyncio.AbstractEventLoop | None = None) -> TransporteUDP:
        loop = loop or asyncio.get_running_loop()
        protocolo = TransporteUDP()
        transporte, _ = await loop.create_datagram_endpoint(lambda: protocolo, remote_addr=(ip, porta))
        protocolo.transporte = transporte
        self.transporte_udp = protocolo
        self.estado = "udp_conectada"
        self._endereco = (ip, int(porta))
        return protocolo

    async def descobrir_ip(self, *, timeout: float = 5.0) -> tuple[str, int]:
        """Executa o IP Discovery do protocolo UDP de voz."""
        if not self.transporte_udp or not self._endereco or not self.informacoes or self.informacoes.ssrc is None:
            raise RuntimeError("UDP, endpoint e SSRC são necessários para IP Discovery")
        pacote = bytearray(70)
        struct.pack_into(">HHI", pacote, 0, 1, 70, int(self.informacoes.ssrc))
        loop = asyncio.get_running_loop()
        futuro: asyncio.Future[tuple[str, int]] = loop.create_future()
        transporte = self.transporte_udp
        anterior = transporte.ao_receber
        def receber(dados: bytes, _endereco: tuple[str, int]) -> None:
            if len(dados) < 70 or futuro.done():
                return
            fim = dados.find(b"\x00", 8)
            endereco = dados[8:fim if fim >= 0 else 72].decode("ascii", "ignore")
            porta = struct.unpack_from(">H", dados, 68)[0]
            futuro.set_result((endereco, porta))
        transporte.ao_receber = receber
        try:
            transporte.enviar(bytes(pacote), self._endereco)
            endereco, porta = await asyncio.wait_for(futuro, timeout=timeout)
            self.estado = "ip_descoberto"
            return endereco, porta
        finally:
            transporte.ao_receber = anterior

    def selecionar_modo(self, preferidos: tuple[str, ...] = ("aead_xchacha20_poly1305_rtpsize", "aead_aes256_gcm_rtpsize", "xsalsa20_poly1305_lite_rtpsize", "xsalsa20_poly1305_lite")) -> str:
        if not self.informacoes:
            raise RuntimeError("As informações READY de voz ainda não foram recebidas")
        self._modo = next((modo for modo in preferidos if modo in self.informacoes.modos), None)
        if not self._modo:
            raise RuntimeError(f"Nenhum modo de voz compatível: {self.informacoes.modos!r}")
        return self._modo

    def construir_select_protocol(self, *, endereco: str, porta: int, modo: str | None = None) -> dict[str, Any]:
        modo = modo or self._modo or self.selecionar_modo()
        return {"op": 1, "d": {"protocol": "udp", "data": {"address": endereco, "port": int(porta), "mode": modo}}}

    async def iniciar_heartbeat(self, enviar: Any, intervalo: float | None = None) -> None:
        if self._heartbeat:
            self._heartbeat.cancel()
        intervalo = intervalo or (self.informacoes.intervalo_heartbeat if self.informacoes else 5.0)
        self._parar.clear()

        async def ciclo() -> None:
            await asyncio.sleep(random.random() * intervalo)
            while not self._parar.is_set():
                pacote = {"op": 3, "d": {"t": int(time.time() * 1000), "seq_ack": self.informacoes.sequencia_ack if self.informacoes else 0}}
                resultado = enviar(pacote)
                if asyncio.iscoroutine(resultado):
                    await resultado
                try:
                    await asyncio.wait_for(self._parar.wait(), timeout=intervalo)
                except asyncio.TimeoutError:
                    pass

        self._heartbeat = asyncio.create_task(ciclo())

    def receber_audio(self, dados: bytes, *, decodificador: Any = None, gravador: Any = None, processador: Any = None, remetente_id: str | None = None) -> list[bytes]:
        """Recebe RTP, ordena pela sequência e decodifica a carga quando solicitado.

        A função é síncrona para poder ser usada diretamente pelo protocolo UDP.
        Interpolação e mistura de canais permanecem responsabilidades posteriores do
        pipeline de áudio, não são simuladas aqui.
        """
        pacote = PacoteRTP.desserializar(dados)
        prontos = self.buffer_jitter.inserir(pacote)
        cargas = [item.carga for item in prontos]
        if self._adaptador_dave is not None:
            if remetente_id is None:
                raise RuntimeError("remetente_id é obrigatório para decifrar mídia DAVE")
            cargas = [self._adaptador_dave.decifrar_frame(remetente_id, carga) for carga in cargas]
        if decodificador is not None:
            cargas = [decodificador.decodificar(carga) for carga in cargas]
        if processador is not None:
            return processador.processar(cargas, gravador=gravador)
        if gravador is not None:
            for carga in cargas:
                gravador.escrever(carga)
        return cargas

    def construir_audio(self, carga: bytes, *, marcador: bool = False, tipo_carga: int = 120, criptografador: CriptografadorVoz | None = None) -> bytes:
        if not self.informacoes or self.informacoes.ssrc is None:
            raise RuntimeError("SSRC de voz ainda não foi recebido")
        if self._adaptador_dave is not None:
            carga = self._adaptador_dave.cifrar_frame(self.usuario_id, bytes(carga))
        pacote = PacoteRTP(self._sequencia, self._timestamp, int(self.informacoes.ssrc), carga, tipo_carga, marcador)
        bruto = pacote.serializar()
        if criptografador is not None:
            cabecalho, carga_bruta = bruto[:12], bruto[12:]
            cifrar_pacote = getattr(criptografador, "cifrar_pacote", None)
            if cifrar_pacote is not None:
                carga_cifrada = cifrar_pacote(cabecalho, carga_bruta, contador=self._sequencia)
            else:
                carga_cifrada = criptografador.cifrar(carga_bruta, cabecalho[:12])
            bruto = cabecalho + carga_cifrada
        self._sequencia = (self._sequencia + 1) & 0xFFFF
        self._timestamp = (self._timestamp + 960) & 0xFFFFFFFF
        return bruto

    def enviar_audio(self, carga: bytes, *, criptografador: CriptografadorVoz | None = None) -> None:
        if not self.transporte_udp or not self._endereco:
            raise RuntimeError("UDP de voz ainda não foi preparado")
        self.transporte_udp.enviar(self.construir_audio(carga, criptografador=criptografador), self._endereco)

    async def sair(self) -> None:
        self._parar.set()
        if self._tarefa_gateway_voz:
            self._tarefa_gateway_voz.cancel()
            self._tarefa_gateway_voz = None
        if self.gateway_voz:
            await self.gateway_voz.fechar()
            self.gateway_voz = None
        if self._heartbeat:
            self._heartbeat.cancel()
            self._heartbeat = None
        if self.transporte_udp:
            self.transporte_udp.fechar()
            self.transporte_udp = None
        self.estado = "desconectada"
        gateway = getattr(self.bot, "gateway", None)
        if gateway and gateway.ws:
            await gateway.ws.send_json({"op": 4, "d": {"guild_id": self.servidor_id, "channel_id": None, "self_mute": False, "self_deaf": False}})


__all__ = ["CodificadorAudio", "CriptografadorVoz", "InformacoesVoz", "PacoteRTP", "TransporteUDP", "SessaoVoz"]


class ClienteGatewayVoz:
    """Cliente WebSocket do Voice Gateway com dependência HTTP injetável."""

    def __init__(self, sessao: SessaoVoz, sessao_http: Any = None):
        self.sessao = sessao
        self.sessao_http = sessao_http
        self.ws: Any = None
        self.logger = logging.getLogger("pimcord.voz.gateway")
        self.sequencia = 0
        self.pronto = False
        self._protocolo_selecionado = False

    async def conectar(self) -> None:
        import aiohttp
        if not self.sessao.informacoes:
            raise RuntimeError("As informações do servidor de voz ainda não foram preparadas")
        endpoint = self.sessao.informacoes.endpoint
        if not endpoint.startswith("ws"):
            endpoint = "wss://" + endpoint
        sessao_http = self.sessao_http or aiohttp.ClientSession()
        self._sessao_http_interna = self.sessao_http is None
        self._sessao_http = sessao_http
        self.ws = await sessao_http.ws_connect(endpoint + "?v=8&encoding=json")
        await self.ws.send_json({"op": 0, "d": {"server_id": self.sessao.servidor_id, "user_id": self.sessao.usuario_id, "session_id": self.sessao.informacoes.sessao_id, "token": self.sessao.informacoes.token, "max_dave_protocol_version": 1}})
        self.logger.info("Voice Gateway conectado ao servidor %s", self.sessao.servidor_id)

    async def processar_binario(self, dados: bytes) -> None:
        """Processa uma mensagem binária oficial do Voice Gateway.

        O envelope é decodificado localmente; payloads MLS permanecem opacos e
        só são encaminhados a métodos semânticos explícitos do backend. Assim,
        bytes incompletos ou um backend sem capacidade real não são aceitos como
        uma transição válida.
        """
        from .dave import MensagemDAVE, OpcodeDAVE

        if self.sessao._adaptador_dave is None:
            raise RuntimeError("Mensagem DAVE recebida sem backend DAVE ativo")
        mensagem = MensagemDAVE.desserializar(dados, tem_sequencia=True)
        backend = self.sessao._adaptador_dave
        if mensagem.opcode is OpcodeDAVE.REMETENTE_EXTERNO:
            metodo = getattr(backend, "processar_remetente_externo", None)
            if not callable(metodo):
                raise TypeError("backend DAVE não processa external sender")
            metodo(mensagem.payload)
        elif mensagem.opcode is OpcodeDAVE.PROPOSTAS:
            backend.processar_propostas(mensagem.payload)
        elif mensagem.opcode is OpcodeDAVE.ANUNCIAR_COMMIT:
            backend.processar_commit(mensagem.payload)
        elif mensagem.opcode is OpcodeDAVE.WELCOME:
            backend.processar_welcome(mensagem.payload)
        else:
            metodo = getattr(backend, "processar_evento_dave", None)
            if not callable(metodo):
                raise TypeError(f"backend DAVE não processa opcode {int(mensagem.opcode)}")
            metodo(int(mensagem.opcode), mensagem.payload, mensagem.sequencia)

    async def enviar_binario_dave(self, dados: bytes) -> None:
        if not self.ws:
            raise RuntimeError("Voice Gateway não está conectado")
        from .dave import MensagemDAVE
        MensagemDAVE.desserializar(dados, tem_sequencia=False)
        await self.ws.send_bytes(dados)

    async def _completar_udp(self) -> None:
        """Completa o handshake UDP oficial depois do Voice Ready."""
        if self._protocolo_selecionado:
            return
        informacoes = self.sessao.informacoes
        if informacoes is None or informacoes.ip is None or informacoes.porta is None:
            raise RuntimeError("Voice Ready sem IP/porta para UDP")
        await self.sessao.preparar_udp(ip=str(informacoes.ip), porta=int(informacoes.porta))
        endereco, porta = await self.sessao.descobrir_ip()
        await self.enviar(self.sessao.construir_select_protocol(endereco=endereco, porta=porta))
        self._protocolo_selecionado = True
        self.sessao.estado = "protocolo_selecionado"

    async def processar(self, pacote: dict[str, Any]) -> None:
        if pacote.get("s") is not None:
            self.sequencia = int(pacote["s"])
            if self.sessao.informacoes:
                self.sessao.informacoes.sequencia_ack = self.sequencia
        op, dados = pacote.get("op"), pacote.get("d") or {}
        if op == 2:
            if self.sessao.informacoes:
                self.sessao.informacoes.ssrc = dados.get("ssrc")
                self.sessao.informacoes.ip = dados.get("ip")
                self.sessao.informacoes.porta = dados.get("port")
                self.sessao.informacoes.modos = list(dados.get("modes", []))
                self.sessao.informacoes.intervalo_heartbeat = float(dados.get("heartbeat_interval", 5000)) / 1000
                if self.sessao._adaptador_dave is not None and self.sessao.informacoes.ssrc is not None:
                    configurar = getattr(self.sessao._adaptador_dave, "configurar_midia", None)
                    if callable(configurar):
                        configurar(tipo="audio", ssrc=int(self.sessao.informacoes.ssrc), codec="opus")
            self.sessao.estado = "pronta_udp"
            self.sessao.selecionar_modo()
            if self.sessao.informacoes and self.sessao.informacoes.ip and self.sessao.informacoes.porta:
                await self._completar_udp()
        elif op == 8:
            await self.sessao.iniciar_heartbeat(self.enviar, float(dados.get("heartbeat_interval", 5000)) / 1000)
        elif op == 6:
            self.logger.debug("Heartbeat de voz confirmado")
        elif op == 4:
            chave = dados.get("secret_key")
            if not isinstance(chave, (bytes, bytearray, list)) or not chave:
                raise ValueError("SESSION_DESCRIPTION sem secret_key válido")
            self.sessao.informacoes.chave_secreta = bytes(chave)
            modo = dados.get("mode")
            if modo:
                self.sessao.informacoes.modo_selecionado = str(modo)
                self.sessao._modo = str(modo)
            self.pronto = True
            self.sessao.estado = "conectada"

    async def executar(self, *, maximo_tentativas: int | None = None) -> None:
        tentativa = 0
        while not self.sessao._parar.is_set():
            try:
                await self.conectar()
                tentativa = 0
                async for mensagem in self.ws:
                    if getattr(mensagem, "type", None) == 1:
                        await self.processar(json.loads(mensagem.data))
                    elif getattr(mensagem, "type", None) == 2:
                        await self.processar_binario(bytes(mensagem.data))
                    elif getattr(mensagem, "type", None) in (8, 258):
                        break
            except asyncio.CancelledError:
                raise
            except Exception as erro:
                tentativa += 1
                self.logger.warning("Voice Gateway desconectado: %s", erro)
                if maximo_tentativas is not None and tentativa >= maximo_tentativas:
                    raise
                await asyncio.sleep(min(60.0, 2 ** min(tentativa, 6)))
            finally:
                if self.ws:
                    await self.ws.close()
                    self.ws = None

    async def enviar(self, pacote: dict[str, Any]) -> None:
        if not self.ws:
            raise RuntimeError("Voice Gateway não está conectado")
        await self.ws.send_json(pacote)

    async def selecionar_protocolo(self, cliente: "ClienteGatewayVoz" | None = None, *, endereco: str, porta: int) -> None:
        """Envia Select Protocol; `cliente` permanece por compatibilidade antiga."""
        enviar = cliente.enviar if cliente is not None else self.enviar
        await enviar(self.sessao.construir_select_protocol(endereco=endereco, porta=porta))
        self._protocolo_selecionado = True
        self.sessao.estado = "protocolo_selecionado"

    async def sinalizar_fala(self, falando: bool, *, prioridade: int = 0) -> None:
        await self.enviar({"op": 5, "d": {"speaking": 1 if falando else 0, "delay": 0, "ssrc": self.sessao.informacoes.ssrc if self.sessao.informacoes else 0, "priority": prioridade}})

    async def fechar(self) -> None:
        if self.ws:
            await self.ws.close()
            self.ws = None
        if getattr(self, "_sessao_http_interna", False):
            await self._sessao_http.close()


__all__ = ["CodificadorAudio", "CriptografadorVoz", "InformacoesVoz", "PacoteRTP", "TransporteUDP", "SessaoVoz", "ClienteGatewayVoz"]


class FonteAudio(Protocol):
    async def proximo_quadro(self) -> bytes | None: ...


class FontePCM:
    def __init__(self, dados: bytes, *, tamanho_quadro: int = 3840):
        self.dados = dados
        self.tamanho_quadro = tamanho_quadro
        self.posicao = 0

    async def proximo_quadro(self) -> bytes | None:
        if self.posicao >= len(self.dados):
            return None
        quadro = self.dados[self.posicao:self.posicao + self.tamanho_quadro]
        self.posicao += len(quadro)
        return quadro


class FonteSilencio:
    def __init__(self, quadros: int | None = None, *, tamanho_quadro: int = 3840):
        self.quadros = quadros
        self.tamanho_quadro = tamanho_quadro

    async def proximo_quadro(self) -> bytes | None:
        if self.quadros is not None:
            if self.quadros <= 0:
                return None
            self.quadros -= 1
        return bytes(self.tamanho_quadro)


class FilaAudio:
    """Fila limitada que evita explodir a memória durante reprodução."""

    def __init__(self, limite: int = 128):
        self.fila: asyncio.Queue[FonteAudio | None] = asyncio.Queue(maxsize=limite)
        self.limite = limite
        self.quadros_enviados = 0
        self.bytes_enviados = 0
        self.iniciada_em: float | None = None

    async def adicionar(self, fonte: FonteAudio) -> None:
        await self.fila.put(fonte)

    async def parar(self) -> None:
        await self.fila.put(None)

    async def reproduzir(self, sessao: SessaoVoz, *, intervalo: float = 0.02, codificador: CodificadorAudio | None = None) -> None:
        self.iniciada_em = time.monotonic()
        while True:
            fonte = await self.fila.get()
            if fonte is None:
                return
            while True:
                quadro = await fonte.proximo_quadro()
                if quadro is None:
                    break
                carga = codificador.codificar(quadro) if codificador else quadro
                sessao.enviar_audio(carga)
                self.quadros_enviados += 1
                self.bytes_enviados += len(carga)
                await asyncio.sleep(intervalo)

    @property
    def duracao_aproximada(self) -> float:
        return self.quadros_enviados * 0.02


__all__ = ["CodificadorAudio", "CriptografadorVoz", "InformacoesVoz", "PacoteRTP", "TransporteUDP", "SessaoVoz", "ClienteGatewayVoz", "FonteAudio", "FontePCM", "FonteSilencio", "FilaAudio"]


class CodificadorIdentidade:
    """Codec simples para transporte de PCM em simuladores e testes."""
    def codificar(self, pcm: bytes) -> bytes:
        return pcm


class FonteWAV:
    """Fonte WAV baseada apenas na biblioteca padrão do Python."""
    def __init__(self, caminho: str, *, tamanho_quadro: int = 3840):
        import wave
        self._arquivo = wave.open(caminho, "rb")
        self.tamanho_quadro = tamanho_quadro
        self.canais = self._arquivo.getnchannels()
        self.amostragem = self._arquivo.getframerate()
        self.amostras = self._arquivo.getsampwidth()

    async def proximo_quadro(self) -> bytes | None:
        quadro = self._arquivo.readframes(max(1, self.tamanho_quadro // max(1, self.canais * self.amostras)))
        return quadro or None

    def fechar(self) -> None:
        self._arquivo.close()


class GravadorWAV:
    """Gravador WAV PCM leve, útil para testes e bots móveis."""
    def __init__(self, caminho: str, *, canais: int = 2, amostragem: int = 48000, bytes_amostra: int = 2):
        import wave
        self._arquivo = wave.open(caminho, "wb")
        self._arquivo.setnchannels(canais)
        self._arquivo.setframerate(amostragem)
        self._arquivo.setsampwidth(bytes_amostra)
        self.quadros = 0

    def escrever(self, dados: bytes) -> None:
        self._arquivo.writeframesraw(dados)
        self.quadros += len(dados)

    def fechar(self) -> None:
        self._arquivo.close()


class InterpoladorPCM:
    """Interpola linearmente dois quadros PCM 16-bit conhecidos.

    A classe não decide quando uma perda deve ser preenchida. O aplicativo deve
    fornecer os quadros vizinhos e a posição intermediária explicitamente.
    """

    def __init__(self, *, bytes_amostra: int = 2):
        if bytes_amostra != 2:
            raise ValueError("InterpoladorPCM suporta apenas PCM assinado de 16 bits")
        self.bytes_amostra = bytes_amostra

    def interpolar(self, inicio: bytes, fim: bytes, *, passo: int, total_passos: int) -> bytes:
        if total_passos < 2 or not 1 <= passo < total_passos:
            raise ValueError("passo deve estar entre 1 e total_passos - 1")
        if len(inicio) != len(fim) or len(inicio) % self.bytes_amostra:
            raise ValueError("quadros PCM precisam ter o mesmo tamanho e amostras completas")
        quantidade = len(inicio) // 2
        amostras_inicio = struct.unpack("<" + "h" * quantidade, inicio)
        amostras_fim = struct.unpack("<" + "h" * quantidade, fim)
        valores = []
        for esquerdo, direito in zip(amostras_inicio, amostras_fim):
            valor = esquerdo + (direito - esquerdo) * passo / total_passos
            valores.append(max(-32768, min(32767, round(valor))))
        return struct.pack("<" + "h" * quantidade, *valores)


class ProcessadorPCMRecebido:
    """Etapa explícita para frames PCM já ordenados pelo recebedor RTP.

    O processador nunca decide perdas sozinho. O chamador escolhe se deseja
    misturar o lote ou interpolar uma lacuna com quadros vizinhos conhecidos.
    """

    def __init__(self, *, misturador: "MisturadorPCM | None" = None, interpolador: "InterpoladorPCM | None" = None):
        self.misturador = misturador or MisturadorPCM()
        self.interpolador = interpolador or InterpoladorPCM()

    def processar(self, quadros: list[bytes] | tuple[bytes, ...], *, misturar: bool = False, gravador: Any = None) -> list[bytes]:
        saida = [bytes(quadro) for quadro in quadros]
        if misturar and saida:
            saida = [self.misturador.misturar(saida)]
        if gravador is not None:
            for quadro in saida:
                gravador.escrever(quadro)
        return saida

    def preencher_lacuna(self, inicio: bytes, fim: bytes, *, passo: int, total_passos: int) -> bytes:
        return self.interpolador.interpolar(inicio, fim, passo=passo, total_passos=total_passos)


class MisturadorPCM:
    """Mistura quadros PCM little-endian assinados com saturação.

    O mixador exige a mesma largura de amostra e não preenche perdas. Quadros
    ausentes devem ser tratados pela política de perdas antes desta etapa.
    """

    def __init__(self, *, bytes_amostra: int = 2):
        if bytes_amostra != 2:
            raise ValueError("MisturadorPCM suporta apenas PCM assinado de 16 bits")
        self.bytes_amostra = bytes_amostra

    def misturar(self, quadros: list[bytes] | tuple[bytes, ...]) -> bytes:
        if not quadros:
            return b""
        tamanho = len(quadros[0])
        if tamanho % self.bytes_amostra:
            raise ValueError("Quadro PCM precisa conter amostras completas")
        if any(len(quadro) != tamanho for quadro in quadros):
            raise ValueError("Todos os quadros PCM precisam ter o mesmo tamanho")
        amostras = [0] * (tamanho // self.bytes_amostra)
        for quadro in quadros:
            valores = struct.unpack("<" + "h" * (tamanho // 2), quadro)
            for indice, valor in enumerate(valores):
                amostras[indice] += valor
        quantidade = len(quadros)
        normalizadas = [max(-32768, min(32767, round(valor / quantidade))) for valor in amostras]
        return struct.pack("<" + "h" * len(normalizadas), *normalizadas)


__all__ = ["CodificadorAudio", "CriptografadorVoz", "CodificadorIdentidade", "InformacoesVoz", "PacoteRTP", "BufferJitter", "TransporteUDP", "SessaoVoz", "ClienteGatewayVoz", "FonteAudio", "FontePCM", "FonteSilencio", "FonteWAV", "GravadorWAV", "InterpoladorPCM", "MisturadorPCM", "ProcessadorPCMRecebido", "FilaAudio"]


class CodificadorOpus:
    """Codec Opus real com backend nativo e compatibilidade opuslib.

    O backend ctypes não exige `opuslib`, o que reduz a superfície de instalação
    em Linux e permite que ambientes móveis escolham explicitamente seu backend.
    """
    def __init__(self, *, amostragem: int = 48000, canais: int = 2, bitrate: int = 128000, backend: str = "automatico"):
        from .opus import CodecOpus, OpusIndisponivel
        self._backend = None
        if backend.lower() in {"automatico", "nativo", "ctypes"}:
            try:
                self._backend = CodecOpus(taxa=amostragem, canais=canais, frame_size=960, bitrate=bitrate)
            except OpusIndisponivel:
                if backend.lower() != "automatico":
                    raise
        if self._backend is None:
            try:
                import opuslib
            except ImportError as erro:
                raise RuntimeError("Codec Opus indisponível: instale libopus ou opuslib com sua biblioteca nativa") from erro
            self._backend = opuslib.Encoder(amostragem, canais, opuslib.APPLICATION_AUDIO)
            self._backend.bitrate = bitrate
        self.amostragem = amostragem
        self.canais = canais

    def codificar(self, pcm: bytes) -> bytes:
        return self._backend.codificar(pcm) if hasattr(self._backend, "codificar") else self._backend.encode(pcm, 960)

    def decodificar(self, pacote: bytes, *, frame_size: int = 960) -> bytes:
        if not hasattr(self._backend, "decodificar"):
            raise RuntimeError("O backend opuslib selecionado não oferece decodificação por este adaptador")
        return self._backend.decodificar(pacote, frame_size=frame_size)

    def fechar(self) -> None:
        if hasattr(self._backend, "fechar"):
            self._backend.fechar()


class CriptografiaVozOpcional:
    """Cifras opcionais reais; nunca rotula uma cifra incompatível como XChaCha20/DAVE."""
    def __init__(self, modo: str, chave: bytes):
        self.modo = modo.lower()
        self.chave = chave
        self._cifra = None
        self._secretbox = None
        if "aes" in self.modo:
            try:
                from cryptography.hazmat.primitives.ciphers.aead import AESGCM
                if len(chave) != 32:
                    raise ValueError("AES-256-GCM exige uma chave de 32 bytes")
                self._cifra = AESGCM(chave)
            except ImportError as erro:
                raise RuntimeError("AES-GCM exige a dependência opcional cryptography") from erro
        elif self.modo in {"xsalsa20_poly1305_lite", "xsalsa20_poly1305_lite_rtpsize"}:
            try:
                from nacl.secret import SecretBox
                if len(chave) != SecretBox.KEY_SIZE:
                    raise ValueError("XSalsa20-Poly1305 exige uma chave de 32 bytes")
                self._secretbox = SecretBox(chave)
            except ImportError as erro:
                raise RuntimeError("XSalsa20-Poly1305 exige a dependência opcional PyNaCl") from erro
        else:
            raise RuntimeError(f"Modo de criptografia '{modo}' exige um adaptador compatível injetado")

    def cifrar(self, dados: bytes, nonce: bytes) -> bytes:
        if self._cifra is not None:
            return self._cifra.encrypt(nonce[:12], dados, None)
        if self._secretbox is not None:
            if len(nonce) != 24:
                raise ValueError("XSalsa20-Poly1305 exige nonce de 24 bytes")
            return self._secretbox.encrypt(dados, nonce).ciphertext
        raise RuntimeError("Nenhum backend de criptografia foi inicializado")

    def cifrar_pacote(self, cabecalho_rtp: bytes, carga: bytes, *, contador: int = 0) -> bytes:
        """Cifra uma carga RTP usando o nonce exigido pelo modo escolhido."""
        if self.modo == "xsalsa20_poly1305_lite":
            nonce = b"\x00" * 20 + struct.pack("<I", contador & 0xFFFFFFFF)
            return self.cifrar(carga, nonce)
        if self.modo == "xsalsa20_poly1305_lite_rtpsize":
            nonce = b"\x00" * 20 + struct.pack("<I", contador & 0xFFFFFFFF)
            return self.cifrar(carga, nonce) + struct.pack("<I", contador & 0xFFFFFFFF)
        if "aes" in self.modo:
            nonce = (cabecalho_rtp + b"\x00" * 12)[:12]
            return self.cifrar(carga, nonce)
        raise RuntimeError("Este modo requer um adaptador de pacote específico")


__all__ = ["CodificadorAudio", "CriptografadorVoz", "CodificadorIdentidade", "CodificadorOpus", "CriptografiaVozOpcional", "InformacoesVoz", "PacoteRTP", "BufferJitter", "TransporteUDP", "SessaoVoz", "ClienteGatewayVoz", "FonteAudio", "FontePCM", "FonteSilencio", "FonteWAV", "GravadorWAV", "FilaAudio"]
