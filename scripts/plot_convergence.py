"""Redraw frozen 17-case errors; no solver, fitting, smoothing or new norms."""
import argparse
import hashlib
import json
import math
import os
import platform
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault('MPLCONFIGDIR', str(ROOT / '.mplconfig'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from convergence_data import DATA, FIELDS, GRIDS, load_checked, sha256

LABELS = (r'$u:\ H^1$', r'$\widetilde p_{\mathrm{stage}}:\ L^2$', r'$\omega:\ H^1$',
          r'$m:\ H(\mathrm{div})$', r'$H:\ H(\mathrm{curl})$', r'$k:\ L^2$', r'$\varphi:\ H^1$')
COLORS = ('#bc6c25', '#237a57', '#2771a5', '#794b9d')
MARKERS = ('o', 's', '^', 'D')


def draw(data, kind, out_dir):
    plt.rcParams.update({'font.family': 'DejaVu Serif', 'mathtext.fontset': 'dejavuserif',
                         'font.size': 9, 'pdf.fonttype': 42})
    fig, axes = plt.subplots(2, 4, figsize=(12.5, 6.3))
    axes = axes.ravel()
    for index, (field, label) in enumerate(zip(FIELDS, LABELS)):
        ax = axes[index]
        for series, color, marker in zip(data['series'], COLORS, MARKERS):
            x = [row['K'] for row in series['rows']]
            y = [row['errors'][field][kind] for row in series['rows']]
            ax.loglog(x, y, color=color, marker=marker, ms=4, lw=1.45, label=f"Order {series['order']}")
            rate = series['rows'][-1]['errors'][field][kind + '_rate']
            ax.annotate(f'{rate:.2f}', (math.sqrt(x[-2] * x[-1]), .75 * math.sqrt(y[-2] * y[-1])),
                        color=color, ha='center', va='top', fontsize=8)
        ax.set_xscale('log', base=2)
        ax.set_xticks([2, 4, 8, 16, 32], ['2', '4', '8', '16', '32'])
        ax.minorticks_off()
        ax.set_title(label, fontsize=11)
        ax.set_xlabel(r'$K$')
        ax.grid(True, alpha=.2)
        if index % 4 == 0:
            ax.set_ylabel(kind.capitalize() + ' error')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
    axes[7].axis('off')
    handles, labels = axes[0].get_legend_handles_labels()
    axes[7].legend(handles, labels, loc='upper left', frameon=False, fontsize=9,
                   ncol=2, columnspacing=.8, handlelength=1.7)
    notes = ['One continuous reference problem', r'$T=2,\quad\Delta t=1/(2K)$',
             'Labels: measured finest-segment rates.',
             'Pressure: actual RK-stage weighted norm.',
             'Other fields: terminal norms.', 'Joint space/time refinement.']
    axes[7].text(.03, .65, '\n'.join(notes), transform=axes[7].transAxes, va='top', fontsize=8.2, linespacing=1.5)
    fig.suptitle('FHD orders 1-4 on the same manufactured solution', fontsize=14, y=.99)
    fig.tight_layout(rect=(0, 0, 1, .95), h_pad=2, w_pad=1.5)
    out_dir.mkdir(parents=True, exist_ok=True)
    stem = out_dir / (kind + '_errors')
    for suffix in ('.png', '.pdf'):
        metadata = {'CreationDate': None, 'ModDate': None} if suffix == '.pdf' else None
        fig.savefig(stem.with_suffix(suffix), dpi=300, bbox_inches='tight', metadata=metadata)
    plt.close(fig)
    proof = {'input': 'data/convergence_17/CONVERGENCE_17_CASES.json',
             'input_sha256': sha256(DATA / 'CONVERGENCE_17_CASES.json'),
             'script_sha256': sha256(__file__), 'orders': [1, 2, 3, 4], 'K': GRIDS,
             'norms': FIELDS, 'error_kind': kind, 'python': platform.python_version(),
             'matplotlib': matplotlib.__version__, 'numpy': np.__version__,
             'annotations': 'Measured finest adjacent-grid rates; not enforced targets',
             'outputs_sha256': {s: sha256(stem.with_suffix(s)) for s in ('.png', '.pdf')},
             'numerical_recomputation': False}
    stem.with_suffix('.source.json').write_text(json.dumps(proof, indent=2) + '\n')
    return str(stem)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out-dir', type=Path, default=ROOT / 'figures/convergence_17')
    parser.add_argument('--kind', choices=('absolute', 'relative', 'both'), default='both')
    args = parser.parse_args()
    data, _, _ = load_checked()
    kinds = ('absolute', 'relative') if args.kind == 'both' else (args.kind,)
    print(json.dumps({'rendered': [draw(data, kind, args.out_dir) for kind in kinds]}, indent=2))


if __name__ == '__main__':
    main()
