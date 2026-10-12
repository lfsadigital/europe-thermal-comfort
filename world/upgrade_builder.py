from pathlib import Path
p=Path('build_world.py');s=p.read_text().replace('samples every second native grid point (1° spacing)','uses every native grid point (0.5° spacing)').replace('lat=native_lat[::2]','lat=native_lat').replace('native_lon[::2]','native_lon').replace('.isel(lat=slice(None,None,2),lon=slice(None,None,2))','')
s=s.replace('position=0;annual=[];annual_days=[]','position=0;annual=[];annual_days=[];annual_valid=[];annual_count=[];annual_sum=[];annual_comfort=[]')
a=s.index('  good=np.isfinite(t)&np.isfinite(r)&(r>=0);complete=');b=s.index(' position+=days',a)
s=s[:a]+'''  good=np.isfinite(t)&np.isfinite(r)&(r>=0);count=good.sum(axis=0);eligible=np.ones(n,bool)
  for month in range(1,13):
   selected=td.time.dt.month.values==month;eligible&=good[selected].sum(axis=0)>=np.ceil(selected.sum()*.9)
  pen=np.select([r<=1,r<=10,r<=20],[0,1,2],default=3)
  sums=np.where(good,100-np.abs(t.astype(float)-np.clip(t.astype(float),18,26))-pen,0).sum(axis=0)
  comfort=(good&(t>=18)&(t<=26)&(r<=1)).sum(axis=0)
  rawscore=np.divide(sums,count,out=np.full(n,np.nan),where=count>0);rawdays=np.divide(comfort*days,count,out=np.full(n,np.nan),where=count>0)
  rawscore[~eligible]=np.nan;rawdays[~eligible]=np.nan
  annual.append(rawscore);annual_days.append(rawdays);annual_valid.append(eligible);annual_count.append(count);annual_sum.append(sums);annual_comfort.append(comfort)
  print(year,'paired dates',days,'eligible points',int(eligible.sum()),'complete',int((count==days).sum()),flush=True)
''' +s[b:]
a=s.index('mean_score=');b=s.index('\ndef rain_bins',a)
s=s[:a]+'''annual_valid=np.stack(annual_valid);annual_count=np.stack(annual_count);annual_sum=np.stack(annual_sum);annual_comfort=np.stack(annual_comfort)
mean_valid=annual_valid.all(axis=0);mean_count=annual_count.sum(axis=0)
mean_score=np.divide(annual_sum.sum(axis=0),mean_count,out=np.full(n,np.nan),where=mean_count>0);mean_days=np.divide(annual_comfort.sum(axis=0)*TOTAL/6,mean_count,out=np.full(n,np.nan),where=mean_count>0);mean_score[~mean_valid]=np.nan;mean_days[~mean_valid]=np.nan
np.savez_compressed(CACHE/'direct.npz',annual_score=annual,annual_days=annual_days,score=mean_score,days=mean_days,indices=indices,annual_valid=annual_valid,annual_count=annual_count,mean_valid=mean_valid,mean_count=mean_count)
for key,count in [('mean',mean_count)]+[(str(y),annual_count[i]) for i,y in enumerate(YEARS)]:
 grid_count=np.zeros(mask.size,dtype='<u2');grid_count[indices]=count;grid_count.tofile(OUT/f'coverage-{key}.bin')
''' +s[b:]
s=s.replace('files=[];largest_error=0','files=[];largest_error=0;eligible=mean_valid if key==\'mean\' else annual_valid[YEARS.index(int(key))]')
s=s.replace('v.append(len(t))','v.append(len(t) if eligible[node] else 0)').replace('if len(t)==days:','if eligible[node]:').replace('/days;d=', '/len(t);d=').replace("].sum())/years", "].sum())/len(t)*days/years")
s=s.replace('0x57434C4D,1,start','0x57434C4D,2,start')
s=s.replace('i=np.clip(np.rint((lat[0]-y)).astype(int)','i=np.clip(np.rint((lat[0]-y)/.5).astype(int)').replace('np.rint(x-lon[0])','np.rint((x-lon[0])/.5)').replace('dist[i,j]>1.5','dist[i,j]>.75/.5')
s=s.replace("'sample_spacing_degrees':1","'sample_spacing_degrees':0.5").replace("'rain_step_mm':0.1}","'rain_step_mm':0.1,'coverage_rule':'At least 90% paired valid days in every month of the selected period','minimum_monthly_coverage':0.9,'coastline_extension_degrees':0.75}")
s=s.replace('Scores use /2192; comfortable-day totals use /6; incomplete periods remain missing','Scores use available paired days; comfortable-day rates are scaled by calendar days / years. At least 90% coverage is required in every month; no missing records are imputed')
s=s.replace("'complete_points':int(np.isfinite(mean_score).sum()),'land_points':n", "'eligible_points':int(mean_valid.sum()),'complete_points':int((mean_count==TOTAL).sum()),'land_points':n,'minimum_monthly_coverage':0.9")
p.write_text(s)
