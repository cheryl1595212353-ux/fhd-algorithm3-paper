"""Shared LaTeX typography and vector export for every manuscript figure."""

from io import BytesIO
from pathlib import Path

import matplotlib as mpl


def configure_tex(*, font_size=9, label_size=10):
    mpl.rcParams.update({
        "text.usetex": True,
        "text.latex.preamble": (
            r"\usepackage[T1]{fontenc}\usepackage{lmodern}\usepackage{amsmath}"
        ),
        "font.family": "serif",
        "font.serif": ["Computer Modern Roman"],
        "font.size": font_size,
        "axes.labelsize": label_size,
        "xtick.labelsize": font_size,
        "ytick.labelsize": font_size,
        "axes.linewidth": 0.7,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "legend.frameon": False,
        "pdf.fonttype": 42,
        "svg.fonttype": "path",
    })


def save_figure(fig, stem: Path):
    for extension in ("pdf", "svg", "png"):
        path = stem.with_suffix("." + extension)
        buffer = BytesIO()
        fig.savefig(buffer, format=extension, dpi=400)
        data = buffer.getvalue()
        if extension == "svg":
            lines = (line.rstrip() for line in data.decode("utf-8").splitlines())
            data = ("\n".join(lines) + "\n").encode("utf-8")
        temporary = path.with_suffix(path.suffix + ".tmp")
        temporary.write_bytes(data)
        temporary.replace(path)
        print(path.name)
