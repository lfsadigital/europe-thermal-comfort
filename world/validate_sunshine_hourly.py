import json,urllib.request,urllib.parse
from pathlib import Path
params={'latitude':'41.25','longitude':'-8.25','start_date':'2025-06-01','end_date':'2025-06-03','hourly':'sunshine_duration,temperature_2m','daily':'sunshine_duration,temperature_2m_max','models':'era5','timezone':'GMT','elevation':'nan','cell_selection':'nearest'}
url='https://archive-api.open-meteo.com/v1/archive?'+urllib.parse.urlencode(params)
with urllib.request.urlopen(url,timeout=60) as r:d=json.load(r)
rows=[]
for i,date in enumerate(d['daily']['time']):
 sun=sum(d['hourly']['sunshine_duration'][i*24:(i+1)*24]);temp=max(d['hourly']['temperature_2m'][i*24:(i+1)*24]);
 assert abs(sun-d['daily']['sunshine_duration'][i])<.2
 assert abs(temp-d['daily']['temperature_2m_max'][i])<.11
 rows.append({'date':date,'hourly_sum_seconds':sun,'daily_sunshine_seconds':d['daily']['sunshine_duration'][i],'hourly_max_C':temp,'daily_max_C':d['daily']['temperature_2m_max'][i]})
result={'result':'PASS','model':'ERA5','timezone':'GMT','requested':[41.25,-8.25],'returned':[d['latitude'],d['longitude']],'url':url,'rows':rows}
Path('/Users/luizfellipealmeida/LFSA/personal/world-comfort/share/sunshine-hourly-check.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
