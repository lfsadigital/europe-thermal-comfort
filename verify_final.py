"""Audit formula, full-period weighting, provenance and final artifacts."""
import json
from pathlib import Path
import numpy as np
import xarray as xr
from scoring import daily_score

np.testing.assert_equal(daily_score([22,18,27,15,30,20,25,-100,150]),[100,98,98,95,95,100,100,-20,-25])
p=np.load('output-final/comfort_grid.npz')
assert int(p['days'])==1827
assert p['score'].shape==(370,700)
assert np.isfinite(p['score'][p['source_grid']>0]).all()
assert (p['count'][p['source_grid']>0]==1827).all()
weights=np.array([366,365,365,365,366])[:,None,None]
complete=np.isfinite(p['annual']).all(axis=0)
expected=(p['annual']*weights).sum(axis=0)/1827
np.testing.assert_allclose(p['eobs_score'][complete],expected[complete],rtol=0,atol=1e-10)
# Independently recompute a NOAA source cell from its raw daily records.
temperatures=[]
for year in range(2020,2025):
 with xr.open_dataset(f'.cache/noaa/tmax.{year}.nc',engine='h5netcdf') as ds:
  temperatures.extend(ds.tmax.sel(lat=60.25,lon=40.25).values.tolist())
assert len(temperatures)==1827
scalar_mean=sum(100-(20-t if t<20 else t-25 if t>25 else 0) for t in temperatures)/1827
q=np.load('.cache/noaa/scores-2020-01-01-2024-12-31.npz')
i=np.flatnonzero(q['latitude']==60.25)[0];j=np.flatnonzero(q['longitude']==40.25)[0]
np.testing.assert_allclose(q['score'][i,j],scalar_mean,rtol=0,atol=1e-10)
metadata=json.loads(Path('output-final/metadata.json').read_text())
assert metadata['eobs_land_cells']+metadata['noaa_land_cells']==metadata['complete_land_cells']
assert metadata['complete_land_cells']+metadata['missing_land_cells']==metadata['land_grid_cells']
from PIL import Image
with Image.open('output-final/europe_comfort.png') as image:
 assert image.size==(4140,3600)
 assert abs(image.info['dpi'][0]-300)<.1
with open('output-final/europe_comfort.pdf','rb') as f:
 assert f.read(5)==b'%PDF-'
print(json.dumps({'formula':'PASS','complete_days':'PASS','leap_day_weighting':'PASS','raw_noaa_recalculation':'PASS','provenance':'PASS','png':'4140×3600 / 300 dpi','pdf':'PASS','coverage':metadata['coverage_fraction'],'noaa_check_score':float(scalar_mean)},indent=2))
