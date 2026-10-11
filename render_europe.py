"""Render measured scores over Natural Earth geographic boundaries."""
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, Normalize
import matplotlib.patheffects as pe
from matplotlib.patches import PathPatch
import cartopy
import cartopy.crs as ccrs
from cartopy.io import shapereader
from cartopy.mpl.path import shapely_to_path
import shapely
from shapely.geometry import box
from scipy.ndimage import distance_transform_edt

PALETTE = ['#efb1f2','#c784dc','#707ad9','#408fe0','#20bdf0','#47dddc','#65e895','#a8ed57','#f0f431','#ffd429','#ff8c26','#f03f28','#b90934']
LABELS = [
('Iceland',-18.6,64.9),('Ireland',-8.2,53.3),('United\nKingdom',-2.5,54.0),
('Portugal',-8.0,39.5),('Spain',-3.7,40.2),('France',2.4,46.5),
('Belgium',4.4,50.5),('Netherlands',5.7,52.3),('Germany',10.0,51.0),
('Switzerland',8.1,46.7),('Austria',14.0,47.7),('Italy',12.4,43.2),
('Norway',8.5,61.1),('Sweden',16.1,62.0),('Finland',26.2,64.1),
('Denmark',9.5,56.0),('Poland',19.0,52.0),('Czechia',15.1,49.8),
('Slovakia',19.5,48.7),('Hungary',19.4,47.1),('Romania',25.0,45.8),
('Bulgaria',25.3,42.7),('Greece',23.1,39.1),('Türkiye',34.3,39.2),
('Ukraine',31.3,49.3),('Belarus',28.0,53.5),('Lithuania',23.7,55.1),
('Latvia',25.0,57.0),('Estonia',25.5,58.7),('Serbia',20.8,44.0),
('Croatia',16.5,45.4),('Bosnia',17.7,44.0),('Albania',20.0,41.0),
('Russia',39.0,58.0),('Cyprus',33.3,35.1)]

