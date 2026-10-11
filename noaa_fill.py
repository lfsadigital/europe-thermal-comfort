"""Supplement missing eastern E-OBS cells with NOAA CPC daily Tmax, 0.5°."""
from pathlib import Path
from datetime import date
import numpy as np
import requests
import xarray as xr
from scipy.interpolate import RegularGridInterpolator
from scoring import daily_score

SOURCE='https://downloads.psl.noaa.gov/Datasets/cpc_global_temp/'

def supplement(data,start,end):
    folder=Path('.cache/noaa');folder.mkdir(parents=True,exist_ok=True)
    score_path=folder/f'scores-{start}-{end}.npz'
    if score_path.exists():
        with np.load(score_path) as p: noaa={k:p[k] for k in p.files}
    else:
        total=None;count=None
        for year in range(start.year,end.year+1):
            path=folder/f'tmax.{year}.nc'
            if not path.exists():
                temp=path.with_suffix('.tmp')
                with requests.get(SOURCE+path.name,stream=True,timeout=(20,180)) as r:
                    r.raise_for_status()
                    expected=int(r.headers.get('Content-Length',0))
                    with temp.open('wb') as f:
                        for chunk in r.iter_content(4*1024*1024): f.write(chunk)
                if expected and temp.stat().st_size!=expected: raise ValueError('Incomplete NOAA file')
                temp.replace(path)
                print(f'NOAA {year}: arquivo recebido ({path.stat().st_size/1e6:.1f} MB)',flush=True)
            with xr.open_dataset(path,engine='h5netcdf') as ds:
                if ds.tmax.attrs.get('units') != 'degC': raise ValueError('Unexpected NOAA unit')
                period=ds.sel(time=slice(str(start),str(end)),lat=slice(72,34),lon=slice(24,46))
                expected_dates=np.arange(np.datetime64(max(start,date(year,1,1))),np.datetime64(min(end,date(year,12,31)))+np.timedelta64(1,'D'))
                if not np.array_equal(period.time.values.astype('datetime64[D]'),expected_dates): raise ValueError('Missing NOAA date')
                t=period.tmax.values.astype(np.float64)
                valid=np.isfinite(t)
                s=daily_score(t)
                if total is None:
                    total=np.zeros(t.shape[1:]);count=np.zeros(t.shape[1:],dtype=np.uint16)
                    lat,lon=period.lat.values,period.lon.values
                total+=np.nansum(s,axis=0);count+=valid.sum(axis=0).astype(np.uint16)
                print(f'NOAA {year}: {len(expected_dates)} dias verificados',flush=True)
        expected_days=(end-start).days+1
        mean=np.divide(total,count,out=np.full(total.shape,np.nan),where=count==expected_days)
        noaa=dict(latitude=lat,longitude=lon,score=mean,count=count)
        np.savez_compressed(score_path,**noaa)
    lat=noaa['latitude'][::-1];lon=noaa['longitude'];grid=noaa['score'][::-1]
    yy,xx=np.meshgrid(data['latitude'],data['longitude'],indexing='ij')
    interp=RegularGridInterpolator((lat,lon),grid,method='linear',bounds_error=False,fill_value=np.nan)
    candidates=interp(np.stack([yy,xx],axis=-1))
    mask=(~np.isfinite(data['score'])) & np.isfinite(candidates)
    combined=data['score'].copy();combined[mask]=candidates[mask]
    provenance=np.zeros(combined.shape,dtype=np.uint8)
    provenance[np.isfinite(data['score'])]=1;provenance[mask]=2
    result=dict(data)
    result.update(score=combined,source_grid=provenance,eobs_score=data['score'])
    result['count']=data['count'].copy();result['count'][mask]=(end-start).days+1
    print(f'Complemento NOAA: {mask.sum()} células da grade de apresentação',flush=True)
    return result
