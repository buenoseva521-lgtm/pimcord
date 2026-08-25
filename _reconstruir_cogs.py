from pathlib import Path

path = Path('/home/ubuntu/Pimcord/pimcord/projeto_ia.py')
text = path.read_text(encoding='utf-8')
start = text.index('    cog_conteudos = {')
end = text.index('    arquivos.append({"caminho": "cogs/geral.py"', start)

conteudos = {
    "economia": '''from pimcord import EconomiaSQLite

def configurar(bot):
    banco = EconomiaSQLite("economia.sqlite3", diaria=100)

    @bot.comando_hibrido("saldo", descricao="Consulta o saldo de moedas do autor")
    async def saldo(ctx):
        total = banco.saldo(ctx.autor_id or "desconhecido")
        await ctx.responder(f"Seu saldo atual é {total} moedas.")

    @bot.comando_hibrido("diaria", descricao="Resgata a recompensa diária de 100 moedas", aliases=["daily"])
    async def diaria(ctx):
        total = banco.diaria(ctx.autor_id or "desconhecido")
        await ctx.responder(f"Recompensa resgatada. Seu saldo agora é {total} moedas.")

    @bot.comando_hibrido("ranking", descricao="Mostra os maiores saldos do servidor", aliases=["top"])
    async def ranking(ctx):
        linhas = banco.ranking()
        if not linhas:
            await ctx.responder("Ainda não há usuários no ranking.")
            return
        texto = "\\n".join(f"{i}. {linha['usuario_id']}: {linha['saldo']} moedas" for i, linha in enumerate(linhas, 1))
        await ctx.responder(texto)
''',
    "moderacao": '''import sqlite3
from pimcord import Permissoes

def configurar(bot):
    @bot.comando_hibrido(
        "limpar",
        descricao="Apaga de 1 a 100 mensagens deste canal",
        aliases=["purge"],
        permissoes=int(Permissoes.gerenciar_mensagens),
    )
    async def limpar(ctx, quantidade: int = 10):
        canal = ctx.canal_atual
        if canal is None:
            await ctx.responder("Este comando precisa ser usado em um canal de texto.")
            return
        quantidade = max(1, min(100, quantidade))
        apagadas = await canal.purge(limite=quantidade)
        total = len(apagadas) if apagadas is not None else quantidade
        await ctx.responder(f"Apaguei {total} mensagem(ns).")

    @bot.comando_hibrido(
        "avisar",
        descricao="Registra uma advertência persistente para um membro",
        permissoes=int(Permissoes.gerenciar_mensagens),
    )
    async def avisar(ctx, membro: str, motivo: str = "Sem motivo informado"):
        with sqlite3.connect("moderacao.sqlite3") as banco:
            banco.execute("CREATE TABLE IF NOT EXISTS avisos (id INTEGER PRIMARY KEY, servidor_id TEXT, membro TEXT, motivo TEXT, autor TEXT)")
            banco.execute("INSERT INTO avisos (servidor_id, membro, motivo, autor) VALUES (?, ?, ?, ?)", (getattr(ctx.canal_atual, "servidor_id", None), membro, motivo, ctx.autor_id))
            banco.commit()
        await ctx.responder(f"Advertência registrada para {membro}: {motivo}.")
''',
    "tickets": '''from pimcord import Permissoes

def configurar(bot):
    @bot.comando_hibrido("ticket", descricao="Cria um canal de atendimento", aliases=["suporte"])
    async def ticket(ctx, assunto: str = "atendimento"):
        canal = ctx.canal_atual
        servidor_id = getattr(canal, "servidor_id", None)
        cliente = getattr(canal, "cliente", None)
        if not servidor_id or cliente is None:
            await ctx.responder("Não consegui identificar o servidor deste atendimento.")
            return
        nome = "ticket-" + "-".join(assunto.lower().split())[:70]
        criado = await cliente.criar_canal(servidor_id, name=nome, type=0, topic=f"Atendimento de {ctx.autor_id}: {assunto}")
        await ctx.responder(f"Ticket criado: <#{criado.get('id', '')}>.")

    @bot.comando_hibrido("fechar_ticket", descricao="Fecha o canal atual de atendimento", aliases=["fechar"], permissoes=int(Permissoes.gerenciar_canais))
    async def fechar_ticket(ctx):
        canal = ctx.canal_atual
        cliente = getattr(canal, "cliente", None)
        if canal is None or cliente is None:
            await ctx.responder("Este comando precisa ser usado em um canal de ticket.")
            return
        await cliente.excluir_canal(canal.id)
''',
    "boas_vindas": '''def configurar(bot):
    @bot.evento("membro_adicionado")
    async def membro_entrou(membro):
        bot.logger.info("Novo membro recebido: %s", getattr(membro, "nome", membro))

    @bot.comando_hibrido("configurar_boas_vindas", descricao="Mostra o estado do módulo de boas-vindas")
    async def configurar_boas_vindas(ctx):
        await ctx.responder("Boas-vindas ativas. Registre um canal específico para mensagens de entrada.")
''',
    "diversao": '''import random

def configurar(bot):
    @bot.comando_hibrido("dado", descricao="Rola um dado de seis lados")
    async def dado(ctx):
        await ctx.responder(f"{ctx.autor_id or 'Jogador'} rolou: {random.randint(1, 6)}.")

    @bot.comando_hibrido("moeda", descricao="Lança uma moeda e informa o resultado")
    async def moeda(ctx):
        await ctx.responder(f"Resultado: {random.choice(('cara', 'coroa'))}.")
''',
    "utilidades": '''def configurar(bot):
    @bot.comando_hibrido("userinfo", descricao="Mostra o identificador do autor", aliases=["perfil"])
    async def userinfo(ctx):
        await ctx.responder(f"Seu ID é {ctx.autor_id or 'desconhecido'}.")

    @bot.comando_hibrido("servidor", descricao="Mostra o identificador do servidor atual")
    async def servidor(ctx):
        servidor_id = getattr(ctx.canal_atual, "servidor_id", None)
        await ctx.responder(f"Servidor atual: {servidor_id or 'mensagem privada'}.")
''',
}
ordem = ["economia", "moderacao", "tickets", "boas_vindas", "diversao", "utilidades"]
linhas = ["    cog_conteudos = {"]
for indice, nome in enumerate(ordem):
    virgula = "," if indice < len(ordem) - 1 else ","
    linhas.append(f"        {nome!r}: {conteudos[nome]!r}{virgula}")
linhas.append("    }\n")
text = text[:start] + "\n".join(linhas) + text[end:]
text = text.replace('@bot.comando_hibrido("ping", aliases=["latencia"])', '@bot.comando_hibrido("ping", descricao="Verifica se o bot está online", aliases=["latencia"])')
text = text.replace('@bot.comando_hibrido("ajuda")', '@bot.comando_hibrido("ajuda", descricao="Lista os comandos disponíveis no bot")')
path.write_text(text, encoding='utf-8')
