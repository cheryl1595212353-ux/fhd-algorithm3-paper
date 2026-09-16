"""Regenerate both convergence figures without changing archived errors."""

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FixedFormatter, FixedLocator, NullFormatter, NullLocator
import numpy as np

from figure_style import configure_tex, save_figure


ROOT = Path(__file__).resolve().parents[1]
FIELDS = (
    ("u_h1_full_rel", r"$\mathbf{u}:H^1$"),
    ("p_tilde_l2_rel", r"$\widetilde{p}:L^2$"),
    ("omega_h1_full_rel", r"$\boldsymbol{\omega}:H^1$"),
    ("m_hdiv_rel", r"$\mathbf{m}:H(\mathrm{div})$"),
    ("k_l2_rel", r"$\mathbf{k}:L^2$"),
    ("phi_h1_rel", r"$\varphi:H^1$"),
    ("H_hcurl_rel", r"$\mathbf{H}:H(\mathrm{curl})$"),
)
COLORS = ("#2166ac", "#b35806", "#6a51a3", "#238b45", "#333333", "#b2182b", "#2166ac")
MARKERS = ("o", "s", "^", "D", "o", "s", "^")


def main():
    rows = json.loads((ROOT / "data/results.json").read_text())
    configure_tex(font_size=8, label_size=8)
    for scheme in ("first", "second"):
        selected = sorted((r for r in rows if r["scheme"] == scheme), key=lambda r: r["K"])
        x = np.array([r["K"] for r in selected])
        np.testing.assert_array_equal(x, [4, 8, 16, 32])
        fig, axes = plt.subplots(1, 2, figsize=(7.15, 3.45))
        fig.subplots_adjust(left=0.085, right=0.98, bottom=0.34, top=0.88, wspace=0.3)
        for panel, indices in enumerate((range(4), range(4, 7))):
            ax = axes[panel]
            for index in indices:
                field, label = FIELDS[index]
                values = np.array([r[field] for r in selected])
                assert np.isfinite(values).all() and (values > 0).all()
                ax.loglog(x, values, color=COLORS[index], marker=MARKERS[index],
                          markerfacecolor="white", markersize=4, linewidth=1.2,
                          linestyle="--" if index == 6 else "-", label=label)
            ax.loglog(x, (x[0] / x) * (0.20 if scheme == "first" else 0.05),
                      ":", color="0.45", linewidth=1, label=r"$K^{-1}$")
            if scheme == "second" or panel == 0:
                ax.loglog(x, (x[0] / x)**2 * (0.035 if scheme == "first" else 0.015),
                          "-.", color="0.65", linewidth=1, label=r"$K^{-2}$")
            ax.set_xlabel(r"Mesh resolution $K$")
            ax.set_ylabel("Relative error")
            ax.set_title(("(a) Primary fields", "(b) Curl field and magnetic potential/field")[panel],
                         loc="left", fontsize=8)
            ax.xaxis.set_major_locator(FixedLocator(x))
            ax.xaxis.set_major_formatter(FixedFormatter(["4", "8", "16", "32"]))
            ax.xaxis.set_minor_locator(NullLocator())
            ax.xaxis.set_minor_formatter(NullFormatter())
            ax.grid(which="major", color="0.91", linewidth=0.5)
            ax.tick_params(which="minor", bottom=False)
            ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.26), ncol=2,
                      fontsize=7, handlelength=2)
        save_figure(fig, ROOT / "figures" / f"{scheme}_order_errors")
        plt.close(fig)


if __name__ == "__main__":
    main()
