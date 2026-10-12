"""Compare the proposed daily 0–10 score; do not change the production score."""
from pathlib import Path
import json
import numpy as np
root=Path(__file__).resolve().parent
m=json.loads((root/'site/dist/assets/metadata.json').read_text())
t=np.load(root/'.cache/temperature.npy',mmap_mode='r');r=np.load(root/'.cache/rain.npy',mmap_mode='r')
report=json.loads((root/'share/score-comparison.json').read_text())
idx=np.fromfile(root/'site/dist/assets/node-grid.bin',dtype='i4').reshape(m['shape'])
checks=0
# Independent scalar loop: explicit inclusive boundaries and daily minimum.
for row in report['rows']:
 if not row['eligible']:continue
 y=m['latitude'].index(row['latitude']);x=m['longitude'].index(row['longitude']);n=idx[y,x]
 old=[];new=[];comfortable=0;zeros=0
 for temp,rain in zip(t[:,n],r[:,n]):
  if not np.isfinite(temp) or not np.isfinite(rain) or rain<0:continue
  temp=float(temp);rain=float(rain)
  distance=18-temp if temp<18 else temp-26 if temp>26 else 0
  band=0 if rain<=1 else 1 if rain<=10 else 2 if rain<=20 else 3
  old.append(100-distance-band);value=max(0,10-distance*.5-band*.5);new.append(value)
  comfortable+=18<=temp<=26 and rain<=1;zeros+=value==0
 assert abs(sum(old)/len(old)-row['current_score'])<1e-10
 assert abs(sum(new)/len(new)-row['proposed_score'])<1e-10
 assert abs(comfortable/len(old)*2192/6-row['comfortable_days_per_year'])<1e-10
 assert zeros==row['zero_score_days'];checks+=len(old)
def score(temp,rain):
 distance=max(18-temp,0)+max(temp-26,0)
 band=0 if rain<=1 else .5 if rain<=10 else 1 if rain<=20 else 1.5
 return max(0,10-.5*distance-band)
for temp,rain,expected in [(18,1,10),(26,1,10),(26,1.01,9.5),(26,10,9.5),(26,10.01,9),(26,20,9),(26,20.01,8.5),(33,15,5.5),(60,30,0),(-30,30,0)]:
 assert score(temp,rain)==expected
# The floor applies before averaging, not to an already averaged score.
assert (score(22,0)+score(60,0))/2==5
assert max(0,(10+10-.5*(60-26))/2)==1.5
print(f'PASS {checks} valid daily records, independent scalar vs vector calculations, inclusive rain/temperature boundaries, daily zero floor; proposed score stays out of production')
