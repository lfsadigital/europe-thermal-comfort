"""Download official NOAA global daily files; reuse existing temperature files read-only."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import time,requests,xarray as xr,numpy as np
CACHE=Path('.cache/noaa');CACHE.mkdir(parents=True,exist_ok=True)
OLD=Path('../europe-comfort/.cache/noaa')
def download(item):
 kind,year=item;p=CACHE/f'{kind}.{year}.nc'
 if p.exists():return
 original=OLD/p.name
 if kind=='tmax' and year<2025 and original.exists():
  with xr.open_dataset(original,engine='h5netcdf') as d:assert dict(d.sizes)=={'time':366 if year in (2020,2024) else 365,'lat':360,'lon':720}
  p.symlink_to(original.resolve());print('Reused original global temperature',year,flush=True);return
 dataset='cpc_global_temp' if kind=='tmax' else 'cpc_global_precip'
 url=f'https://downloads.psl.noaa.gov/Datasets/{dataset}/{kind}.{year}.nc'
 tmp=p.with_suffix('.download')
 for attempt in range(5):
  try:
   with requests.get(url,stream=True,timeout=(30,180)) as r:
    r.raise_for_status();expected=int(r.headers.get('Content-Length',0));size=0
    with tmp.open('wb') as f:
     for block in r.iter_content(1024*1024):f.write(block);size+=len(block)
    if expected:assert size==expected
   with xr.open_dataset(tmp,engine='h5netcdf') as d:
    assert d.sizes['lat']==360 and d.sizes['lon']==720 and d[kind].attrs['units']==('degC' if kind=='tmax' else 'mm')
    np.testing.assert_array_equal(d.time.values.astype('datetime64[D]'),np.arange(np.datetime64(f'{year}-01-01'),np.datetime64(f'{year+1}-01-01')))
   tmp.replace(p);print('Downloaded',p.name,size,'bytes',flush=True);return
  except requests.RequestException:
   if attempt==4:raise
   time.sleep(min(30,5*2**attempt))
with ThreadPoolExecutor(max_workers=2) as pool:list(pool.map(download,[(kind,y) for kind in ['tmax','precip'] for y in range(2020,2026)]))
