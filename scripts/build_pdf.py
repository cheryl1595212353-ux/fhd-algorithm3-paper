"""Compile the single authoritative manuscript with Tectonic or latexmk."""
import argparse
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--engine", default="auto", help="auto, tectonic, latexmk, or executable path")
    args = parser.parse_args()
    engine = args.engine
    if engine == "auto":
        engine = shutil.which("tectonic") or shutil.which("latexmk")
    elif engine in ("tectonic", "latexmk"):
        engine = shutil.which(engine)
    if not engine or not Path(engine).is_file():
        parser.error("Install Tectonic/latexmk or supply --engine /path/to/executable")
    (ROOT / "build").mkdir(exist_ok=True)
    if Path(engine).name == "tectonic":
        command = [engine, "-X", "compile", "--untrusted", "--keep-logs", "--outdir", "build", "main.tex"]
    elif Path(engine).name == "latexmk":
        command = [engine, "-norc", "-pdf", "-interaction=nonstopmode", "-halt-on-error", "-outdir=build", "main.tex"]
    else:
        parser.error("Supported executable names: tectonic and latexmk")
    subprocess.run(command, cwd=ROOT, check=True)


if __name__ == "__main__":
    main()
