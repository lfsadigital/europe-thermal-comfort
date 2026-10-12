"""Read-only source benchmark; uses the production cell selection and daily formula."""
import gzip, json, math, datetime, urllib.request, urllib.parse, time, hashlib
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'share/era5-comparison';OUT.mkdir(exist_ok=True)
meta=json.loads((ROOT/'site/dist/assets/metadata.json').read_text())
node=np.fromfile(ROOT/'site/dist/assets/node-grid.bin',dtype='<i4').reshape(360,720)
temp=np.load(ROOT/'.cache/temperature.npy',mmap_mode='r');rain=np.load(ROOT/'.cache/rain.npy',mmap_mode='r')
points=[('Europe','Porto',41.1579,-8.6291),('Europe','Madrid',40.4168,-3.7038),('Europe','London',51.5074,-.1278),('Europe','Rome',41.9028,12.4964),('USA','Los Angeles',34.0522,-118.2437),('USA','New York',40.7128,-74.006),('USA','Miami',25.7617,-80.1918),('USA','Chicago',41.8781,-87.6298),('Africa','Nairobi',-1.2921,36.8219),('Africa','Nguruka',-5.1,30.4),('Africa','Cape Town',-33.9249,18.4241),('Africa','Marrakech',31.6295,-7.9811)]
# Nguruka coordinates replaced below with exact catalog coordinates when available.
places=json.load(gzip.open(ROOT/'site/dist/assets/places.json.gz'))
print(type(places),flush=True)
if isinstance(places,dict): places=places.get('places',[])
for p in places:
 if isinstance(p,list) and p[1]=='Nguruka':
  points=[(reg,name,p[2],p[3]) if name=='Nguruka' else (reg,name,lat,lon) for reg,name,lat,lon in points];break
cells=[]
for reg,name,lat,lon in points:
 row=int(math.floor((meta['latitude'][0]-lat)/.5+.5));col=int(math.floor((lon-meta['longitude'][0])/.5+.5))%720
 best=(float('inf'),None,None)
 for y in range(max(0,row-2),min(359,row+2)+1):
  for dx in range(-2,3):
   x=(col+dx)%720;dlon=(meta['longitude'][x]-lon+540)%360-180;dist=math.hypot(meta['latitude'][y]-lat,dlon)
   if node[y,x]>=0 and dist<best[0]:best=(dist,y,x)
 dist,y,x=best;assert dist<=.75
 cells.append(dict(region=reg,city=name,city_coordinates=[lat,lon],cell=[meta['latitude'][y],meta['longitude'][x]],node=int(node[y,x])))
expected=[(datetime.date(2020,1,1)+datetime.timedelta(days=i)).isoformat() for i in range(2192)]
def calc(tv,rv):
 tv=np.array(tv,dtype=float);rv=np.array(rv,dtype=float);good=np.isfinite(tv)&np.isfinite(rv)&(rv>=0)
 eligible=True
 for year in range(2020,2026):
  for month in range(1,13):
   ii=np.array([d.startswith(f'{year}-{month:02}') for d in expected]);eligible &= int(good[ii].sum())>=math.ceil(int(ii.sum())*.9)
 t=tv[good];r=rv[good];pen=np.select([r<=1,r<=10,r<=20],[0,.5,1],default=1.5)
 daily=np.maximum(0,10-.5*np.maximum(18-t,0)-.5*np.maximum(t-26,0)-pen)
 comfy=(t>=18)&(t<=26)&(r<=1)
 # Independent scalar implementation verifies threshold handling and zero floor.
 scores=[max(0,10-.5*max(18-a,0,a-26)-(0 if b<=1 else .5 if b<=10 else 1 if b<=20 else 1.5)) for a,b in zip(t,r)]
 assert abs(sum(scores)/len(scores)-float(daily.mean()))<1e-10
 assert sum(18<=a<=26 and b<=1 for a,b in zip(t,r))==int(comfy.sum())
 return dict(score=float(daily.mean()),days_per_year=float(comfy.sum()/good.sum()*2192/6),qualifying_days=int(comfy.sum()),valid_days=int(good.sum()),eligible=bool(eligible),mean_tmax=float(t.mean()),mean_precip=float(r.mean()),dry_days_per_year=float((r<=1).sum()/len(r)*2192/6)),good,tv,rv
