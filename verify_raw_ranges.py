"""Independent custom-range reference from four raw NOAA daily series."""
import json,numpy as np,xarray as xr
from pathlib import Path
p=np.load('output-final/comfort_grid.npz');source=np.fromfile('site/dist/assets/source.bin',dtype='u1').reshape(p['score'].shape)
y,x=np.argwhere(source==2)[len(np.argwhere(source==2))//2];lat=p['latitude'][y];lon=p['longitude'][x];series=[]
for year in range(2020,2025):
 with xr.open_dataset(f'.cache/noaa/tmax.{year}.nc',engine='h5netcdf') as ds:
  lats=ds.lat.values[::-1];lons=ds.lon.values;iy=np.searchsorted(lats,lat)-1;ix=np.searchsorted(lons,lon)-1;fy=(lat-lats[iy])/(lats[iy+1]-lats[iy]);fx=(lon-lons[ix])/(lons[ix+1]-lons[ix])
  series.append(np.stack([ds.tmax.sel(lat=lats[a],lon=lons[b]).values.astype(np.float64) for a,b in [(iy,ix),(iy,ix+1),(iy+1,ix),(iy+1,ix+1)]],axis=1))
w=np.array([(1-fy)*(1-fx),(1-fy)*fx,fy*(1-fx),fy*fx]);refs=[]
for period,t in [('mean',np.concatenate(series)),('2024',series[-1])]:
 for lo,hi in [(18,28),(15,30),(-10,5),(25,26),(20,21)]:
  score=np.mean(100-np.abs(t-np.clip(t,lo,hi)),axis=0)@w;days=((t>=lo)&(t<=hi)).sum(axis=0)@w/(5 if period=='mean' else 1)
  refs.append(dict(period=period,lower=lo,upper=hi,index=int(y*p['score'].shape[1]+x),score=float(score),days=float(days)))
Path('site/dist/assets/dynamic-reference.json').write_text(json.dumps(refs))
