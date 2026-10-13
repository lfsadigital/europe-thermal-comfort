"""Download bounded official city homicide sources; no credentials are persisted."""
import argparse,json,pathlib,urllib.request
p=argparse.ArgumentParser();p.add_argument('--input-dir',default='/private/tmp');a=p.parse_args();dest=pathlib.Path(a.input_dir);dest.mkdir(parents=True,exist_ok=True)
def get(url,limit):
 with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'ComfyDays/1.0 source audit'}),timeout=120) as response:
  blob=response.read(limit+1)
  if len(blob)>limit:raise ValueError('Source exceeds download bound')
  return blob
for year in range(2020,2026):
 key=f'cius/{year}/offenses-known-to-le-{year}.zip';resolver=json.loads(get('https://cde.ucr.cjis.gov/LATEST/s3/signedurl?key='+key,100000));blob=get(resolver[key],30_000_000);path=dest/f'comfy-fbi-offenses-{year}.zip';path.write_bytes(blob);print(path.name,len(blob))
blob=get('https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/crim_hom_vcit?lang=EN&sex=T&sinceTimePeriod=2020',2_000_000);(dest/'comfy-localcrime-eurostat.txt').write_bytes(blob);print('Eurostat',len(blob))
