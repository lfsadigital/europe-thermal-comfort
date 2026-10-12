"""Losslessly pack joint temperature sums and omit statistics for ineligible cells."""
from pathlib import Path
import gzip,json,struct
import numpy as np

def parse(b):
 h=np.frombuffer(b,dtype='<u4',count=11);n,nt,nj=map(int,h[[3,4,5]]);o=44;c={}
 for key,dt,num in [('valid','<u2',n),('toff','<u4',n+1),('tb','<i2',nt),('tc','<u2',nt),('ts','<f8',nt),('jo','<u4',n+1),('jt','<i2',nj),('jr','<u2',nj),('jc','<u2',nj),('je','<u2',nj)]:
  c[key]=np.frombuffer(b,dtype=dt,count=num,offset=o);o+=num*np.dtype(dt).itemsize
 return h,c,o


root=Path(__file__).resolve().parent;out=root/'site/dist/assets';m=json.loads((out/'metadata.json').read_text());before=after=0
for key,files in m['period_files'].items():
 for name in files:
  p=out/name;before+=p.stat().st_size;b=gzip.decompress(p.read_bytes());h,c,o=parse(b)
  if h[1]==4:after+=p.stat().st_size;continue
  js=np.frombuffer(b,dtype='<f8',offset=o,count=int(h[5]));eligible=c['valid']>0;tn=np.repeat(np.arange(int(h[3])),np.diff(c['toff']));jn=np.repeat(np.arange(int(h[3])),np.diff(c['jo']));tk=eligible[tn];jk=eligible[jn];toff=np.r_[0,np.cumsum(np.where(eligible,np.diff(c['toff']),0))].astype('<u4');jo=np.r_[0,np.cumsum(np.where(eligible,np.diff(c['jo']),0))].astype('<u4');hh=h.copy();hh[1]=4;hh[4]=tk.sum();hh[5]=jk.sum();parts=[hh.tobytes(),c['valid'].tobytes(),toff.tobytes()]+[c[n][tk].tobytes() for n in ['tb','tc','ts']]+[jo.tobytes()]+[c[n][jk].tobytes() for n in ['jt','jr','jc','je']]
  sums=js[jk].astype('<f8');shuffled=sums.view('u1').reshape(-1,8).T.copy().tobytes();decoded=np.frombuffer(shuffled,dtype='u1').reshape(8,-1).T.copy().tobytes();assert decoded==sums.tobytes();parts.append(shuffled);p.write_bytes(gzip.compress(b''.join(parts),compresslevel=6));after+=p.stat().st_size
 print(key,'packed',flush=True)
m['climate_format_version']=4;(out/'metadata.json').write_text(json.dumps(m,separators=(',',':')));print('Lossless bytes before',before,'after',after,flush=True)