def render(data,start,end,output):
    cartopy.config['data_dir']=Path('.cache/cartopy')
    records=list(shapereader.Reader(shapereader.natural_earth('10m','cultural','admin_0_countries')).records())
    countries=[r for r in records if r.attributes['CONTINENT']=='Europe' or r.attributes['ADMIN'] in ('Turkey','Cyprus','Northern Cyprus')]
    bounds=box(-25,34.5,45,71.5)
    geometries=[r.geometry.intersection(bounds) for r in countries if r.geometry.intersects(bounds)]
    land=shapely.union_all(geometries)
    lon,lat=np.meshgrid(data['longitude'],data['latitude'])
    on_land=shapely.contains_xy(land,lon,lat)
    values=data['score'].copy()
    valid=on_land & np.isfinite(values)
    missing=on_land & ~np.isfinite(values)
    coverage=float(valid.sum()/on_land.sum())
    print(f'Cobertura terrestre dos dados: {valid.sum()}/{on_land.sum()} ({coverage:.2%})',flush=True)
    # E-OBS has a coastal mask. Extend only the display by <=0.2 degrees
    # from an existing complete cell; the exported numerical grid stays unchanged.
    distance,nearest=distance_transform_edt(~np.isfinite(values),return_indices=True)
    display=values[tuple(nearest)]
    display[distance>2]=np.nan
    finite=values[valid]
    # Fixed numeric range in points; no percentile remapping of individual scores.
    vmin,vmax=76.,98.
    cmap=LinearSegmentedColormap.from_list('tweet_comfort',PALETTE,N=512)
    cmap.set_bad('#f0f0f0');cmap.set_under(PALETTE[0]);cmap.set_over(PALETTE[-1])
    norm=Normalize(vmin,vmax,clip=False)
    proj=ccrs.LambertConformal(central_longitude=15,central_latitude=53,standard_parallels=(35,65))
    fig=plt.figure(figsize=(13.8,12.0),facecolor='white')
    ax=fig.add_axes([.025,.165,.95,.70],projection=proj)
    ax.set_extent([-24.5,44.5,34.6,71.4],ccrs.PlateCarree())
    ax.set_facecolor('white')
    ax.spines['geo'].set_visible(False)
    ax.add_geometries(geometries,ccrs.PlateCarree(),facecolor='#f0f0f0',edgecolor='none',zorder=0)
    mesh=ax.pcolormesh(lon,lat,np.ma.masked_invalid(display),transform=ccrs.PlateCarree(),cmap=cmap,norm=norm,shading='gouraud',rasterized=True,zorder=1)
    projected=proj.project_geometry(land.simplify(.005,preserve_topology=True),ccrs.PlateCarree())
    clip=PathPatch(shapely_to_path(projected),transform=ax.transData)
    mesh.set_clip_path(clip)
    ax.add_geometries(geometries,ccrs.PlateCarree(),facecolor='none',edgecolor='#394853',linewidth=.32,alpha=.75,zorder=3)
    for label,x,y in LABELS:
        ax.text(x,y,label,transform=ccrs.PlateCarree(),ha='center',va='center',fontsize=7.4,color='#183246',zorder=5,path_effects=[pe.withStroke(linewidth=1.5,foreground='white',alpha=.75)])
    fig.text(.5,.953,'Conforto térmico na Europa',ha='center',fontsize=26,fontweight='bold',color='#172633')
    fig.text(.5,.916,'Máxima diária entre 20 e 25 °C = 100 pontos · −1 ponto por °C fora da faixa',ha='center',fontsize=12,color='#36434d')
    combined='source_grid' in data
    sources='E-OBS 0,1° + NOAA CPC 0,5°' if combined else 'E-OBS 0,1°'
    fig.text(.5,.885,f'Média de todos os dias · {start.year}–{end.year} · {sources}',ha='center',fontsize=10.5,color='#64707a')
    cax=fig.add_axes([.16,.107,.68,.016])
    cb=fig.colorbar(matplotlib.cm.ScalarMappable(norm=norm,cmap=cmap),cax=cax,orientation='horizontal',extend='both',ticks=np.arange(76,99,2))
    cb.outline.set_linewidth(.6);cb.ax.tick_params(labelsize=9,length=3)
    fig.text(.5,.139,'Pontuação média diária de conforto térmico',ha='center',fontsize=11,fontweight='bold',color='#253746')
    fig.text(.16,.064,'Menor conforto',ha='left',fontsize=10,color='#66717c')
    fig.text(.84,.064,'Maior conforto',ha='right',fontsize=10,color='#66717c')
    fig.text(.5,.037,'Temperatura apenas: chuva, vento e umidade não entram na nota. Cinza: dados ausentes.',ha='center',fontsize=8.5,color='#66717c')
    fig.text(.5,.018,'Dados: KNMI / Copernicus C3S / ECA&D'+(' + NOAA PSL (lacunas no leste)' if combined else '')+'   |   Cartografia: Natural Earth, 1:10 milhões',ha='center',fontsize=8,color='#66717c')
    output=Path(output);output.mkdir(parents=True,exist_ok=True)
    fig.savefig(output/'europe_comfort.png',dpi=300,facecolor='white')
    fig.savefig(output/'europe_comfort.pdf',dpi=300,facecolor='white')
    plt.close(fig)
    summary=dict(source='E-OBS v33.0e ensemble mean daily maximum temperature',source_url='https://surfobs.climate.copernicus.eu/dataaccess/access_eobs.php',start=str(start),end=str(end),days=int(data['days']),grid_degrees=.1,formula='100-max(20-Tmax,0)-max(Tmax-25,0)',land_grid_cells=int(on_land.sum()),complete_land_cells=int(valid.sum()),missing_land_cells=int(missing.sum()),coverage_fraction=coverage,score_min=float(finite.min()),score_max=float(finite.max()),display_coastal_extension_degrees=.2,color_range=[vmin,vmax],country_boundaries='Natural Earth admin_0_countries 10m')
    if combined:
        summary.update(supplement_source='NOAA CPC Global Daily Temperature 0.5 degrees',supplement_url='https://psl.noaa.gov/data/gridded/data.cpc.globaltemp.html',eobs_land_cells=int((on_land&(data['source_grid']==1)).sum()),noaa_land_cells=int((on_land&(data['source_grid']==2)).sum()),supplement_resampling='Bilinear interpolation of computed five-year scores; original resolution remains 0.5 degrees',daily_definition='E-OBS station reporting day; NOAA 06:00–06:00 UTC',annual_scores_note='Annual arrays refer to E-OBS only; combined score is the daily-weighted full-period score')
    (output/'metadata.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False))
    print(f'Mapa salvo: {output}/europe_comfort.png',flush=True)
