import asyncio

import pytest

from pimcord import CoordenaçãoLocal, GerenciadorDeShards


@pytest.mark.asyncio
async def test_cancelamento_e_reinicio_de_shard_recuperam_lease():
    coordenador = CoordenaçãoLocal()
    iniciou = asyncio.Event()
    permitir = asyncio.Event()
    tentativas = 0

    async def iniciar(shard):
        nonlocal tentativas
        tentativas += 1
        iniciou.set()
        await permitir.wait()
        return 0.01

    gerente = GerenciadorDeShards(
        1,
        iniciar,
        coordenador=coordenador,
        trabalhador="processo-a",
        duração_lease=0.2,
        atraso_inicial=0.001,
        atraso_maximo=0.002,
    )
    await gerente.iniciar()
    await asyncio.wait_for(iniciou.wait(), 0.2)
    await gerente.reiniciar(0)
    estados_durante = await coordenador.estados()
    assert estados_durante["shard:0"]["estado"] in {"encerrado", "conectando", "conectado"}
    permitir.set()
    assert await gerente.aguardar_saude(0.5)
    assert tentativas >= 2
    assert len(await coordenador.estados()) == 1
    await gerente.parar()


@pytest.mark.asyncio
async def test_falha_transitoria_repetida_mantem_exclusividade_entre_processos():
    coordenador = CoordenaçãoLocal()
    donos_simultaneos: dict[int, set[str]] = {}
    maior_concorrencia: dict[int, int] = {}
    chamadas: dict[tuple[str, int], int] = {}

    def iniciar_para(nome):
        async def iniciar(shard):
            chave = (nome, shard.id)
            chamadas[chave] = chamadas.get(chave, 0) + 1
            ativos = donos_simultaneos.setdefault(shard.id, set())
            ativos.add(nome)
            maior_concorrencia[shard.id] = max(maior_concorrencia.get(shard.id, 0), len(ativos))
            try:
                if chamadas[chave] == 1:
                    raise RuntimeError("queda de processo simulada")
                await asyncio.sleep(0.01)
                return 0.02
            finally:
                ativos.discard(nome)
        return iniciar

    primeiro = GerenciadorDeShards(3, iniciar_para("a"), coordenador=coordenador, trabalhador="a", duração_lease=0.05, atraso_inicial=0.001, atraso_maximo=0.002)
    segundo = GerenciadorDeShards(3, iniciar_para("b"), coordenador=coordenador, trabalhador="b", duração_lease=0.05, atraso_inicial=0.001, atraso_maximo=0.002)
    await primeiro.iniciar()
    await segundo.iniciar()
    assert await primeiro.aguardar_saude(0.5)
    await asyncio.sleep(0.08)
    assert all(maior_concorrencia.get(shard_id, 0) <= 1 for shard_id in range(3))
    assert all(sum(chamadas.get((nome, shard_id), 0) for nome in ("a", "b")) >= 1 for shard_id in range(3))
    await primeiro.parar()
    await segundo.parar()


@pytest.mark.asyncio
async def test_voice_gateway_reconecta_apos_queda_durante_stream(monkeypatch):
    from pimcord import Bot, ClienteGatewayVoz, SessaoVoz
    import pimcord.voz as modulo_voz

    class WSFechando:
        def __aiter__(self):
            return self

        async def __anext__(self):
            raise StopAsyncIteration

        async def close(self):
            return None

    sessao = SessaoVoz(Bot(), "10", "20")
    cliente = ClienteGatewayVoz(sessao)
    tentativas = 0

    async def conectar_simulado():
        nonlocal tentativas
        tentativas += 1
        if tentativas == 1:
            raise ConnectionError("processo de voz caiu durante stream")
        cliente.ws = WSFechando()
        sessao._parar.set()

    cliente.conectar = conectar_simulado
    sono_original = modulo_voz.asyncio.sleep

    async def sono_curto(_duracao):
        await sono_original(0)

    monkeypatch.setattr(modulo_voz.asyncio, "sleep", sono_curto)
    await cliente.executar(maximo_tentativas=3)
    assert tentativas == 2
    assert cliente.ws is None
