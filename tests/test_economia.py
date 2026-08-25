import pytest

from pimcord import EconomiaSQLite


def test_economia_saldo_diaria_transferencia_ranking(tmp_path):
    economia = EconomiaSQLite(tmp_path / "economia.db", saldo_inicial=10, diaria=100)
    assert economia.saldo("a") == 10
    assert economia.diaria("a", agora=1000) == 110
    with pytest.raises(ValueError, match="cooldown"):
        economia.diaria("a", agora=1001)
    assert economia.saldo("b") == 10
    assert economia.transferir("a", "b", 25) == (85, 35)
    assert economia.ranking(2)[0]["usuario_id"] == "a"
    economia.fechar()


def test_economia_rejeita_valores_invalidos(tmp_path):
    economia = EconomiaSQLite(tmp_path / "economia.db")
    with pytest.raises(ValueError):
        economia.transferir("a", "b", 0)
    with pytest.raises(ValueError):
        economia.ranking(101)
    economia.fechar()
