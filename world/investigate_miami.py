import json,urllib.request,urllib.parse,calendar,datetime,math
from pathlib import Path
import numpy as np,xarray as xr
ROOT=Path(__file__).resolve().parent;out=ROOT/'share/miami-audit';out.mkdir(exist_ok=True)
station='USW00012839';url=f'https://www.ncei.noaa.gov/pub/data/ghcn/daily/all/{station}.dly';file=out/f'{station}.dly'
if not file.exists():
 with urllib.request.urlopen(url,timeout=120) as r:file.write_bytes(r.read())
dates=[(datetime.date(2020,1,1)+datetime.timedelta(days=i)).isoformat() for i in range(2192)];ix={d:i for i,d in enumerate(dates)}
obs={k:np.full(2192,np.nan) for k in ['TMAX','PRCP']};flags={k:{} for k in obs}
for line in file.read_text().splitlines():
 y=int(line[11:15]);m=int(line[15:17]);el=line[17:21]
 if y<2020 or y>2025 or el not in obs:continue
 for day in range(1,calendar.monthrange(y,m)[1]+1):
  field=line[21+(day-1)*8:21+day*8];v=int(field[:5]);q=field[6];flag=field[5:8];d=f'{y}-{m:02}-{day:02}'
  flags[el][flag]=flags[el].get(flag,0)+1
  if v!=-9999 and q==' ':obs[el][ix[d]]=v/10
report={'station':station,'station_coordinates':[25.78805,-80.31694],'station_url':url,'quality_policy':'Exclude missing -9999 or any nonblank QFLAG; retain trace PRCP as supplied zero','flags':flags,'sources':{}}
miami=next(c for c in json.load(open(ROOT/'share/era5-comparison/results.json'))['results'] if c['city']=='Miami');tv=np.load(ROOT/'.cache/temperature.npy',mmap_mode='r')[:,miami['node']];rv=np.load(ROOT/'.cache/rain.npy',mmap_mode='r')[:,miami['node']]
sources={'Station':(obs['TMAX'],obs['PRCP']),'NOAA CPC':(tv,rv)}
e=json.load(open(ROOT/'share/era5-comparison/era5-raw-1.json'))[2];sources['ERA5 grid UTC']=(np.array(e['daily']['temperature_2m_max']),np.array(e['daily']['precipitation_sum']))
for label,lat,lon,tz in [('ERA5 grid local',25.75,-80.25,'America/New_York'),('ERA5 station local',25.78805,-80.31694,'America/New_York')]:
 p=out/(label.replace(' ','-')+'.json');par=dict(latitude=lat,longitude=lon,start_date=dates[0],end_date=dates[-1],daily='temperature_2m_max,precipitation_sum',models='era5',timezone=tz,elevation='nan',cell_selection='nearest')
 if not p.exists():
  with urllib.request.urlopen('https://archive-api.open-meteo.com/v1/archive?'+urllib.parse.urlencode(par),timeout=120) as r:p.write_text(json.dumps(json.load(r)))
 d=json.loads(p.read_text());assert d['daily']['time']==dates
 report[label]={'requested':[lat,lon],'returned':[d['latitude'],d['longitude']],'timezone':d['timezone']}
 sources[label]=(np.array(d['daily']['temperature_2m_max']),np.array(d['daily']['precipitation_sum']))
common=np.ones(2192,dtype=bool)
for t,r in sources.values():common &= np.isfinite(t)&np.isfinite(r)&(r>=0)
def metric(t,r,mask):
 t=np.asarray(t)[mask];r=np.asarray(r)[mask];pen=np.select([r<=1,r<=10,r<=20],[0,.5,1],default=1.5);score=np.maximum(0,10-.5*np.maximum(18-t,0)-.5*np.maximum(t-26,0)-pen)
 return dict(score=float(score.mean()),days_year=float(((t>=18)&(t<=26)&(r<=1)).sum()/len(t)*2192/6),mean_tmax=float(t.mean()),annual_precip=float(r.mean()*2192/6),temperature_eligible_days_year=float(((t>=18)&(t<=26)).sum()/len(t)*2192/6),dry_days_year=float((r<=1).sum()/len(r)*2192/6))
st,sp=obs['TMAX'],obs['PRCP'];report['common_days']=int(common.sum())
for name,(t,r) in sources.items():
 good=np.isfinite(t)&np.isfinite(r)&(r>=0);a=metric(t,r,good);a['valid_days']=int(good.sum());a['common_dates']=metric(t,r,common)
 if name!='Station':
  a['tmax_error_vs_station']=dict(bias=float((t[common]-st[common]).mean()),mae=float(np.abs(t[common]-st[common]).mean()),rmse=float(np.sqrt(((t[common]-st[common])**2).mean())))
  a['precip_error_vs_station']=dict(bias=float((r[common]-sp[common]).mean()),mae=float(np.abs(r[common]-sp[common]).mean()),dry_class_agreement=float(((r[common]<=1)==(sp[common]<=1)).mean()))
 a['monthly_tmax']=[float(t[np.array([d[5:7]==f'{m:02}' for d in dates])&good].mean()) for m in range(1,13)]
 report['sources'][name]=a
# Verify raw NOAA extraction and metadata: original native grid is longitude 0..360.
for year in range(2020,2026):
 sel=np.array([d.startswith(str(year)) for d in dates])
 for var,arr in [('tmax',tv),('precip',rv)]:
  with xr.open_dataset(ROOT/f'.cache/noaa/{var}.{year}.nc',engine='h5netcdf') as d:
   raw=d[var].sel(lat=25.75,lon=279.75).values
   np.testing.assert_allclose(raw,arr[sel],equal_nan=True)
   if year==2020:report[var+'_attributes']=dict(d[var].attrs)
# Separate effects via swapped input variables on common dates.
report['swapped_inputs']={name:metric(t,r,common) for name,(t,r) in {'NOAA temp + ERA5 rain':(tv,sources['ERA5 grid UTC'][1]),'ERA5 temp + NOAA rain':(sources['ERA5 grid UTC'][0],rv)}.items()}
(out/'results.json').write_text(json.dumps(report,indent=2,default=lambda x:x.tolist() if hasattr(x,'tolist') else str(x))+'\n')
print(json.dumps(report['sources'],indent=2));print('common',report['common_days']);print('swapped',report['swapped_inputs'])
