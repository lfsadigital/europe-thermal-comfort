"""Read cached official daily rain fields and preserve exact joint temperature/rain counts."""
from pathlib import Path
from datetime import date
import gzip,json,struct
import h5py,numpy as np,xarray as xr
from eobs_data import HTTPRangeFile
from country_table import CachedEOBS

RAIN_URL='https://knmi-ecad-assets-prd.s3.amazonaws.com/ensembles/data/Grid_0.1deg_reg_ensemble/rr_ens_mean_0.1deg_reg_v33.0e.nc'
RAIN_SIZE=3163228118
class CachedRain(CachedEOBS):
 def __init__(self):
  self.size=RAIN_SIZE;self.position=0;self.block_size=4*1024*1024;self.cache=Path('.cache/eobs-rain-v33');self.memory={}

def grid_nodes(values,mapping,weights,shape):
 out=np.full(mapping.shape[0],np.nan)
 for j in range(4):
  active=(mapping[:,j]>=0)&(weights[:,j]>0)
  if j==0:out[active]=0
  out[active]+=values[mapping[active,j]]*weights[active,j]
 return out.reshape(shape)

def prepare():
 """Download official E-OBS daily fields and NOAA subsets; all downloads remain local."""
 import requests
 from concurrent.futures import ThreadPoolExecutor
 out=Path('.cache/rain-daily');out.mkdir(exist_ok=True)
 if any(not (out/f'{year}.npy').exists() for year in range(2020,2025)):
  with HTTPRangeFile(RAIN_URL,Path('.cache/eobs-rain-v33')) as remote,h5py.File(remote,'r') as f:
   assert remote.size==RAIN_SIZE
   ys=np.flatnonzero((f['latitude'][:]>=34.5)&(f['latitude'][:]<=71.5));xs=np.flatnonzero((f['longitude'][:]>=-25)&(f['longitude'][:]<=45))
   for year in range(2020,2025):
    p=out/f'{year}.npy'
    if p.exists():continue
    first=(date(year,1,1)-date(1950,1,1)).days;n=(date(year+1,1,1)-date(year,1,1)).days
    a=np.lib.format.open_memmap(p.with_suffix('.tmp'),mode='w+',dtype='f4',shape=(n,len(ys),len(xs)))
    for day in range(n):
     assert f['time'][first+day]==first+day
     a[day]=f['rr'][first+day,ys[0]:ys[-1]+1,xs[0]:xs[-1]+1]
     if (day+1)%100==0:print(year,day+1,'daily rain fields cached',flush=True)
    a.flush();del a;p.with_suffix('.tmp').replace(p)
 noaa=Path('.cache/noaa-rain');noaa.mkdir(exist_ok=True)
 def download(year):
  p=noaa/f'precip.{year}.nc'
  if p.exists():return
  url=f'https://psl.noaa.gov/thredds/ncss/grid/Datasets/cpc_global_precip/precip.{year}.nc'
  params={'var':'precip','north':72,'south':34,'west':24,'east':46,'time_start':f'{year}-01-01T00:00:00Z','time_end':f'{year}-12-31T23:59:59Z','accept':'netcdf4'}
  for attempt in range(3):
   try:
    r=requests.get(url,params=params,timeout=180);r.raise_for_status();tmp=p.with_suffix('.tmp');tmp.write_bytes(r.content)
    with xr.open_dataset(tmp,engine='h5netcdf') as d:assert d.precip.attrs['units']=='mm'
    tmp.replace(p);return
   except requests.RequestException:
    if attempt==2:raise
 with ThreadPoolExecutor(max_workers=5) as pool:list(pool.map(download,range(2020,2025)))

