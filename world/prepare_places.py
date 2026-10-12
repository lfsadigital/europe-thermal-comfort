from pathlib import Path
import requests,zipfile,io,json,gzip
root=Path('.cache/geonames');root.mkdir(parents=True,exist_ok=True)
for name in ['cities1000.zip','admin1CodesASCII.txt','countryInfo.txt']:
 p=root/name
 if not p.exists():
  r=requests.get('https://download.geonames.org/export/dump/'+name,timeout=180);r.raise_for_status();p.write_bytes(r.content)
admins={l.split('\t')[0]:l.split('\t')[1] for l in (root/'admin1CodesASCII.txt').read_text().splitlines() if '\t' in l}
countries={l.split('\t')[0]:l.split('\t')[4] for l in (root/'countryInfo.txt').read_text().splitlines() if l and not l.startswith('#')}
rows=[]
with zipfile.ZipFile(root/'cities1000.zip') as z:
 for line in z.read('cities1000.txt').decode().splitlines():
  c=line.split('\t')
  if c[7] not in {'PPL','PPLA','PPLA2','PPLA3','PPLA4','PPLC','PPLG'}:continue
  rows.append([int(c[0]),c[1],float(c[4]),float(c[5]),admins.get(c[8]+'.'+c[10],''),countries.get(c[8],c[8])])
with gzip.open('site/dist/assets/places.json.gz','wt',encoding='utf-8') as f:json.dump(rows,f,ensure_ascii=False,separators=(',',':'))
print('GeoNames places',len(rows),flush=True)
