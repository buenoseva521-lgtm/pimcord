from pimcord.projeto_ia import projeto_local_pimcord

pedidos = [
    "crie um bot com apenas um comando .clear que apaga uma quantidade de mensagens informada pelo usuário",
    "crie um bot de economia com .saldo, .diaria e ranking persistente em sqlite",
    "crie um bot de tickets com botão para abrir atendimento e fechar o canal",
    "crie um bot com um comando .nuke que apaga canais, cria cargos e bane membros",
]

for pedido in pedidos:
    projeto = projeto_local_pimcord(pedido)
    plano = projeto.plano
    print("\n=== PEDIDO ===")
    print(pedido)
    print("ARQUIVOS:", [item["caminho"] for item in plano["arquivos"]])
    for item in plano["arquivos"]:
        if item["caminho"].startswith("cogs/") and item["caminho"].endswith(".py"):
            print(f"--- {item['caminho']} ---")
            print(item["conteudo"][:1200])
