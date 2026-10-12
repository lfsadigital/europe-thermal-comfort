"""Resumable ERA5 bulk importer. Does not modify the production Site or NOAA cache.
Reads Open-Meteo's public OM archive; hourly maximum/sum in UTC; no downscaling.
Keeps original 0.05°C hourly source precision rather than API display rounding.
"""
import json,math,datetime,time,threading,concurrent.futures,os
from pathlib import Path
import numpy as np,fsspec
from omfiles import OmFileReader
from fsspec.implementations.http import HTTPFileSystem
ROOT=Path(__file__).resolve().parent;OUT=ROOT/'.cache/era5';OUT.mkdir(exist_ok=True)
m=json.loads((ROOT/'site/dist/assets/metadata.json').read_text());grid=np.fromfile(ROOT/'site/dist/assets/node-grid.bin',dtype='<i4').reshape(360,720);n=m['nodes'];nd=2192
orig=HTTPFileSystem._cat_file
async def compat(self,url=None,path=None,**kwargs):return await orig(self,url or path,**kwargs)
HTTPFileSystem._cat_file=compat
arrays={}
for variable,name in [('temperature_2m','temperature'),('precipitation','rain')]:
 p=OUT/(name+'.npy')
 if not p.exists():
  a=np.lib.format.open_memmap(p,mode='w+',dtype='f4',shape=(nd,n),fortran_order=True);a[:]=np.nan;a.flush()
 arrays[variable]=np.load(p,mmap_mode='r+')
progress_path=OUT/'progress.json';done=set(json.loads(progress_path.read_text()) if progress_path.exists() else []);lock=threading.Lock();started=time.time();completed=0
start=datetime.datetime(2020,1,1,tzinfo=datetime.timezone.utc);end=datetime.datetime(2026,1,1,tzinfo=datetime.timezone.utc);epoch=datetime.datetime(1970,1,1,tzinfo=datetime.timezone.utc)
files=[]
for year in [2020,2021]:
 begin=datetime.datetime(year,1,1,tzinfo=datetime.timezone.utc);stop=datetime.datetime(year+1,1,1,tzinfo=datetime.timezone.utc);files.append((f'year_{year}',begin,int((stop-begin).total_seconds()/3600),0,int((stop-begin).total_seconds()/3600)))
first=datetime.datetime(2022,1,1,tzinfo=datetime.timezone.utc)
for chunk in range(int((first-epoch).total_seconds()//3600)//504,math.ceil((end-epoch).total_seconds()/3600/504)):
 begin=epoch+datetime.timedelta(hours=chunk*504);lo=max(first,begin);hi=min(end,begin+datetime.timedelta(hours=504));files.append((f'chunk_{chunk}',begin,504,int((lo-begin).total_seconds()/3600),int((hi-begin).total_seconds()/3600)))
# File boundaries are multiples of 21 days, and selected start/end are midnight UTC.
assert sum((hi-lo)//24 for _,_,_,lo,hi in files)==2192

def task(variable,item,row):
 global completed
 tag,begin,hours,lo,hi=item;key=f'{variable}/{tag}/{row}'
 if key in done:return
 xs=np.flatnonzero(grid[row]>=0);assert len(xs)>0
 # ERA5 grid is south-to-north from -90, west-to-east from -180, in 0.25°.
 erow=int(round((m['latitude'][row]+90)/.25));ex=(xs*2+1).astype(int);left=int(ex.min());right=int(ex.max())+1
 url=f'https://openmeteo.s3.amazonaws.com/data/copernicus_era5/{variable}/{tag}.om'
 for attempt in range(4):
  try:
   with OmFileReader(fsspec.open(url,'rb',block_size=65536)) as reader:
    assert tuple(reader.shape[:2])==(721,1440)
    assert hi<=reader.shape[2]
    block=reader[erow:erow+1,left:right,lo:hi][0][ex-left]
   break
  except Exception:
   if attempt==3:raise
   time.sleep(2*(attempt+1))
 assert block.shape==(len(xs),hi-lo)
 daily=block.reshape(len(xs),-1,24)
 aggregate=np.max(daily,axis=2) if variable=='temperature_2m' else np.sum(daily,axis=2,dtype=np.float64).astype('f4')
 # Any missing hourly record must propagate to daily NaN. No gap filling.
 if variable=='precipitation':assert ((aggregate>=0)|np.isnan(aggregate)).all()
 offset=int(((begin+datetime.timedelta(hours=lo))-start).total_seconds()/86400)
 arrays[variable][offset:offset+aggregate.shape[1],grid[row,xs]]=aggregate.T
 with lock:
  done.add(key);completed+=1
  if completed%40==0:
   for a in arrays.values():a.flush()
   tmp=progress_path.with_suffix('.tmp');tmp.write_text(json.dumps(sorted(done)));tmp.replace(progress_path)
   print(f'{len(done)}/{total} row/file imports; {time.time()-started:.0f}s; latest {key}',flush=True)
rows=[y for y in range(360) if (grid[y]>=0).any()];total=len(files)*len(rows)*2
print('ERA5 files',len(files),'rows',len(rows),'tasks',total,'completed',len(done),'daily cells',n,flush=True)
# One file at a time per variable keeps remote lookup reuse local to a bounded batch.
try:
 with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
  for item in files:
   for variable in arrays:
    list(pool.map(lambda row:task(variable,item,row),rows))
    print('COMPLETED',variable,item[0],flush=True)
finally:
 for a in arrays.values():a.flush()
 progress_path.write_text(json.dumps(sorted(done)))
report={'source':'Copernicus ERA5 / ECMWF, Open-Meteo AWS Open Data','period':'2020–2025','days':nd,'nodes':n,'native_resolution_degrees':.25,'sampling_degrees':.5,'timezone':'UTC','elevation_downscaling':False,'daily_temperature':'Maximum of 24 hourly 2m temperatures; original stored 0.05°C precision','daily_precipitation':'Sum of 24 hourly total precipitation values (mm)','completed_tasks':len(done),'required_tasks':total,'files':[x[0] for x in files]}
(OUT/'import.json').write_text(json.dumps(report,indent=2)+'\n');print('IMPORT COMPLETE',flush=True)
