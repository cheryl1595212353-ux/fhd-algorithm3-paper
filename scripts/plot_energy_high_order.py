"""Draw archived order 1-4 energy curves; never execute or reintegrate a solver."""
import csv
import hashlib
import json
import math
import os
import platform
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
os.environ.setdefault('MPLCONFIGDIR',str(ROOT/'.mplconfig'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import LogLocator, NullFormatter
import numpy as np

COLORS=('#35659B','#478274','#B5674C')
MARKERS=('o','s','^')
LINES=('-','--','-.')
LABELS={1:'First',2:'Second',3:'Third',4:'Fourth'}
sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()


def load_curves():
    with (ROOT/'data/energy/curves.csv').open(newline='') as stream:
        old=list(csv.DictReader(stream))
    with (ROOT/'data/energy_high_order/curves.csv').open(newline='') as stream:
        new=list(csv.DictReader(stream))
    curves={}
    for order in (1,2,3,4):
        for denominator in (16,32,64):
            if order<3:
                rows=[r for r in old if r['scheme']==LABELS[order].lower() and float(r['dt'])==1/denominator]
                tkey,ekey='t','energy_normalized'
            else:
                rows=[r for r in new if int(r['order'])==order and float(r['dt'])==1/denominator]
                tkey,ekey='time','normalized_energy'
            rows.sort(key=lambda r:int(r['step']))
            assert len(rows)==denominator//2+1
            t=np.array([float(r[tkey]) for r in rows])
            en=np.array([float(r['energy']) for r in rows])
            normalized=np.array([float(r[ekey]) for r in rows])
            assert np.isfinite(en).all() and (en>0).all()
            assert np.all(np.diff(en)<=en[:-1]*1e-10)
            np.testing.assert_allclose(t,np.arange(len(rows))/denominator,rtol=0,atol=1e-14)
            np.testing.assert_allclose(normalized,en/en[0],rtol=1e-13,atol=0)
            assert t[-1]==.5
            curves[order,denominator]=(t,normalized)
    return curves


def draw(ax,curves,order,limits):
    for index,denominator in enumerate((16,32,64)):
        t,en=curves[order,denominator]
        ax.semilogy(t,en,color=COLORS[index],linestyle=LINES[index],linewidth=1.35,
            marker=MARKERS[index],markersize=3.4,markerfacecolor='white',markeredgewidth=.85,
            label=rf'$\Delta t=1/{denominator}$')
    ax.set_xlabel(r'Time $t$')
    ax.set_ylabel(r'Normalized energy $E_h(t)/E_h(0)$')
    ax.set_xlim(-.008,.508);ax.set_ylim(*limits)
    ax.set_xticks(np.arange(0,.501,.1))
    ax.yaxis.set_major_locator(LogLocator(base=10,numticks=7))
    ax.yaxis.set_minor_locator(LogLocator(base=10,subs=np.arange(2,10),numticks=100))
    ax.yaxis.set_minor_formatter(NullFormatter())
    ax.tick_params(which='major',direction='out',width=.7,length=3.5)
    ax.tick_params(which='minor',direction='out',width=.5,length=2)
    ax.grid(axis='y',which='major',color='.90',linewidth=.55)
    ax.legend(loc='upper right',fontsize=9.5,handlelength=2.4,labelspacing=.6,borderaxespad=.4)


def save(fig,stem):
    for suffix in ('.pdf','.png','.svg'):
        metadata={'CreationDate':None,'ModDate':None} if suffix=='.pdf' else ({'Date':None} if suffix=='.svg' else None)
        fig.savefig(stem.with_suffix(suffix),dpi=300,metadata=metadata)
    plt.close(fig)
    return {suffix:sha(stem.with_suffix(suffix)) for suffix in ('.pdf','.png','.svg')}


def main():
    curves=load_curves()
    minimum=min(float(en.min()) for t,en in curves.values())
    limits=(min(5e-6,10**math.floor(math.log10(minimum))*.5),1.5)
    plt.rcParams.update({'font.family':'DejaVu Serif','mathtext.fontset':'dejavuserif',
        'font.size':9.5,'axes.labelsize':10.5,'axes.linewidth':.7,
        'axes.spines.top':False,'axes.spines.right':False,'legend.frameon':False,
        'pdf.fonttype':42,'svg.fonttype':'path','svg.hashsalt':'fhd-energy-orders-1to4'})
    out=ROOT/'figures/energy_high_order';out.mkdir(parents=True,exist_ok=True)
    outputs={}
    for order in (1,2,3,4):
        fig,ax=plt.subplots(figsize=(3.6,2.8),layout='constrained')
        draw(ax,curves,order,limits)
        stem=out/f'{LABELS[order].lower()}_order_energy'
        outputs[stem.name]=save(fig,stem)
    fig,axes=plt.subplots(2,2,figsize=(7.4,6.0),layout='constrained')
    for order,ax in enumerate(axes.flat,1):
        draw(ax,curves,order,limits)
        ax.set_title(f'({chr(96+order)}) {LABELS[order]}-order scheme',fontsize=11)
    outputs['energy_orders_1to4']=save(fig,out/'energy_orders_1to4')
    proof={'input_sha256':{str(p.relative_to(ROOT)):sha(p) for p in [ROOT/'data/energy/curves.csv',ROOT/'data/energy_high_order/curves.csv']},
        'script_sha256':sha(Path(__file__)),'outputs_sha256':outputs,
        'orders':[1,2,3,4],'K':8,'T':.5,'time_steps':[1/16,1/32,1/64],
        'common_ylim':list(limits),'normalization':'each curve divided by its own discrete initial energy',
        'interpretation':'Each order uses its matching spatial spaces; not an isolated temporal accuracy comparison.',
        'python':platform.python_version(),'matplotlib':matplotlib.__version__,'numpy':np.__version__,
        'plotting_recomputes_solver':False}
    (out/'provenance.json').write_text(json.dumps(proof,indent=2)+'\n')
    print(json.dumps(proof,indent=2))


if __name__=='__main__':main()
