"""Worldwide sunshine build. Refuses to run bulk work on a local computer."""
import os
if os.environ.get('GITHUB_ACTIONS')!='true':raise SystemExit('Bulk processing is remote-only. Run the sunshine GitHub Actions workflow.')
import json,datetime,time,hashlib,gzip,struct,concurrent.futures,xml.etree.ElementTree as ET,subprocess,tarfile,shutil,threading
from pathlib import Path
import numpy as np,requests
from omfiles import OmFileReader
from solar import sunshine
ROOT=Path(__file__).resolve().parents[1];OUT=Path(os.environ['RUNNER_TEMP'])/'comfy-sunshine-output';OUT.mkdir(exist_ok=True);CACHE=Path(os.environ['RUNNER_TEMP'])/'comfy-sunshine-cache';CACHE.mkdir(exist_ok=True)
CONTROL='https://comfy-days-sunshine-build-control.lfsalmeida92.workers.dev';KEY=os.environ['COMFY_SUN_BUILD_KEY'];REPO=os.environ['GITHUB_REPOSITORY'];HEADERS={'User-Agent':'ComfyDays-RemoteSunshineBuild/1.0'}
def control(name,value):
 r=requests.post(CONTROL+'/'+name,json=value,headers={'Authorization':'Bearer '+KEY},timeout=60);r.raise_for_status()
status_lock=threading.RLock();last_status=0
def status(**values):
 global last_status
 with status_lock:
  time.sleep(max(0,1.05-(time.monotonic()-last_status)));last_status=time.monotonic()
  values.update(at=datetime.datetime.now(datetime.timezone.utc).isoformat());control('status',values);print(json.dumps(values),flush=True)
def put(name,data):
 p=OUT/name;p.write_bytes(data);return name
m=json.loads((ROOT/'site/dist/assets/metadata.json').read_text());grid=np.fromfile(ROOT/'site/dist/assets/node-grid.bin',dtype='<i4').reshape(360,720);n=m['nodes'];nd=2192;dates=np.arange(np.datetime64('2020-01-01'),np.datetime64('2026-01-01'));months=dates.astype('datetime64[M]');offset=np.cumsum([0]+m['year_days']);start=datetime.datetime(2020,1,1,tzinfo=datetime.timezone.utc);epoch=datetime.datetime(1970,1,1,tzinfo=datetime.timezone.utc);end=datetime.datetime(2026,1,1,tzinfo=datetime.timezone.utc)
places=[('Porto',41.25,-8.25),('Paris',48.75,2.25),('Miami',25.75,-80.25),('Los Angeles',34.25,-118.25),('Nairobi',-1.25,36.75),('Nguruka',-5.25,30.75),('Cape Town',-33.75,18.75),('Oslo',59.75,10.75),('Buenos Aires',-34.75,-58.25),('Tokyo',35.75,139.75),('Sydney',-33.75,151.25),('Tromso',69.75,18.75)]
# Reject invalid reference coordinates before any bulk download.
for city,lat,lon in places:
 assert int(grid[int(round((89.75-lat)/.5)),int(round((lon+179.75)/.5))])>=0,('Reference has no land cell',city,lat,lon)
checkpoint=CACHE/'completed.json';done=set(json.loads(checkpoint.read_text()) if checkpoint.exists() else [])
arrays={}
for name in ['temperature','rain','sunshine']:
 path=CACHE/(name+'.npy');existing=path.exists();arrays[name]=np.lib.format.open_memmap(path,mode='r+' if existing else 'w+',dtype='f4',shape=(n,nd))
 assert arrays[name].shape==(n,nd) and arrays[name].dtype==np.float32
 if not existing:arrays[name][:]=np.nan
files=[]
for y in [2020,2021]:
 begin=datetime.datetime(y,1,1,tzinfo=datetime.timezone.utc);hours=(366 if y==2020 else 365)*24;files.append((f'year_{y}',begin,0,hours))
