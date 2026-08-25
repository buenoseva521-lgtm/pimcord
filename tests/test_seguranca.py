import logging

from pimcord import FiltroSegredos, token_redigido


def test_token_redigido_preserva_apenas_fragmentos_diagnosticos():
    assert token_redigido(None) == "[ausente]"
    assert token_redigido("curto") == "[REDACTED]"
    assert token_redigido("abc123456xyz") == "abc…xyz"


def test_filtro_redige_segredo_e_chaves_sensiveis():
    filtro = FiltroSegredos(["segredo-super-seguro"])
    registro = logging.LogRecord("teste", logging.WARNING, __file__, 1, "token=%s senha=abc123", (), None)
    registro.args = ("segredo-super-seguro",)
    filtro.filter(registro)
    assert "segredo-super-seguro" not in str(registro.msg)
    assert "[REDACTED]" in str(registro.msg)


def test_filtro_preserva_tipos_numericos_no_logging_formatado():
    registro = logging.LogRecord(
        "pimcord.gateway",
        logging.WARNING,
        __file__,
        1,
        "Gateway desconectado: %s; tentativa %s/%s em %.1fs",
        ("falha", 1, 5, 1.0),
        None,
    )
    filtro = FiltroSegredos(["segredo-super-seguro"])
    assert filtro.filter(registro) is True
    assert registro.getMessage() == "Gateway desconectado: falha; tentativa 1/5 em 1.0s"
    assert registro.args[1:] == (1, 5, 1.0)
