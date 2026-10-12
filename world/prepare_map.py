from pathlib import Path
import cartopy
from cartopy.io import shapereader
cartopy.config['data_dir']=Path('.cache/cartopy').resolve()
p=shapereader.natural_earth('50m','cultural','admin_0_countries')
print('Real world borders ready',p,flush=True)
