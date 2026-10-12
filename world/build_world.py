"""Exact global daily temperature/rain statistics and real Natural Earth cartography.

Source: NOAA CPC daily Tmax and precipitation, 2020–2025, native 0.5°.
This review version uses every native grid point (0.5° spacing).
Temperature controls use integers; rainfall controls use 0.1 mm increments.
Rain comparisons use the original float32 source precision, without rounding
observations to 0.1 mm. Original fractional temperature sums are float64.
"""
from pathlib import Path
from datetime import date
import json,gzip,struct
import numpy as np,xarray as xr,shapely,cartopy
from cartopy.io import shapereader
from scipy.ndimage import distance_transform_edt
from PIL import Image
OUT=Path('site/dist/assets');OUT.mkdir(parents=True,exist_ok=True)
CACHE=Path('.cache');YEARS=list(range(2020,2026));ND=[(date(y+1,1,1)-date(y,1,1)).days for y in YEARS];TOTAL=sum(ND);PALETTE=['#efb1f2','#c784dc','#707ad9','#408fe0','#20bdf0','#47dddc','#65e895','#a8ed57','#f0f431','#ffd429','#ff8c26','#f03f28','#b90934']
cartopy.config['data_dir']=CACHE.joinpath('cartopy').resolve()
records=list(shapereader.Reader(shapereader.natural_earth('50m','cultural','admin_0_countries')).records());geoms=[r.geometry for r in records];land=shapely.union_all(geoms);shapely.prepare(land)
with xr.open_dataset(CACHE/'noaa/tmax.2020.nc',engine='h5netcdf') as d:
 native_lat=d.lat.values;native_lon=d.lon.values;lat=native_lat;lon=np.where(native_lon>=180,native_lon-360,native_lon);order=np.argsort(lon);lon=lon[order]
xx,yy=np.meshgrid(lon,lat);mask=shapely.contains_xy(land,xx,yy);indices=np.flatnonzero(mask.ravel());n=len(indices);shape=list(mask.shape);node_grid=np.full(mask.size,-1,dtype='<i4');node_grid[indices]=np.arange(n);node_grid.tofile(OUT/'node-grid.bin')
country=np.zeros(mask.shape,dtype='<u2');names=['']
for rec in records:
 names.append(rec.attributes.get('NAME_EN') or rec.attributes['ADMIN']);country[shapely.contains_xy(rec.geometry,xx,yy)]=len(names)-1
country.tofile(OUT/'country.bin')
print('Worldwide sampled land points',n,'grid',shape,flush=True)
ta=np.lib.format.open_memmap(CACHE/'temperature.npy',mode='w+',dtype='f4',shape=(TOTAL,n),fortran_order=True);ra=np.lib.format.open_memmap(CACHE/'rain.npy',mode='w+',dtype='f4',shape=(TOTAL,n),fortran_order=True)
position=0;annual=[];annual_days=[];annual_valid=[];annual_count=[];annual_sum=[];annual_comfort=[]
for year,days in zip(YEARS,ND):
 with xr.open_dataset(CACHE/f'noaa/tmax.{year}.nc',engine='h5netcdf') as td,xr.open_dataset(CACHE/f'noaa/precip.{year}.nc',engine='h5netcdf') as pd:
  expected=np.arange(np.datetime64(f'{year}-01-01'),np.datetime64(f'{year+1}-01-01'));np.testing.assert_array_equal(td.time.values.astype('datetime64[D]'),expected);np.testing.assert_array_equal(pd.time.values.astype('datetime64[D]'),expected)
  for ds in [td,pd]:np.testing.assert_array_equal(ds.lat.values,native_lat);np.testing.assert_array_equal(ds.lon.values,native_lon)
  assert td.tmax.attrs['units']=='degC' and pd.precip.attrs['units']=='mm'
  t=td.tmax.values[:,:,order].reshape(days,-1)[:,indices];r=pd.precip.values[:,:,order].reshape(days,-1)[:,indices]
  ta[position:position+days]=t;ra[position:position+days]=r
  good=np.isfinite(t)&np.isfinite(r)&(r>=0);count=good.sum(axis=0);eligible=np.ones(n,bool)
  for month in range(1,13):
   selected=td.time.dt.month.values==month;eligible&=good[selected].sum(axis=0)>=np.ceil(selected.sum()*.9)
  pen=np.select([r<=1,r<=10,r<=20],[0,1,2],default=3)
  sums=np.where(good,100-np.abs(t.astype(float)-np.clip(t.astype(float),18,26))-pen,0).sum(axis=0)
  comfort=(good&(t>=18)&(t<=26)&(r<=1)).sum(axis=0)
  rawscore=np.divide(sums,count,out=np.full(n,np.nan),where=count>0);rawdays=np.divide(comfort*days,count,out=np.full(n,np.nan),where=count>0)
  rawscore[~eligible]=np.nan;rawdays[~eligible]=np.nan
  annual.append(rawscore);annual_days.append(rawdays);annual_valid.append(eligible);annual_count.append(count);annual_sum.append(sums);annual_comfort.append(comfort)
  print(year,'paired dates',days,'eligible points',int(eligible.sum()),'complete',int((count==days).sum()),flush=True)
 position+=days
