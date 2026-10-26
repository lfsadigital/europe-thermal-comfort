"""Small independent API comparison before waiting for a global build."""
import datetime as dt,json,os,math,tempfile,concurrent.futures
from pathlib import Path
import requests,numpy as np
from omfiles import OmFileReader
from provider import VARIABLES,hourly,daily
start=dt.datetime(2025,1,1,tzinfo=dt.timezone.utc);epoch=dt.datetime(1970,1,1,tzinfo=dt.timezone.utc);first=int((start-epoch).total_seconds()/3600)-24;last=first+24+168;step=217;tmp=Path(tempfile.mkdtemp());chunks=range(first//step,math.ceil(last/step));places=[('Lisbon',38.75,-9.25),('New Delhi',28.75,77.25),('Sydney',-33.75,151.25)]
def load(v):
 arrays=[]
 for c in chunks:
  key=f'data/cams_global/{v}/chunk_{c}.om';r=requests.get('https://openmeteo.s3.amazonaws.com/'+key,timeout=180);r.raise_for_status();p=tmp/(v+'.om');p.write_bytes(r.content);lo=max(first,c*step)-c*step;hi=min(last,(c+1)*step)-c*step
  with OmFileReader(str(p))as reader:
   vals=[]
   for _,lat,lon in places:
    y=int(math.floor((lat+90)/.4+.5));x=int(math.floor((lon+180)/.4+.5))%900;vals.append(reader[y:y+1,x:x+1,lo:hi].reshape(-1))
   arrays.append(np.stack(vals))
  p.unlink()
 return v,np.concatenate(arrays,axis=1)
with concurrent.futures.ThreadPoolExecutor(max_workers=3)as pool:data=dict(pool.map(load,VARIABLES))
actual=hourly(data);checks=[]
for i,(name,lat,lon)in enumerate(places):
 r=requests.get('https://air-quality-api.open-meteo.com/v1/air-quality',params={'latitude':lat,'longitude':lon,'start_date':'2025-01-01','end_date':'2025-01-07','domains':'cams_global','hourly':'us_aqi,us_aqi_pm2_5,us_aqi_pm10,us_aqi_nitrogen_dioxide,us_aqi_ozone,us_aqi_sulphur_dioxide,us_aqi_carbon_monoxide','timezone':'UTC'},timeout=120);r.raise_for_status();d=r.json();expected=np.array(d['hourly']['us_aqi'],dtype='f4');err=float(np.nanmax(np.abs(actual[i]-expected)));print(json.dumps({'place':name,'sourceCell':[d['latitude'],d['longitude']],'maximumError':err,'ours':actual[i,:12].tolist(),'api':expected[:12].tolist()}),flush=True);assert np.isfinite(expected).sum()==168 and err<=.16,(name,err);checks.append({'place':name,'hours':168,'maximumError':err})
print(json.dumps({'result':'PASS','checks':checks}),flush=True)
