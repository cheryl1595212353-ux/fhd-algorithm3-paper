"""Regenerate the two standalone energy figures from the archived time steps."""

import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import LogLocator, NullFormatter
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
COLORS = ("#35659B", "#478274", "#B5674C")
MARKERS = ("o", "s", "^")
LINES = ("-", "--", "-.")


def main():
    with (ROOT / "data/energy/curves.csv").open(newline="") as f:
        rows = list(csv.DictReader(f))
    plt.rcParams.update({
        "text.usetex": True,
        "text.latex.preamble": r"\usepackage[T1]{fontenc}\usepackage{lmodern}",
        "font.family": "serif",
        "font.serif": ["Computer Modern Roman"],
        "font.size": 9,
        "axes.labelsize": 10,
        "xtick.labelsize": 9,
        "ytick.labelsize": 9,
        "axes.linewidth": 0.7,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "legend.frameon": False,
        "pdf.fonttype": 42,
        "svg.fonttype": "path",
    })
    for scheme in ("first", "second"):
        fig, ax = plt.subplots(figsize=(4.8, 3.45), layout="constrained")
        for index, denominator in enumerate((16, 32, 64)):
            curve = sorted((r for r in rows if r["scheme"] == scheme
                            and float(r["dt"]) == 1 / denominator),
                           key=lambda r: int(r["step"]))
            assert len(curve) == denominator // 2 + 1
            t = np.array([float(r["t"]) for r in curve])
            energy = np.array([float(r["energy"]) for r in curve])
            recorded = np.array([float(r["energy_normalized"]) for r in curve])
            assert np.isfinite(energy).all() and (energy > 0).all()
            assert np.all(np.diff(energy) <= 0)
            np.testing.assert_allclose(recorded, energy / energy[0], rtol=1e-14, atol=0)
            assert t[0] == 0 and t[-1] == 0.5
            ax.semilogy(t, recorded, color=COLORS[index], linestyle=LINES[index],
                        linewidth=1.35, marker=MARKERS[index], markersize=3.4,
                        markerfacecolor="white", markeredgewidth=0.85,
                        label=rf"$\Delta t=1/{denominator}$")
        ax.set_xlabel(r"Time $t$")
        ax.set_ylabel(r"Normalized energy $E_h(t)/E_h(0)$")
        ax.set_xlim(-0.008, 0.508)
        ax.set_ylim(5e-6, 1.5)
        ax.set_xticks(np.arange(0, 0.501, 0.1))
        ax.yaxis.set_major_locator(LogLocator(base=10, numticks=7))
        ax.yaxis.set_minor_locator(LogLocator(base=10, subs=np.arange(2, 10), numticks=100))
        ax.yaxis.set_minor_formatter(NullFormatter())
        ax.tick_params(which="major", direction="out", width=0.7, length=3.5)
        ax.tick_params(which="minor", direction="out", width=0.5, length=2)
        ax.grid(axis="y", which="major", color="0.90", linewidth=0.55)
        ax.legend(loc="upper right", fontsize=9, handlelength=2.4,
                  labelspacing=0.6, borderaxespad=0.4)
        for extension in ("pdf", "svg", "png"):
            path = ROOT / "figures" / f"{scheme}_order_energy.{extension}"
            fig.savefig(path, dpi=400)
            if extension == "svg":
                path.write_text("\n".join(line.rstrip() for line in path.read_text().splitlines()) + "\n")
            print(path.relative_to(ROOT))
        plt.close(fig)


if __name__ == "__main__":
    main()
