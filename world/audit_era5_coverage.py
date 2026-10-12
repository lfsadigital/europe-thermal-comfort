"""Audit all imported daily values, units/ranges and paired coverage."""
from pathlib import Path
import numpy as np,json
p=Path(__file__).resolve().parent;imp=json.loads((p/'.cache/era5/import.json').read_text());assert imp['completed_tasks']==imp['required_tasks'];t=np.load(p/'.cache/era5/temperature.npy',mmap_mode='r');r=np.load(p/'.cache/era5/rain.npy',mmap_mode='r');assert t.shape==r.shape==(2192,85699);counts=[];tlo=np.inf;thi=-np.inf;rlo=np.inf;rhi=-np.inf
for a in range(0,t.shape[1],2048):
 tt=t[:,a:a+2048];rr=r[:,a:a+2048];assert ((rr>=0)|np.isnan(rr)).all();assert ((tt>=-110)&(tt<=65)|np.isnan(tt)).all();good=np.isfinite(tt)&np.isfinite(rr);counts.extend(good.sum(axis=0).tolist());tlo=min(tlo,float(np.nanmin(tt)));thi=max(thi,float(np.nanmax(tt)));rlo=min(rlo,float(np.nanmin(rr)));rhi=max(rhi,float(np.nanmax(rr)))
result=dict(result='PASS',days=2192,cells=85699,paired_days_min=min(counts),paired_days_max=max(counts),complete_cells=sum(x==2192 for x in counts),temperature_c_min=tlo,temperature_c_max=thi,precipitation_mm_min=rlo,precipitation_mm_max=rhi)
(p/'share/era5-coverage-verification.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
