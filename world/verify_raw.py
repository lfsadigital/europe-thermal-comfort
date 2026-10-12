import numpy as np,json
from pathlib import Path
m=json.loads(Path('site/dist/assets/metadata.json').read_text());t=np.load('.cache/temperature.npy',mmap_mode='r');r=np.load('.cache/rain.npy',mmap_mode='r');idx=np.fromfile('site/dist/assets/node-grid.bin',dtype='i4');data=np.load('.cache/direct.npz');complete=data['mean_count']==2192;eligible=data['mean_valid'];a=np.flatnonzero(complete&eligible);b=np.flatnonzero(eligible&~complete);nodes=np.concatenate([a[::max(1,len(a)//20)][:20],b[::max(1,len(b)//20)][:20]]);configs=[m['default'],dict(m['default'],lower=20,upper=25,rain0=.1,rain1=1.1,rain2=9.9,pen1=.5,pen2=2.5,pen3=7,drymax=1.1),dict(m['default'],rain0=2,rain1=5,rain2=30,pen1=0,pen2=0,pen3=0,drymax=10),dict(m['default'],lower=-10,upper=10,rain0=0,rain1=.1,rain2=1,pen1=2,pen2=4,pen3=8,drymax=0)]
refs=[];offset=np.cumsum([0]+m['year_days'])
for key in ['mean']+list(map(str,m['available_years'])):
 a,b,years=(0,2192,6) if key=='mean' else (offset[int(key)-2020],offset[int(key)-2019],1)
 for p in configs:
  for n in nodes:
   tv=t[a:b,n].astype(float);rv=r[a:b,n];good=np.isfinite(tv)&np.isfinite(rv)&(rv>=0);tv=tv[good];rv=rv[good];pen=np.select([rv<=np.float32(p['rain0']),rv<=np.float32(p['rain1']),rv<=np.float32(p['rain2'])],[0,p['pen1'],p['pen2']],default=p['pen3']);score=float(np.mean(np.maximum(0,10-.5*np.maximum(p['lower']-tv,0)-.5*np.maximum(tv-p['upper'],0)-pen)));days=float(((tv>=p['lower'])&(tv<=p['upper'])&(rv<=np.float32(p['drymax']))).sum()/len(tv)*(b-a)/years);refs.append(dict(period=key,node=int(n),params=p,score=score,days=days))
Path('references.json').write_text(json.dumps(refs));print('Independent original daily references:',len(refs))
