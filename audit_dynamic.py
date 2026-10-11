"""Independent raw-data audit and lossless sufficient statistics for integer limits."""
from pathlib import Path
from datetime import date
import gzip,json,struct
import numpy as np,h5py,xarray as xr
from country_table import CachedEOBS
from scipy.interpolate import RegularGridInterpolator

OUT=Path('site/dist/assets'); CACHE=Path('.cache/dynamic');CACHE.mkdir(exist_ok=True)
p=np.load('output-final/comfort_grid.npz');old=np.load('output-final/site_grid.npz')
shape=p['score'].shape;ncell=p['score'].size
source=np.fromfile(OUT/'source.bin',dtype=np.uint8).reshape(shape)
eidx=np.flatnonzero(source.ravel()==1);ne=len(eidx)
with xr.open_dataset('.cache/noaa/tmax.2020.nc',engine='h5netcdf') as ds:
 d=ds.sel(lat=slice(72,34),lon=slice(24,46));nlat=d.lat.values[::-1];nlon=d.lon.values
nn=len(nlat)*len(nlon);nodes=ne+nn
BMIN=-80;BMAX=80;NB=BMAX-BMIN+1
mapping=np.full((ncell,4),-1,dtype='<i4');weights=np.zeros((ncell,4),dtype='<f8')
mapping[eidx,0]=np.arange(ne);weights[eidx,0]=1
for index in np.flatnonzero(source.ravel()==2):
 y,x=divmod(int(index),shape[1]);la=p['latitude'][y];lo=p['longitude'][x]
 iy=np.searchsorted(nlat,la)-1;ix=np.searchsorted(nlon,lo)-1
 assert 0<=iy<len(nlat)-1 and 0<=ix<len(nlon)-1
 fy=(la-nlat[iy])/(nlat[iy+1]-nlat[iy]);fx=(lo-nlon[ix])/(nlon[ix+1]-nlon[ix])
 mapping[index]=[ne+iy*len(nlon)+ix,ne+iy*len(nlon)+ix+1,ne+(iy+1)*len(nlon)+ix,ne+(iy+1)*len(nlon)+ix+1]
 weights[index]=[(1-fy)*(1-fx),(1-fy)*fx,fy*(1-fx),fy*fx]
mapping.tofile(OUT/'dynamic-nodes.bin');weights.tofile(OUT/'dynamic-weights.bin')
used_nodes=np.unique(mapping[weights>0]);node_ids=np.arange(nodes)
def add(counts,sums,t,ids):
 valid=np.isfinite(t);t=t[valid];ids=ids[valid];bins=np.ceil(t).astype(int)-BMIN
 assert np.all((bins>=0)&(bins<NB))
 counts[bins,ids]+=1;sums[bins,ids]+=t

def measures(counts,sums,lo,hi,days,years):
 bins=np.arange(BMIN,BMAX+1)[:,None]
 below=bins<=lo;above=bins>hi
 loss=np.where(below,lo*counts-sums,0).sum(axis=0)+np.where(above,sums-hi*counts,0).sum(axis=0)
 score=100-loss/days
 comfortable=counts[(bins[:,0]>lo)&(bins[:,0]<=hi)].sum(axis=0).astype(float)
 # ceil(T)==lo includes exact lo and temperatures below lo: retain exact-boundary counts separately.
 comfortable+=exact_counts[lo-BMIN]
 return score,comfortable/years

def grid(node_values):
 a=np.full(ncell,np.nan);valid=source.ravel()>0
 a[valid]=(node_values[np.maximum(mapping[valid],0)]*weights[valid]).sum(axis=1)
 return a.reshape(shape)

