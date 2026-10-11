"""Country scores and annualized comfortable-day counts from cached original data."""
import io
import json
from datetime import date
from pathlib import Path
import h5py
import numpy as np
import xarray as xr
import shapely
import cartopy
from cartopy.io import shapereader
from scipy.interpolate import RegularGridInterpolator
import pandas as pd
from eobs_data import HTTPRangeFile
from scoring import daily_score

class CachedEOBS(HTTPRangeFile):
    def __init__(self):
        # Exact length observed in the official v33.0e HTTP response during download.
        self.size=4964123195
        self.position=0
        self.block_size=4*1024*1024
        self.cache=Path('.cache/eobs-v33')
        self.memory={}
    def block(self,number):
        if number not in self.memory:
            path=self.cache/f'{self.block_size}-{number}.bin'
            if not path.exists(): raise RuntimeError(f'Original block not cached: {number}')
            if len(self.memory)>=16:self.memory.pop(next(iter(self.memory)))
            self.memory[number]=path.read_bytes()
        return self.memory[number]

NAMES={'Portugal':'Portugal','Spain':'Espanha','France':'França','Italy':'Itália','Greece':'Grécia','Turkey':'Turquia','Cyprus':'Chipre','United Kingdom':'Reino Unido','Ireland':'Irlanda','Germany':'Alemanha','Netherlands':'Países Baixos','Belgium':'Bélgica','Switzerland':'Suíça','Austria':'Áustria','Norway':'Noruega','Sweden':'Suécia','Finland':'Finlândia','Iceland':'Islândia','Russia':'Rússia (recorte)','Poland':'Polônia','Romania':'Romênia','Ukraine':'Ucrânia','Denmark':'Dinamarca','Czechia':'Tchéquia','Slovakia':'Eslováquia','Hungary':'Hungria','Bulgaria':'Bulgária','Croatia':'Croácia','Albania':'Albânia','Republic of Serbia':'Sérvia','Bosnia and Herzegovina':'Bósnia e Herzegovina','Slovenia':'Eslovênia','Montenegro':'Montenegro','North Macedonia':'Macedônia do Norte','Moldova':'Moldávia','Belarus':'Belarus','Estonia':'Estônia','Latvia':'Letônia','Lithuania':'Lituânia','Luxembourg':'Luxemburgo','Malta':'Malta','Northern Cyprus':'Chipre do Norte','Andorra':'Andorra','Liechtenstein':'Liechtenstein','San Marino':'San Marino','Kosovo':'Kosovo'}

