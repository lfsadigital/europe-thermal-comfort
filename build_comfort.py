#!/usr/bin/env python3
"""Europe thermal preference map from official E-OBS daily Tmax, 0.1 degrees."""
import os
from pathlib import Path
os.environ.setdefault('MPLCONFIGDIR', str(Path(__file__).resolve().parent/'.cache/matplotlib'))
import argparse
import json
from datetime import date, timedelta
import h5py
import numpy as np
from eobs_data import HTTPRangeFile, URL
from scoring import daily_score

START, END = date(2020,1,1), date(2024,12,31)

def aggregate(start=START, end=END):
    target = Path('.cache/eobs-scores'); target.mkdir(parents=True, exist_ok=True)
    cached = target/f'{start}-{end}.npz'
    if cached.exists():
        with np.load(cached) as d:
            return {k:d[k] for k in d.files}
    with HTTPRangeFile() as remote:
        with h5py.File(remote,'r') as f:
            lat, lon = f['latitude'][:], f['longitude'][:]
            yi = np.flatnonzero((lat>=34.5)&(lat<=71.5)); xi=np.flatnonzero((lon>=-25)&(lon<=45))
            lat, lon = lat[yi],lon[xi]
            ds = f['tx']
            if ds.attrs['units'].decode() != 'Celsius': raise ValueError('Unexpected units')
            scale, offset = float(ds.attrs['scale_factor'][0]),float(ds.attrs['add_offset'][0])
            fill = int(ds.attrs['_FillValue'][0])
            all_times = f['time'][:]
            origin=date(1950,1,1)
            expected_days = (end-start).days+1
            total = np.zeros((len(lat),len(lon)),dtype=np.float64)
            counts = np.zeros(total.shape,dtype=np.uint16)
            annual = []
            for year in range(start.year,end.year+1):
                first,last=max(start,date(year,1,1)),min(end,date(year,12,31))
                year_cache=target/f'{first}-{last}-annual.npz'
                days=(last-first).days+1
                if year_cache.exists():
                    with np.load(year_cache) as d:
                        sums=d['sum']; count=d['count']
                    print(f'{year}: cache completo ({days} dias)',flush=True)
                else:
                    sums=np.zeros_like(total);count=np.zeros_like(counts)
                    for n in range(days):
                        when=first+timedelta(days=n); time_value=(when-origin).days
                        idx=np.searchsorted(all_times,time_value)
                        if idx>=len(all_times) or all_times[idx]!=time_value: raise ValueError(f'Missing date: {when}')
                        raw=ds[idx,yi[0]:yi[-1]+1,xi[0]:xi[-1]+1]
                        valid=raw!=fill
                        t=raw.astype(np.float64)*scale+offset
                        daily=daily_score(t)
                        sums+=np.where(valid,daily,0);count+=valid.astype(np.uint16)
                        if (n+1)%30==0 or n==days-1:
                            print(f'{year}: {n+1}/{days} dias; download novo {remote.downloaded/1e6:.1f} MB',flush=True)
                    np.savez_compressed(year_cache,sum=sums,count=count)
                total+=sums;counts+=count
                annual.append(np.divide(sums,count,out=np.full(total.shape,np.nan),where=count==days))
            average=np.divide(total,counts,out=np.full(total.shape,np.nan),where=counts==expected_days)
            result=dict(latitude=lat,longitude=lon,score=average,count=counts,annual=np.stack(annual),days=np.array(expected_days))
            np.savez_compressed(cached,**result)
            return result

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--start',type=date.fromisoformat,default=START)
    parser.add_argument('--end',type=date.fromisoformat,default=END)
    parser.add_argument('--data-only',action='store_true')
    parser.add_argument('--eobs-only',action='store_true',help='Preservar apenas a cobertura original E-OBS')
    parser.add_argument('--output',type=Path,default=Path('output-final'))
    args=parser.parse_args()
    if args.end<args.start: parser.error('Invalid date range')
    result=aggregate(args.start,args.end)
    if not args.eobs_only:
        from noaa_fill import supplement
        result=supplement(result,args.start,args.end)
    print('Complete grid:',result['score'].shape,'valid:',int(np.isfinite(result['score']).sum()),'range:',float(np.nanmin(result['score'])),float(np.nanmax(result['score'])),flush=True)
    args.output.mkdir(parents=True,exist_ok=True)
    np.savez_compressed(args.output/'comfort_grid.npz',**result)
    if not args.data_only:
        from render_europe import render
        render(result,args.start,args.end,args.output)

if __name__=='__main__': main()