ta.flush();ra.flush();annual=np.stack(annual);annual_days=np.stack(annual_days)
annual_valid=np.stack(annual_valid);annual_count=np.stack(annual_count);annual_sum=np.stack(annual_sum);annual_comfort=np.stack(annual_comfort)
mean_valid=annual_valid.all(axis=0);mean_count=annual_count.sum(axis=0)
mean_score=np.divide(annual_sum.sum(axis=0),mean_count,out=np.full(n,np.nan),where=mean_count>0);mean_days=np.divide(annual_comfort.sum(axis=0)*TOTAL/6,mean_count,out=np.full(n,np.nan),where=mean_count>0);mean_score[~mean_valid]=np.nan;mean_days[~mean_valid]=np.nan
np.savez_compressed(CACHE/'direct.npz',annual_score=annual,annual_days=annual_days,score=mean_score,days=mean_days,indices=indices,annual_valid=annual_valid,annual_count=annual_count,mean_valid=mean_valid,mean_count=mean_count)
for key,count in [('mean',mean_count)]+[(str(y),annual_count[i]) for i,y in enumerate(YEARS)]:
 grid_count=np.zeros(mask.size,dtype='<u2');grid_count[indices]=count;grid_count.tofile(OUT/f'coverage-{key}.bin')

def rain_bins(values):
 # Find the least tenth-mm limit (at source float32 precision) that includes R.
 b=np.ceil(values.astype(float)*10).astype(np.int32)
 prev=np.maximum(b-1,0)
 b-=((b>0)&(values<=(prev/10).astype('f4')))
 assert (b>=0).all() and (b<65536).all()
 assert (values<=(b/10).astype('f4')).all()
 assert (values[b>0]>((b[b>0]-1)/10).astype('f4')).all()
 return b.astype('u2')

