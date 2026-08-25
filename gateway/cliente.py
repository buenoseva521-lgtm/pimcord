from __future__ import annotations
import asyncio, json, logging
import aiohttp
from ..nucleo import ErroDoGateway

class Gateway:
    def __init__(self, bot: object, url: str, token: str, intents: int):
        self.bot, self.url, self.token, self.intents = bot, url, token, intents
        self.logger = logging.getLogger("pimcord.gateway"); self.sequencia = None; self.sessao_id = None
        self._parar = False; self._heartbeat: asyncio.Task | None = None
    async def executar(self) -> None:
        atraso = 1.0
        while not self._parar:
            try:
                async with aiohttp.ClientSession() as sessao:
                    async with sessao.ws_connect(self.url + "?v=10&encoding=json", heartbeat=None) as ws:
                        self.ws = ws; atraso = 1.0
                        async for msg in ws:
                            if msg.type == aiohttp.WSMsgType.TEXT:
                                await self._processar(ws, json.loads(msg.data))
                            elif msg.type in (aiohttp.WSMsgType.CLOSED, aiohttp.WSMsgType.ERROR): break
            except asyncio.CancelledError: raise
            except Exception as erro:
                self.logger.warning("Gateway desconectado: %s; reconectando em %.1fs", erro, atraso)
                await asyncio.sleep(atraso); atraso = min(atraso * 2, 60)
    async def _processar(self, ws: aiohttp.ClientWebSocketResponse, pacote: dict) -> None:
        op, dados = pacote.get("op"), pacote.get("d")
        if pacote.get("s") is not None: self.sequencia = pacote["s"]
        if op == 10:
            intervalo = dados["heartbeat_interval"] / 1000
            self._heartbeat = asyncio.create_task(self._bater(intervalo))
            await ws.send_json({"op": 2, "d": {"token": self.token, "properties": {"os": "linux", "browser": "pimcord", "device": "pimcord"}, "intents": self.intents}})
        elif op == 1: await ws.send_json({"op": 1, "d": self.sequencia})
        elif op == 7: await ws.close()
        elif op == 9: await ws.close()
        elif op == 0: await self._evento(pacote.get("t"), dados)
    async def _bater(self, intervalo: float) -> None:
        while True:
            await asyncio.sleep(intervalo)
            await self.ws.send_json({"op": 1, "d": self.sequencia})
    async def _evento(self, nome: str | None, dados: dict) -> None:
        if nome == "READY": self.sessao_id = dados.get("session_id"); await self.bot.disparar("pronto")
        elif nome == "MESSAGE_CREATE": await self.bot.receber_mensagem(dados)
        elif nome: await self.bot.disparar(nome.lower(), dados)
    async def parar(self) -> None:
        self._parar = True
        if self._heartbeat: self._heartbeat.cancel()
        if hasattr(self, "ws"): await self.ws.close()
