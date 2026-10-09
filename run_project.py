"""One-command runner: regenerate synthetic inputs, then solve all scenarios."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(script: str) -> None:
    subprocess.run([sys.executable, str(ROOT / "src" / script)], check=True, cwd=ROOT)


if __name__ == "__main__":
    run("generate_data.py")
    run("optimize_network.py")
