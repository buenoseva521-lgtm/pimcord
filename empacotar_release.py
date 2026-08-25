from __future__ import annotations

import hashlib
import shutil
import subprocess
import zipfile
from pathlib import Path

raiz = Path(__file__).resolve().parent
staging = Path('/tmp/pimcord-release-final')
zip_path = raiz / 'pimcordia.file.zip'
sha_path = raiz / 'pimcordia.file.zip.sha256'

if staging.exists():
    shutil.rmtree(staging)
staging.mkdir(parents=True)

excluir = {
    '.git', '.gitignore', '.pytest_cache', '__pycache__', '.mypy_cache',
    '.ruff_cache', '.env', '.dist_pimcord', 'dist', 'build', 'pimcordia.file.zip',
    'pimcordia.file.zip.sha256', 'empacotar_release.py',
}
excluir_sufixos = {'.pyc', '.pyo'}

def copiar(origem: Path, destino: Path) -> None:
    relativo = origem.relative_to(raiz)
    if any(parte in excluir for parte in relativo.parts):
        return
    if origem.name in excluir or origem.suffix in excluir_sufixos:
        return
    if origem.is_symlink() or origem.is_file():
        destino.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(origem, destino)

for caminho in raiz.rglob('*'):
    if caminho.is_file():
        copiar(caminho, staging / caminho.relative_to(raiz))

relatorio = raiz / 'RELATORIO_RELEASE_0_7_0.md'
if relatorio.exists():
    shutil.copy2(relatorio, staging / relatorio.name)

if zip_path.exists():
    zip_path.unlink()
with zipfile.ZipFile(zip_path, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as arquivo_zip:
    for caminho in sorted(staging.rglob('*')):
        if caminho.is_file():
            arquivo_zip.write(caminho, caminho.relative_to(staging).as_posix())

sha256 = hashlib.sha256(zip_path.read_bytes()).hexdigest()
sha_path.write_text(f'{sha256}  {zip_path.name}\n', encoding='utf-8')
print(f'arquivos={sum(1 for p in staging.rglob("*") if p.is_file())}')
print(f'zip={zip_path} bytes={zip_path.stat().st_size}')
print(f'sha256={sha256}')

with zipfile.ZipFile(zip_path) as arquivo_zip:
    nomes = arquivo_zip.namelist()
    proibidos = [n for n in nomes if n.endswith(('.pyc', '.pyo')) or '/__pycache__/' in f'/{n}' or n.endswith('.env')]
    if proibidos:
        raise SystemExit(f'artefatos proibidos no ZIP: {proibidos}')
    obrigatorios = {'pimcord/__init__.py', 'pimcord/bot.py', 'pimcord/gateway/cliente.py', 'pimcord/projeto_ia.py'}
    faltantes = obrigatorios - set(nomes)
    if faltantes:
        raise SystemExit(f'arquivos obrigatorios ausentes: {sorted(faltantes)}')
print('zip-verificado=ok')

try:
    subprocess.run(['python', '-m', 'build', '--wheel', '--sdist'], cwd=raiz, check=False)
except FileNotFoundError:
    print('build-module=indisponivel; ZIP continua valido')
