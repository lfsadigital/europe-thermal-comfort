from pathlib import Path
import zipfile,gzip,json
from cartopy.io import shapereader
from shapely.geometry import mapping
root=Path(__file__).resolve().parent;dest=root/'.cache/natural-earth-us-states';dest.mkdir(parents=True,exist_ok=True)
with zipfile.ZipFile('/private/tmp/comfy-states-10m.zip') as z:z.extractall(dest)
def rounded(v):
 if isinstance(v,dict):return {k:rounded(x) for k,x in v.items()}
 if isinstance(v,(list,tuple)):return [rounded(x) for x in v]
 return round(v,4) if isinstance(v,float) else v
features=[]
for rec in shapereader.Reader(dest/'ne_10m_admin_1_states_provinces.shp').records():
 a=rec.attributes
 if a.get('iso_a2')!='US':continue
 g=rec.geometry;p=g.representative_point();features.append({'type':'Feature','properties':{'name':'District of Columbia' if a['postal']=='DC' else a.get('name_en') or a['name'],'abbr':a['postal'],'label':[round(p.y,4),round(p.x,4)]},'geometry':rounded(mapping(g))})
assert len(features)==51,len(features)
with gzip.open(root/'site/dist/assets/us-states.geojson.gz','wt') as f:json.dump({'type':'FeatureCollection','features':features},f,separators=(',',':'))
print('Real US state polygons:',len(features))
