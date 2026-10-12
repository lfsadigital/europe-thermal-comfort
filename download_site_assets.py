"""Fetch the publicly hosted derived assets for local development (not for Git)."""
import argparse,json,urllib.request
from pathlib import Path
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--base-url',default='https://conforto-termico-europa.lfsadigital.chatgpt.site')
args=parser.parse_args();out=Path('site/dist/assets');out.mkdir(parents=True,exist_ok=True)
base=args.base_url.rstrip('/')+'/assets/'
def request(name):
 return urllib.request.Request(base+name,headers={'User-Agent':'Mozilla/5.0','Accept':'*/*'})
# These data retain the non-commercial E-OBS research/education terms.
with urllib.request.urlopen(request('metadata.json'),timeout=120) as r:meta=json.load(r)
assert meta['shape']==[370,700] and meta['total_days']==1827
files=['metadata.json','source.bin','country.bin','dynamic-nodes.bin','dynamic-weights.bin','map-lookup.gz','map-overlay.png','audit.json','dynamic-reference.json','rain-audit.json']
for period in ['mean','2020','2021','2022','2023','2024']:
 files.extend([f'hist-{period}.gz',f'rain-{period}.gz'])
 for metric in ['score','days']:
  for ext in ['bin','webp']:files.append(f'{metric}-{period}.{ext}')
for name in files:
 target=out/name;temporary=target.with_suffix(target.suffix+'.download')
 with urllib.request.urlopen(request(name),timeout=120) as r,temporary.open('wb') as f:
  expected=r.headers.get('Content-Length');size=0
  while block:=r.read(1024*1024):f.write(block);size+=len(block)
 if expected and size!=int(expected):raise RuntimeError(f'Incomplete download: {name}')
 temporary.replace(target);print(name,flush=True)
print('Local assets ready. Keep them out of Git; see DATA_LICENSE.md.')
