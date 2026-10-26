"""Remote-only, bounded-memory global daily AQI build and independent validation."""
import os
if os.environ.get('GITHUB_ACTIONS')!='true':raise SystemExit('Use the remote AQI daily build workflow; no local bulk import.')
import json,hashlib,gzip,struct,time,datetime as dt,math,subprocess,concurrent.futures,xml.etree.ElementTree as ET,tarfile,email.utils
from pathlib import Path
import requests,numpy as np
from omfiles import OmFileReader
from provider import VARIABLES,hourly,daily
ROOT=Path(__file__).resolve().parents[2];TMP=Path(os.environ['RUNNER_TEMP'])/'comfy-aqi-daily';TMP.mkdir(exist_ok=True);OUT=TMP/'out';OUT.mkdir(exist_ok=True)
pinned=ROOT/'site/dist/assets/aqi-daily-manifest.json'
if pinned.exists():
 descriptor=json.loads(pinned.read_text());assert descriptor['nodes']==85699 and descriptor['years']==[2023,2024,2025] and descriptor['independent_api_checks']
 print(json.dumps({'stage':'already_pinned','dataset':descriptor['dataset'],'data_url':descriptor['data_url']}),flush=True);raise SystemExit(0)
m=json.loads((ROOT/'site/dist/assets/metadata.json').read_text());grid=np.fromfile(ROOT/'site/dist/assets/node-grid.bin',dtype='<i4').reshape(m['shape']);n=m['nodes'];epoch=dt.datetime(1970,1,1,tzinfo=dt.timezone.utc);start=dt.datetime(2023,1,1,tzinfo=dt.timezone.utc);end=dt.datetime(2026,1,1,tzinfo=dt.timezone.utc);nd=(end-start).days
# Map every ERA5 cell centre to its nearest CAMS grid point, with explicit wrap.
coords=np.zeros((n,2));
for y,x in zip(*np.where(grid>=0)):coords[grid[y,x]]=[m['latitude'][y],m['longitude'][x]]
cy=np.floor((coords[:,0]+90)/.4+.5).astype(int);cx=(np.floor((coords[:,1]+180)/.4+.5).astype(int)%900)
probes=[('Lisbon',38.75,-9.25),('New Delhi',28.75,77.25),('Sydney',-33.75,151.25)]
pidx=[int(grid[int(round((89.75-lat)/.5)),int(round((lon+179.75)/.5))]) for _,lat,lon in probes];assert all(i>=0 for i in pidx)
step=217;first=int((start-epoch).total_seconds()/3600)-24;last=int((end-epoch).total_seconds()/3600);chunks=list(range(first//step,math.ceil(last/step)))
ns={'s':'http://s3.amazonaws.com/doc/2006-03-01/'};inventory={}
for v in VARIABLES:
 r=requests.get('https://openmeteo.s3.amazonaws.com',params={'list-type':2,'prefix':f'data/cams_global/{v}/'},timeout=60);r.raise_for_status();root=ET.fromstring(r.content);assert root.find('s:IsTruncated',ns).text=='false'
 for e in root.findall('s:Contents',ns):inventory[e.find('s:Key',ns).text]={'etag':e.find('s:ETag',ns).text,'bytes':int(e.find('s:Size',ns).text)}
needed={f'data/cams_global/{v}/chunk_{c}.om':inventory[f'data/cams_global/{v}/chunk_{c}.om'] for c in chunks for v in VARIABLES};fingerprint=hashlib.sha256(json.dumps(needed,sort_keys=True).encode()).hexdigest()
print(json.dumps({'stage':'inventory','nodes':n,'days':nd,'chunks':len(chunks),'sourceBytes':sum(v['bytes'] for v in needed.values()),'fingerprint':fingerprint}),flush=True)
repo=os.environ['GITHUB_REPOSITORY'];tag='comfy-aqi-daily-max3h-v1'
def gh(*args):
 for attempt in range(4):
  r=subprocess.run(['gh',*args,'--repo',repo])
  if r.returncode==0:return
  if attempt==3:raise RuntimeError('GitHub data checkpoint operation failed')
  time.sleep(5*(attempt+1))
r=subprocess.run(['gh','release','view',tag,'--repo',repo,'--json','assets'],capture_output=True,text=True);assets=set(a['name'] for a in json.loads(r.stdout)['assets']) if r.returncode==0 else set()
restored=False
if 'aqi-daily-checkpoint.tar' in assets:
 gh('release','download',tag,'--pattern','aqi-daily-checkpoint.tar','--dir',str(TMP),'--clobber')
 with tarfile.open(TMP/'aqi-daily-checkpoint.tar')as archive:archive.extractall(OUT,filter='data')
 manifest=json.loads((OUT/'aqi-daily-candidate.json').read_text());assert manifest['source_fingerprint']==fingerprint and manifest['grid_sha256']==hashlib.sha256((ROOT/'site/dist/assets/node-grid.bin').read_bytes()).hexdigest()
 assert hashlib.sha256((OUT/'aqi-daily-probes.npz').read_bytes()).hexdigest()==manifest['probe_sha256']
 saved=np.load(OUT/'aqi-daily-probes.npz');ph=saved['hourly'];probe_daily=saved['daily'];files=manifest['files'];restored=True
 for name,info in files.items():assert (OUT/name).stat().st_size==info['bytes'] and hashlib.sha256((OUT/name).read_bytes()).hexdigest()==info['sha256']
 print(json.dumps({'stage':'checkpoint_restored','dataset':manifest['dataset'],'files':len(files)}),flush=True)
if not restored:
 result=np.lib.format.open_memmap(TMP/'daily.npy',mode='w+',dtype='f8',shape=(n,nd));result[:]=np.nan
 previous={};carry=np.empty((n,0),dtype='f4');probe_hourly=[];day_offset=0
 
 def fetch_variable(v,chunk):
  key=f'data/cams_global/{v}/chunk_{chunk}.om';info=needed[key];path=TMP/(v+'.om')
  for attempt in range(4):
   try:
    r=requests.get('https://openmeteo.s3.amazonaws.com/'+key,headers={'If-Match':info['etag']},timeout=(30,180));r.raise_for_status();assert len(r.content)==info['bytes'];path.write_bytes(r.content);break
   except Exception:
    if attempt==3:raise
    time.sleep(2*(attempt+1))
  with OmFileReader(str(path)) as reader:
   assert tuple(reader.shape)==(451,900,step),(key,reader.shape)
   # Full chunk is ~350 MB; three decoders fit runner memory and avoid repeated
   # decompression of overlapping spatial blocks for hundreds of row slices.
   full=reader[:,:,:];sampled=full[cy,cx,:].copy();del full
  path.unlink();return v,sampled
 
 for ci,c in enumerate(chunks):
  began=time.time()
  with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:data=dict(pool.map(lambda v:fetch_variable(v,c),VARIABLES))
  lo=max(first,c*step)-c*step;hi=min(last,(c+1)*step)-c*step
  data={v:a[:,lo:hi] for v,a in data.items()}
  if not previous:
   previous={v:a[:,:24].copy() for v,a in data.items()};data={v:a[:,24:] for v,a in data.items()}
  data={v:np.concatenate([previous[v],a],axis=1) for v,a in data.items()};aq=hourly(data);previous={v:a[:,-24:].copy() for v,a in data.items()}
  probe_hourly.append(aq[pidx].copy());joined=np.concatenate([carry,aq],axis=1);full=joined.shape[1]//24
  if full:result[:,day_offset:day_offset+full]=daily(joined[:,:full*24].reshape(n,full,24));day_offset+=full
  carry=joined[:,full*24:].copy();result.flush();print(json.dumps({'stage':'import','done':ci+1,'of':len(chunks),'days':day_offset,'seconds':round(time.time()-began,1)}),flush=True)
 assert day_offset==nd and carry.shape[1]==0
 
 ph=np.concatenate(probe_hourly,axis=1);assert ph.shape==(len(probes),nd*24)
 probe_daily=np.asarray(result[pidx],dtype='f8')
 files={}
 for yi,year in enumerate([2023,2024,2025]):
  offset=sum(366 if y==2024 else 365 for y in range(2023,year));days=366 if year==2024 else 365
  for part in range(math.ceil(n/2048)):
   a=part*2048;b=min(n,a+2048);v=np.asarray(result[a:b,offset:offset+days],dtype='<f8');name=f'aqi-daily-{year}-{part}.gz';header=struct.pack('<8I',0x41514431,1,a,b-a,days,year,3,22);payload=gzip.compress(header+v.tobytes(),compresslevel=6,mtime=0);(OUT/name).write_bytes(payload);files[name]={'bytes':len(payload),'sha256':hashlib.sha256(payload).hexdigest()}
 np.savez_compressed(OUT/'aqi-daily-probes.npz',hourly=ph,daily=probe_daily)
 manifest={'version':1,'dataset':'cams-global-max3h-'+fingerprint[:16],'years':[2023,2024,2025],'nodes':n,'chunk_size':2048,'method':'max of complete 3-hour windows within UTC day','minimum_valid_hours':22,'source':'CAMS global / ECMWF via Open-Meteo AWS','source_commit':'03d62919c419f1eccad8dcbbcf7f92a2dd7069b4','license':'CC BY 4.0','grid_sha256':hashlib.sha256((ROOT/'site/dist/assets/node-grid.bin').read_bytes()).hexdigest(),'data_url':f'https://github.com/{repo}/releases/download/{tag}/','files':files,'independent_api_checks':[],'validation':'pending','source_fingerprint':fingerprint,'source_objects':needed,'daily_valid_count':int(np.isfinite(result).sum()),'daily_expected_count':n*nd,'probe_sha256':hashlib.sha256((OUT/'aqi-daily-probes.npz').read_bytes()).hexdigest()}
 (OUT/'aqi-daily-candidate.json').write_text(json.dumps(manifest))
 with tarfile.open(TMP/'aqi-daily-checkpoint.tar','w')as archive:
  for file in OUT.iterdir():archive.add(file,arcname=file.name)
 if not assets:gh('release','create',tag,'--target',os.environ['GITHUB_SHA'],'--prerelease','--title','CAMS daily AQI candidate — validation pending','--notes','Recoverable derived global daily AQI files. Not a validated production dataset until aqi-daily-manifest.json records passed API comparisons. CC BY 4.0.')
 gh('release','upload',tag,str(TMP/'aqi-daily-checkpoint.tar'),'--clobber')
 gh('release','upload',tag,str(OUT/'aqi-daily-candidate.json'),str(OUT/'aqi-daily-probes.npz'),'--clobber')
 print(json.dumps({'stage':'checkpoint_saved','tag':tag,'bytes':sum(f['bytes'] for f in files.values())}),flush=True)
# Complete any interrupted per-file upload from the durable checkpoint bundle.
missing=[name for name in files if name not in assets]
for offset in range(0,len(missing),20):gh('release','upload',tag,*[str(OUT/x) for x in missing[offset:offset+20]],'--clobber')
# Source checks are independent of ingestion and may retry without rebuilding.
def api_get(q):
 for attempt in range(4):
  try:
   r=requests.get('https://air-quality-api.open-meteo.com/v1/air-quality',params=q,timeout=(15,60))
   if r.status_code==429:
    value=r.headers.get('Retry-After','');delay=float(value) if value.isdigit() else max(1,email.utils.parsedate_to_datetime(value).timestamp()-time.time()) if value else 60
    if delay>300:raise RuntimeError('Source requested a longer wait; checkpoint is retained')
    time.sleep(delay);continue
   r.raise_for_status();return r.json()
  except requests.RequestException as error:
   print(json.dumps({'stage':'api_retry','attempt':attempt+1,'error':type(error).__name__}),flush=True)
   if attempt==3:raise
   time.sleep(5*(attempt+1))
 raise RuntimeError('Source quota retries exhausted; checkpoint is retained')
checks=[]
for pi,(name,lat,lon) in enumerate(probes):
 for month in [1,7]:
  a=dt.datetime(2025,month,1,tzinfo=dt.timezone.utc);b=a+dt.timedelta(days=7)
  q={'latitude':lat,'longitude':lon,'start_date':a.strftime('%Y-%m-%d'),'end_date':(b-dt.timedelta(days=1)).strftime('%Y-%m-%d'),'hourly':'us_aqi','domains':'cams_global','timezone':'UTC'}
  d=api_get(q);expected=np.array([np.nan if v is None else v for v in d['hourly']['us_aqi']]);offset=int((a-start).total_seconds()/3600);actual=ph[pi,offset:offset+len(expected)];mask=np.isfinite(actual)&np.isfinite(expected)
  err=float(np.max(np.abs(actual[mask]-expected[mask])));assert mask.sum()==168 and err<=.501,(name,month,err)
  target=daily(expected.reshape(-1,24));got=probe_daily[pi,offset//24:offset//24+7];assert np.nanmax(np.abs(got-target))<=.501
  checks.append({'place':name,'start':a.strftime('%Y-%m-%d'),'hours':int(mask.sum()),'maxAQIErrorVsIntegerRoundedAPI':err});print(json.dumps({'stage':'api_check_passed',**checks[-1]}),flush=True);time.sleep(2)
manifest['independent_api_checks']=checks;manifest['validation']='passed';(OUT/'aqi-daily-manifest.json').write_text(json.dumps(manifest));gh('release','upload',tag,str(OUT/'aqi-daily-manifest.json'),'--clobber');gh('release','edit',tag,'--title','Validated Comfy daily AQI · global 2023–2025','--notes','Validated derived CAMS global US AQI: maximum 3-hour daily mean, >=22 valid UTC hours. Global grid/date checks and six independent real API comparisons passed; see aqi-daily-manifest.json. CC BY 4.0. The checkpoint bundle preserves resumability and source provenance.')
print(json.dumps({'stage':'published_data','tag':tag,'dataset':manifest['dataset'],'manifest':manifest['data_url']+'aqi-daily-manifest.json','bytes':sum(x['bytes'] for x in files.values()),'checks':checks}),flush=True)