first=datetime.datetime(2022,1,1,tzinfo=datetime.timezone.utc)
for chunk in range(int((first-epoch).total_seconds()//3600)//504,int(np.ceil((end-epoch).total_seconds()/3600/504))):
 begin=epoch+datetime.timedelta(hours=chunk*504);lo=max(first,begin);hi=min(end,begin+datetime.timedelta(hours=504));files.append((f'chunk_{chunk}',begin,int((lo-begin).total_seconds()/3600),int((hi-begin).total_seconds()/3600)))
assert sum((hi-lo)//24 for _,_,lo,hi in files)==nd
ns={'s':'http://s3.amazonaws.com/doc/2006-03-01/'};inventory={};old=json.loads((ROOT/'site/docs/era5-import.json').read_text())['objects']
for variable in ['temperature_2m','precipitation','direct_radiation']:
 r=requests.get('https://openmeteo.s3.amazonaws.com',params={'list-type':'2','prefix':f'data/copernicus_era5/{variable}/'},timeout=60);r.raise_for_status()
 for item in ET.fromstring(r.text).findall('s:Contents',ns):
  key=item.find('s:Key',ns).text;inventory[key]={'bytes':int(item.find('s:Size',ns).text),'etag':item.find('s:ETag',ns).text}
 for tag,*_ in files:
  key=f'data/copernicus_era5/{variable}/{tag}.om';assert key in inventory
  if variable!='direct_radiation':assert inventory[key]==old[key],('Existing source changed',key)
required=sum(inventory[f'data/copernicus_era5/{v}/{x[0]}.om']['bytes'] for v in ['temperature_2m','precipitation','direct_radiation'] for x in files)
status(stage='import',required_source_bytes=required,completed=len(done),total=len(files)*3)
def download(variable,tag):
 key=f'data/copernicus_era5/{variable}/{tag}.om';info=inventory[key];path=CACHE/(variable+'-working.om');fd=os.open(path,os.O_CREAT|os.O_RDWR|os.O_TRUNC,0o600);os.ftruncate(fd,info['bytes']);block=8*1024*1024
 def part(lo):
  hi=min(info['bytes'],lo+block)-1
  for attempt in range(5):
   try:
    r=requests.get('https://openmeteo.s3.amazonaws.com/'+key,headers={'Range':f'bytes={lo}-{hi}','If-Match':info['etag']},timeout=(20,120));r.raise_for_status();assert r.status_code==206 and len(r.content)==hi-lo+1;assert os.pwrite(fd,r.content,lo)==len(r.content);return
   except Exception:
    if attempt==4:raise
    time.sleep(2*(attempt+1))
 try:
  with concurrent.futures.ThreadPoolExecutor(max_workers=24) as pool:list(pool.map(part,range(0,info['bytes'],block)))
 finally:os.close(fd)
 return path
completed=len(done);rows=[row for row in range(360) if (grid[row]>=0).any()]
def process(variable,name,tag,begin,lo,hi):
 global completed
 key=variable+'/'+tag
 if key in done:return
 seconds=np.arange(int(begin.timestamp())+lo*3600,int(begin.timestamp())+hi*3600,3600,dtype='i8');off=int(((begin+datetime.timedelta(hours=lo))-start).total_seconds()/86400)
 began=time.time();path=download(variable,tag)
 with OmFileReader(str(path)) as reader:
  assert tuple(reader.shape[:2])==(721,1440) and reader.shape[2]>=hi
  for row in rows:
   xs=np.flatnonzero(grid[row]>=0);erow=int(round((m['latitude'][row]+90)/.25));ex=xs*2+1;left=int(ex.min());right=int(ex.max())+1;hourly=reader[erow:erow+1,left:right,lo:hi][0][ex-left]
   assert hourly.shape==(len(xs),hi-lo)
   if name=='sunshine':hourly=sunshine(hourly,m['latitude'][row],np.asarray(m['longitude'])[xs],seconds)
   hourly=hourly.reshape(len(xs),-1,24);daily=np.max(hourly,axis=2) if name=='temperature' else np.sum(hourly,axis=2,dtype=np.float64).astype('f4')
   if name=='rain':assert ((daily>=0)|np.isnan(daily)).all()
   if name=='sunshine':assert ((daily>=0)&(daily<=86400)|np.isnan(daily)).all()
   arrays[name][grid[row,xs],off:off+daily.shape[1]]=daily
 arrays[name].flush();path.unlink()
 with status_lock:
  done.add(key);temporary=checkpoint.with_suffix('.tmp');temporary.write_text(json.dumps(sorted(done)));temporary.replace(checkpoint);completed+=1;status(stage='import',completed=completed,total=len(files)*3,latest=key,elapsed_seconds=round(time.time()-began))
for tag,begin,lo,hi in files:
 variables=[('temperature_2m','temperature'),('precipitation','rain'),('direct_radiation','sunshine')]
 if tag.startswith('year_'):
  for variable,name in variables:process(variable,name,tag,begin,lo,hi)
 else:
  with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
   for future in [pool.submit(process,v,nm,tag,begin,lo,hi) for v,nm in variables]:future.result()
def rainbins(rr):
 b=np.ceil(rr.astype(float)*10).astype('i8');prev=np.maximum(b-1,0);b-=((b>0)&(rr<=(prev/10).astype('f4')));assert ((b>=0)&(b<65535)).all();return b.astype('<u2')
def gridfile(name,values,dtype):
 out=np.full(grid.shape,0 if dtype=='<u2' else np.nan,dtype=dtype);mask=grid>=0;out[mask]=values[grid[mask]];return put(name,gzip.compress(out.tobytes(),compresslevel=9,mtime=0))
thresholds=np.arange(0,24.01,.5);defaults={};periods={};audits=[];referencehash=json.loads((ROOT/'site/docs/era5-data-manifest.json').read_text())['sha256'];default_maps={};chunk_size=2048
for period in ['mean']+list(map(str,range(2020,2026))):
 first,last,years=(0,nd,6) if period=='mean' else (int(offset[int(period)-2020]),int(offset[int(period)-2019]),1);days=last-first
 scores=np.full((49,n),np.nan,dtype='f4');counts=np.full((49,n),np.nan,dtype='f4');hours=np.full(n,np.nan,dtype='f4');coverage=np.zeros(n,dtype='<u2');maxerr=0;old_scores=np.full(n,np.nan,dtype='f4');old_days=np.full(n,np.nan,dtype='f4')
 for begin in range(0,n,chunk_size):
  stop=min(n,begin+chunk_size);tv=np.asarray(arrays['temperature'][begin:stop,first:last],dtype=float);rv=np.asarray(arrays['rain'][begin:stop,first:last]);ss=np.asarray(arrays['sunshine'][begin:stop,first:last],dtype=float)/3600;paired=np.isfinite(tv)&np.isfinite(rv)&(rv>=0);good=paired&np.isfinite(ss);eligible=np.ones(stop-begin,bool);oldeligible=eligible.copy()
  for month in np.unique(months[first:last]):
   ii=months[first:last]==month;eligible&=good[:,ii].sum(axis=1)>=np.ceil(ii.sum()*.9);oldeligible&=paired[:,ii].sum(axis=1)>=np.ceil(ii.sum()*.9)
  valid=good.sum(axis=1);coverage[begin:stop]=valid;rainpen=np.select([rv<=1,rv<=10,rv<=20],[0,.5,1],default=1.5);base=np.maximum(0,10-.5*np.maximum(18-tv,0)-.5*np.maximum(tv-26,0)-rainpen);comfortable=paired&(tv>=18)&(tv<=26)&(rv<=1)
  old_scores[begin:stop]=np.where(oldeligible,np.where(paired,base,0).sum(axis=1)/paired.sum(axis=1),np.nan);old_days[begin:stop]=np.where(oldeligible,comfortable.sum(axis=1)/paired.sum(axis=1)*days/years,np.nan)
  for k in range(stop-begin):
   if not eligible[k]:continue
   s=ss[k,good[k]];a=base[k,good[k]];sorted_s=np.sort(s);sorted_z=np.sort(s+2*a);prefix_s=np.r_[0,np.cumsum(sorted_s)];prefix_z=np.r_[0,np.cumsum(sorted_z)];i=np.searchsorted(sorted_s,thresholds,side='left');j=np.searchsorted(sorted_z,thresholds,side='left');values=np.clip((a.sum()-.5*(thresholds*i-prefix_s[i])+.5*(thresholds*j-prefix_z[j]))/len(s),0,10)
   comfort_s=np.sort(ss[k,good[k]&comfortable[k]]);total=len(comfort_s)-np.searchsorted(comfort_s,thresholds,side='left');annual=total/len(s)*days/years
   scores[:,begin+k]=values;counts[:,begin+k]=annual;hours[begin+k]=s.mean()
   direct=np.maximum(0,a-.5*np.maximum(6-s,0)).mean();err=abs(values[12]-direct);assert err<1e-9;maxerr=max(maxerr,err)
  status(stage='statistics',period=period,completed=stop,total=n)
 offhashes={}
 for label,v in [('score',old_scores),('days',old_days)]:
  a=np.full(grid.shape,np.nan,dtype='<f4');mask=grid>=0;a[mask]=v[grid[mask]];digest=hashlib.sha256(a.tobytes()).hexdigest();assert digest==referencehash[f'{label}-{period}.bin'],('Sunshine-off baseline changed',label,period);offhashes[label]=digest
 defaults[period]={}
 for idx,h in enumerate(thresholds):
  tag=f'{h:g}';defaults[period][tag]={'score':gridfile(f'sun-score-{period}-{tag}.bin.gz',scores[idx],'<f4'),'days':gridfile(f'sun-days-{period}-{tag}.bin.gz',counts[idx],'<f4')}
 periods[period]={'hours':gridfile(f'sun-hours-{period}.bin.gz',hours,'<f4'),'coverage':gridfile(f'sun-coverage-{period}.bin.gz',coverage,'<u2')}
 audits.append({'period':period,'eligible_cells':int(np.isfinite(hours).sum()),'minimum_paired_days':int(coverage.min()),'maximum_raw_default_error':maxerr,'sunshine_off_sha256':offhashes})
# Pack daily triples by year. Temperature is a lossless Float32 dictionary; rain bins match the existing engine.
raw_files={str(y):[] for y in range(2020,2026)}
for year in range(2020,2026):
 first,last=int(offset[year-2020]),int(offset[year-2019]);days=last-first
 for begin in range(0,n,chunk_size):
  stop=min(n,begin+chunk_size);tv=np.asarray(arrays['temperature'][begin:stop,first:last]);rv=np.asarray(arrays['rain'][begin:stop,first:last]);ss=np.asarray(arrays['sunshine'][begin:stop,first:last]);finite=np.isfinite(tv);dictionary=np.unique(tv[finite]).astype('<f4');assert len(dictionary)<65535
  index=np.where(finite,np.searchsorted(dictionary,tv),65535).astype('<u2');rain=rainbins(np.where(np.isfinite(rv)&(rv>=0),rv,0));rain[~np.isfinite(rv)|(rv<0)]=65535
  count=(stop-begin)*days;sun=ss.astype('<f4');shuffled=sun.view('u1').reshape(-1,4).T.copy().tobytes();body=struct.pack('<12I',0x53434C4D,1,begin,stop-begin,days,year,len(dictionary),0,0,0,0,0)+dictionary.tobytes()+index.tobytes()+rain.tobytes()+shuffled
  name=f'sun-daily-{year}-{begin//chunk_size}.gz';put(name,gzip.compress(body,compresslevel=9,mtime=0));assert (OUT/name).stat().st_size<25*1024*1024;raw_files[str(year)].append(name)
  status(stage='packing',year=year,completed=stop,total=n)
refs=[]
for name,lat,lon in places:
 y=int(round((89.75-lat)/.5));x=int(round((lon+179.75)/.5));node=int(grid[y,x]);assert node>=0
 refs.append({'city':name,'latitude':lat,'longitude':lon,'node':node,'temperature':arrays['temperature'][node].astype(float).tolist(),'rain':arrays['rain'][node].astype(float).tolist(),'sunshine_seconds':arrays['sunshine'][node].astype(float).tolist()})
put('sunshine-references.json.gz',gzip.compress(json.dumps({'dates':[str(d) for d in dates],'references':refs},separators=(',',':')).encode(),compresslevel=9,mtime=0))
meta={'version':1,'data_url':'https://comfy-days-climate-sunshine.lfsalmeida92.workers.dev/sun-v1/','periods':periods,'defaults':defaults,'daily_files':raw_files,'chunk_size':chunk_size,'minimum_default':6,'minimum_step':.5,'penalty_per_missing_hour':.5,'enabled_default':False,'source':'ERA5 direct radiation; Open-Meteo sunshine method; NREL SPA','units':'seconds in daily files; hours in panel','day_timezone':'UTC','coverage_threshold':.9,'total_days':nd,'nodes':n}
put('sunshine-metadata.json',json.dumps(meta,separators=(',',':')).encode());report={'result':'PASS','source':'ERA5 only; unchanged temperature/rain archive objects','source_transfer_bytes':required,'dates':nd,'nodes':n,'audits':audits,'hourly_api_pilot':json.loads(Path(__file__).with_name('pilot-verification.json').read_text()),'import_objects':{k:v for k,v in inventory.items() if any(k.endswith('/'+x[0]+'.om') for x in files)},'local_bulk_processing':False}
put('sunshine-audit.json',json.dumps(report,indent=2).encode())
manifest={'/sun-v1/'+p.name:{'hash':hashlib.md5(p.read_bytes()).hexdigest(),'size':p.stat().st_size} for p in OUT.iterdir() if p.is_file()};report['output_files']=len(manifest);report['output_bytes']=sum(v['size'] for v in manifest.values());control('manifest',manifest);control('report',report)
# A release provides a remote restart/rollback copy without Git history or artifact-storage charges.
bundle=CACHE/'sunshine-bundle.tar'
with tarfile.open(bundle,'w') as tar:
 for p in OUT.iterdir():tar.add(p,arcname=p.name)
if subprocess.run(['gh','release','view','comfy-sunshine-data-v1'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL).returncode:
 subprocess.run(['gh','release','create','comfy-sunshine-data-v1',str(bundle),'--repo',REPO,'--prerelease','--title','ERA5 sunshine data v1','--notes','Derived ERA5 daily sunshine data for Comfy Days, 2020–2025. Temperature/rain objects pinned to the current release. See world/sunshine source and audit. Data processing ran on GitHub-hosted Linux; raw archives are not stored in Git history.'],check=True)
else:subprocess.run(['gh','release','upload','comfy-sunshine-data-v1',str(bundle),'--clobber'],check=True)
status(stage='ready-for-upload',output_files=len(manifest),output_bytes=report['output_bytes'])
# The upload session is created by the authorized Cloudflare connector, not an account-wide token in CI.
for _ in range(180):
 r=requests.get(CONTROL+'/upload-session',headers={'Authorization':'Bearer '+KEY},timeout=60);r.raise_for_status();session=r.json()
 if session:break
 time.sleep(10)
else:raise TimeoutError('Waiting for scoped Cloudflare upload session; bundle remains remotely available')
def upload_bucket(bucket):
 form=[]
 for digest in bucket:
  path=next(path for path,v in manifest.items() if v['hash']==digest);data=(OUT/path.rsplit('/',1)[-1]).read_bytes();import base64;form.append((digest,(digest,base64.b64encode(data),'application/octet-stream')))
 for attempt in range(5):
  r=requests.post('https://api.cloudflare.com/client/v4/accounts/b555ed6cfcea943c34fd2da2101b6511/workers/assets/upload?base64=true',headers={'Authorization':'Bearer '+session['jwt']},files=form,timeout=(20,180));data=r.json()
  if r.ok and data.get('success'):return data.get('result',{}).get('jwt')
  if attempt==4:raise RuntimeError('Asset upload failed: HTTP '+str(r.status_code))
  time.sleep(2*(attempt+1))
completion=None
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
 for i,future in enumerate(concurrent.futures.as_completed([pool.submit(upload_bucket,b) for b in session['buckets']]),1):
  token=future.result()
  if token:completion=token
  print('Uploaded bucket',i,'/',len(session['buckets']),flush=True)
assert completion
control('completion',{'jwt':completion});status(stage='uploaded',output_files=len(manifest),output_bytes=report['output_bytes']);shutil.rmtree(CACHE)
