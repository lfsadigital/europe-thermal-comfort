from pathlib import Path
import zipfile,gzip,json
from cartopy.io import shapereader
from shapely.geometry import mapping
root=Path(__file__).resolve().parent;dest=root/'.cache/cartopy/shapefiles/natural_earth/cultural/detail10m';dest.mkdir(parents=True,exist_ok=True)
with zipfile.ZipFile('/private/tmp/comfy-countries-10m.zip') as z:z.extractall(dest)
features=[]
def rounded(v):
 if isinstance(v,dict):return {k:rounded(x) for k,x in v.items()}
 if isinstance(v,(list,tuple)):return [rounded(x) for x in v]
 if isinstance(v,float):return round(v,4)
 return v
for rec in shapereader.Reader(dest/'ne_10m_admin_0_countries.shp').records():
 a=rec.attributes;p=rec.geometry.representative_point();features.append({'type':'Feature','properties':{'name':a.get('NAME_EN') or a['NAME'],'label':[round(p.y,4),round(p.x,4)]},'geometry':rounded(mapping(rec.geometry))})
with gzip.open(root/'site/dist/assets/borders.geojson.gz','wt') as f:json.dump({'type':'FeatureCollection','features':features},f,separators=(',',':'))
print('Detailed Natural Earth countries:',len(features),'gzip bytes:',(root/'site/dist/assets/borders.geojson.gz').stat().st_size)
