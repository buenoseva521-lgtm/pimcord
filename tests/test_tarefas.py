import asyncio

import pytest

from pimcord import Agendador, FilaAssincrona, PoliticaRetentativa


def test_politica_de_retentativa_tem_limite():
    politica = PoliticaRetentativa(atraso_inicial=1, fator=2, atraso_maximo=3, jitter=0)
    assert politica.atraso(1) == 1
    assert politica.atraso(3) == 3

@pytest.mark.asyncio
async def test_fila_assincrona_processa_e_encerrra():
    fila = FilaAssincrona(limite=4)
    valores = []
    tarefas = await fila.consumir(valores.append, consumidores=2)
    await fila.colocar(1)
    await fila.colocar(2)
    await fila._fila.join()
    await fila.encerrar(consumidores=2)
    await asyncio.gather(*tarefas)
    assert sorted(valores) == [1, 2]
    assert fila.processados == 2

@pytest.mark.asyncio
async def test_agendador_inicia_e_para():
    chamadas = []
    agendador = Agendador()
    agendador.registrar("teste", lambda: chamadas.append(1), 0.001).iniciar()
    await asyncio.sleep(0.01)
    await agendador.parar_todas()
    assert chamadas
