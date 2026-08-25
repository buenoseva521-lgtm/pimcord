import pytest

from pimcord import AcaoModeracao, Bot, MotorAutomoderacao, RegraModeracao


def test_motor_normaliza_variacoes_e_abre_ticket_auditavel():
    motor = MotorAutomoderacao([
        RegraModeracao("palavra", ("golpe",), acao=AcaoModeracao.BLOQUEAR, motivo="conteúdo suspeito"),
    ])
    decisao = motor.avaliar("GÓLPE", servidor_id="10", canal_id="20", mensagem_id="30", usuario_id="40")
    assert decisao.detectada is True
    assert decisao.acao is AcaoModeracao.BLOQUEAR
    assert decisao.correspondencia == "golpe"
    assert len(motor.tickets_abertos()) == 1
    assert motor.exportar_logs()[0]["usuario_id"] == "40"


def test_motor_regex_e_regras_desabilitadas():
    motor = MotorAutomoderacao([
        RegraModeracao("regex", (r"p[i1]mcord",), regex=True),
        RegraModeracao("desligada", ("qualquer",), habilitada=False),
    ])
    assert motor.avaliar("P1mcord").regra == "regex"
    assert motor.avaliar("qualquer").detectada is False
    with pytest.raises(ValueError):
        motor.adicionar_regra(RegraModeracao("regex", ("outro",)))


def test_bot_expoe_automod_em_portugues():
    bot = Bot()
    regra = RegraModeracao("links", ("encurte.me",), acao=AcaoModeracao.APAGAR)
    assert bot.adicionar_regra_automoderacao(regra) is regra
    assert bot.automod.regras["links"].acao is AcaoModeracao.APAGAR
    assert bot.remover_regra_automoderacao("links") is regra
