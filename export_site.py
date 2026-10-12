"""Export both climate measures, exact map projection and static map layers."""
import os,sys
from pathlib import Path
os.environ.setdefault('MPLCONFIGDIR',str(Path('.cache/matplotlib').resolve()))
import json
import numpy as np
import xarray as xr
import shapely
import cartopy
from cartopy.io import shapereader
import cartopy.crs as ccrs
from cartopy.mpl.path import shapely_to_path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap,Normalize
from matplotlib.patches import PathPatch
import matplotlib.patheffects as pe
from shapely.geometry import box
from scipy.interpolate import RegularGridInterpolator
from scipy.ndimage import distance_transform_edt
from render_europe import PALETTE,LABELS
from scoring import daily_score

OUT=Path('site/dist/assets')
OUT.mkdir(parents=True,exist_ok=True)
p=np.load('output-final/comfort_grid.npz')
latitude,longitude=p['latitude'],p['longitude']
lon,lat=np.meshgrid(longitude,latitude)
points=np.stack([lat,lon],axis=-1)
if Path('output-final/rain_site_grid.npz').exists() and '--temperature-only' not in sys.argv:
 rain=np.load('output-final/rain_site_grid.npz')
 annual_score=rain['annual_score'];annual_days=rain['annual_days'];mean_days=rain['days_per_year'];mean_score=rain['score'];valid=np.isfinite(mean_score)
 rain_enabled=True
else:
 annual_score=p['annual'].copy()
 annual_days=np.load('.cache/eobs-scores/ideal-days-2020-2024.npz')['annual_days'].astype(float)
 mask=p['source_grid']==2
 for i,year in enumerate(range(2020,2025)):
  with xr.open_dataset(f'.cache/noaa/tmax.{year}.nc',engine='h5netcdf') as ds:
   d=ds.sel(lat=slice(72,34),lon=slice(24,46))
   t=d.tmax.values.astype(float);good=np.isfinite(t).all(axis=0)
   score=np.mean(daily_score(t),axis=0);days=((t>=20)&(t<=25)).sum(axis=0).astype(float)
   score[~good]=np.nan;days[~good]=np.nan
   coords=(d.lat.values[::-1],d.lon.values)
   ns=RegularGridInterpolator(coords,score[::-1],bounds_error=False,fill_value=np.nan)(points)
   nd=RegularGridInterpolator(coords,days[::-1],bounds_error=False,fill_value=np.nan)(points)
   annual_score[i][mask]=ns[mask];annual_days[i][mask]=nd[mask]
  print(f'{year}: duas medidas exportadas',flush=True)
 valid=np.isfinite(p['score'])
 annual_days[:,~valid]=np.nan;annual_score[:,~valid]=np.nan
 mean_days=annual_days.sum(axis=0)/5
 np.testing.assert_allclose(np.nansum(annual_score*np.array([366,365,365,365,366])[:,None,None],axis=0)[valid]/1827,p['score'][valid],atol=1e-10,rtol=0)
 np.savez_compressed('output-final/site_grid.npz',latitude=latitude,longitude=longitude,score=p['score'],days_per_year=mean_days,annual_score=annual_score,annual_days=annual_days,source=p['source_grid'])
 mean_score=p['score'];rain_enabled=False
cartopy.config['data_dir']=Path('.cache/cartopy')
records=list(shapereader.Reader(shapereader.natural_earth('10m','cultural','admin_0_countries')).records())
selected=[r for r in records if r.attributes['CONTINENT']=='Europe' or r.attributes['ADMIN'] in ('Turkey','Cyprus','Northern Cyprus')]
bounds=box(-25,34.5,45,71.5)
geoms=[r.geometry.intersection(bounds) for r in selected if r.geometry.intersects(bounds)]
land=shapely.union_all(geoms)
on_land=shapely.contains_xy(land,lon,lat)
source=np.where(on_land,p['source_grid'],0).astype(np.uint8)
source.tofile(OUT/'source.bin')
# Country lookup for the queried cell, with real geographic boundaries.
country=np.zeros(lon.shape,dtype=np.uint8)
names=['']
for r in selected:
 names.append(r.attributes.get('NAME_EN') or r.attributes['ADMIN'])
 country[shapely.contains_xy(r.geometry,lon,lat)]=len(names)-1
