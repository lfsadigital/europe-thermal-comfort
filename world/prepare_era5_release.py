"""Install fully verified staging data into the Site, without publishing."""
import json,hashlib,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parent;staging=ROOT/'era5-staging/assets';site=ROOT/'site';m=json.loads((staging/'metadata.json').read_text());imp=json.loads((ROOT/'.cache/era5/import.json').read_text())
assert imp['completed_tasks']==imp['required_tasks']==47808
assert m['source_model']=='ERA5' and m['nodes']==85699
for period in ['mean']+list(map(str,range(2020,2026))):
 v=json.loads((ROOT/f'share/era5-core-{period}-verification.json').read_text());assert v['result']=='PASS' and v['maxError']<1e-9
assert len(json.loads((ROOT/'share/era5-bulk-api-validation.json').read_text()))==12
names=[f'{metric}-{period}.bin' for period in ['mean']+list(map(str,range(2020,2026))) for metric in ['score','days','coverage']]+['metadata.json','audit.json','score-audit.json']
for name in names:shutil.copy2(staging/name,site/'dist/assets'/name)
chunks=[f for files in m['period_files'].values() for f in files];assert len(chunks)==294 and len(set(chunks))==294
for name in chunks:shutil.copy2(staging/name,site/'climate-data'/name)
assert set(p.name for p in (site/'climate-data').glob('climate-*.gz'))==set(chunks)
manifest={'/era5-v1/'+name:{'hash':hashlib.md5((staging/name).read_bytes()).hexdigest(),'size':(staging/name).stat().st_size} for name in chunks}
(ROOT/'era5-staging/upload-manifest.json').write_text(json.dumps(manifest))
(site/'docs/era5-import.json').write_text(json.dumps(imp,indent=2)+'\n')
(site/'docs/era5-data-manifest.json').write_text(json.dumps({'source':m['source'],'sha256':{name:hashlib.sha256((staging/name).read_bytes()).hexdigest() for name in names+chunks}},indent=2)+'\n')
print('READY:',len(names),'default scientific assets;',len(chunks),'dynamic chunks;',sum(x['size'] for x in manifest.values()),'compressed bytes')
