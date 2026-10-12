"""Independent raw daily references and bulk/API precision validation."""
import json,math
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT/'.cache/era5';t=np.load(SOURCE/'temperature.npy',mmap_mode='r');r=np.load(SOURCE/'rain.npy',mmap_mode='r');report=json.loads((ROOT/'share/era5-comparison/results.json').read_text());refs=[];validation=[]
for i,c in enumerate(report['results']):
 data=json.loads((ROOT/f'share/era5-comparison/era5-raw-{i//4}.json').read_text())[i%4]['daily'];n=c['node'];tv=np.asarray(t[:,n],dtype=float);rv=np.asarray(r[:,n],dtype=float);et=np.asarray(data['temperature_2m_max']);er=np.asarray(data['precipitation_sum']);assert np.isfinite(tv).all() and np.isfinite(rv).all()
 # API rounds temperature to one decimal; original OM archive retains 0.05°C.
 assert np.abs(tv-et).max()<=.05001
 assert np.abs(rv-er).max()<.011
 validation.append(dict(city=c['city'],max_temperature_api_difference=float(np.abs(tv-et).max()),max_precipitation_api_difference=float(np.abs(rv-er).max())))
 for period,first,last,years in [('mean',0,2192,6),('2025',1827,2192,1)]:
  for p in [dict(lower=18,upper=26,rain0=1,rain1=10,rain2=20,pen1=.5,pen2=1,pen3=1.5,drymax=1),dict(lower=20,upper=25,rain0=.1,rain1=1.1,rain2=9.9,pen1=.5,pen2=2.5,pen3=7,drymax=.1)]:
   tt=tv[first:last];rr=rv[first:last];scores=[max(0,10-.5*max(p['lower']-a,a-p['upper'],0)-(0 if b<=float(np.float32(p['rain0'])) else p['pen1'] if b<=float(np.float32(p['rain1'])) else p['pen2'] if b<=float(np.float32(p['rain2'])) else p['pen3'])) for a,b in zip(tt,rr)];days=sum(p['lower']<=a<=p['upper'] and b<=float(np.float32(p['drymax'])) for a,b in zip(tt,rr))/years
   refs.append(dict(city=c['city'],latitude=c['city_coordinates'][0],longitude=c['city_coordinates'][1],cell=c['cell'],period=period,params=p,score=sum(scores)/len(scores),days=days))
(ROOT/'share/era5-references.json').write_text(json.dumps(refs,indent=2)+'\n');(ROOT/'share/era5-bulk-api-validation.json').write_text(json.dumps(validation,indent=2)+'\n');print('PASS',len(validation),'bulk/API cell checks;',len(refs),'independent references')
