import json,gzip,unicodedata,math,datetime,pathlib
import argparse
parser=argparse.ArgumentParser();parser.add_argument('input');parser.add_argument('--dist',default=str(pathlib.Path(__file__).resolve().parent.parent/'site/dist'));args=parser.parse_args()
root=pathlib.Path(args.dist)
places=json.load(gzip.open(root/'assets/places.json.gz'))
raw=json.load(open(args.input))['cities']
def norm(s):return ''.join(c for c in unicodedata.normalize('NFKD',s.casefold()) if not unicodedata.combining(c)).replace(' ','').replace('-','').replace("'",'')
alias={'United States':'United States','Czech Republic':'Czechia','Czechia':'Czech Republic','Bosnia':'Bosnia and Herzegovina','South Korea':'South Korea','Russia':'Russia','Türkiye':'Turkey','Netherlands':'The Netherlands'}
bycountry={}
for p in places:bycountry.setdefault(p[5],[]).append(p)
def km(a,b,c,d):
 r=math.pi/180;h=math.sin((a-c)*r/2)**2+math.cos(a*r)*math.cos(c*r)*math.sin((b-d)*r/2)**2;return 6371.0088*2*math.asin(min(1,math.sqrt(h)))
rows=[]; unmatched=[]
for c in raw:
 candidates=bycountry.get(c['country'],bycountry.get(alias.get(c['country']),[])); name=norm(c['name']); near=[]
 for p in candidates:
  if abs(p[2]-c['latitude'])>.5:continue
  d=km(p[2],p[3],c['latitude'],c['longitude'])
  if d<=15 and (norm(p[1])==name or norm(p[1]).replace('city','')==name.replace('city','')):near.append((d,p))
 if not near:unmatched.append(c['name']);continue
 d,p=min(near,key=lambda x:x[0]);rows.append({'id':p[0],'name':c['name'],'country':c['country'],'slug':c['short_slug'],'latitude':c['latitude'],'longitude':c['longitude'],'score':c['nomad_score'],'monthly_cost_usd':c['cost_of_living_usd'],'match_km':round(d,3)})
out={'source':'https://nomads.com/api/cities','retrieved_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'score_scale':[0,5],'cost_type':'Nomad monthly cost estimate, USD','source_cities':len(raw),'matched_cities':len(rows),'match_method':'Same country, normalized name and coordinates within 15 km; no proximity-only fallback','cities':rows}
(root/'assets/nomads-cities.json').write_text(json.dumps(out,separators=(',',':')))
(root.parent/'docs/nomads-matching-audit.json').write_text(json.dumps({'source_cities':len(raw),'matched_cities':len(rows),'unmatched_names':unmatched,'max_match_km':max(x['match_km'] for x in rows),'bytes':(root/'assets/nomads-cities.json').stat().st_size},indent=2))
print('Matched',len(rows),'/',len(raw),'bytes',(root/'assets/nomads-cities.json').stat().st_size)
