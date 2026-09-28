"""Rebuild the six application figures from archived, unmodified FE samples.

Matplotlib draws only geometry and colors. A small LaTeX/TikZ wrapper adds
the colorbar text in Latin Modern; manuscript captions are never baked in.
"""
import argparse,hashlib,itertools,json,shutil,subprocess
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.colors import Normalize,LinearSegmentedColormap
from matplotlib.patches import Polygon
from scipy.interpolate import RegularGridInterpolator

ROOT=Path(__file__).resolve().parents[1]
FIELDS=('u','m','omega')
CMAP=LinearSegmentedColormap.from_list('application',
    [(0.,'#426ba6'),(.25,'#a8c9df'),(.5,'#fff5c4'),(.70,'#ffd084'),(.86,'#ef8655'),(1.,'#c94129')])
STEP=np.array([[0,.1],[.2,.1],[.2,0],[1,0],[1,.2],[0,.2]])
BOX=np.array(list(itertools.product([0.,1.],[0.,.2],[0.,.2])))

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def frame_settings(kind):
    camera=np.array([-.9,-1.,.3] if kind=='step' else [-1.1,.315,1.]);camera/=np.linalg.norm(camera)
    vertical=np.array([0.,0.,1.] if kind=='step' else [0.,1.,0.])
    right=np.cross(vertical,camera);right/=np.linalg.norm(right)
    up=np.cross(camera,right);projection=np.stack([right,up],axis=1)
    project=lambda p:(np.asarray(p)-np.array([.5,.1,.1]))@projection
    if kind=='step':
        polys=[np.stack([STEP[:,0],np.full(6,y),STEP[:,1]],axis=1) for y in (0.,.2)]
        edges=[(p[i],p[(i+1)%6]) for p in polys for i in range(6)]+list(zip(*polys))
    else:edges=[(a,b) for i,a in enumerate(BOX) for b in BOX[i+1:] if np.count_nonzero(a!=b)==1]
    return camera,projection,project,edges

def wire(ax,kind,project,edges,front):
    depth=1 if kind=='step' else 2;segments=[]
    for a,b in edges:
        parts=[(a,b)]
        if min(a[depth],b[depth])<.1<max(a[depth],b[depth]):
            middle=a+(.1-a[depth])/(b[depth]-a[depth])*(b-a);parts=[(a,middle),(middle,b)]
        for p,q in parts:
            near=(p[depth]+q[depth])/2<=.1 if kind=='step' else (p[depth]+q[depth])/2>=.1
            if bool(near)==front:segments.append(project([p,q]))
    ax.add_collection(LineCollection(segments,colors='#969ba0' if front else '#c0c4c8',linewidths=.42,zorder=7 if front else 0))

