from pathlib import Path
import ast
import tempfile
from pimcord.projeto_ia import projeto_local_pimcord

projeto = projeto_local_pimcord('''crie um bot completo com economia, moderação, tickets, boas-vindas, diversão e utilidades''')
assert len(projeto.arquivos) >= 10
por_caminho = {item['caminho']: item['conteudo'] for item in projeto.arquivos}
for caminho, conteudo in por_caminho.items():
    if caminho.endswith('.py'):
        ast.parse(conteudo, filename=caminho)
mod = por_caminho['cogs/moderacao.py']
eco = por_caminho['cogs/economia.py']
ticket = por_caminho['cogs/tickets.py']
assert 'canal.purge' in mod and 'Apaga de 1 a 100' in mod
assert 'EconomiaSQLite' in eco and 'banco.saldo' in eco and 'banco.diaria' in eco
assert 'criar_canal' in ticket and 'excluir_canal' in ticket
assert 'executa o comando' not in '\n'.join(por_caminho.values()).casefold()
print(f'gerado={len(projeto.arquivos)} arquivos; ações concretas verificadas')
