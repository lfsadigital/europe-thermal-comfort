exec(open(__file__.replace('miami_followup.py','investigate_miami.py')).read().split('report={')[0])
base=json.load(open(out/'results.json'));extra={}
for label,lat,lon,selection in [('land-selection',25.78805,-80.31694,'land'),('western-cell',25.75,-80.5,'nearest')]:
 p=out/(label+'.json');par=dict(latitude=lat,longitude=lon,start_date=dates[0],end_date=dates[-1],daily='temperature_2m_max,precipitation_sum',models='era5',timezone='America/New_York',elevation='nan',cell_selection=selection)
 if not p.exists():
  with urllib.request.urlopen('https://archive-api.open-meteo.com/v1/archive?'+urllib.parse.urlencode(par),timeout=120) as response:p.write_text(json.dumps(json.load(response)))
 d=json.loads(p.read_text());t=np.array(d['daily']['temperature_2m_max']);r=np.array(d['daily']['precipitation_sum']);pen=np.select([r<=1,r<=10,r<=20],[0,.5,1],default=1.5)
 extra[label]=dict(returned=[d['latitude'],d['longitude']],score=float(np.maximum(0,10-.5*np.maximum(18-t,0)-.5*np.maximum(t-26,0)-pen).mean()),days_year=float(((t>=18)&(t<=26)&(r<=1)).sum()/6),mean_tmax=float(t.mean()),mae_vs_MIA=float(np.abs(t-obs['TMAX']).mean()))
p=out/'USW00012882.dly'
if not p.exists():
 with urllib.request.urlopen('https://www.ncei.noaa.gov/pub/data/ghcn/daily/all/USW00012882.dly',timeout=120) as response:p.write_bytes(response.read())
a={k:np.full(2192,np.nan) for k in obs}
for line in p.read_text().splitlines():
 y=int(line[11:15]);m=int(line[15:17]);el=line[17:21]
 if y not in range(2020,2026) or el not in a:continue
 for day in range(1,calendar.monthrange(y,m)[1]+1):
  field=line[21+(day-1)*8:21+day*8];v=int(field[:5])
  if v!=-9999 and field[6]==' ':a[el][ix[f'{y}-{m:02}-{day:02}']]=v/10
mask=np.isfinite(a['TMAX'])&np.isfinite(a['PRCP']);t=a['TMAX'][mask];r=a['PRCP'][mask];pen=np.select([r<=1,r<=10,r<=20],[0,.5,1],default=1.5)
extra['Opa Locka station']=dict(valid_days=int(mask.sum()),mean_tmax=float(t.mean()),score=float(np.maximum(0,10-.5*np.maximum(18-t,0)-.5*np.maximum(t-26,0)-pen).mean()),days_year=float(((t>=18)&(t<=26)&(r<=1)).sum()/len(t)*2192/6))
# Comparison of temperature at same date labels, restricted to available station records.
miami=next(c for c in json.load(open(ROOT/'share/era5-comparison/results.json'))['results'] if c['city']=='Miami');nt=np.load(ROOT/'.cache/temperature.npy',mmap_mode='r')[:,miami['node']];et=np.array(json.load(open(ROOT/'share/era5-comparison/era5-raw-1.json'))[2]['daily']['temperature_2m_max'])
extra['Opa Locka station']['noaa_tmax_mae']=float(np.abs(nt[mask]-t).mean());extra['Opa Locka station']['era5_tmax_mae']=float(np.abs(et[mask]-t).mean())
(out/'followup-results.json').write_text(json.dumps(extra,indent=2)+'\n');print(json.dumps(extra,indent=2))
