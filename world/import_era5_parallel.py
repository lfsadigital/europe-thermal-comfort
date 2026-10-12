"""Parallel bounded-disk import of small 21-day ERA5 archive objects."""
from pathlib import Path
source=Path(__file__).with_name('import_era5_local.py').read_text().split('# Keep chronological order')[0]
source=source.replace("path=OUT/'working-source.om';marker=OUT/'working-source.json'", "path=OUT/f'working-{variable}-{tag}.om';marker=OUT/f'working-{variable}-{tag}.json'")
source=source.replace('max_workers=48','max_workers=24')
source=source.replace("exec(open(__file__.replace('import_era5_local.py','import_era5.py')).read().split('def task(')[0])", "exec(Path(__file__).with_name('import_era5.py').read_text().split('def task(')[0])")
exec(source)
# Completed yearly objects must not be downloaded in parallel (disk bound).
assert all(f'{v}/year_{y}/{row}' in done for y in [2020,2021] for v in arrays for row in rowlist)
def process(pair):
 variable,item=pair;tag,begin,hours,lo,hi=item;todo=[row for row in rowlist if f'{variable}/{tag}/{row}' not in done]
 if not todo:return
 began=time.time();path=download(variable,item)
 with OmFileReader(str(path)) as reader:
  assert tuple(reader.shape[:2])==(721,1440) and reader.shape[2]>=hi
  for row in todo:
   xs=np.flatnonzero(grid[row]>=0);erow=int(round((m['latitude'][row]+90)/.25));ex=xs*2+1;left=int(ex.min());right=int(ex.max())+1
   block=reader[erow:erow+1,left:right,lo:hi][0][ex-left];assert block.shape==(len(xs),hi-lo)
   hourly=block.reshape(len(xs),-1,24);aggregate=np.max(hourly,axis=2) if variable=='temperature_2m' else np.sum(hourly,axis=2,dtype=np.float64).astype('f4')
   if variable=='precipitation':assert ((aggregate>=0)|np.isnan(aggregate)).all()
   offset=int(((begin+datetime.timedelta(hours=lo))-start).total_seconds()/86400);arrays[variable][offset:offset+aggregate.shape[1],grid[row,xs]]=aggregate.T
 arrays[variable].flush()
 with lock:
  done.update(f'{variable}/{tag}/{row}' for row in todo)
  tmp=progress_path.with_suffix('.tmp');tmp.write_text(json.dumps(sorted(done)));tmp.replace(progress_path)
 path.unlink();path.with_suffix('.json').unlink();print('COMPLETED',variable,tag,len(done),'/',total,'in',round(time.time()-began),'s',flush=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:list(pool.map(process,[(v,item) for item in files[2:] for v in arrays]))
assert len(done)==total
report={'source':'Copernicus ERA5 / ECMWF, Open-Meteo AWS Open Data','period':'2020–2025','days':nd,'nodes':n,'native_resolution_degrees':.25,'sampling_degrees':.5,'timezone':'UTC','elevation_downscaling':False,'daily_temperature':'Maximum of 24 hourly 2m temperatures; original stored 0.05°C precision','daily_precipitation':'Sum of 24 hourly total precipitation values (mm)','completed_tasks':len(done),'required_tasks':total,'files':[x[0] for x in files],'objects':{key:{'bytes':inventory[key][0],'etag':inventory[key][1]} for item in files for variable in arrays for key in [f'data/copernicus_era5/{variable}/{item[0]}.om']}}
(OUT/'import.json').write_text(json.dumps(report,indent=2)+'\n');print('IMPORT COMPLETE',flush=True)