def main():
    output=Path('output-final')
    p=np.load(output/'comfort_grid.npz')
    lat,lon=p['latitude'],p['longitude']
    days_cache=Path('.cache/eobs-scores/ideal-days-2020-2024.npz')
    if days_cache.exists():
        eobs_days=np.load(days_cache)['annual_days']
    else:
        years=[]
        with CachedEOBS() as remote:
            with h5py.File(remote,'r') as f:
                ds=f['tx'];ys=np.flatnonzero((f['latitude'][:]>=34.5)&(f['latitude'][:]<=71.5));xs=np.flatnonzero((f['longitude'][:]>=-25)&(f['longitude'][:]<=45))
                fill=int(ds.attrs['_FillValue'][0]);scale=float(ds.attrs['scale_factor'][0]);offset=float(ds.attrs['add_offset'][0]);origin=date(1950,1,1)
                for year in range(2020,2025):
                    first=date(year,1,1);last=date(year,12,31);n=(last-first).days+1
                    count=np.zeros(p['score'].shape,dtype=np.uint16)
                    for i in range(n):
                        raw=ds[(first-origin).days+i,ys[0]:ys[-1]+1,xs[0]:xs[-1]+1]
                        t=raw.astype(float)*scale+offset
                        # Integer packing is hundredths of a degree. Include exact 20/25 boundaries.
                        count+=((raw!=fill)&(raw>=round((20-offset)/scale))&(raw<=round((25-offset)/scale))).astype(np.uint16)
                    years.append(count)
                    print(f'E-OBS {year}: dias na faixa calculados',flush=True)
        eobs_days=np.stack(years)
        np.savez_compressed(days_cache,annual_days=eobs_days)
    yy,xx=np.meshgrid(lat,lon,indexing='ij');points=np.stack([yy,xx],axis=-1)
    all_annual_score=p['annual'].copy()
    annual_ideal=eobs_days.astype(float)
    for yi,year in enumerate(range(2020,2025)):
        with xr.open_dataset(f'.cache/noaa/tmax.{year}.nc',engine='h5netcdf') as ds:
            d=ds.sel(lat=slice(72,34),lon=slice(24,46))
            t=d.tmax.values.astype(float);n=t.shape[0]
            good=np.isfinite(t).all(axis=0)
            mean=np.mean(daily_score(t),axis=0);ideal=((t>=20)&(t<=25)).sum(axis=0).astype(float)
            mean[~good]=np.nan;ideal[~good]=np.nan
            coords=(d.lat.values[::-1],d.lon.values)
            ns=RegularGridInterpolator(coords,mean[::-1],bounds_error=False,fill_value=np.nan)(points)
            nd=RegularGridInterpolator(coords,ideal[::-1],bounds_error=False,fill_value=np.nan)(points)
            mask=p['source_grid']==2
            all_annual_score[yi][mask]=ns[mask];annual_ideal[yi][mask]=nd[mask]
        print(f'NOAA {year}: dias e notas anuais calculados',flush=True)
    ideal_year=annual_ideal.sum(axis=0)/5
    cartopy.config['data_dir']=Path('.cache/cartopy')
    records=shapereader.Reader(shapereader.natural_earth('10m','cultural','admin_0_countries')).records()
    weight=np.cos(np.deg2rad(yy))
    rows=[]
    for record in records:
        a=record.attributes
        if a['CONTINENT']!='Europe' and a['ADMIN'] not in ('Turkey','Cyprus','Northern Cyprus'):continue
        land=shapely.contains_xy(record.geometry,xx,yy)
        valid=land&np.isfinite(p['score'])&np.isfinite(ideal_year)&np.isfinite(all_annual_score).all(axis=0)
        total=float(weight[land].sum())
        if not total:continue
        if not valid.any():continue
        def avg(grid):return float(np.average(grid[valid],weights=weight[valid]))
        row={'pais':NAMES.get(a['ADMIN'],a.get('NAME_PT') or a['ADMIN']),'iso3':a.get('ADM0_A3'),'nota_media':avg(p['score']),'dias_20_25_por_ano':avg(ideal_year),'percentual_dias_20_25':avg(ideal_year)*5/1827*100,'cobertura_percentual':float(weight[valid].sum()/total*100),'celulas_validas':int(valid.sum()),'parcela_noaa_percentual':float(weight[valid&(p['source_grid']==2)].sum()/weight[valid].sum()*100)}
        for i,y in enumerate(range(2020,2025)):
            row[f'nota_{y}']=avg(all_annual_score[i]);row[f'dias_20_25_{y}']=avg(annual_ideal[i])
        rows.append(row)
    table=pd.DataFrame(rows).sort_values('nota_media',ascending=False).reset_index(drop=True)
    table.insert(0,'posicao',np.arange(1,len(table)+1))
    table.to_csv(output/'country_scores.csv',index=False,float_format='%.4f')
    table.to_json(output/'country_scores.json',orient='records',indent=2,force_ascii=False)
    formatted=table[['posicao','pais','nota_media','dias_20_25_por_ano','cobertura_percentual']].copy()
    formatted.columns=['Posição','País / território','Nota média','Dias 20–25 °C / ano','Cobertura %']
    for c in formatted.columns[2:]:formatted[c]=formatted[c].map(lambda x:f'{x:.1f}')
    html='''<!doctype html><html lang="pt-BR"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Conforto térmico — tabela por país</title><style>body{font:16px system-ui;color:#183044;max-width:1100px;margin:40px auto;padding:0 20px}h1{font-size:30px}p{line-height:1.5;color:#526271}table{width:100%;border-collapse:collapse;font-variant-numeric:tabular-nums}th{position:sticky;top:0;background:#183044;color:white;text-align:left;padding:12px}td{padding:10px;border-bottom:1px solid #e3e9ee}tr:nth-child(even){background:#f5f8fa}td:nth-child(n+3){text-align:right}input{padding:10px;font:inherit;margin:15px 0;width:280px;border:1px solid #bac9d4;border-radius:6px}.scroll{overflow:auto}</style><h1>Conforto térmico na Europa</h1><p>2020–2024 · Nota média diária: 100 entre 20 e 25 °C; −1 ponto por °C fora da faixa. Dias por ano: contagem dos dias na faixa ao longo dos cinco anos, dividida por 5.</p><p>Média geográfica ponderada pela área das células válidas, sem peso por população. Dados: E-OBS 0,1° e NOAA CPC 0,5°. Rússia e países na borda referem-se ao recorte do mapa. Países com cobertura incompleta exigem cautela na comparação.</p><input id="filter" placeholder="Filtrar país" aria-label="Filtrar país"><div class="scroll">'''+formatted.to_html(index=False,border=0)+'''</div><p>O CSV contém as notas e os dias de cada ano, a cobertura e a participação da NOAA.</p><script>document.getElementById('filter').addEventListener('input',e=>{document.querySelectorAll('tbody tr').forEach(r=>r.hidden=!r.innerText.toLowerCase().includes(e.target.value.toLowerCase()))})</script></html>'''
    (output/'country_scores.html').write_text(html)
    print(table[['pais','nota_media','dias_20_25_por_ano','cobertura_percentual']].to_string(index=False),flush=True)
    # Annualization checks: full-period score equals day-weighted annual country means.
    weights=np.array([366,365,365,365,366])
    np.testing.assert_allclose(table['nota_media'],table[[f'nota_{y}' for y in range(2020,2025)]].values@weights/1827,atol=1e-10,rtol=0)
    np.testing.assert_allclose(table['dias_20_25_por_ano'],table[[f'dias_20_25_{y}' for y in range(2020,2025)]].sum(axis=1)/5,atol=1e-10,rtol=0)
    print('Verificação: médias anuais e contagens anualizadas consistentes.',flush=True)

if __name__=='__main__':main()
