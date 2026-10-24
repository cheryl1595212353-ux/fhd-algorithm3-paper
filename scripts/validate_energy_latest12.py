"""Validate new order1/2 data and its extension of the protected manuscript."""
import csv,gzip,hashlib,json,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];DATA=ROOT/'data/energy_latest_12'
read=lambda p:json.loads(gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def validate():
    p=read(DATA/'provenance.json');ex=read(DATA/'EXPORT.json')
    assert ex['status']=='ALL_SIX_ACCEPTED' and ex['curve_rows']==118
    for name,digest in p['data_sha256'].items():assert sha(DATA/name)==digest,name
    for name,digest in p['protected_existing_data_sha256'].items():assert sha(ROOT/name)==digest,name
    assert sha(ROOT/'main.tex')==p['updated_manuscript_sha256']
    previous=read(ROOT/'data/energy_high_order/provenance.json')
    assert p['previous_manuscript_sha256']==previous['updated_manuscript_sha256']
    text=(ROOT/'main.tex').read_text();prefix,tail=text.split('\\subsection{Energy dissipation test}',1);_,suffix=tail.split('\\subsection{Magnetically forced flows',1)
    assert hashlib.sha256(prefix.encode()).hexdigest()==previous['protected_manuscript_prefix_sha256']
    assert hashlib.sha256(suffix.encode()).hexdigest()==previous['protected_manuscript_suffix_sha256']
    line=read(DATA/'solver_lineage.json');contract=read(DATA/'experiment_contract.json')
    prior=read(ROOT/'data/energy_high_order/experiment_contract.json')
    assert contract['parameters']==prior['parameters']
    assert line['common_core_byte_identical_for_orders1and2']
    old=read(ROOT/'data/energy_high_order/cases.json.gz')
    assert line['reference_initial_field_module_sha256']==old['order3_dt1_16']['config']['source_sha256']['model.py']
    source=read(DATA/'source_manifest.json')['files']
    assert all(source['core_src/'+name]==digest for name,digest in line['core_sha256'].items())
    archive=read(DATA/'cases.json.gz');gates=read(DATA/'small_grid_gates.json');raw=read(DATA/'raw_checkpoint_manifest.json')
    assert len(raw)==ex['raw_checkpoint_files'] and sum(x['bytes'] for x in raw.values())==ex['raw_checkpoint_bytes']
    assert set(archive)=={f'order{o}_dt1_{d}' for o in (1,2) for d in (16,32,64)}
    rows=list(csv.DictReader((DATA/'curves.csv').open(newline='')));assert len(rows)==118
    residuals=[];balances=[]
    for key,c in archive.items():
        cfg=c['config'];order=cfg['order'];den=round(1/cfg['dt']);acc=c['acceptance'];initial=c['initial']
        assert cfg['K']==8 and cfg['T']==.5 and cfg['steps']==den//2 and cfg['ranks']==32
        assert cfg['problem']['forcing']=='f=g=r=He=Het=Ge=0'
        assert c['status']['status']=='complete' and c['status']['steps']==den//2 and c['status']['time']==.5
        assert c['accounting']['state']=='COMPLETED' and c['accounting']['exit_code']=='0:0' and acc['status']=='PASS'
        assert acc['guard']['reason'] is None and acc['guard']['exit_code']==0 and acc['guard']['error'] is None
        assert acc['guard']['job_cgroup_peak_bytes']<=acc['guard']['guard_bytes']
        for name,digest in cfg['source_sha256'].items():assert source[name]==digest,name
        assert max(initial['constraints_zero'].values())<1e-8 and initial['homogeneous_boundary_error']<1e-12
        assert all(x['true_residual']['relative']<1e-10 for x in initial['projections'].values())
        curve=sorted((r for r in rows if int(r['order'])==order and int(r['dt_denominator'])==den),key=lambda r:int(r['step']))
        assert len(curve)==den//2+1 and len(c['steps'])==den//2
        e0=initial['energy'];prev=e0;diss=0.;num=0.
        for n,r in enumerate(curve):
            en=float(r['energy']);assert int(r['step'])==n and float(r['time'])==n/den
            assert math.isfinite(en) and 0<en<=prev*(1+1e-10)
            assert math.isclose(float(r['normalized_energy']),en/e0,rel_tol=1e-13)
            if n:
                s=c['steps'][n-1];v=s['energy'];assert s['step']==n and s['time']==n/den and en==v['current']
                assert abs(v['previous']-prev)<1e-12*max(e0,prev)
                assert v['forcing']==v['lifting_work']==0 and v['dissipation']>=0 and v['RK_numerical_dissipation']>=-1e-25
                assert s['homogeneous_boundary_error']<1e-12
                gap=en-prev+v['dissipation']+v['RK_numerical_dissipation'];scale=en+prev+v['dissipation']+abs(v['RK_numerical_dissipation'])
                assert abs(gap)/scale<5e-8 and abs(v['boundary_work'])/scale<1e-12
                assert v['zero_input_relative_gap']<5e-8
                assert float(r['relative_gap'])==v['zero_input_relative_gap'] and float(r['gap'])==v['zero_input_gap']
                assert float(r['dissipation'])==v['dissipation'] and float(r['numerical_dissipation'])==v['RK_numerical_dissipation']
                assert float(r['load'])==v['forcing']+v['boundary_work']+v['lifting_work']
                assert len(s['corrections'])==(order if n<order else 1)
                for correction in s['corrections']:
                    for res in (correction['refinement'][-1]['true_residual']['relative'],correction['physical_unpack_residual']['relative'],correction['uneliminated_free_residual_relative']):
                        assert math.isfinite(res) and res<1e-8;residuals.append(res)
                balances.append(v['zero_input_relative_gap']);diss+=v['dissipation'];num+=v['RK_numerical_dissipation']
            assert math.isclose(float(r['cumulative_dissipation']),diss,rel_tol=1e-13,abs_tol=1e-30)
            assert math.isclose(float(r['cumulative_numerical_dissipation']),num,rel_tol=1e-13,abs_tol=1e-30)
            prev=en
        assert abs(prev-e0+diss+num)/e0<1e-7
        base=c['archive_relative_path']+'/checkpoints/';expected=set()
        for n in range(den//2+1):
            prefix=base+f'step_{n:05d}/';expected.add(prefix+'state.json');expected.update(prefix+f'rank{i:04d}.npz' for i in range(32))
        assert {name for name in raw if name.startswith(base)}==expected
        assert all(raw[name]['bytes']>0 and len(raw[name]['sha256'])==64 for name in expected)
    assert set(gates)=={'1','2'}
    for c in gates.values():
        a=c['acceptance'];assert a['status']=='PASS' and len(a['monolithic_differences'])==2 and max(a['monolithic_differences'])<1e-8
        assert max(a['quadrature_differences'])<1e-8
        assert c['accounting']['state']=='COMPLETED' and c['accounting']['exit_code']=='0:0'
    f=ROOT/'figures/energy_all_orders';proof=read(f/'provenance.json')
    assert proof['script_sha256']==sha(ROOT/'scripts/plot_energy_all_orders.py')
    for name,digest in proof['input_sha256'].items():assert sha(ROOT/name)==digest
    for stem,outputs in proof['outputs_sha256'].items():
        for suffix,digest in outputs.items():assert sha(f/(stem+suffix))==digest
    return {'status':'PASS','cases':6,'steps':112,'rows':118,'latest_core_verified':True,'old_data_preserved':True,
            'maximum_true_relative_residual':max(residuals),'maximum_energy_relative_gap':max(balances),
            'initial_shapes_match_orders3and4':True,'zero_input_energy_nonincreasing':True}
if __name__=='__main__':print(json.dumps(validate(),indent=2))
