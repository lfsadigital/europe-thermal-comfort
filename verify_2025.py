"""Independently recompute every 2025 cell from paired daily fields.

This audit does not use the sparse histogram to calculate its reference values.
"""
from pathlib import Path
from datetime import date
import json,numpy as np,h5py,xarray as xr
from country_table import CachedEOBS
from rain_data import CachedRain,grid_nodes
from period_config import YEARS,YEAR_DAYS,TOTAL_DAYS,N_YEARS,DEFAULT_RANGE
out=Path('site/dist/assets');meta=json.loads((out/'metadata.json').read_text());shape=tuple(meta['shape']);source=np.fromfile(out/'source.bin',dtype='u1').reshape(shape);eidx=np.flatnonzero(source.ravel()==1);ne=len(eidx)
mapping=np.fromfile(out/'dynamic-nodes.bin',dtype='<i4').reshape(-1,4);weights=np.fromfile(out/'dynamic-weights.bin',dtype='<f8').reshape(-1,4);r=np.load('.cache/rain-joint/2025.npz');nodes=len(r['valid']);lo,hi=DEFAULT_RANGE
rawscore=np.zeros(nodes);rawdays=np.zeros(nodes);valid=np.zeros(nodes,dtype='u2');wet=np.zeros(nodes,dtype='u2');first=(date(2025,1,1)-date(1950,1,1)).days
with CachedEOBS() as remote,h5py.File(remote,'r') as tf,CachedRain() as rr,h5py.File(rr,'r') as rf:
 ys=np.flatnonzero((tf['latitude'][:]>=34.5)&(tf['latitude'][:]<=71.5));xs=np.flatnonzero((tf['longitude'][:]>=-25)&(tf['longitude'][:]<=45));scale=float(tf['tx'].attrs['scale_factor'][0]);fill=int(tf['tx'].attrs['_FillValue'][0]);rainfill=float(rf['rr'].attrs['_FillValue'][0]);rain=np.load('.cache/rain-daily/2025.npy',mmap_mode='r')
 # Source coordinates use slightly different floating-point representations (max 1.864e-6 degrees).
 for axis in ['latitude','longitude']:
  np.testing.assert_array_equal(np.round(tf[axis][:],4),np.round(rf[axis][:],4))
  np.testing.assert_allclose(tf[axis][:],rf[axis][:],atol=2e-6,rtol=0)
 for day in range(365):
  assert tf['time'][first+day]==rf['time'][first+day]==first+day
  a=tf['tx'][first+day,ys[0]:ys[-1]+1,xs[0]:xs[-1]+1].ravel()[eidx];p=rain[day].ravel()[eidx].astype(float);t=a.astype(float)*scale;good=(a!=fill)&np.isfinite(p)&(p>=0)&(p!=rainfill)
  valid[:ne]+=good;wet[:ne]+=good&(p>1);rawscore[:ne]+=np.where(good,100-np.abs(t-np.clip(t,lo,hi))-(p>1),0)
  rawdays[:ne]+=good&(a>=lo*100)&(a<=hi*100)&(p<=1)
  if (day+1)%100==0:print('Independent paired 2025 E-OBS fields checked',day+1,flush=True)
with xr.open_dataset('.cache/noaa/tmax.2025.nc',engine='h5netcdf') as td,xr.open_dataset('.cache/noaa-rain/precip.2025.nc',engine='h5netcdf') as pd:
 td=td.sel(lat=slice(72,34),lon=slice(24,46));pd=pd.precip.sel(lat=td.lat,lon=td.lon);dates=np.arange(np.datetime64('2025-01-01'),np.datetime64('2026-01-01'));np.testing.assert_array_equal(td.time.values.astype('datetime64[D]'),dates);np.testing.assert_array_equal(pd.time.values.astype('datetime64[D]'),dates);assert td.tmax.attrs['units']=='degC' and pd.attrs['units']=='mm'
 t=td.tmax.values[:,::-1].reshape(365,-1).astype(float);p=pd.values[:,::-1].reshape(365,-1).astype(float);good=np.isfinite(t)&np.isfinite(p)&(p>=0)
 valid[ne:]=good.sum(axis=0);wet[ne:]=(good&(p>1)).sum(axis=0);rawscore[ne:]=np.where(good,100-np.abs(t-np.clip(t,lo,hi))-(p>1),0).sum(axis=0);rawdays[ne:]=(good&(t>=lo)&(t<=hi)&(p<=1)).sum(axis=0)
np.testing.assert_array_equal(valid,r['valid']);np.testing.assert_array_equal(wet,r['wet']);rawscore/=365;complete=valid==365;rawscore[~complete]=np.nan;rawdays[~complete]=np.nan
score=grid_nodes(rawscore,mapping,weights,shape);days=grid_nodes(rawdays,mapping,weights,shape)
z=np.load('output-final/default_site_grid.npz');np.testing.assert_allclose(score,z['annual_score'][-1],atol=1e-10,rtol=0,equal_nan=True);np.testing.assert_allclose(days,z['annual_days'][-1],atol=1e-10,rtol=0,equal_nan=True)
np.testing.assert_allclose(z['score'],(z['annual_score']*np.array(YEAR_DAYS)[:,None,None]).sum(axis=0)/TOTAL_DAYS,atol=1e-10,rtol=0,equal_nan=True)
np.testing.assert_allclose(z['days_per_year'],z['annual_days'].sum(axis=0)/N_YEARS,atol=1e-10,rtol=0,equal_nan=True)
assert TOTAL_DAYS==2192 and N_YEARS==6 and z['annual_score'].shape[0]==6
for i,n in enumerate(YEAR_DAYS):
 v=z['annual_days'][i];assert (v[np.isfinite(v)]>=0).all() and (v[np.isfinite(v)]<=n+1e-9).all()
previous=Path('.cache/regression-pre-2025-default.npz')
if previous.exists():
 old=np.load(previous);np.testing.assert_allclose(z['annual_score'][:5],old['annual_score'],atol=1e-10,rtol=0,equal_nan=True);np.testing.assert_array_equal(z['annual_days'][:5],old['annual_days']);print('2020–2024 regression: all annual values unchanged PASS',flush=True)
report=json.loads((out/'rain-audit.json').read_text());report['checks'].extend(['Independent 2025 audit: all 365 original daily paired E-OBS fields and all native NOAA nodes match the exported 18–26 °C scores and counts PASS','Recorded dates, native coordinates and units checked; missing-data masks and wet-day counts match raw daily data PASS','All six annual grids: score weighted by actual year days /2192; comfortable-day sum /6; yearly day-count bounds PASS']);report['default_range']=list(DEFAULT_RANGE);report['raw_2025_valid_land_cells']=int(np.isfinite(score).sum());report['max_raw_2025_score_error']=float(np.nanmax(abs(score-z['annual_score'][-1])));report['max_raw_2025_days_error']=float(np.nanmax(abs(days-z['annual_days'][-1])))
(out/'rain-audit.json').write_text(json.dumps(report,indent=2));Path('output-final/rain-audit.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items() if k!='reference_cases'},indent=2),flush=True)
