from datetime import date
import numpy as np
from pathlib import Path
import json
m=json.loads(Path('site/dist/assets/metadata.json').read_text());d=np.load('.cache/direct.npz');t=np.load('.cache/temperature.npy',mmap_mode='r');r=np.load('.cache/rain.npy',mmap_mode='r');bounds=[];offset=0
for j,year in enumerate(m['available_years']):
 for month in range(1,13):
  next_year,next_month=(year+1,1) if month==12 else (year,month+1);n=(date(next_year,next_month,1)-date(year,month,1)).days;bounds.append((j,offset,offset+n,n));offset+=n
for first in range(0,m['nodes'],2048):
 last=min(first+2048,m['nodes']);a=t[:,first:last];b=r[:,first:last];good=np.isfinite(a)&np.isfinite(b)&(b>=0);eligible=np.ones((6,last-first),bool);counts=np.zeros((6,last-first),int)
 for j,begin,end,n in bounds:
  v=good[begin:end].sum(axis=0);counts[j]+=v;eligible[j]&=v>=int(np.ceil(n*.9))
 np.testing.assert_array_equal(eligible,d['annual_valid'][:,first:last]);np.testing.assert_array_equal(counts,d['annual_count'][:,first:last]);np.testing.assert_array_equal(eligible.all(axis=0),d['mean_valid'][first:last])
assert offset==2192;print('PASS independent coverage checks for all 72 months, all 85,699 land points; no absent records counted as dry')
