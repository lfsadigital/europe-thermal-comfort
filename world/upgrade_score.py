"""Upgrade joint statistics for exact daily 0–10 clipping under dynamic rules."""
from pathlib import Path
import gzip,json,struct
import numpy as np
ROOT=Path(__file__).resolve().parent;OUT=ROOT/'site/dist/assets';m=json.loads((OUT/'metadata.json').read_text());t=np.load(ROOT/'.cache/temperature.npy',mmap_mode='r');r=np.load(ROOT/'.cache/rain.npy',mmap_mode='r');nodegrid=np.fromfile(OUT/'node-grid.bin',dtype='<i4');offset=np.cumsum([0]+m['year_days']);report=[]
def parse(b):
 h=np.frombuffer(b,dtype='<u4',count=11);n,nt,nj=map(int,h[[3,4,5]]);o=44;c={}
 for key,dt,num in [('valid','<u2',n),('toff','<u4',n+1),('tb','<i2',nt),('tc','<u2',nt),('ts','<f8',nt),('jo','<u4',n+1),('jt','<i2',nj),('jr','<u2',nj),('jc','<u2',nj),('je','<u2',nj)]:
  c[key]=np.frombuffer(b,dtype=dt,count=num,offset=o);o+=num*np.dtype(dt).itemsize
 return h,c,o
for key,files in m['period_files'].items():
 first,last=(0,2192) if key=='mean' else (offset[int(key)-2020],offset[int(key)-2019]);values=np.full(m['nodes'],np.nan);maxerr=0
 for file in files:
  path=OUT/file;b=gzip.decompress(path.read_bytes());h,c,o=parse(b);start,n,nj=map(int,h[[2,3,5]])
  if h[1]==3:js=np.frombuffer(b,dtype='<f8',count=nj,offset=o)
  else:
   tv=np.asarray(t[first:last,start:start+n]);rv=np.asarray(r[first:last,start:start+n]);good=np.isfinite(tv)&np.isfinite(rv)&(rv>=0);tt=tv[good];rr=rv[good];local=np.broadcast_to(np.arange(n),(last-first,n))[good];tb=np.ceil(tt).astype('i8');rb=np.ceil(rr.astype(float)*10).astype('i8');prev=np.maximum(rb-1,0);rb-=((rb>0)&(rr<=(prev/10).astype('f4')))
   code=(local*256+(tb+100))*65536+rb;jn=np.repeat(np.arange(n),np.diff(c['jo']));expected=(jn*256+(c['jt'].astype('i8')+100))*65536+c['jr'];where=np.searchsorted(expected,code);assert np.array_equal(expected[where],code)
   js=np.bincount(where,weights=tt.astype(float),minlength=nj).astype('<f8');counts=np.bincount(where,minlength=nj);assert np.array_equal(counts,c['jc']);hh=h.copy();hh[1]=3;path.write_bytes(gzip.compress(hh.tobytes()+b[44:o]+js.tobytes(),compresslevel=6))
  jn=np.repeat(np.arange(n),np.diff(c['jo']));pen=np.select([c['jr']<=10,c['jr']<=100,c['jr']<=200],[0,.5,1],default=1.5);bt=c['jt'];ct=c['jc'].astype(float);lower=18-20+2*pen;upper=26+20-2*pen;positive=(bt>lower)&(bt<=upper);loss=np.where(bt<=18,18*ct-js,np.where(bt>26,js-26*ct,0));sums=np.where(positive,(10-pen)*ct-.5*loss,0);aggregate=np.bincount(jn,weights=sums,minlength=n);v=np.divide(aggregate,c['valid'],out=np.full(n,np.nan),where=c['valid']>0);values[start:start+n]=v
  # Independent daily computation for every eligible cell in this chunk.
  tv=np.asarray(t[first:last,start:start+n]).astype(float);rv=np.asarray(r[first:last,start:start+n]);good=np.isfinite(tv)&np.isfinite(rv)&(rv>=0);rain=np.select([rv<=1,rv<=10,rv<=20],[0,.5,1],default=1.5);raw=np.where(good,np.maximum(0,10-.5*np.maximum(18-tv,0)-.5*np.maximum(tv-26,0)-rain),0);ref=np.divide(raw.sum(axis=0),good.sum(axis=0),out=np.full(n,np.nan),where=good.sum(axis=0)>0);eligible=c['valid']>0;err=np.abs(v[eligible]-ref[eligible]);assert (err<1e-10).all();maxerr=max(maxerr,float(err.max(initial=0)));print(key,file,'PASS',flush=True)
 grid=np.full(nodegrid.size,np.nan);active=nodegrid>=0;grid[active]=values[nodegrid[active]];grid.astype('<f4').tofile(OUT/f'score-{key}.bin');m['period_stats'][key]['score'].update(min=float(np.nanmin(values)),max=float(np.nanmax(values)));report.append({'period':key,'eligible_cells':int(np.isfinite(values).sum()),'max_raw_difference':maxerr})
m['default'].update(pen1=.5,pen2=1,pen3=1.5);m['score']={'maximum':10,'minimum':0,'temperature_penalty_per_degree':.5,'daily_floor_before_average':True};m['climate_format_version']=3;(OUT/'metadata.json').write_text(json.dumps(m,separators=(',',':')));(OUT/'score-audit.json').write_text(json.dumps({'comparisons':report,'method':'All eligible cells in every period compared against original paired daily records. Clamp each daily score before averaging. Comfortable-day assets unchanged.'},indent=2));print('ALL SCORE PERIODS VERIFIED',json.dumps(report),flush=True)
