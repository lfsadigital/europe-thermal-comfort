"""Keep the same Natural Earth map and projection for browser recalculation."""
from pathlib import Path
import os,gzip,json
os.environ.setdefault('MPLCONFIGDIR',str(Path('.cache/matplotlib').resolve()))
import numpy as np,cartopy,cartopy.crs as ccrs,shapely
from cartopy.io import shapereader
from shapely.geometry import box
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from scipy.ndimage import distance_transform_edt
from render_europe import LABELS
out=Path('site/dist/assets');m=json.loads((out/'metadata.json').read_text());w,h=m['image_size'];xmin,xmax,ymin,ymax=m['extent'];projection=ccrs.LambertConformal(central_longitude=15,central_latitude=53,standard_parallels=(35,65))
cartopy.config['data_dir']=Path('.cache/cartopy')
records=list(shapereader.Reader(shapereader.natural_earth('10m','cultural','admin_0_countries')).records());selected=[r for r in records if r.attributes['CONTINENT']=='Europe' or r.attributes['ADMIN'] in ('Turkey','Cyprus','Northern Cyprus')];bounds=box(-25,34.5,45,71.5);geoms=[r.geometry.intersection(bounds) for r in selected if r.geometry.intersects(bounds)];land=shapely.union_all(geoms)
# A native projection lookup avoids reprojecting millions of pixels on every change.
lookup=np.full((h,w),-1,dtype='<i4');source=np.fromfile(out/'source.bin',dtype='u1').reshape(m['shape']);distance,near=distance_transform_edt(source==0,return_indices=True)
for start in range(0,h,100):
 end=min(h,start+100);x=np.linspace(xmin,xmax,w,endpoint=False)+(xmax-xmin)/w/2;y=ymax-(np.arange(start,end)+.5)*(ymax-ymin)/h;xx,yy=np.meshgrid(x,y);geo=ccrs.PlateCarree().transform_points(projection,xx,yy);lo,la=geo[...,0],geo[...,1];valid=shapely.contains_xy(land,lo,la);rows=np.rint((la-m['latitude'][0])/.1).astype(int);cols=np.rint((lo-m['longitude'][0])/.1).astype(int);valid&=(rows>=0)&(rows<m['shape'][0])&(cols>=0)&(cols<m['shape'][1]);r=np.clip(rows,0,m['shape'][0]-1);c=np.clip(cols,0,m['shape'][1]-1);lookup[start:end][valid]=-2;good=valid&(distance[r,c]<=2);lookup[start:end][good]=near[0,r[good],c[good]]*m['shape'][1]+near[1,r[good],c[good]]
with gzip.open(out/'map-lookup.gz','wb',compresslevel=6) as f:f.write(lookup.tobytes())
fig=plt.figure(figsize=(12,10.5),dpi=200,facecolor='none');ax=fig.add_axes([0,0,1,1],projection=projection);ax.set_extent([-24.5,44.5,34.6,71.4],ccrs.PlateCarree());ax.set_aspect('auto');ax.patch.set_alpha(0);ax.spines['geo'].set_visible(False);ax.add_geometries(geoms,ccrs.PlateCarree(),facecolor='none',edgecolor='#394853',linewidth=.32,alpha=.75,zorder=3)
for label,x,y in LABELS:ax.text(x,y,label,transform=ccrs.PlateCarree(),ha='center',va='center',fontsize=7.2,color='#183246',zorder=5,path_effects=[pe.withStroke(linewidth=1.5,foreground='white',alpha=.75)])
fig.savefig(out/'map-overlay.png',transparent=True,dpi=200);plt.close(fig)
print('Natural Earth overlay and pixel lookup exported',flush=True)
