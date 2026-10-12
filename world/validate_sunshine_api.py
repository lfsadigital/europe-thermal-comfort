import urllib.request,urllib.parse,urllib.error,json,datetime,math
from pathlib import Path
root=Path('/Users/luizfellipealmeida/LFSA/personal/world-comfort')
points=[('Porto cell',41.25,-8.25),('Nairobi cell',-1.25,36.75),('Los Angeles cell',34.25,-118.25)]
params={'latitude':','.join(str(p[1]) for p in points),'longitude':','.join(str(p[2]) for p in points),'start_date':'2020-01-01','end_date':'2025-12-31','daily':'sunshine_duration,daylight_duration,temperature_2m_max,precipitation_sum','models':'era5','timezone':'GMT','elevation':'nan,nan,nan','cell_selection':'nearest'}
url='https://archive-api.open-meteo.com/v1/archive?'+urllib.parse.urlencode(params)
try:
 with urllib.request.urlopen(url,timeout=120) as response: data=json.load(response)
except urllib.error.HTTPError as e:
 print(e.read().decode());raise SystemExit(1)
(root/'share/sunshine-api-response.json').write_text(json.dumps(data))
if not isinstance(data,list):data=[data]
expected=[(datetime.date(2020,1,1)+datetime.timedelta(days=i)).isoformat() for i in range(2192)]
report={'source':'Open-Meteo Historical API, explicitly ERA5','url':url,'period':'2020–2025','timezone':'GMT','elevation_downscaling':False,'samples':[]}
for point,d in zip(points,data):
 assert d['daily']['time']==expected
 assert d['daily_units']['sunshine_duration']=='s'
 v=d['daily']['sunshine_duration']; daylight=d['daily']['daylight_duration'];valid=[x for x in v if x is not None and math.isfinite(x)]
 assert len(valid)==2192
 assert all(0<=x<=86400 for x in valid)
 assert all(s<=l+1 for s,l in zip(v,daylight))
 report['samples'].append({'name':point[0],'requested':[point[1],point[2]],'returned':[d['latitude'],d['longitude']],'dates':len(v),'missing_sunshine':len(v)-len(valid),'missing_other_variables':{k:sum(x is None for x in d['daily'][k]) for k in ['temperature_2m_max','precipitation_sum']},'daily_units':d['daily_units'],'mean_sunshine_hours':sum(valid)/len(valid)/3600,'min_hours':min(valid)/3600,'max_hours':max(valid)/3600,'first_day':{k:d['daily'][k][0] for k in ['sunshine_duration','temperature_2m_max','precipitation_sum']}})
(root/'share/sunshine-api-samples.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