def build():
 out=Path('site/dist/assets');cache=Path('.cache/rain-joint');cache.mkdir(exist_ok=True)
 meta=json.loads((out/'metadata.json').read_text());shape=tuple(meta['shape']);source=np.fromfile(out/'source.bin',dtype='u1').reshape(shape);eidx=np.flatnonzero(source.ravel()==1);ne=len(eidx)
 mapping=np.fromfile(out/'dynamic-nodes.bin',dtype='<i4').reshape(-1,4);weights=np.fromfile(out/'dynamic-weights.bin',dtype='<f8').reshape(-1,4);used=np.unique(mapping[weights>0]);nodes=int(mapping.max())+1
 # The temperature histogram contains also unused NOAA nodes; use its actual node count.
 with gzip.open(out/'hist-mean.gz','rb') as f:header=f.read(40)
 nodes=struct.unpack('<8I',header[:32])[2];nb=161;bmin=-80
 all_dry=np.zeros((nb,nodes),dtype=np.uint16);all_exact=np.zeros_like(all_dry);all_wet=np.zeros(nodes,dtype=np.uint16);all_valid=np.zeros_like(all_wet)
 annual_score=[];annual_days=[];annual_valid=[];checks=[];refs=[];periods=[]
 # Independent scalar cases: boundaries, fractions, combined penalties, no floor zero.
 temperatures=np.array([22,22,19,18,20,25,25.5,-100.]);rain=np.array([0,2,2,2,1,1,1.01,2])
 score=100-np.maximum(20-temperatures,0)-np.maximum(temperatures-25,0)-(rain>1)
 np.testing.assert_allclose(score,[100,99,98,97,100,100,98.5,-21]);np.testing.assert_equal((temperatures>=20)&(temperatures<=25)&(rain<=1),[1,0,0,0,1,1,0,0]);checks.append('Scalar examples, exactly 1 mm, exact temperature boundaries, fractions and additive penalties PASS')
 with CachedEOBS() as tr,h5py.File(tr,'r') as tf,CachedRain() as rr,h5py.File(rr,'r') as rf:
  ys=np.flatnonzero((tf['latitude'][:]>=34.5)&(tf['latitude'][:]<=71.5));xs=np.flatnonzero((tf['longitude'][:]>=-25)&(tf['longitude'][:]<=45))
  np.testing.assert_allclose(tf['latitude'][:],rf['latitude'][:],atol=1e-6);np.testing.assert_allclose(tf['longitude'][:],rf['longitude'][:],atol=1e-6)
  tx=tf['tx'];rds=rf['rr'];tscale=float(tx.attrs['scale_factor'][0]);tfill=int(tx.attrs['_FillValue'][0]);rfill=float(rds.attrs['_FillValue'][0]);assert rds.attrs['units']==b'mm'
  for year in range(2020,2025):
   nc=(date(year+1,1,1)-date(year,1,1)).days;p=cache/f'{year}.npz'
   if p.exists():
    z=np.load(p);dry=z['dry'];exact=z['exact'];wet=z['wet'];valid=z['valid'];directscore=z['directscore'];directdays=z['directdays']
   else:
    dry=np.zeros((nb,nodes),dtype=np.uint16);exact=np.zeros_like(dry);wet=np.zeros(nodes,dtype=np.uint16);valid=np.zeros_like(wet);directscore=np.zeros(nodes);directdays=np.zeros(nodes)
    first=(date(year,1,1)-date(1950,1,1)).days;ids=np.arange(ne);rainfields=np.load(f'.cache/rain-daily/{year}.npy',mmap_mode='r')
    for day in range(nc):
     assert tf['time'][first+day]==rf['time'][first+day]==first+day
     raw=tx[first+day,ys[0]:ys[-1]+1,xs[0]:xs[-1]+1].ravel()[eidx];rain=rainfields[day].ravel()[eidx].astype(float);t=raw.astype(float)*tscale
     good=(raw!=tfill)&(rain!=rfill)&np.isfinite(rain)&(rain>=0);dryday=good&(rain<=1);wet[:ne]+=(good&(rain>1));valid[:ne]+=good
     bins=((raw.astype(np.int32)+99)//100)-bmin;dry[bins[dryday],ids[dryday]]+=1
     exactday=dryday&(raw%100==0);exact[raw[exactday]//100-bmin,ids[exactday]]+=1
     directscore[:ne]+=np.where(good,100-np.abs(t-np.clip(t,20,25))-(rain>1),0);directdays[:ne]+=dryday&(raw>=2000)&(raw<=2500)
     if (day+1)%100==0:print(year,day+1,'paired E-OBS days',flush=True)
    with xr.open_dataset(f'.cache/noaa/tmax.{year}.nc',engine='h5netcdf') as td,xr.open_dataset(f'.cache/noaa-rain/precip.{year}.nc',engine='h5netcdf') as pd:
     t=td.sel(lat=slice(72,34),lon=slice(24,46));r=pd.precip.sel(lat=t.lat,lon=t.lon)
     np.testing.assert_array_equal(t.time.values.astype('datetime64[D]'),r.time.values.astype('datetime64[D]'));assert t.tmax.attrs['units']=='degC' and r.attrs['units']=='mm'
     tv=t.tmax.values[:,::-1].reshape(nc,-1).astype(float);rv=r.values[:,::-1].reshape(nc,-1).astype(float);assert tv.shape==rv.shape and tv.shape[1]==nodes-ne
     ids=np.arange(ne,nodes)
     for row,rain in zip(tv,rv):
      good=np.isfinite(row)&np.isfinite(rain)&(rain>=0);dryday=good&(rain<=1);wet[ne:]+=good&(rain>1);valid[ne:]+=good;bins=np.ceil(row[dryday]).astype(int)-bmin;dry[bins,ids[dryday]]+=1;integer=dryday&(row==np.floor(row));exact[row[integer].astype(int)-bmin,ids[integer]]+=1
      directscore[ne:]+=np.where(good,100-np.abs(row-np.clip(row,20,25))-(rain>1),0);directdays[ne:]+=dryday&(row>=20)&(row<=25)
     # Direct daily reference for several ranges on a used NOAA node.
     node=int(used[used>=ne][0]);j=node-ne
     for lo,hi in [(20,25),(18,33),(18,28),(-10,5),(25,26)]:
      good=np.isfinite(tv[:,j])&np.isfinite(rv[:,j])&(rv[:,j]>=0)
      if good.all():refs.append({'period':str(year),'node':node,'lower':lo,'upper':hi,'score':float((100-np.maximum(lo-tv[:,j],0)-np.maximum(tv[:,j]-hi,0)-(rv[:,j]>1)).mean()),'days':int(((tv[:,j]>=lo)&(tv[:,j]<=hi)&(rv[:,j]<=1)).sum())})
    np.savez_compressed(p,dry=dry,exact=exact,wet=wet,valid=valid,directscore=directscore,directdays=directdays)
   temp=np.load(f'.cache/dynamic/{year}.npz');counts=temp['counts'];sums=temp['sums'];bins=np.arange(bmin,bmin+nb)[:,None]
   node_score=100-(np.where(bins<=20,20*counts-sums,0).sum(axis=0)+np.where(bins>25,sums-25*counts,0).sum(axis=0)+wet)/nc
   node_days=dry[(np.arange(bmin,bmin+nb)>20)&(np.arange(bmin,bmin+nb)<=25)].sum(axis=0)+exact[20-bmin]
   good=valid==nc;np.testing.assert_allclose(node_score[good],directscore[good]/nc,atol=1e-10,rtol=0);np.testing.assert_equal(node_days[good],directdays[good]);node_score[~good]=np.nan;node_days=node_days.astype(float);node_days[~good]=np.nan
   annual_score.append(grid_nodes(node_score,mapping,weights,shape));annual_days.append(grid_nodes(node_days,mapping,weights,shape));annual_valid.append(good)
   save_rain(out,str(year),dry,exact,wet,valid,nc,1,counts)
   all_dry+=dry;all_exact+=exact;all_wet+=wet;all_valid+=valid
   print(year,'rain nodes complete',int(good[used].sum()),'/',len(used),flush=True)
  temp=np.load('.cache/dynamic/2020.npz');counts=np.zeros_like(temp['counts'])
  for year in range(2020,2025):counts+=np.load(f'.cache/dynamic/{year}.npz')['counts']
  save_rain(out,'mean',all_dry,all_exact,all_wet,all_valid,1827,5,counts)
 annual_score=np.stack(annual_score);annual_days=np.stack(annual_days)
 mean_score=np.sum(annual_score*np.array([366,365,365,365,366])[:,None,None],axis=0)/1827;mean_days=annual_days.sum(axis=0)/5
 np.savez_compressed('output-final/rain_site_grid.npz',latitude=meta['latitude'],longitude=meta['longitude'],score=mean_score,days_per_year=mean_days,annual_score=annual_score,annual_days=annual_days,source=source)
 checks.append('All 1,827 daily paired fields: histogram results match independent raw daily scores and joint comfortable-day counts PASS')
 checks.append('Leap-day weighting and five-year annualization PASS; incomplete joint records excluded')
 report={'checks':checks,'period_days':1827,'year_days':[366,365,365,365,366],'rain_threshold_mm':1,'wet_rule':'precipitation > 1 mm','comfortable_rule':'lower <= Tmax <= upper AND precipitation <= 1 mm','score_rule':'100 - max(lower-Tmax,0) - max(Tmax-upper,0) - (precipitation>1)','valid_land_cells':int(np.isfinite(mean_score).sum()),'reference_cases':refs}
 (out/'rain-audit.json').write_text(json.dumps(report,indent=2));Path('output-final/rain-audit.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items() if k!='reference_cases'},indent=2),flush=True)

def save_rain(out,key,dry,exact,wet,valid,days,years,counts):
 occupied=counts.T>0;node,binidx=np.nonzero(occupied);entries=len(node)
 data=struct.pack('<6I',0x5241494E,1,len(wet),entries,days,years)+wet.astype('<u2').tobytes()+valid.astype('<u2').tobytes()+dry[binidx,node].astype('<u2').tobytes()+exact[binidx,node].astype('<u2').tobytes()
 with gzip.open(out/f'rain-{key}.gz','wb',compresslevel=6) as f:f.write(data)
 print(key,'rain statistics',round((out/f'rain-{key}.gz').stat().st_size/1e6,2),'MB',flush=True)
if __name__=='__main__':prepare();build()
