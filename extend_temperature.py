"""Add 2025 daily temperature statistics on the established source grid.

Keep the original source provenance and native NOAA interpolation weights.
Incomplete new records remain missing; never replace them with a guessed value.
"""
from pathlib import Path
from datetime import date
import gzip,json,struct
import h5py,numpy as np,xarray as xr,requests
from eobs_data import HTTPRangeFile
from country_table import CachedEOBS
from period_config import YEARS,YEAR_DAYS,TOTAL_DAYS,N_YEARS,PERIOD
OUT=Path('site/dist/assets');CACHE=Path('.cache/dynamic')

def prepare():
 p=Path('.cache/noaa/tmax.2025.nc')
 if not p.exists():
  url='https://psl.noaa.gov/thredds/ncss/grid/Datasets/cpc_global_temp/tmax.2025.nc'
  params={'var':'tmax','north':72,'south':34,'west':24,'east':46,'time_start':'2025-01-01T00:00:00Z','time_end':'2025-12-31T23:59:59Z','accept':'netcdf4'}
  r=requests.get(url,params=params,timeout=180);r.raise_for_status();tmp=p.with_suffix('.tmp');tmp.write_bytes(r.content)
  with xr.open_dataset(tmp,engine='h5netcdf') as d:assert len(d.time)==365 and d.tmax.attrs['units']=='degC'
  tmp.replace(p)
 if not (CACHE/'2025.npz').exists():
  with HTTPRangeFile() as remote,h5py.File(remote,'r') as f:
   assert remote.size==4964123195
   ys=np.flatnonzero((f['latitude'][:]>=34.5)&(f['latitude'][:]<=71.5));xs=np.flatnonzero((f['longitude'][:]>=-25)&(f['longitude'][:]<=45));first=(date(2025,1,1)-date(1950,1,1)).days
   for day in range(365):
    assert f['time'][first+day]==first+day
    f['tx'][first+day,ys[0]:ys[-1]+1,xs[0]:xs[-1]+1]
    if (day+1)%100==0:print('2025 temperature blocks available',day+1,flush=True)

def save(key,counts,sums,exact,days,years,ne,scale):
 occupied=counts.T>0;offset=np.concatenate([[0],np.cumsum(occupied.sum(axis=1))]).astype('<u4');node,binidx=np.nonzero(occupied)
 bins=(binidx-80).astype('i1');c=counts[binidx,node].astype('<u2');s=sums[binidx,node].astype('<f8');e=exact[binidx,node].astype('<u2');ne_entries=int(offset[ne]);residual=np.zeros(len(s),dtype='<i2')
 center=(bins[:ne_entries].astype(np.int64)*100-50)*c[:ne_entries].astype(np.int64);delta=np.rint(s[:ne_entries]/scale).astype(np.int64)-center
 assert delta.min()>=-32768 and delta.max()<=32767
 residual[:ne_entries]=delta;np.testing.assert_allclose((residual[:ne_entries].astype(np.int64)+center)*scale,s[:ne_entries],atol=1e-8,rtol=0)
 data=struct.pack('<8I',0x434C494D,3,counts.shape[1],len(bins),days,years,ne,ne_entries)+struct.pack('<d',scale)+offset.tobytes()+bins.tobytes()+c.tobytes()+residual.tobytes()+e.tobytes()+s[ne_entries:].tobytes()
 with gzip.open(OUT/f'hist-{key}.gz','wb',compresslevel=6) as f:f.write(data)
 print('Temperature histogram',key,days,'days',years,'years',flush=True)

