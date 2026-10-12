import fsspec,json,numpy as np
from omfiles import OmFileReader
from fsspec.implementations.http import HTTPFileSystem
orig=HTTPFileSystem._cat_file
async def compat(self,url=None,path=None,**kwargs):return await orig(self,url or path,**kwargs)
HTTPFileSystem._cat_file=compat
out={}
for var in ['temperature_2m','precipitation']:
 b=fsspec.open(f'https://openmeteo.s3.amazonaws.com/data/copernicus_era5/{var}/year_2020.om','rb',block_size=65536)
 with OmFileReader(b) as r:
  print(var,r.shape,r.chunks,flush=True);a=r[463:464,399:400,:].ravel();daily=a.reshape(366,24).max(axis=1) if var=='temperature_2m' else a.reshape(366,24).sum(axis=1);out[var]=daily.tolist()
np.savez('world-comfort/share/era5-probe.npz',**out)
e=json.load(open('world-comfort/share/era5-comparison/era5-raw-1.json'))[2]['daily']
for var,key in [('temperature_2m','temperature_2m_max'),('precipitation','precipitation_sum')]:
 d=np.array(out[var]);api=np.array(e[key][:366]);print(var,'maximum API delta',np.abs(d-api).max(),'mean',np.abs(d-api).mean(),'first',d[:5],api[:5],flush=True)
