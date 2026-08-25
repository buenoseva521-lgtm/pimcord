from pathlib import Path
path = Path('/home/ubuntu/Pimcord/pimcord/projeto_ia.py')
text = path.read_text(encoding='utf-8')
old = 'texto = "\\n".join'
new = 'texto = "\\\\n".join'
if text.count(old) != 1:
    raise SystemExit(f'ocorrências inesperadas: {text.count(old)}')
path.write_text(text.replace(old, new), encoding='utf-8')