def indices(shape,mask,slice_only):
    if slice_only:
        dims=[np.rint(np.linspace(.025,.975,25)*(shape[0]-1)).astype(int),[shape[1]//2],np.rint(np.linspace(.075,.925,9)*(shape[2]-1)).astype(int)]
    else:
        fractions=(np.linspace(.025,.975,20),[.1875,.5,.8125],np.linspace(.125,.875,5))
        dims=[np.rint(np.array(f)*(n-1)).astype(int) for f,n in zip(fractions,shape)]
    ids=np.arange(np.prod(shape)).reshape(shape)[np.ix_(*dims)].reshape(-1)
    return ids[mask.reshape(-1)[ids]]

def figure_body(kind,data,field,limit,path):
    shape=tuple(map(int,data['shape']));xyz=data['points'].reshape(*shape,3)
    values=data[field].reshape(*shape,3);mask=data.get('fluid_mask',np.ones(np.prod(shape),dtype=bool))
    camera,projection,project,edges=frame_settings(kind);sliced=kind=='step' and field=='m'
    selected=indices(shape,mask,sliced);points=data['points'][selected];v=data[field][selected]
    mag=np.linalg.norm(v,axis=1);nonzero=mag>1e-14;points=points[nonzero];v=v[nonzero];mag=mag[nonzero]
    fig=plt.figure(figsize=(12.8,3.6),facecolor='white');axs=[fig.add_axes([x,.22,.466,.74]) for x in (.022,.512)]
    boxxy=project(BOX);lo=boxxy.min(0);hi=boxxy.max(0)
    for ax in axs:
        ax.set_xlim(lo[0]-.035,hi[0]+.035);ax.set_ylim(lo[1]-.028,hi[1]+.035);ax.set_aspect('equal');ax.set_axis_off()
        wire(ax,kind,project,edges,False)
        if kind=='step' and field!='m':
            solid=np.array([[0,0,0],[.2,0,0],[.2,0,.1],[0,0,.1]])
            ax.add_patch(Polygon(project(solid),facecolor='#f6f7f8',edgecolor='#b4b8bd',linewidth=.4,zorder=1))
    center=project(points);d=((.09 if sliced else .06)*v/limit)@projection
    norm=Normalize(0,limit)
    axs[0].quiver(center[:,0],center[:,1],d[:,0],d[:,1],mag,cmap=CMAP,norm=norm,
        angles='xy',scale_units='xy',scale=1,pivot='mid',width=.00125,headwidth=3,
        headlength=4,headaxislength=3.6,minlength=0,minshaft=1,zorder=4)
    wire(axs[0],kind,project,edges,True)
    axes=(xyz[:,0,0,0],xyz[0,:,0,1],xyz[0,0,:,2])
    if kind=='step':
        assert abs(axes[1][shape[1]//2]-.1)<1e-12
        plane=xyz[:,shape[1]//2,:,:];surface=np.ma.masked_invalid(np.linalg.norm(values[:,shape[1]//2,:,:],axis=-1))
    else:
        xx,yy=np.meshgrid(np.linspace(axes[0][0],axes[0][-1],321),np.linspace(axes[1][0],axes[1][-1],81),indexing='ij')
        plane=np.stack([xx,yy,np.full_like(xx,.1)],axis=-1)
        surface=np.linalg.norm(RegularGridInterpolator(axes,values,bounds_error=True)(plane),axis=-1)
    uv=project(plane);color=axs[1].pcolormesh(uv[:,:,0],uv[:,:,1],surface,cmap=CMAP,norm=norm,shading='gouraud',rasterized=True,zorder=3)
    if kind=='step':
        outline=project(np.stack([STEP[:,0],np.full(6,.1),STEP[:,1]],axis=1));clip=Polygon(outline,facecolor='none',edgecolor='none')
        axs[1].add_patch(clip);color.set_clip_path(clip)
    wire(axs[1],kind,project,edges,True)
    # Three legible ticks at manuscript width; these do not change the color range.
    ticks=np.linspace(0,limit,3)
    for x in (.302,.792):
        ax=fig.add_axes([x,.175,.165,.026]);bar=fig.colorbar(matplotlib.cm.ScalarMappable(norm=norm,cmap=CMAP),cax=ax,orientation='horizontal',ticks=ticks)
        ax.set_xticklabels([]);ax.tick_params(length=1.5,pad=2,width=.4);bar.outline.set_linewidth(.35)
    fig.savefig(path,dpi=300,metadata={'CreationDate':None,'ModDate':None});plt.close(fig)
    return ticks,len(selected),camera.tolist()

def wrapper(stem,field,limit,ticks):
    symbol=r'\lvert\boldsymbol{'+(r'\omega' if field=='omega' else field)+r'}\rvert'
    nodes=[]
    for x in (.302,.792):
        for tick in ticks:
            xpos=12.8*(x+.165*float(tick)/limit)
            nodes.append(r'\node[anchor=north,inner sep=0pt,font=\fontsize{12}{13}\selectfont] at ('+f'{xpos:.8f},0.59000000'+r') {$'+f'{float(tick):g}'+r'$};')
        nodes.append(r'\node[anchor=east,inner sep=0pt,font=\fontsize{14}{15}\selectfont] at ('+f'{12.8*(x-.0132):.8f},{3.6*(.175+.013):.8f}'+r') {$'+symbol+r'$};')
    return '\n'.join([r'\documentclass[tikz,border=0pt]{standalone}',r'\usepackage[T1]{fontenc}',r'\usepackage{lmodern,amsmath,bm,graphicx}',r'\begin{document}',r'\begin{tikzpicture}[x=1in,y=1in]',r'\path[use as bounding box] (0,0.35) rectangle (12.8,3.6);',r'\node[anchor=south west,inner sep=0pt,overlay] at (0,0) {\includegraphics[width=12.8in]{'+stem+r'_body.pdf}};',*nodes,r'\end{tikzpicture}',r'\end{document}',''])

def main():
    p=argparse.ArgumentParser();p.add_argument('--engine',default=shutil.which('pdflatex') or shutil.which('tectonic'));a=p.parse_args()
    if not a.engine:raise SystemExit('Supply --engine /path/to/pdflatex or /path/to/tectonic')
    engine=str(Path(a.engine).resolve());data_dir=ROOT/'data/applications';build=ROOT/'build/applications';out=ROOT/'figures/applications'
    build.mkdir(parents=True,exist_ok=True);out.mkdir(parents=True,exist_ok=True)
    provenance=json.loads((data_dir/'provenance.json').read_text());records={}
    for kind,cfg in provenance['cases'].items():
        source=data_dir/cfg['snapshot'];assert sha(source)==cfg['snapshot_sha256']
        with np.load(source,allow_pickle=False) as z:data={k:z[k].copy() for k in z.files}
        assert float(data['time'])==cfg['snapshot_time']
        for field in FIELDS:
            stem=kind+'_'+field;ticks,count,camera=figure_body(kind,data,field,cfg['color_limits'][field],build/(stem+'_body.pdf'))
            tex=build/(stem+'.tex');tex.write_text(wrapper(stem,field,cfg['color_limits'][field],ticks))
            if 'tectonic' in Path(engine).name:cmd=[engine,'--keep-logs','--outdir',str(out),tex.name]
            else:cmd=[engine,'-interaction=nonstopmode','-halt-on-error','-output-directory',str(out),tex.name]
            result=subprocess.run(cmd,cwd=build,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
            (build/(stem+'_compile.txt')).write_text(result.stdout)
            if result.returncode:raise RuntimeError(result.stdout)
            pdf=out/(stem+'.pdf');assert pdf.exists()
            records[stem]={'pdf_sha256':sha(pdf),'snapshot_time':float(data['time']),'snapshot_sha256':sha(source),'color_limit':cfg['color_limits'][field],'arrow_points':count,'camera':camera,'labels':'LaTeX Latin Modern','temporal_interpolation':False,'embedded_caption':False}
            if shutil.which('pdftoppm'):subprocess.run(['pdftoppm','-scale-to','2400','-png','-singlefile',str(pdf),str(out/stem)],check=True)
            print(stem,flush=True)
        assert sha(source)==cfg['snapshot_sha256']
    (out/'manifest.json').write_text(json.dumps(records,indent=2)+'\n')

if __name__=='__main__':main()
