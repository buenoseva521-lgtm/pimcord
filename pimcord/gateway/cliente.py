"""Transporte Gateway do Discord para o Pimcord."""
from __future__ import annotations

import asyncio
import json
import logging
import random
import time
import zlib
from typing import Any

import aiohttp

from .eventos import EVENTOS_PORTUGUES, modelar_evento
from ..seguranca import FiltroSegredos


class Gateway:
    def __init__(self, bot: object, url: str, token: str, intents: int, *, max_reconexoes: int = 5, timeout_conexao: float = 15.0):
        self.bot = bot
        self.url = url
        self.token = token
        self.intents = intents
        self.max_reconexoes = max(1, int(max_reconexoes))
        self.timeout_conexao = max(1.0, float(timeout_conexao))
        self._falhas_reconexao = 0
        self.logger = logging.getLogger("pimcord.gateway")
        self.logger.addFilter(FiltroSegredos([token]))
        self.sequencia: int | None = None
        self.sessao_id: str | None = None
        self.url_resume: str | None = None
        self.ws: aiohttp.ClientWebSocketResponse | None = None
        self._parar = False
        self._heartbeat: asyncio.Task[None] | None = None
        self._heartbeat_ack = True
        self._intervalo_heartbeat = 41.25
        self._heartbeat_enviado_em: float | None = None
        self._latencia: float | None = None
        self._primeiro_heartbeat = True
        self._compressao = zlib.decompressobj()
        self._buffer_compressao = bytearray()
        self._cauda_compressao = b""
        self._quadros_compressao = 0

    @property
    def latencia(self) -> float | None:
        """Latência em segundos entre heartbeat e ACK mais recentes."""
        return self._latencia

    async def executar(self) -> None:
        atraso = 1.0
        self._falhas_reconexao = 0
        self.logger.info("Conectando ao Gateway do Discord")
        while not self._parar:
            try:
                endpoint = self.url_resume or self.url
                timeout = aiohttp.ClientTimeout(total=30.0, sock_connect=self.timeout_conexao, sock_read=None)
                async with aiohttp.ClientSession(timeout=timeout) as sessao:
                    self._compressao = zlib.decompressobj()
                    self._buffer_compressao.clear()
                    self._cauda_compressao = b""
                    self._quadros_compressao = 0
                    async with sessao.ws_connect(
                        endpoint + "?v=10&encoding=json",
                        heartbeat=None,
                        timeout=self.timeout_conexao,
                        autoclose=True,
                        autoping=True,
                    ) as ws:
                        self.ws = ws
                        atraso = 1.0
                        if hasattr(self.bot, "_definir_estado_conexao"):
                            self.bot._definir_estado_conexao("conectado")
                        self.logger.info("Gateway conectado; aguardando identificação")
                        await self._loop_ws(ws)
            except asyncio.CancelledError:
                raise
            except Exception as erro:
                if self._parar:
                    break
                self._falhas_reconexao += 1
                if hasattr(getattr(self.bot, "metricas", None), "reconexoes"):
                    self.bot.metricas.reconexoes += 1
                if self._falhas_reconexao >= self.max_reconexoes:
                    self._parar = True
                    self.logger.error("Gateway falhou %s vezes consecutivas; reconexão interrompida: %s", self._falhas_reconexao, erro)
                    if hasattr(self.bot, "_definir_estado_conexao"):
                        self.bot._definir_estado_conexao("erro_gateway")
                    break
                if hasattr(self.bot, "_definir_estado_conexao"):
                    self.bot._definir_estado_conexao("reconectando")
                self.logger.warning("Gateway desconectado: %s; tentativa %s/%s em %.1fs", erro, self._falhas_reconexao, self.max_reconexoes, atraso)
                await asyncio.sleep(atraso)
                atraso = min(atraso * 2, 60.0)
            finally:
                if self._heartbeat:
                    self._heartbeat.cancel()
                    self._heartbeat = None
                self.ws = None
                if not self._parar and hasattr(self.bot, "_definir_estado_conexao"):
                    self.bot._definir_estado_conexao("reconectando")

    async def _loop_ws(self, ws: aiohttp.ClientWebSocketResponse) -> None:
        async for mensagem in ws:
            if mensagem.type == aiohttp.WSMsgType.TEXT:
                await self._processar(ws, json.loads(mensagem.data))
            elif mensagem.type == aiohttp.WSMsgType.BINARY:
                for dados in self._descompactar_varios(mensagem.data):
                    await self._processar(ws, json.loads(dados))
            elif mensagem.type in (aiohttp.WSMsgType.CLOSED, aiohttp.WSMsgType.ERROR):
                break
        codigo = getattr(ws, "close_code", None)
        self._tratar_close_code(codigo)
        # Uma saída silenciosa não é uma conexão saudável: sem esta exceção,
        # o laço externo reinicia imediatamente e cria um loop infinito sem
        # consumir o limite de reconexões.
        if not self._parar:
            raise ConnectionError(f"Gateway encerrou a conexão com close code {codigo}")

    def _descompactar_varios(self, dados: bytes) -> list[str]:
        """Decodifica zero, uma ou várias mensagens do fluxo zlib-stream."""
        try:
            self._buffer_compressao.extend(self._compressao.decompress(dados))
            marcador = b"\x00\x00\xff\xff"
            fronteiras = (self._cauda_compressao + dados).count(marcador)
            self._cauda_compressao = (self._cauda_compressao + dados)[-3:]
            self._quadros_compressao += fronteiras
            mensagens: list[str] = []
            decodificador = json.JSONDecoder()
            while self._quadros_compressao:
                texto = bytes(self._buffer_compressao).decode("utf-8")
                deslocamento = len(texto) - len(texto.lstrip())
                try:
                    objeto, fim = decodificador.raw_decode(texto.lstrip())
                except json.JSONDecodeError:
                    break
                inicio_real = deslocamento
                consumido = inicio_real + fim
                mensagens.append(json.dumps(objeto, ensure_ascii=False))
                del self._buffer_compressao[:consumido]
                self._quadros_compressao -= 1
            return mensagens
        except (zlib.error, UnicodeDecodeError) as erro:
            self.logger.error("Falha ao descompactar pacote do Gateway: %s", erro)
            self._compressao = zlib.decompressobj()
            self._buffer_compressao.clear()
            self._cauda_compressao = b""
            self._quadros_compressao = 0
            return []

    def _descompactar(self, dados: bytes) -> str | None:
        """Compatibilidade: retorna a primeira mensagem decodificada."""
        mensagens = self._descompactar_varios(dados)
        return mensagens[0] if mensagens else None

    def _tratar_close_code(self, codigo: int | None) -> None:
        """Aplica as regras de sessão dos close codes do Gateway."""
        if codigo is None or codigo in {1000, 1001}:
            return
        if codigo in {4007, 4009}:
            self.logger.warning("Sessão do Gateway expirou ou tem sequência inválida (%s); iniciando IDENTIFY", codigo)
            self.sessao_id = None
            self.sequencia = None
            self.url_resume = None
            return
        if codigo == 4004:
            self._parar = True
            self.logger.error("Token do bot rejeitado pelo Gateway (close code 4004)")
            if hasattr(self.bot, "_definir_estado_conexao"):
                self.bot._definir_estado_conexao("erro_autenticacao")
            return
        if codigo in {4013, 4014}:
            self._parar = True
            self.logger.error("Intents inválidos ou não autorizados pelo Gateway (close code %s)", codigo)
            if hasattr(self.bot, "_definir_estado_conexao"):
                self.bot._definir_estado_conexao("erro_intents")
            return
        if codigo == 4011:
            self._parar = True
            self.logger.error("O bot exige sharding para conectar (close code 4011)")
            if hasattr(self.bot, "_definir_estado_conexao"):
                self.bot._definir_estado_conexao("sharding_necessario")
            return
        self.logger.warning("Gateway encerrou a sessão com close code %s; reconexão será tentada", codigo)

    async def _processar(self, ws: aiohttp.ClientWebSocketResponse, pacote: dict[str, Any]) -> None:
        if pacote is None:
            self.logger.debug("Frame vazio ignorado pelo Gateway")
            return
        if not isinstance(pacote, dict):
            self.logger.warning("Pacote inválido ignorado pelo Gateway: %s", type(pacote).__name__)
            return
        op = pacote.get("op")
        dados = pacote.get("d")
        if pacote.get("s") is not None:
            self.sequencia = pacote["s"]
        if op == 10:
            await self._hello(ws, dados or {})
        elif op == 1:
            await self._enviar_heartbeat(ws)
        elif op == 11:
            self._heartbeat_ack = True
            if self._heartbeat_enviado_em is not None:
                self._latencia = max(0.0, time.monotonic() - self._heartbeat_enviado_em)
                self.logger.debug("Heartbeat confirmado; latência %.3fs", self._latencia)
        elif op == 7:
            await ws.close()
        elif op == 9:
            self.logger.warning("Sessão do Gateway inválida; resumível=%s", dados)
            if not dados:
                self.sessao_id = None
                self.sequencia = None
                self.url_resume = None
            if ws is not None:
                await ws.close()
        elif op == 0:
            await self._evento(pacote.get("t"), dados or {})

    async def _hello(self, ws: aiohttp.ClientWebSocketResponse, dados: dict[str, Any]) -> None:
        self._intervalo_heartbeat = float(dados.get("heartbeat_interval", 41250)) / 1000
        if self._heartbeat:
            self._heartbeat.cancel()
        self._heartbeat_ack = True
        self._primeiro_heartbeat = True
        self._heartbeat = asyncio.create_task(self._bater())
        if hasattr(self.bot, "_definir_estado_conexao"):
            self.bot._definir_estado_conexao("identificando")
        if self.sessao_id and self.sequencia is not None and self.url_resume:
            pacote = {"op": 6, "d": {"token": self.token, "session_id": self.sessao_id, "seq": self.sequencia}}
        else:
            pacote = {"op": 2, "d": {"token": self.token, "properties": {"os": "linux", "browser": "pimcord", "device": "pimcord"}, "intents": self.intents}}
        self.logger.info("Enviando %s ao Gateway", "RESUME" if pacote["op"] == 6 else "IDENTIFY")
        await ws.send_json(pacote)

    async def _enviar_heartbeat(self, ws: aiohttp.ClientWebSocketResponse) -> None:
        self._heartbeat_ack = False
        self._heartbeat_enviado_em = time.monotonic()
        await ws.send_json({"op": 1, "d": self.sequencia})

    async def _bater(self) -> None:
        while not self._parar:
            if self._primeiro_heartbeat:
                self._primeiro_heartbeat = False
                await asyncio.sleep(random.uniform(0.0, self._intervalo_heartbeat))
            else:
                await asyncio.sleep(self._intervalo_heartbeat)
            if not self.ws or self.ws.closed:
                return
            if not self._heartbeat_ack:
                self.logger.warning("Heartbeat sem ACK; fechando conexão para reconectar")
                await self.ws.close()
                return
            await self._enviar_heartbeat(self.ws)

    async def _evento(self, nome: str | None, dados: dict[str, Any]) -> None:
        """Despacha o evento oficial, o alias português e o modelo tipado quando disponível."""
        if not nome:
            return
        if nome == "READY":
            self.sessao_id = dados.get("session_id")
            self.url_resume = dados.get("resume_gateway_url") or self.url
            if hasattr(self.bot, "_aplicar_ready"):
                self.bot._aplicar_ready(dados)
            self._falhas_reconexao = 0
            if hasattr(self.bot, "_definir_estado_conexao"):
                self.bot._definir_estado_conexao("pronto")
            usuario = (dados.get("user") or {}).get("username", "bot")
            self.logger.info("Conectado ao Discord como %s", usuario)
            if hasattr(self.bot, "_sincronizar_automaticamente"):
                await self.bot._sincronizar_automaticamente()
        if nome == "MESSAGE_CREATE":
            await self.bot.receber_mensagem(dados)
        elif nome == "VOICE_STATE_UPDATE" and hasattr(self.bot, "_processar_estado_voz"):
            await self.bot._processar_estado_voz(dados)
        elif nome == "VOICE_SERVER_UPDATE" and hasattr(self.bot, "_processar_servidor_voz"):
            await self.bot._processar_servidor_voz(dados)
        elif nome == "INTERACTION_CREATE":
            await self.bot.receber_interacao(dados)
        elif nome in {"GUILD_CREATE", "GUILD_UPDATE"} and hasattr(self.bot, "_aplicar_servidor"):
            self.bot._aplicar_servidor(dados)
        elif nome == "GUILD_DELETE":
            servidor_id = str(dados.get("id", ""))
            if servidor_id and hasattr(self.bot, "_invalidar_servidor"):
                self.bot._invalidar_servidor(servidor_id)
            elif servidor_id and hasattr(self.bot, "_servidores"):
                self.bot._servidores.pop(servidor_id, None)
                self.bot.cache.remover(f"servidor:{servidor_id}")
        elif nome in {"CHANNEL_CREATE", "CHANNEL_UPDATE"} and hasattr(self.bot, "_aplicar_canal"):
            self.bot._aplicar_canal(dados)
        elif nome == "CHANNEL_DELETE":
            canal_id = str(dados.get("id", ""))
            if canal_id and hasattr(self.bot, "_canais"):
                self.bot._canais.pop(canal_id, None)
                self.bot.cache.remover(f"canal:{canal_id}")
        evento_oficial = nome.lower()
        evento_portugues = EVENTOS_PORTUGUES.get(nome, evento_oficial)
        modelo = modelar_evento(nome, dados, self.bot.http if hasattr(self.bot, "http") else None)
        eventos_registrados = getattr(self.bot, "eventos", {})
        # Compatibilidade: eventos antigos continuam recebendo o payload bruto.
        if evento_oficial in eventos_registrados:
            await self.bot.disparar(evento_oficial, dados)
        if evento_portugues in eventos_registrados:
            await self.bot.disparar(evento_portugues, modelo)
        # Permite observar qualquer evento tipado sem reservar nomes oficiais.
        evento_modelo = "modelo_" + evento_portugues
        if evento_modelo in eventos_registrados:
            await self.bot.disparar(evento_modelo, modelo)

    async def parar(self) -> None:
        self._parar = True
        if self._heartbeat:
            self._heartbeat.cancel()
            self._heartbeat = None
        if self.ws and not self.ws.closed:
            await self.ws.close()
