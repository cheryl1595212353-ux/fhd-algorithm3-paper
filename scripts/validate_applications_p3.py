"""Check the published figure files and exact manuscript addition boundaries."""
from pathlib import Path
import hashlib,json,re
ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data/applications_p3_K8'
FIG=ROOT/'figures/applications_p3_K8'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def validate_manuscript_extension(text):
    proof=json.loads((DATA/'MANUSCRIPT_EXTENSION.json').read_text())
    for name,digest in proof['inserted_blocks_sha256'].items():
        matches=list(re.finditer(r'% BEGIN PUBLICATION_'+name+r'\n.*?% END PUBLICATION_'+name+r'\n',text,re.S))
        assert len(matches)==1,name
        match=matches[0];assert hashlib.sha256(match.group().encode()).hexdigest()==digest
        text=text[:match.start()]+text[match.end():]
    assert hashlib.sha256(text.encode()).hexdigest()==proof['base_main_sha256']
    return text

def validate():
    validate_manuscript_extension((ROOT/'main.tex').read_text())
    manifest=json.loads((FIG/'RENDER_MANIFEST.json').read_text())
    assert manifest['passed'] and manifest['no_pde_solve'] and len(manifest['figures'])==6
    assert set(manifest['figures'])=={c+'_'+f for c in ('channel','step_channel') for f in ('u','m','omega')}
    for name,entry in manifest['figures'].items():
        expected=(117,0.585) if name.startswith('step_') else (128,0.640)
        assert (entry['step'],entry['time'])==expected and not entry['temporal_interpolation']
        assert entry['section']==('y=0.1' if name.startswith('step_') else 'z=0.1')
        assert max(entry['section_sample_maximum'],entry['volume_sample_maximum'])<=entry['color_limits'][1]
        for suffix,digest in entry['outputs_sha256'].items():assert sha(FIG/(name+suffix))==digest
    proof=json.loads((DATA/'PUBLICATION_VALIDATION.json').read_text());assert proof['passed']
    for name,digest in proof['outputs_sha256'].items():assert sha(ROOT/name)==digest
    return {'passed':True,'cases':2,'figures':6,'previous_manuscript_restored_exactly':True,
            'PDF_PNG_hashes_checked':True,'scope':'Published figure integrity; full numerical samples/audits remain separately archived.'}

if __name__=='__main__':print(json.dumps(validate(),indent=2))
