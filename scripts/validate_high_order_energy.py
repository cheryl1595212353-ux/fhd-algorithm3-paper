"""Validate the six supplemental energy cases without running FEM/MPI."""
import csv
import gzip
import hashlib
import json
import math
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data/energy_high_order'
sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
read=lambda path:json.loads(gzip.decompress(path.read_bytes()) if path.suffix=='.gz' else path.read_text())
START='\\subsection{Energy dissipation test}'
END='\\subsection{Magnetically forced flows'


def validate():
    provenance=read(DATA/'provenance.json')
    for name,digest in provenance['data_sha256'].items():
        assert sha(DATA/name)==digest,name
    sources=read(DATA/'solver_source_manifest.json')
    for order,hashes in provenance['solver_source_sha256_by_order'].items():
        assert sources[order]['files_sha256']==hashes
    for name in ['engine.py','model.py','linear.py','rk.py','spaces.py','rk_diagnostics.py','hardware.py','diagnostics.py']:
        assert provenance['solver_source_sha256_by_order']['3'][name]==provenance['solver_source_sha256_by_order']['4'][name],name
    manuscript=(ROOT/'main.tex').read_text()
    prefix,rest=manuscript.split(START,1)
    section,suffix=rest.split(END,1)
    assert hashlib.sha256(prefix.encode()).hexdigest()==provenance['protected_manuscript_prefix_sha256']
    assert hashlib.sha256(suffix.encode()).hexdigest()==provenance['protected_manuscript_suffix_sha256']
    assert sha(ROOT/'main.tex')==provenance['updated_manuscript_sha256']
    baseline=read(ROOT/'data/convergence_17/provenance.json')
    assert baseline['approved_manuscript_sha256']==provenance['previous_manuscript_sha256']
    with (DATA/'curves.csv').open(newline='') as stream:
        csvrows=list(csv.DictReader(stream))
    assert len(csvrows)==118
    archive=read(DATA/'cases.json.gz')
    assert set(archive)=={f'order{o}_dt1_{d}' for o in (3,4) for d in (16,32,64)}
    checkpoints=read(DATA/'raw_checkpoint_manifest.json')
    export=read(DATA/'EXPORT.json')
    assert export['raw_checkpoint_files']==len(checkpoints)
    assert export['raw_checkpoint_bytes']==sum(x['bytes'] for x in checkpoints.values())
    contract=read(DATA/'experiment_contract.json')
    assert all(value==1 for value in contract['parameters'].values())
    protocol=read(DATA/'recovery_protocol.json')
    assert protocol['guard_controls']['status']=='PASS' and protocol['guard_controls']['controller_queries']==0
    assert set(protocol['small_grid_replays'])=={'3','4'}
    for replay in protocol['small_grid_replays'].values():
        assert replay['slurm_state']=='COMPLETED' and replay['slurm_exit_code']=='0:0'
        assert replay['acceptance']['status']=='PASS'
        comparison=replay['acceptance']['small_grid_replay']
        assert comparison['combined_relative_coefficient_difference']<1e-11
        assert max(comparison['field_relative_differences'].values())<1e-9
    residuals=[]; balances=[]; initial_by_order={3:[],4:[]}; recovered=0
    for order in (3,4):
        for denominator in (16,32,64):
            key=f'order{order}_dt1_{denominator}'; case=archive[key]
            cfg=case['config']; accept=case['acceptance']; initial=case['initial']
            assert cfg['order']==order and cfg['K']==8 and cfg['dt']==1/denominator and cfg['T']==.5
            assert cfg['forcing']=='zero' and cfg['matrix_degree']==max(12,3*order+2)
            assert cfg['load_degree']==24 and cfg['init_degree']==28
            assert cfg['startup_corrections_per_step']==order and cfg['startup_steps']==order-1
            assert accept['status']=='PASS' and case['status']['status']=='complete'
            guard=accept['guard'];assert guard['reason'] is None and guard['exit_code']==0 and guard['error'] is None
            assert case['slurm_state']=='COMPLETED' and case['slurm_exit_code']=='0:0'
            assert case['status']['steps']==denominator//2 and case['status']['time']==.5
            # Cover every accepted time level, including t=0, and every MPI rank.
            checkpoint_root=case['archive_relative_path']+'/checkpoints/'
            expected_files=set()
            for n in range(denominator//2+1):
                directory=checkpoint_root+f'step_{n:05d}/'
                expected_files.add(directory+'state.json')
                expected_files.update(directory+f'slot{n%2}/rank{rank:04d}.npz' for rank in range(cfg['ranks']))
            assert {name for name in checkpoints if name.startswith(checkpoint_root)}==expected_files
            for name in expected_files:
                evidence=checkpoints[name]
                assert evidence['bytes']>0 and len(evidence['sha256'])==64
                int(evidence['sha256'],16)
            if 'resumed_from' in cfg:
                recovered+=1; recovery=case['recovery']; proof=recovery['restore']; accepted=recovery['acceptance']
                assert proof['status']=='PASS' and accepted['status']=='PASS'
                assert len(proof['ranks'])==cfg['ranks']
                assert all(r['geometry_and_all_dof_maps_exact'] and r['all_history_and_stage_coefficients_bitwise_equal_after_ghost_exchange'] for r in proof['ranks'])
                assert max(proof['energy_relative_differences'].values())<1e-12
                assert accepted['original_files_verified_unchanged']==len(recovery['prefix_copy_sha256'])
                assert accepted['copied_prefix_files_verified']==len(recovery['prefix_copy_sha256'])
                assert accepted['resume_driver_sha256']==protocol['implementation_sha256']['resume_energy.py']
                assert recovery['interrupted_guard']['reason']=='monitor_error'
                assert 'TimeoutExpired' in recovery['interrupted_guard']['error'] and 'scontrol' in recovery['interrupted_guard']['error']
            assert cfg['source_sha256']==provenance['solver_source_sha256_by_order'][str(order)]
            assert max(initial['constraints_zero'].values())<1e-8
            for name,check in initial.items():
                if isinstance(check,dict) and 'relative' in check:assert check['relative']<1e-8,name
            assert initial['homogeneous_boundary_error']<1e-12
            initial_by_order[order].append(initial['energy'])
            rows=[r for r in csvrows if int(r['order'])==order and int(r['dt_denominator'])==denominator]
            rows.sort(key=lambda r:int(r['step']))
            assert len(rows)==denominator//2+1 and len(case['steps'])==denominator//2
            e0=float(rows[0]['energy']);previous=e0;diss=0.
            for n,row in enumerate(rows):
                assert int(row['step'])==n and float(row['time'])==n/denominator
                energy=float(row['energy']);assert math.isfinite(energy) and energy>0
                assert energy<=previous*(1+1e-10)
                assert math.isclose(float(row['normalized_energy']),energy/e0,rel_tol=1e-13)
                if n:
                    raw=case['steps'][n-1];en=raw['energy']
                    assert raw['step']==n and raw['time']==float(row['time'])
                    assert float(row['energy'])==en['current']
                    assert abs(en['previous']-previous)<=1e-12*max(e0,previous)
                    assert en['load']==0 and en['dissipation']>=0 and en['relative_gap']<5e-8
                    assert raw['homogeneous_boundary_error']<1e-12
                    assert len(raw['corrections'])==(order if n<order else 1)
                    for correction in raw['corrections']:
                        residual=correction['true_residual']['relative']
                        assert math.isfinite(residual) and residual<1e-8
                        residuals.append(residual)
                    balances.append(en['relative_gap']);diss+=en['dissipation']
                    for field in ('dissipation','load','gap','relative_gap'):
                        assert float(row[field])==en[field]
                assert math.isclose(float(row['cumulative_dissipation']),diss,rel_tol=1e-13,abs_tol=1e-30)
                previous=energy
            assert abs(previous-e0+diss)/e0<1e-7
    for energies in initial_by_order.values():
        assert (max(energies)-min(energies))/max(energies)<1e-12
    for gate in read(DATA/'small_grid_gates.json').values():
        assert gate['acceptance']['status']=='PASS'
        assert len(gate['acceptance']['monolithic_differences'])==2
        assert max(gate['acceptance']['monolithic_differences'])<1e-8
        assert gate['slurm_state']=='COMPLETED' and gate['slurm_exit_code']=='0:0'
        assert gate['config']['source_sha256']==provenance['solver_source_sha256_by_order'][str(gate['config']['order'])]
        assert max(s['energy_quadrature_relative_difference'] for s in gate['steps'])<1e-8
    figure_dir=ROOT/'figures/energy_high_order';proof=read(figure_dir/'provenance.json')
    assert proof['script_sha256']==sha(ROOT/'scripts/plot_energy_high_order.py')
    for name,digest in proof['input_sha256'].items():assert sha(ROOT/name)==digest,name
    for stem,outputs in proof['outputs_sha256'].items():
        for suffix,digest in outputs.items():assert sha(figure_dir/(stem+suffix))==digest
    return {'cases':6,'strictly_recovered_cases':recovered,'curve_rows':118,'steps':112,'small_grid_gates':2,
        'maximum_true_relative_residual':max(residuals),'maximum_energy_relative_gap':max(balances),
        'monotonic_unforced_energy':True,'original_manuscript_outside_energy_section_unchanged':True,
        'raw_checkpoints':'Preserved on the compute server; manifest with sizes and SHA256 included.'}


if __name__=='__main__':print(json.dumps(validate(),indent=2))