def save(key,counts,sums,exact,days,years):
 occupied=counts.T>0;offset=np.concatenate([[0],np.cumsum(occupied.sum(axis=1))]).astype('<u4')
 node,binidx=np.nonzero(occupied);bins=(binidx+BMIN).astype('i1');c=counts[binidx,node].astype('<u2');s=sums[binidx,node].astype('<f8');e=exact[binidx,node].astype('<u2')
 ne_entries=int(offset[ne]);centi=np.zeros(len(s),dtype='<i4');centi[:ne_entries]=np.rint(s[:ne_entries]/scale).astype('<i4')
 np.testing.assert_allclose(centi[:ne_entries].astype(float)*scale,s[:ne_entries],atol=1e-8,rtol=0)
 data=struct.pack('<8I',0x434C494D,2,nodes,len(bins),days,years,ne,ne_entries)+struct.pack('<d',scale)+offset.tobytes()+bins.tobytes()+c.tobytes()+centi.tobytes()+e.tobytes()+s[ne_entries:].tobytes()
 with gzip.open(OUT/f'hist-{key}.gz','wb',compresslevel=6) as f:f.write(data)
 print(key,'histogram:',len(data)//1000000,'MB raw,',(OUT/f'hist-{key}.gz').stat().st_size//1000000,'MB gzip',flush=True)

report={'checks':[],'period_days':1827,'year_days':[366,365,365,365,366],'nodes':nodes,'land_cells':int((source>0).sum()),'method':'Exact integer temperature limits; counts and sums preserve original fractional temperatures.'}
all_counts=np.zeros((NB,nodes),dtype=np.uint16);all_sums=np.zeros((NB,nodes));all_exact=np.zeros_like(all_counts)
# Scalar independent synthetic check, including boundaries, fractions and extremes.
sample=np.array([-100.,19.99,20.,20.01,22.,24.99,25.,25.01,150.])
scalar=[100-(20-t if t<20 else t-25 if t>25 else 0) for t in sample]
np.testing.assert_equal(scalar,[-20,99.99,100,100,100,100,100,99.99,-25])
report['checks'].append('1: independent scalar formula and inclusive boundary examples PASS')
with CachedEOBS() as remote,h5py.File(remote,'r') as f:
 ds=f['tx'];scale=float(ds.attrs['scale_factor'][0]);offset=float(ds.attrs['add_offset'][0]);fill=int(ds.attrs['_FillValue'][0]);assert abs(scale-.01)<1e-8 and offset==0
 ys=np.flatnonzero((f['latitude'][:]>=34.5)&(f['latitude'][:]<=71.5));xs=np.flatnonzero((f['longitude'][:]>=-25)&(f['longitude'][:]<=45))
 for yi,year in enumerate(range(2020,2025)):
  nc=(date(year+1,1,1)-date(year,1,1)).days;cache=CACHE/f'{year}.npz'
  if cache.exists():
   z=np.load(cache);counts=z['counts'];sums=z['sums'];exact=z['exact'];directscore=z['directscore'];directdays=z['directdays']
  else:
   counts=np.zeros((NB,nodes),dtype=np.uint16);sums=np.zeros((NB,nodes));exact=np.zeros_like(counts);directscore=np.zeros(nodes);directdays=np.zeros(nodes)
   first=(date(year,1,1)-date(1950,1,1)).days
   for day in range(nc):
    assert f['time'][first+day]==first+day
    raw=ds[first+day,ys[0]:ys[-1]+1,xs[0]:xs[-1]+1].ravel()[eidx]
    assert np.all(raw!=fill)
    t=raw.astype(float)*scale;ids=np.arange(ne);bins=((raw.astype(np.int32)+99)//100)-BMIN
    counts[bins,ids]+=1;sums[bins,ids]+=t
    integer=(raw%100)==0;exact[(raw[integer]//100)-BMIN,ids[integer]]+=1
    # independent rule uses clipping distance rather than scoring.py
    directscore[:ne]+=100-np.abs(t-np.clip(t,20,25));directdays[:ne]+=((raw>=2000)&(raw<=2500))
    if (day+1)%100==0:print(year,day+1,'raw E-OBS days checked',flush=True)
   with xr.open_dataset(f'.cache/noaa/tmax.{year}.nc',engine='h5netcdf') as nd:
    d=nd.sel(lat=slice(72,34),lon=slice(24,46));assert len(d.time)==nc and d.tmax.attrs['units']=='degC'
    t=d.tmax.values[:,::-1].reshape(nc,nn).astype(float);assert np.isfinite(t[:,used_nodes[used_nodes>=ne]-ne]).all()
    ids=np.arange(ne,nodes)
    for row in t:
     add(counts,sums,row,ids);integer=np.isfinite(row)&(row==np.floor(row));exact[row[integer].astype(int)-BMIN,ids[integer]]+=1
    directscore[ne:]=np.nansum(100-np.abs(t-np.clip(t,20,25)),axis=0);directdays[ne:]=((t>=20)&(t<=25)).sum(axis=0)
   np.savez_compressed(cache,counts=counts,sums=sums,exact=exact,directscore=directscore,directdays=directdays)
  assert np.all(counts.sum(axis=0)[used_nodes]==nc)
  exact_counts=exact
  score,days=measures(counts,sums,20,25,nc,1)
  np.testing.assert_allclose(score[used_nodes],(directscore/nc)[used_nodes],atol=1e-10,rtol=0);np.testing.assert_equal(days[used_nodes],directdays[used_nodes])
  mask=source>0
  np.testing.assert_allclose(grid(score)[mask],old['annual_score'][yi][mask],atol=1e-10,rtol=0)
  np.testing.assert_allclose(grid(days)[mask],old['annual_days'][yi][mask],atol=1e-10,rtol=0)
  all_counts+=counts;all_sums+=sums;all_exact+=exact
  save(str(year),counts,sums,exact,nc,1)
report['checks'].append('2: all 1,827 raw daily fields; all displayed land cells; old annual scores and counts PASS')
exact_counts=all_exact;score,days=measures(all_counts,all_sums,20,25,1827,5);mask=source>0
np.testing.assert_allclose(grid(score)[mask],old['score'][mask],atol=1e-10,rtol=0);np.testing.assert_allclose(grid(days)[mask],old['days_per_year'][mask],atol=1e-10,rtol=0)
for key in ['mean','2020','2021','2022','2023','2024']:
 for mode,values,factor in [('score',old['score'] if key=='mean' else old['annual_score'][int(key)-2020],100),('days',old['days_per_year'] if key=='mean' else old['annual_days'][int(key)-2020],10)]:
  binary=np.fromfile(OUT/f'{mode}-{key}.bin',dtype='<u2').reshape(shape)
  np.testing.assert_array_equal(binary[mask],np.rint(values[mask]*factor).astype(np.uint16))
report['checks'].append('3: 12 served binary grids, leap-day weighting and /5 annualization PASS')
report['max_score_error']=float(np.max(abs(grid(score)[mask]-old['score'][mask])));report['max_days_error']=float(np.max(abs(grid(days)[mask]-old['days_per_year'][mask])))
save('mean',all_counts,all_sums,all_exact,1827,5)
Path('output-final/audit.json').write_text(json.dumps(report,indent=2));(OUT/'audit.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2),flush=True)
