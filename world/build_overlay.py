from pathlib import Path
import os
os.environ.setdefault('MPLCONFIGDIR',str(Path('.cache/matplotlib').resolve()))
import cartopy
import cartopy.crs as ccrs
from cartopy.io import shapereader
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
cartopy.config['data_dir']=Path('.cache/cartopy').resolve()
records=list(shapereader.Reader(shapereader.natural_earth('50m','cultural','admin_0_countries')).records())
fig=plt.figure(figsize=(12,6),dpi=200,facecolor='none');ax=fig.add_axes([0,0,1,1],projection=ccrs.PlateCarree());ax.set_global();ax.set_aspect('auto');ax.spines['geo'].set_visible(False);ax.set_facecolor('none')
ax.add_geometries([r.geometry for r in records],ccrs.PlateCarree(),facecolor='none',edgecolor='#435b68',linewidth=.28,alpha=.6)
for label,lon,lat in [('Canada',-108,57),('United States',-101,37),('Mexico',-103,23),('Brazil',-52,-12),('Argentina',-64,-36),('Greenland',-42,72),('Russia',102,60),('China',103,35),('India',80,23),('Australia',134,-25),('South Africa',25,-29),('Nigeria',8,9),('Egypt',30,26),('Türkiye',35,39),('Japan',139,36),('Indonesia',118,-3),('Antarctica',10,-78)]:
 ax.text(lon,lat,label,fontsize=7,color='#294453',ha='center',va='center',path_effects=[pe.withStroke(linewidth=1.5,foreground='white',alpha=.8)])
fig.savefig('site/dist/assets/map-overlay.png',transparent=True,dpi=200)
plt.close(fig);print('Real borders overlay ready',flush=True)
