from pimcord.projeto_ia import projeto_local_pimcord

pedidos = (
    "crie um bot com um comando .alpha que envia uma mensagem de boas vindas",
    "crie um bot com um comando .beta que lista mensagens e aceita quantidade",
    "crie um bot com um comando .gamma que salva um lembrete com texto e motivo",
)
saidas = []
for pedido in pedidos:
    projeto = projeto_local_pimcord(pedido)
    arquivos = {item["caminho"]: item["conteudo"] for item in projeto.plano["arquivos"]}
    print(pedido)
    print(sorted(arquivos))
    print(arquivos["cogs/comandos.py"][:500])
    assert "cogs/comandos.py" in arquivos
    assert "cogs/especificacao.py" in arquivos
    assert "personalidade.py" not in arquivos
    saidas.append(arquivos["cogs/comandos.py"])
assert len(set(saidas)) == len(pedidos)
print("PROMPTS_DISTINTOS: aprovado")