country.tofile(OUT/'country.bin')
projection=ccrs.LambertConformal(central_longitude=15,central_latitude=53,standard_parallels=(35,65))
projected=projection.project_geometry(land.simplify(.005,preserve_topology=True),ccrs.PlateCarree())
width,height=2400,2100
fig=plt.figure(figsize=(12,10.5),dpi=200,facecolor='white')
ax=fig.add_axes([0,0,1,1],projection=projection)
ax.set_extent([-24.5,44.5,34.6,71.4],ccrs.PlateCarree());ax.set_aspect('auto')
ax.set_facecolor('white');ax.spines['geo'].set_visible(False)
ax.add_geometries(geoms,ccrs.PlateCarree(),facecolor='#efefef',edgecolor='none',zorder=0)
clip=PathPatch(shapely_to_path(projected),transform=ax.transData)
ax.add_geometries(geoms,ccrs.PlateCarree(),facecolor='none',edgecolor='#394853',linewidth=.32,alpha=.75,zorder=3)
for label,x,y in LABELS:
 ax.text(x,y,label,transform=ccrs.PlateCarree(),ha='center',va='center',fontsize=7.2,color='#183246',zorder=5,path_effects=[pe.withStroke(linewidth=1.5,foreground='white',alpha=.75)])
cmap=LinearSegmentedColormap.from_list('tweet_comfort',PALETTE,N=512)
cmap.set_bad('#efefef');cmap.set_under(PALETTE[0]);cmap.set_over(PALETTE[-1])
periods=[('mean',mean_score,mean_days)]+[(str(year),annual_score[i],annual_days[i]) for i,year in enumerate(range(2020,2025))]
period_stats={}
for key,score,days in periods:
 period_stats[key]={}
 for mode,values,factor,vmin,vmax in [('score',score,100,76,98),('days',days,10,0,150)]:
  encoded=np.full(values.shape,65535,dtype='<u2');finite=np.isfinite(values)&on_land
  encoded[finite]=np.rint(values[finite]*factor).astype(np.uint16)
  encoded.tofile(OUT/f'{mode}-{key}.bin')
  distance,nearest=distance_transform_edt(~np.isfinite(values),return_indices=True)
  display=values[tuple(nearest)];display[distance>2]=np.nan
  mesh=ax.pcolormesh(lon,lat,np.ma.masked_invalid(display),transform=ccrs.PlateCarree(),cmap=cmap,norm=Normalize(vmin,vmax),shading='gouraud',rasterized=True,zorder=1)
  mesh.set_clip_path(clip)
  fig.savefig(OUT/f'{mode}-{key}.webp',format='webp',dpi=200,facecolor='white',pil_kwargs={'quality':88,'method':6})
  mesh.remove()
  period_stats[key][mode]={'min':float(values[finite].min()),'max':float(values[finite].max()),'valid_land_cells':int(finite.sum())}
  print(f'Mapa {mode} {key}: pronto',flush=True)
extent=[float(v) for v in ax.get_extent()]
plt.close(fig)
meta={'period':'2020–2024','total_days':1827,'years':5,'palette':PALETTE,'shape':list(lon.shape),'latitude':latitude.tolist(),'longitude':longitude.tolist(),'extent':extent,'projection':projection.proj4_init,'image_size':[width,height],'countries':names,'score_range':[76,98],'days_range':[0,150],'period_stats':period_stats,'coverage':float((on_land&valid).sum()/on_land.sum()),'source_names':{'1':'E-OBS · 0.1° grid','2':'NOAA CPC · original 0.5° grid'},'methodology':{'score':'100 − max(20 − Tmax, 0) − max(Tmax − 25, 0)','days':'Count of days with 20 ≤ Tmax ≤ 25 °C, divided by 5 for 2020–2024','coastal_display':'Visual extension up to 0.2°; queries use complete cells','noaa':'Interpolation of scores and counts calculated on the original 0.5° grid'}}
if rain_enabled:
 meta['rain_threshold_mm']=1
 meta['land_cells']=int(on_land.sum())
 meta['methodology']['score']='100 − max(lower − Tmax, 0) − max(Tmax − upper, 0) − (precipitation > 1 mm)'
 meta['methodology']['days']='Count days when lower ≤ Tmax ≤ upper AND precipitation ≤ 1 mm; divide by 5 for 2020–2024'
 meta['methodology']['rain']='E-OBS RR daily totals in mm; NOAA CPC global daily precipitation in eastern temperature gaps; records aligned by date. Only complete paired periods are shown.'
 meta['coverage']=float(np.isfinite(mean_score[on_land]).sum()/on_land.sum())
(OUT/'metadata.json').write_text(json.dumps(meta,ensure_ascii=False,separators=(',',':')))
# Projection sample points for an independent JavaScript inverse check.
checks=[]
for x,y in [(-9.1,38.7),(2.35,48.85),(12.5,41.9),(24.94,60.17),(-21.9,64.1)]:
 px,py=projection.transform_point(x,y,ccrs.PlateCarree())
 checks.append({'lon':x,'lat':y,'x':float(px),'y':float(py)})
(OUT/'projection-checks.json').write_text(json.dumps(checks))
print('Camadas e dados prontos.',flush=True)
