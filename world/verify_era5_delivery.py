"""Verify every ERA5 dynamic asset at the live Cloudflare endpoint."""
import json,hashlib,concurrent.futures,time,requests
from pathlib import Path
ROOT=Path(__file__).resolve().parent;m=json.loads((ROOT/'era5-staging/upload-manifest.json').read_text());base='https://comfy-days-climate-era5.lfsalmeida92.workers.dev';results=[]
def check(item):
 path,info=item
 for attempt in range(5):
  try:
   r=requests.get(base+path,timeout=(15,90));r.raise_for_status();assert r.headers.get('Access-Control-Allow-Origin')=='*';assert 'immutable' in r.headers.get('Cache-Control','');assert len(r.content)==info['size'];assert hashlib.md5(r.content).hexdigest()==info['hash'];return dict(path=path,bytes=len(r.content),sha256=hashlib.sha256(r.content).hexdigest())
  except Exception:
   if attempt==4:raise
   time.sleep(2*(attempt+1))
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as p:
 for i,future in enumerate(concurrent.futures.as_completed([p.submit(check,item) for item in m.items()]),1):
  row=future.result();results.append(row)
  if i%42==0:print('Verified live hashes/CORS',i,'/',len(m),flush=True)
(ROOT/'share/era5-delivery-verification.json').write_text(json.dumps(dict(result='PASS',endpoint=base,files=results),indent=2)+'\n');print('PASS all',len(results),'live ERA5 assets')
