"""Restore only the small default maps; never download the climate archive."""
import hashlib,json,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent
manifest=json.loads((ROOT/'site/docs/era5-data-manifest.json').read_text())['sha256']
defaults={name:digest for name,digest in manifest.items() if name.startswith(('score-','days-','coverage-')) and name.endswith('.bin')}
assert len(defaults)==21
for name,digest in defaults.items():
    path=ROOT/'site/dist/assets'/name
    if path.exists() and hashlib.sha256(path.read_bytes()).hexdigest()==digest:
        continue
    request=urllib.request.Request('https://comfy.lfsadigital.com/assets/'+name,headers={'User-Agent':'ComfyDays-CodeRestore/1.0','Accept':'application/octet-stream'})
    with urllib.request.urlopen(request,timeout=90) as response:
        data=response.read()
    if hashlib.sha256(data).hexdigest()!=digest:
        raise ValueError('Published data no longer matches this code version: '+name)
    path.parent.mkdir(parents=True,exist_ok=True)
    temporary=path.with_suffix(path.suffix+'.tmp')
    temporary.write_bytes(data)
    temporary.replace(path)
    print('Restored',name,len(data),'bytes')
print('Verified',len(defaults),'default map arrays')
