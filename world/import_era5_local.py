"""Bounded-disk bulk import: at most one compressed source file is retained.
Verified parallel HTTP ranges; source object ETag pinned for each file; resumable.
"""
exec(open(__file__.replace('import_era5_local.py','import_era5.py')).read().split('def task(')[0])
import requests,xml.etree.ElementTree as ET
NS={'s':'http://s3.amazonaws.com/doc/2006-03-01/'};inventory={}
for variable in arrays:
 response=requests.get('https://openmeteo.s3.amazonaws.com',params={'list-type':'2','prefix':f'data/copernicus_era5/{variable}/'},timeout=60);response.raise_for_status();xml=ET.fromstring(response.text)
 for c in xml.findall('s:Contents',NS):
  key=c.find('s:Key',NS).text;inventory[key]=(int(c.find('s:Size',NS).text),c.find('s:ETag',NS).text)
rowlist=[y for y in range(360) if (grid[y]>=0).any()];total=len(files)*len(rowlist)*2
print('Required source transfers',round(sum(inventory[f'data/copernicus_era5/{var}/{item[0]}.om'][0] for item in files for var in arrays)/1e9,2),'GB; disk bounded to one source object',flush=True)
def download(variable,item):
 tag=item[0];key=f'data/copernicus_era5/{variable}/{tag}.om';size,etag=inventory[key];url='https://openmeteo.s3.amazonaws.com/'+key;path=OUT/'working-source.om';marker=OUT/'working-source.json'
 if marker.exists() and json.loads(marker.read_text())==dict(key=key,etag=etag,size=size) and path.stat().st_size==size:return path
 if path.exists():path.unlink()
 fd=os.open(path,os.O_CREAT|os.O_RDWR,0o600);os.ftruncate(fd,size);block=8*1024*1024
 def part(lo):
  hi=min(size,lo+block)-1
  for attempt in range(4):
   try:
    response=requests.get(url,headers={'Range':f'bytes={lo}-{hi}','If-Match':etag},timeout=(20,120));response.raise_for_status();assert response.status_code==206 and response.headers['Content-Range'].startswith(f'bytes {lo}-{hi}/') and len(response.content)==hi-lo+1
    assert os.pwrite(fd,response.content,lo)==len(response.content);return
   except Exception:
    if attempt==3:raise
    time.sleep(2*(attempt+1))
 try:
  with concurrent.futures.ThreadPoolExecutor(max_workers=48) as pool:list(pool.map(part,range(0,size,block)))
  os.fsync(fd)
 finally:os.close(fd)
 marker.write_text(json.dumps(dict(key=key,etag=etag,size=size)));return path
# Keep chronological order and record completion only after daily data flushed.
for item in files:
 tag,begin,hours,lo,hi=item
 for variable in arrays:
  todo=[row for row in rowlist if f'{variable}/{tag}/{row}' not in done]
  if not todo:continue
  began=time.time();path=download(variable,item);print('Downloaded',variable,tag,round(path.stat().st_size/1e6),'MB in',round(time.time()-began),'s',flush=True)
  with OmFileReader(str(path)) as reader:
   assert tuple(reader.shape[:2])==(721,1440) and reader.shape[2]>=hi
   for row in todo:
    xs=np.flatnonzero(grid[row]>=0);erow=int(round((m['latitude'][row]+90)/.25));ex=xs*2+1;left=int(ex.min());right=int(ex.max())+1
    block=reader[erow:erow+1,left:right,lo:hi][0][ex-left];assert block.shape==(len(xs),hi-lo)
    daily=block.reshape(len(xs),-1,24);aggregate=np.max(daily,axis=2) if variable=='temperature_2m' else np.sum(daily,axis=2,dtype=np.float64).astype('f4')
    if variable=='precipitation':assert ((aggregate>=0)|np.isnan(aggregate)).all()
    offset=int(((begin+datetime.timedelta(hours=lo))-start).total_seconds()/86400);arrays[variable][offset:offset+aggregate.shape[1],grid[row,xs]]=aggregate.T;done.add(f'{variable}/{tag}/{row}')
  arrays[variable].flush();progress_path.write_text(json.dumps(sorted(done)));path.unlink();(OUT/'working-source.json').unlink();print('COMPLETED',variable,tag,len(done),'/',total,flush=True)
report={'source':'Copernicus ERA5 / ECMWF, Open-Meteo AWS Open Data','period':'2020–2025','days':nd,'nodes':n,'native_resolution_degrees':.25,'sampling_degrees':.5,'timezone':'UTC','elevation_downscaling':False,'daily_temperature':'Maximum of 24 hourly 2m temperatures; original stored 0.05°C precision','daily_precipitation':'Sum of 24 hourly total precipitation values (mm)','completed_tasks':len(done),'required_tasks':total,'files':[x[0] for x in files],'objects':{key:{'bytes':inventory[key][0],'etag':inventory[key][1]} for item in files for variable in arrays for key in [f'data/copernicus_era5/{variable}/{item[0]}.om']}}
(OUT/'import.json').write_text(json.dumps(report,indent=2)+'\n');print('IMPORT COMPLETE',flush=True)
