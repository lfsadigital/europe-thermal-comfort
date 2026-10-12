"""Build all default maps + exact dynamic statistics in staging, from ERA5 only."""
import json,gzip,struct,datetime,sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT/'.cache/era5';OUT=ROOT/'era5-staging/assets';OUT.mkdir(parents=True,exist_ok=True)
m=json.loads((ROOT/'site/dist/assets/metadata.json').read_text());nodegrid=np.fromfile(ROOT/'site/dist/assets/node-grid.bin',dtype='<i4');t=np.load(SOURCE/'temperature.npy',mmap_mode='r');r=np.load(SOURCE/'rain.npy',mmap_mode='r');n=m['nodes'];dates=np.arange(np.datetime64('2020-01-01'),np.datetime64('2026-01-01'));months=dates.astype('datetime64[M]');offset=np.cumsum([0]+m['year_days']);audits=[];newfiles={};stats={}
partial=sys.argv[1] if len(sys.argv)>1 else None
if not partial:
 assert json.loads((SOURCE/'import.json').read_text())['completed_tasks']==json.loads((SOURCE/'import.json').read_text())['required_tasks']
else:
 assert partial in list(map(str,range(2020,2026)))

def bins(rr):
 b=np.ceil(rr.astype(float)*10).astype('i8');prev=np.maximum(b-1,0);b-=((b>0)&(rr<=(prev/10).astype('f4')))
 assert ((b>=0)&(b<65536)).all();assert (rr<=(b/10).astype('f4')).all()
 return b.astype('<u2')