results=[];urls=[]
for start in range(0,len(cells),4):
 batch=cells[start:start+4];path=OUT/f'era5-raw-{start//4}.json'
 params=dict(latitude=','.join(str(c['cell'][0]) for c in batch),longitude=','.join(str(c['cell'][1]) for c in batch),start_date='2020-01-01',end_date='2025-12-31',daily='temperature_2m_max,precipitation_sum',models='era5',timezone='GMT',elevation=','.join(['nan']*len(batch)),cell_selection='nearest')
 url='https://archive-api.open-meteo.com/v1/archive?'+urllib.parse.urlencode(params);urls.append(url)
 if not path.exists():
  for attempt in range(3):
   try:
    with urllib.request.urlopen(url,timeout=120) as resp:data=json.load(resp)
    path.write_text(json.dumps(data));break
   except Exception:
    if attempt==2:raise
    time.sleep(5)
 data=json.loads(path.read_text());assert len(data)==len(batch)
 for c,d in zip(batch,data):
  assert d['daily']['time']==expected
  assert d['daily_units']['temperature_2m_max']=='°C' and d['daily_units']['precipitation_sum']=='mm'
  assert abs(d['latitude']-c['cell'][0])<1e-6 and abs(d['longitude']-c['cell'][1])<1e-6
  n,ng,nt,nr=calc(temp[:,c['node']],rain[:,c['node']]);e,eg,et,er=calc(d['daily']['temperature_2m_max'],d['daily']['precipitation_sum'])
  joint=ng&eg
  result=dict(**c,noaa=n,era5=e,delta_score=e['score']-n['score'],delta_days=e['days_per_year']-n['days_per_year'],paired_comparison_days=int(joint.sum()),tmax_mae=float(np.abs(et[joint]-nt[joint]).mean()),tmax_bias=float((et[joint]-nt[joint]).mean()),precip_bias=float((er[joint]-nr[joint]).mean()))
  joint_e,_,_,_=calc(np.where(joint,et,np.nan),np.where(joint,er,np.nan))
  joint_n,_,_,_=calc(np.where(joint,nt,np.nan),np.where(joint,nr,np.nan))
  result['common_dates_delta_score']=joint_e['score']-joint_n['score']
  result['common_dates_delta_days']=joint_e['days_per_year']-joint_n['days_per_year']
  flat=int(np.flatnonzero(node.ravel()==c['node'])[0])
  site_score=float(np.fromfile(ROOT/'site/dist/assets/score-mean.bin',dtype='<f4')[flat]);site_days=float(np.fromfile(ROOT/'site/dist/assets/days-mean.bin',dtype='<f4')[flat])
  if n['eligible']:
   assert abs(site_score-n['score'])<1e-5 and abs(site_days-n['days_per_year'])<2e-5
  else:
   assert math.isnan(site_score) and math.isnan(site_days)
  result['production_verified']=True
  results.append(result);print(c['city'],round(n['score'],2),round(e['score'],2),round(n['days_per_year'],1),round(e['days_per_year'],1),n['valid_days'],flush=True)
report=dict(period='2020–2025',filters=dict(lower=18,upper=26,drymax=1,rain1=10,rain2=20,penalties=[.5,1,1.5],maximum=10,minimum=0,temperature_penalty=.5),era5_daily_timezone='GMT',era5_elevation_downscaling=False,urls=urls,results=results)
(OUT/'results.json').write_text(json.dumps(report,indent=2)+'\n')