def build():
 meta=json.loads((OUT/'metadata.json').read_text());source=np.fromfile(OUT/'source.bin',dtype='u1').reshape(meta['shape']);eidx=np.flatnonzero(source.ravel()==1);ne=len(eidx)
 with gzip.open(OUT/'hist-2020.gz','rb') as f:header=f.read(40)
 nodes=struct.unpack('<8I',header[:32])[2];scale=struct.unpack('<d',header[32:])[0]
 with CachedEOBS() as remote,h5py.File(remote,'r') as f:
  assert float(f['tx'].attrs['scale_factor'][0])==scale
  ys=np.flatnonzero((f['latitude'][:]>=34.5)&(f['latitude'][:]<=71.5));xs=np.flatnonzero((f['longitude'][:]>=-25)&(f['longitude'][:]<=45));fill=int(f['tx'].attrs['_FillValue'][0])
  if not (CACHE/'2025.npz').exists():
   counts=np.zeros((161,nodes),dtype='u2');sums=np.zeros((161,nodes));exact=np.zeros_like(counts);directscore=np.zeros(nodes);directdays=np.zeros(nodes)
   first=(date(2025,1,1)-date(1950,1,1)).days;ids=np.arange(ne)
   for day in range(365):
    assert f['time'][first+day]==first+day
    raw=f['tx'][first+day,ys[0]:ys[-1]+1,xs[0]:xs[-1]+1].ravel()[eidx];good=raw!=fill;r=raw[good].astype(np.int32);t=r.astype(float)*scale;b=(r+99)//100+80;assert ((b>=0)&(b<161)).all()
    counts[b,ids[good]]+=1;sums[b,ids[good]]+=t;integer=good&(raw%100==0);exact[raw[integer]//100+80,ids[integer]]+=1
    directscore[ids[good]]+=100-np.abs(t-np.clip(t,20,25));directdays[ids[good]]+=(r>=2000)&(r<=2500)
    if (day+1)%100==0:print('2025 temperature raw days',day+1,flush=True)
   with xr.open_dataset('.cache/noaa/tmax.2025.nc',engine='h5netcdf') as td,xr.open_dataset('.cache/noaa/tmax.2020.nc',engine='h5netcdf') as old:
    t=td.sel(lat=slice(72,34),lon=slice(24,46));old=old.sel(lat=slice(72,34),lon=slice(24,46));np.testing.assert_array_equal(t.lat.values,old.lat.values);np.testing.assert_array_equal(t.lon.values,old.lon.values)
    np.testing.assert_array_equal(t.time.values.astype('datetime64[D]'),np.arange(np.datetime64('2025-01-01'),np.datetime64('2026-01-01')));assert t.tmax.attrs['units']=='degC'
    tv=t.tmax.values[:,::-1].reshape(365,-1).astype(float);assert tv.shape[1]==nodes-ne;ids=np.arange(ne,nodes)
    for row in tv:
     good=np.isfinite(row);v=row[good];b=np.ceil(v).astype(int)+80;assert ((b>=0)&(b<161)).all();counts[b,ids[good]]+=1;sums[b,ids[good]]+=v;integer=good&(row==np.floor(row));exact[row[integer].astype(int)+80,ids[integer]]+=1
     directscore[ids[good]]+=100-np.abs(v-np.clip(v,20,25));directdays[ids[good]]+=(v>=20)&(v<=25)
   np.savez_compressed(CACHE/'2025.npz',counts=counts,sums=sums,exact=exact,directscore=directscore,directdays=directdays)
  all_counts=np.zeros((161,nodes),dtype='u2');all_sums=np.zeros((161,nodes));all_exact=np.zeros_like(all_counts);bins=np.arange(-80,81)[:,None]
  for year,n in zip(YEARS,YEAR_DAYS):
   z=np.load(CACHE/f'{year}.npz');counts=z['counts'];sums=z['sums'];exact=z['exact'];complete=counts.sum(axis=0)==n
   score=100-(np.where(bins<=20,20*counts-sums,0).sum(axis=0)+np.where(bins>25,sums-25*counts,0).sum(axis=0))/n
   days=counts[(bins[:,0]>20)&(bins[:,0]<=25)].sum(axis=0)+exact[100]
   np.testing.assert_allclose(score[complete],z['directscore'][complete]/n,atol=1e-10,rtol=0);np.testing.assert_array_equal(days[complete],z['directdays'][complete])
   all_counts+=counts;all_sums+=sums;all_exact+=exact
   save(str(year),counts,sums,exact,n,1,ne,scale)
  save('mean',all_counts,all_sums,all_exact,TOTAL_DAYS,N_YEARS,ne,scale)
  report={'period':PERIOD,'period_days':TOTAL_DAYS,'year_days':YEAR_DAYS,'nodes':nodes,'checks':['All six annual temperature histograms match independent raw daily reference scores and inclusive day counts','2192 recorded dates, including leap days in 2020 and 2024','Lossless sparse encoding checked before writing; incomplete temperature records retained as incomplete']}
  (OUT/'audit.json').write_text(json.dumps(report,indent=2))
if __name__=='__main__':prepare();build()