for period in ([partial] if partial else ['mean']+list(map(str,range(2020,2026)))):
 completed=OUT/f'period-{period}-complete.json'
 if completed.exists():
  checkpoint=json.loads(completed.read_text());stats[period]=checkpoint['stats'];newfiles[period]=checkpoint['files'];audits.append(checkpoint['audit']);continue
 first,last,years=(0,2192,6) if period=='mean' else (int(offset[int(period)-2020]),int(offset[int(period)-2019]),1)
 days=last-first;sv=np.full(n,np.nan);dv=np.full(n,np.nan);cv=np.zeros(n,dtype='<u2');files=[];maxerr=0
 for start in range(0,n,2048):
  end=min(n,start+2048);nc=end-start;tv=np.asarray(t[first:last,start:end],dtype=float);rv=np.asarray(r[first:last,start:end]);good=np.isfinite(tv)&np.isfinite(rv)&(rv>=0);eligible=np.ones(nc,bool)
  for month in np.unique(months[first:last]):
   ii=months[first:last]==month;eligible&=good[ii].sum(axis=0)>=np.ceil(ii.sum()*.9)
  count=good.sum(axis=0);cv[start:end]=count
  rainpen=np.select([rv<=1,rv<=10,rv<=20],[0,.5,1],default=1.5);raw=np.where(good,np.maximum(0,10-.5*np.maximum(18-tv,0)-.5*np.maximum(tv-26,0)-rainpen),0);score=np.divide(raw.sum(axis=0),count,out=np.full(nc,np.nan),where=count>0);comfy=(good&(tv>=18)&(tv<=26)&(rv<=1)).sum(axis=0);day=np.divide(comfy*days/years,count,out=np.full(nc,np.nan),where=count>0);score[~eligible]=np.nan;day[~eligible]=np.nan;sv[start:end]=score;dv[start:end]=day
  valid=np.where(eligible,count,0).astype('<u2');jo=[0];jt=[];jr=[];jc=[];je=[];js=[]
  for k in range(nc):
   if not eligible[k]:jo.append(jo[-1]);continue
   tt=tv[:,k][good[:,k]];rr=rv[:,k][good[:,k]];tb=np.ceil(tt).astype('i8');rb=bins(rr);assert ((tb>=-100)&(tb<=100)).all()
   key=(tb+100)*65536+rb;uq,inv,cnt=np.unique(key,return_inverse=True,return_counts=True);bt=uq//65536-100;br=uq%65536;sums=np.bincount(inv,weights=tt);exact=np.bincount(inv,weights=(tt==np.floor(tt)).astype(int)).astype('<u2')
   pen=np.select([br<=10,br<=100,br<=200],[0,.5,1],default=1.5);lo=18-20+2*pen;hi=26+20-2*pen;loss=np.where(bt<=18,18*cnt-sums,np.where(bt>26,sums-26*cnt,0));hs=np.where((bt>lo)&(bt<=hi),(10-pen)*cnt-.5*loss,0).sum()/len(tt)
   hd=(cnt[(bt>18)&(bt<=26)&(br<=10)].sum()+exact[(bt==18)&(br<=10)].sum())/len(tt)*days/years
   assert abs(hs-score[k])<1e-10 and abs(hd-day[k])<1e-10;maxerr=max(maxerr,abs(hs-score[k]))
   jt.extend(bt);jr.extend(br);jc.extend(cnt);je.extend(exact);js.extend(sums);jo.append(len(jt))
  nj=len(jt);h=struct.pack('<11I',0x57434C4D,4,start,nc,0,nj,days,years,n,10,0)
  parts=[h,valid.tobytes(),bytes(4*(nc+1)),np.asarray(jo,dtype='<u4').tobytes()]
  for a,dt in [(jt,'<i2'),(jr,'<u2'),(jc,'<u2'),(je,'<u2')]:parts.append(np.asarray(a,dtype=dt).tobytes())
  sums=np.asarray(js,dtype='<f8');parts.append(sums.view('u1').reshape(-1,8).T.copy().tobytes());name=f'climate-{period}-{start//2048}.gz';p=OUT/name;p.write_bytes(gzip.compress(b''.join(parts),compresslevel=9,mtime=0));assert p.stat().st_size<25*1024*1024;files.append(name)
  print(period,end,'/',n,'eligible',int(eligible.sum()),flush=True)
 for label,values,dtype in [('score',sv,'<f4'),('days',dv,'<f4'),('coverage',cv,'<u2')]:
  grid=np.full(nodegrid.size,0 if label=='coverage' else np.nan,dtype=dtype);active=nodegrid>=0;grid[active]=values[nodegrid[active]];grid.tofile(OUT/f'{label}-{period}.bin')
 stats[period]={label:dict(valid_points=int(np.isfinite(v).sum()),min=float(np.nanmin(v)),max=float(np.nanmax(v))) for label,v in [('score',sv),('days',dv)]};newfiles[period]=files;audits.append(dict(period=period,eligible_cells=int(np.isfinite(sv).sum()),max_histogram_raw_score_error=maxerr))
 (OUT/f'period-{period}-complete.json').write_text(json.dumps(dict(stats=stats[period],files=files,audit=audits[-1])))
if partial:
 print('PERIOD COMPLETE',partial,flush=True);sys.exit(0)
m.update(source_model='ERA5',daily_variables=['temperature_2m_max','precipitation_sum'],daily_aggregation={'temperature_2m_max':'maximum of 24 hourly 2m temperatures','precipitation_sum':'sum of 24 hourly total precipitation values'},source='Copernicus ERA5 / ECMWF · Open-Meteo',native_resolution_degrees=.25,sample_spacing_degrees=.5,period_stats=stats,period_files=newfiles,coverage=stats['mean']['score']['valid_points']/n,climate_format_version=4,day_timezone='UTC',elevation_downscaling=False,source_precision_temperature_degrees=.05)
(OUT/'metadata.json').write_text(json.dumps(m,separators=(',',':')));(OUT/'score-audit.json').write_text(json.dumps({'source':m['source'],'comparisons':audits,'method':'All eligible cells in all 7 periods verified against ERA5 original daily arrays. Daily score floor applied before mean.'},indent=2));(OUT/'audit.json').write_text(json.dumps({'source':m['source'],'period':m['period'],'days':2192,'checks':['UTC hourly aggregation','Same ERA5 source for both variables, all tabs','All default scores/day counts match daily arrays','Monthly paired-day eligibility; no imputation'],'comparisons':audits},indent=2));print('BUILD COMPLETE',flush=True)
