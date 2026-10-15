"""Build exact daily lows for the published ERA5 cells remotely. No local bulk work."""
import os
if os.environ.get('GITHUB_ACTIONS')!='true':raise SystemExit('Remote-only: execute GitHub Actions')
import datetime as dt,json,math,gzip,hashlib,struct,subprocess,concurrent.futures,time,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np,requests
from omfiles import OmFileReader
ROOT=Path(__file__).resolve().parents[1];TMP=Path(os.environ['RUNNER_TEMP'])/'comfy-minimum';TMP.mkdir(exist_ok=True);OUT=TMP/'output';OUT.mkdir(exist_ok=True)
m=json.loads((ROOT/'site/dist/assets/metadata.json').read_text());grid=np.fromfile(ROOT/'site/dist/assets/node-grid.bin',dtype='<i4').reshape(m['shape']);n=m['nodes'];nd=2192
minimum=np.lib.format.open_memmap(TMP/'minimum.npy',mode='w+',dtype='f4',shape=(n,nd));minimum[:]=np.nan
start=dt.datetime(2020,1,1,tzinfo=dt.timezone.utc);first=dt.datetime(2022,1,1,tzinfo=dt.timezone.utc);end=dt.datetime(2026,1,1,tzinfo=dt.timezone.utc);epoch=dt.datetime(1970,1,1,tzinfo=dt.timezone.utc)
files=[]
for year in [2020,2021]:files.append((f'year_{year}',dt.datetime(year,1,1,tzinfo=dt.timezone.utc),0,m['year_days'][year-2020]*24))
for chunk in range(int((first-epoch).total_seconds()/3600)//504,math.ceil((end-epoch).total_seconds()/3600/504)):
 begin=epoch+dt.timedelta(hours=chunk*504);lo=max(first,begin);hi=min(end,begin+dt.timedelta(hours=504));files.append((f'chunk_{chunk}',begin,int((lo-begin).total_seconds()/3600),int((hi-begin).total_seconds()/3600)))
assert sum((hi-lo)//24 for _,_,lo,hi in files)==nd
old=json.loads((ROOT/'site/docs/era5-import.json').read_text())['objects'];ns={'s':'http://s3.amazonaws.com/doc/2006-03-01/'}
r=requests.get('https://openmeteo.s3.amazonaws.com',params={'list-type':2,'prefix':'data/copernicus_era5/temperature_2m/'},timeout=60);r.raise_for_status();inventory={}
for item in ET.fromstring(r.content).findall('s:Contents',ns):
 key=item.find('s:Key',ns).text;inventory[key]={'bytes':int(item.find('s:Size',ns).text),'etag':item.find('s:ETag',ns).text}
for tag,*_ in files:
 key=f'data/copernicus_era5/temperature_2m/{tag}.om';assert inventory[key]==old[key],('Published source changed',key)
print('Pinned source objects verified; remote bytes',sum(inventory[f'data/copernicus_era5/temperature_2m/{tag}.om']['bytes']for tag,*_ in files),flush=True)
def download(key):
 info=inventory[key];path=TMP/'working.om';fd=os.open(path,os.O_RDWR|os.O_CREAT|os.O_TRUNC,0o600);os.ftruncate(fd,info['bytes']);block=8*1024*1024
 def part(lo):
  hi=min(info['bytes'],lo+block)-1
  for attempt in range(5):
   try:
    r=requests.get('https://openmeteo.s3.amazonaws.com/'+key,headers={'Range':f'bytes={lo}-{hi}','If-Match':info['etag']},timeout=(20,120));r.raise_for_status();assert r.status_code==206 and len(r.content)==hi-lo+1;assert os.pwrite(fd,r.content,lo)==len(r.content);return
   except Exception:
    if attempt==4:raise
    time.sleep(2*(attempt+1))
 try:
  with concurrent.futures.ThreadPoolExecutor(max_workers=16)as pool:list(pool.map(part,range(0,info['bytes'],block)))
 finally:os.close(fd)
 return path
rows=[row for row in range(360)if(grid[row]>=0).any()]
for number,(tag,begin,lo,hi)in enumerate(files):
 key=f'data/copernicus_era5/temperature_2m/{tag}.om';path=download(key);off=int(((begin+dt.timedelta(hours=lo))-start).total_seconds()/86400)
 with OmFileReader(str(path))as reader:
  assert tuple(reader.shape[:2])==(721,1440) and reader.shape[2]>=hi
  for row in rows:
   xs=np.flatnonzero(grid[row]>=0);erow=int(round((m['latitude'][row]+90)/.25));ex=xs*2+1;left=int(ex.min());right=int(ex.max())+1
   hourly=reader[erow:erow+1,left:right,lo:hi][0][ex-left];daily=np.min(hourly.reshape(len(xs),-1,24),axis=2);minimum[grid[row,xs],off:off+daily.shape[1]]=daily
 minimum.flush();path.unlink();print(json.dumps({'stage':'import','completed':number+1,'total':len(files),'tag':tag}),flush=True)
# Independent API checks on exact cells and dates, allowing only API display rounding.
checks=[]
for city,lat,lon in [('Porto',41.25,-8.25),('Miami',25.75,-80.25),('Nairobi',-1.25,36.75),('Oslo',59.75,10.75)]:
 idx=int(grid[int(round((89.75-lat)/.5)),int(round((lon+179.75)/.5))]);assert idx>=0
 r=requests.get('https://archive-api.open-meteo.com/v1/archive',params={'latitude':lat,'longitude':lon,'start_date':'2020-01-01','end_date':'2025-12-31','models':'era5','daily':'temperature_2m_min','timezone':'UTC','elevation':'nan','cell_selection':'nearest'},timeout=120);r.raise_for_status();d=r.json();assert d['latitude']==lat and d['longitude']==lon and len(d['daily']['time'])==nd
 expected=np.array([np.nan if v is None else v for v in d['daily']['temperature_2m_min']]);actual=minimum[idx];mask=np.isfinite(expected)&np.isfinite(actual);error=float(np.max(np.abs(expected[mask]-actual[mask])));assert mask.sum()>=nd*.99 and error<=.051,(city,error);checks.append({'city':city,'cell':[lat,lon],'days':int(mask.sum()),'maxRoundedApiErrorC':error})
manifest={};offset=0
for year,days in zip(m['available_years'],m['year_days']):
 for k in range(math.ceil(n/2048)):
  a=k*2048;b=min(n,a+2048);v=np.asarray(minimum[a:b,offset:offset+days],dtype='<f4');header=struct.pack('<8I',0x4d494e54,1,a,b-a,days,year,0,v.size);name=f'minimum-{year}-{k}.gz';payload=gzip.compress(header+v.tobytes(),compresslevel=6,mtime=0);(OUT/name).write_bytes(payload);manifest[name]={'bytes':len(payload),'sha256':hashlib.sha256(payload).hexdigest()}
 offset+=days
 print('Packed',year,flush=True)
report={'passed':True,'nodes':n,'days':nd,'source':'ERA5 via Open-Meteo AWS; immutable source objects match published maxima','timezone':'UTC','method':'Daily minimum of same 24 hourly records; np.min preserves missing hours','sourceObjects':{f'data/copernicus_era5/temperature_2m/{tag}.om':inventory[f'data/copernicus_era5/temperature_2m/{tag}.om']for tag,*_ in files},'independentApiChecks':checks,'files':manifest,'totalBytes':sum(x['bytes']for x in manifest.values())};(OUT/'minimum-audit.json').write_text(json.dumps(report))
# Upload derived files directly from the remote runner; no Mac download.
tag='comfy-minimum-preview-'+os.environ['GITHUB_RUN_ID'];repo=os.environ['GITHUB_REPOSITORY'];subprocess.run(['gh','release','create',tag,'--repo',repo,'--target',os.environ['GITHUB_SHA'],'--prerelease','--title','ERA5 daily minima preview','--notes','Derived ERA5 daily minima, 2020–2025; CC BY 4.0. Source cells and hours match Comfy daily maxima. Remote processing only.'],check=True)
for i in range(0,len(manifest),30):subprocess.run(['gh','release','upload',tag,*[str(OUT/x)for x in list(manifest)[i:i+30]],'--repo',repo],check=True)
meta={'version':1,'source':'ERA5 / ECMWF via Open-Meteo AWS','license':'CC BY 4.0','nodes':n,'years':m['available_years'],'total_days':nd,'data_url':f'/minimum-data/{tag}/','release_tag':tag,'audit_url':f'https://github.com/{repo}/releases/download/{tag}/minimum-audit.json'};(OUT/'minimum-metadata.json').write_text(json.dumps(meta));subprocess.run(['gh','release','upload',tag,str(OUT/'minimum-audit.json'),str(OUT/'minimum-metadata.json'),'--repo',repo],check=True);print(json.dumps({'stage':'complete','tag':tag,'outputBytes':report['totalBytes']}),flush=True)
