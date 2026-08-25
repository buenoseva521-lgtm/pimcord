import subprocess
import sys
import tempfile
from pathlib import Path

wheel = sorted(Path(__file__).parent.glob("dist/pimcord-*.whl"))[-1]
with tempfile.TemporaryDirectory(prefix="pimcord-clean-") as destino:
    venv = Path(destino) / ".venv"
    subprocess.run([sys.executable, "-m", "venv", str(venv)], check=True)
    python = venv / "bin" / "python"
    cli = venv / "bin" / "pimcord"
    subprocess.run([str(python), "-m", "pip", "install", "--quiet", str(wheel)], check=True)
    subprocess.run([str(python), "-c", "import pimcord; print(pimcord.__version__); print(pimcord.Bot(prefixo='!').diagnostico()['versao'])"], check=True)
    subprocess.run([str(cli), "diagnostico"], check=True)
print("instalacao limpa: OK")