def serialize(key,first,last,days,years):
 files=[];largest_error=0;eligible=mean_valid if key=='mean' else annual_valid[YEARS.index(int(key))]
 for start in range(0,n,2048):
  end=min(start+2048,n);v=[];toff=[0];tb=[];tc=[];ts=[];joff=[0];jt=[];jr=[];jc=[];je=[]
  for node in range(start,end):
   t=np.asarray(ta[first:last,node]);r=np.asarray(ra[first:last,node]);good=np.isfinite(t)&np.isfinite(r)&(r>=0);t=t[good];r=r[good];v.append(len(t) if eligible[node] else 0);b=np.ceil(t).astype('i2');assert ((b>=-100)&(b<=100)).all();rb=rain_bins(r)
   bt,inv,ct=np.unique(b,return_inverse=True,return_counts=True);st=np.bincount(inv,weights=t.astype(float));tb.extend(bt);tc.extend(ct);ts.extend(st);toff.append(len(tb))
   keys=(b.astype(np.int64)+100)*65536+rb;unique,inv,c=np.unique(keys,return_inverse=True,return_counts=True);exact=np.bincount(inv,weights=(t==np.floor(t)).astype(int)).astype('u2');jtemp=(unique//65536-100).astype('i2');jrain=(unique%65536).astype('u2');jt.extend(jtemp);jr.extend(jrain);jc.extend(c);je.extend(exact);joff.append(len(jt))
   assert sum(ct)==len(t) and sum(c)==len(t)
   if eligible[node]:
    loss=np.where(bt<=18,18*ct-st,0).sum()+np.where(bt>26,st-26*ct,0).sum();pen=np.where(jrain<=10,0,np.where(jrain<=100,1,np.where(jrain<=200,2,3)));s=100-(loss+(c*pen).sum())/len(t);d=(c[(jtemp>18)&(jtemp<=26)&(jrain<=10)].sum()+exact[(jtemp==18)&(jrain<=10)].sum())/len(t)*days/years
    reference_s=mean_score[node] if key=='mean' else annual[YEARS.index(int(key)),node];reference_d=mean_days[node] if key=='mean' else annual_days[YEARS.index(int(key)),node];assert abs(s-reference_s)<1e-10 and abs(d-reference_d)<1e-10;largest_error=max(largest_error,abs(s-reference_s))
  payload=struct.pack('<11I',0x57434C4D,2,start,end-start,len(tb),len(jt),days,years,n,10,0)
  for a,dtype in [(v,'<u2'),(toff,'<u4'),(tb,'<i2'),(tc,'<u2'),(ts,'<f8'),(joff,'<u4'),(jt,'<i2'),(jr,'<u2'),(jc,'<u2'),(je,'<u2')]:payload+=np.asarray(a,dtype=dtype).tobytes()
  name=f'climate-{key}-{start//2048}.gz'
  with gzip.open(OUT/name,'wb',compresslevel=6) as f:f.write(payload)
  assert (OUT/name).stat().st_size<24*1024*1024
  files.append(name)
  print(key,'statistics',end,'/',n,flush=True)
 return files,largest_error

period_files={};errors={};position=0
for y,days in zip(YEARS,ND):period_files[str(y)],errors[str(y)]=serialize(str(y),position,position+days,days,1);position+=days
period_files['mean'],errors['mean']=serialize('mean',0,TOTAL,TOTAL,6)
# World raster follows the real land polygons; source colours remain sampled values.
w,h=2400,1200;px=-180+(np.arange(w)+.5)*360/w;py=90-(np.arange(h)+.5)*180/h;x,y=np.meshgrid(px,py);ocean=~shapely.contains_xy(land,x,y)
# Nearest sampled land cell up to 1.5 degrees for coastline display only.
dist,near=distance_transform_edt(~mask,return_indices=True)
i=np.clip(np.rint((lat[0]-y)/.5).astype(int),0,len(lat)-1);j=np.mod(np.rint((x-lon[0])/.5).astype(int),len(lon));lookup=(near[0,i,j]*len(lon)+near[1,i,j]).astype('<i4');lookup[dist[i,j]>.75/.5]=-1;lookup[ocean]=-2;lookup.tofile(OUT/'map-lookup.bin')
with gzip.open(OUT/'map-lookup.gz','wb',compresslevel=6) as f:f.write(lookup.tobytes())
(OUT/'map-lookup.bin').unlink()
colours=np.array([[int(c[k:k+2],16) for k in (1,3,5)] for c in PALETTE]);period_stats={}
for key,ss,dd in [('mean',mean_score,mean_days)]+[(str(y),annual[i],annual_days[i]) for i,y in enumerate(YEARS)]:
 period_stats[key]={}
 for metric,values,factor,low,high in [('score',ss,100,76,98),('days',dd,10,0,150)]:
  grid=np.full(mask.size,np.nan);grid[indices]=values;grid.astype('<f4').tofile(OUT/f'{metric}-{key}.bin')
  # Identical colour interpolation and missing-value semantics in the browser worker.
  rgba=np.full((h,w,4),255,dtype='u1');landpixels=lookup!=-2;rgba[landpixels,:3]=[239,239,239];active=(lookup>=0)&np.isfinite(grid[np.maximum(lookup,0)]);v=grid[lookup[active]];q=np.clip((v-low)/(high-low),0,1)*(len(PALETTE)-1);a=np.minimum(len(PALETTE)-2,np.floor(q).astype(int));fraction=q-a;rgba[active,:3]=np.floor(colours[a]+(colours[a+1]-colours[a])*fraction[:,None]+.5).astype('u1');Image.fromarray(rgba).convert('RGB').save(OUT/f'{metric}-{key}.webp',quality=90,method=6)
  period_stats[key][metric]={'valid_points':int(np.isfinite(values).sum()),'min':float(np.nanmin(values)),'max':float(np.nanmax(values))}
meta={'period':'2020–2025','years':6,'total_days':TOTAL,'year_days':ND,'available_years':YEARS,'shape':shape,'latitude':lat.tolist(),'longitude':lon.tolist(),'countries':names,'nodes':n,'land_points':n,'period_stats':period_stats,'image_size':[w,h],'palette':PALETTE,'default':{'lower':18,'upper':26,'rain0':1,'rain1':10,'rain2':20,'pen1':1,'pen2':2,'pen3':3,'drymax':1},'period_files':period_files,'source':'NOAA CPC / NOAA PSL','native_resolution_degrees':0.5,'sample_spacing_degrees':0.5,'coverage':float(np.isfinite(mean_score).sum()/n),'rain_step_mm':0.1,'coverage_rule':'At least 90% paired valid days in every month of the selected period','minimum_monthly_coverage':0.9,'coastline_extension_degrees':0.75}
(OUT/'metadata.json').write_text(json.dumps(meta,separators=(',',':')))
report={'period':meta['period'],'total_days':TOTAL,'years':6,'year_days':ND,'default':meta['default'],'checks':['All original daily dates, coordinates and units match between temperature and rain','All default annual and six-year histogram scores/counts match independently computed raw daily values','Exact temperature endpoints; 0.1-mm threshold comparisons preserve source float32 precision; bucket inequalities checked on every paired record','Scores use available paired days; comfortable-day rates are scaled by calendar days / years. At least 90% coverage is required in every month; no missing records are imputed'],'max_histogram_raw_score_errors':errors,'eligible_points':int(mean_valid.sum()),'complete_points':int((mean_count==TOTAL).sum()),'land_points':n,'minimum_monthly_coverage':0.9}
(OUT/'audit.json').write_text(json.dumps(report,indent=2));print('GLOBAL DATA BUILD PASS',json.dumps(report),flush=True)
