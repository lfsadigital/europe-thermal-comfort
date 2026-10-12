import json,sys,subprocess,math
from pathlib import Path
import numpy as np
root=Path(__file__).resolve().parent;period=sys.argv[1];t=np.load(root/'.cache/era5/temperature.npy',mmap_mode='r');r=np.load(root/'.cache/era5/rain.npy',mmap_mode='r');m=json.loads((root/'site/dist/assets/metadata.json').read_text());offs=np.cumsum([0]+m['year_days']);a,b,y=(0,2192,6) if period=='mean' else (int(offs[int(period)-2020]),int(offs[int(period)-2019]),1)
configs=[m['default'],dict(lower=20,upper=25,rain0=.1,rain1=1.1,rain2=9.9,pen1=.5,pen2=2.5,pen3=7,drymax=.1),dict(lower=-10,upper=10,rain0=0,rain1=.1,rain2=1,pen1=5,pen2=8,pen3=10,drymax=0)]
ns=sorted(set(list(range(0,m['nodes'],2048))+[c['node'] for c in json.load(open(root/'share/era5-comparison/results.json'))['results']]));refs=[]
for n in ns:
 tt=np.asarray(t[a:b,n],dtype=float);rr=np.asarray(r[a:b,n],dtype=float);good=np.isfinite(tt)&np.isfinite(rr)&(rr>=0);tt=tt[good];rr=rr[good]
 for p in configs:
  scores=[max(0,10-.5*max(p['lower']-v,v-p['upper'],0)-(0 if w<=float(np.float32(p['rain0'])) else p['pen1'] if w<=float(np.float32(p['rain1'])) else p['pen2'] if w<=float(np.float32(p['rain2'])) else p['pen3'])) for v,w in zip(tt,rr)];days=sum(p['lower']<=v<=p['upper'] and w<=float(np.float32(p['drymax'])) for v,w in zip(tt,rr))/len(tt)*(b-a)/y
  refs.append(dict(node=n,params=p,score=sum(scores)/len(scores),days=days))
p=root/f'share/era5-period-{period}-references.json';p.write_text(json.dumps(refs));subprocess.run(['node',str(root/'verify_era5_core.cjs'),period,str(p)],check=True)
