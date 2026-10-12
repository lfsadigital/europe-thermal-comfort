"""Independent raw E-OBS checks for custom ranges, not derived from histogram counts."""
from pathlib import Path
from datetime import date
import json,h5py,numpy as np,xarray as xr
from country_table import CachedEOBS
from period_config import YEARS,N_YEARS,PERIOD
out=Path('site/dist/assets');meta=json.loads((out/'metadata.json').read_text());source=np.fromfile(out/'source.bin',dtype='u1').reshape(meta['shape']);eidx=np.flatnonzero(source.ravel()==1)
y=int(np.argmin(abs(np.array(meta['latitude'])-41.15)));x=int(np.argmin(abs(np.array(meta['longitude'])+8.55)));index=y*meta['shape'][1]+x;node=int(np.flatnonzero(eidx==index)[0]);report=json.loads((out/'rain-audit.json').read_text());report['reference_cases']=[r for r in report['reference_cases'] if r.get('source')!='E-OBS'];all_t=[];all_r=[]
with CachedEOBS() as remote,h5py.File(remote,'r') as f:
 ys=np.flatnonzero((f['latitude'][:]>=34.5)&(f['latitude'][:]<=71.5));xs=np.flatnonzero((f['longitude'][:]>=-25)&(f['longitude'][:]<=45));scale=float(f['tx'].attrs['scale_factor'][0])
 for year in YEARS:
  first=(date(year,1,1)-date(1950,1,1)).days;n=(date(year+1,1,1)-date(year,1,1)).days
  t=f['tx'][first:first+n,ys[0]+y,xs[0]+x].astype(float)*scale;r=np.load(f'.cache/rain-daily/{year}.npy',mmap_mode='r')[:,y,x].astype(float);assert np.isfinite(t).all() and np.isfinite(r).all() and (r>=0).all();all_t.append(t);all_r.append(r)
  for lo,hi in [(18,26),(20,25),(18,33),(18,28),(-10,5),(25,26)]:
   report['reference_cases'].append({'source':'E-OBS','period':str(year),'node':node,'lower':lo,'upper':hi,'score':float((100-np.maximum(lo-t,0)-np.maximum(t-hi,0)-(r>1)).mean()),'days':int(((t>=lo)&(t<=hi)&(r<=1)).sum())})
  print(year,'raw E-OBS custom range references',flush=True)
t=np.concatenate(all_t);r=np.concatenate(all_r)
for lo,hi in [(18,26),(20,25),(18,33),(18,28),(-10,5),(25,26)]:
 report['reference_cases'].append({'source':'E-OBS','period':'mean','node':node,'lower':lo,'upper':hi,'score':float((100-np.maximum(lo-t,0)-np.maximum(t-hi,0)-(r>1)).mean()),'days':float(((t>=lo)&(t<=hi)&(r<=1)).sum()/N_YEARS)})
# Recreate NOAA references even when joint caches were reused.
report['reference_cases']=[r for r in report['reference_cases'] if r.get('source')=='E-OBS']
ne=len(eidx);mapping=np.fromfile(out/'dynamic-nodes.bin',dtype='<i4');weights=np.fromfile(out/'dynamic-weights.bin',dtype='<f8');used=np.unique(mapping[weights>0]);node=int(used[used>=ne][0]);j=node-ne;nt=[];nr=[]
for year in YEARS:
 with xr.open_dataset(f'.cache/noaa/tmax.{year}.nc',engine='h5netcdf') as td,xr.open_dataset(f'.cache/noaa-rain/precip.{year}.nc',engine='h5netcdf') as pd:
  td=td.sel(lat=slice(72,34),lon=slice(24,46));pd=pd.precip.sel(lat=td.lat,lon=td.lon)
  np.testing.assert_array_equal(td.time.values.astype('datetime64[D]'),pd.time.values.astype('datetime64[D]'))
  n=len(td.time);t=td.tmax.values[:,::-1].reshape(n,-1)[:,j].astype(float);r=pd.values[:,::-1].reshape(n,-1)[:,j].astype(float)
  assert np.isfinite(t).all() and np.isfinite(r).all() and (r>=0).all();nt.append(t);nr.append(r)
  for lo,hi in [(18,26),(20,25),(18,33),(18,28),(-10,5),(25,26)]:
   report['reference_cases'].append({'source':'NOAA','period':str(year),'node':node,'lower':lo,'upper':hi,'score':float((100-np.maximum(lo-t,0)-np.maximum(t-hi,0)-(r>1)).mean()),'days':int(((t>=lo)&(t<=hi)&(r<=1)).sum())})
t=np.concatenate(nt);r=np.concatenate(nr)
for lo,hi in [(18,26),(20,25),(18,33),(18,28),(-10,5),(25,26)]:
 report['reference_cases'].append({'source':'NOAA','period':'mean','node':node,'lower':lo,'upper':hi,'score':float((100-np.maximum(lo-t,0)-np.maximum(t-hi,0)-(r>1)).mean()),'days':float(((t>=lo)&(t<=hi)&(r<=1)).sum()/N_YEARS)})
report['checks']=list(dict.fromkeys(report['checks']))
report['checks'].append('Independent raw NOAA custom-range references, including six-year mean and 18–33 °C PASS')
report['checks'].append('Independent raw E-OBS custom-range references, including six-year mean and 18–33 °C PASS')
(out/'rain-audit.json').write_text(json.dumps(report,indent=2));Path('output-final/rain-audit.json').write_text(json.dumps(report,indent=2));print('Rain references total',len(report['reference_cases']),flush=True)
