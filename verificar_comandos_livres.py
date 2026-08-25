from pathlib import Path
import tempfile

from pimcord.projeto_ia import projeto_local_pimcord

casos = {
    "bot com .clear e .ban e apenas esses comandos": {"clear", "ban"},
    "bot com .saldo .diaria e .ranking de economia": {"economia"},
    "bot de escola com .provas e .presenca": {"provas", "presenca"},
}

for pedido, esperados in casos.items():
    projeto = projeto_local_pimcord(pedido)
    caminhos = {Path(item).parts[-1] for item in projeto.caminhos()}
    plano = projeto.plano
    texto = "\n".join(arquivo["conteudo"] for arquivo in plano["arquivos"] if arquivo["caminho"].startswith("cogs/"))
    faltantes = [item for item in esperados if item not in texto and item not in caminhos]
    if faltantes:
        raise AssertionError(f"{pedido!r}: faltaram {faltantes}; arquivos={sorted(caminhos)}")
    if "ping" in texto.lower() or 'comando_hibrido("ajuda"' in texto:
        raise AssertionError(f"{pedido!r}: comando auxiliar inventado")
    with tempfile.TemporaryDirectory() as destino:
        projeto.salvar(destino)
        assert (Path(destino) / "cogs" / "__init__.py").is_file()
    print(f"OK: {pedido} -> {sorted(caminhos)}")
