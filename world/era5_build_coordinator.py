"""Overlap annual statistic builds with completed immutable import batches."""
import json,datetime,time,subprocess,sys
from pathlib import Path
root=Path(__file__).resolve().parent;epoch=datetime.datetime(1970,1,1);pending=list(range(2020,2026));rows=332;proc=None;active=None
while pending or proc:
 if proc:
  rc=proc.poll()
  if rc is not None:
   if rc:raise RuntimeError(f'Build failed for {active}, exit {rc}')
   subprocess.run([sys.executable,str(root/'verify_era5_period.py'),str(active)],check=True)
   print('Annual statistics checked',active,flush=True);proc=None
 if proc is None and pending:
  y=pending[0];tags=[f'year_{y}'] if y<=2021 else [f'chunk_{i}' for i in range(int((datetime.datetime(y,1,1)-epoch).total_seconds()//3600)//504, int(((datetime.datetime(y+1,1,1)-epoch).total_seconds()/3600+503)//504))]
  p=root/'.cache/era5/progress.json';done=json.loads(p.read_text()) if p.exists() else [];counts={}
  for d in done:
   var,tag,row=d.split('/');counts[(var,tag)]=counts.get((var,tag),0)+1
  if all(counts.get((v,t),0)==rows for v in ['temperature_2m','precipitation'] for t in tags):
   active=y;pending.pop(0);print('Building complete ERA5 year',y,flush=True);proc=subprocess.Popen([sys.executable,str(root/'build_era5_statistics.py'),str(y)])
 time.sleep(5)
while not (root/'.cache/era5/import.json').exists():time.sleep(3)
subprocess.run([sys.executable,str(root/'build_era5_statistics.py')],check=True)
for period in ['mean']+list(map(str,range(2020,2026))):subprocess.run([sys.executable,str(root/'verify_era5_period.py'),period],check=True)
print('ALL STAGING STATISTICS VERIFIED',flush=True)
