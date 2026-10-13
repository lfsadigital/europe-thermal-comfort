"""Conservative city joins; FBI Table 8 only and Eurostat published victim rates."""
import argparse,collections,datetime,gzip,hashlib,io,json,pathlib,re,subprocess,unicodedata,zipfile
import xml.etree.ElementTree as ET
P=argparse.ArgumentParser();P.add_argument('--input-dir',default='/private/tmp');P.add_argument('--dist',default=str(pathlib.Path(__file__).resolve().parent.parent/'site/dist'));a=P.parse_args();src=pathlib.Path(a.input_dir);dist=pathlib.Path(a.dist);places=json.load(gzip.open(dist/'assets/places.json.gz'))
def norm(s):
 s=''.join(c for c in unicodedata.normalize('NFKD',s.lower()) if not unicodedata.combining(c));s=re.sub(r'\bst[.]?\b','saint',s);s=re.sub(r'\bft[.]?\b','fort',s);s=re.sub(r'\bmt[.]?\b','mount',s);return re.sub(r'[^a-z0-9]','',s)
def rows_xlsx(data):
 w=zipfile.ZipFile(io.BytesIO(data));ns={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'};ss=[''.join(e.itertext()) for e in ET.fromstring(w.read('xl/sharedStrings.xml'))] if 'xl/sharedStrings.xml' in w.namelist() else []
 for _,r in ET.iterparse(w.open('xl/worksheets/sheet1.xml'),events=['end']):
  if not r.tag.endswith('}row'):continue
  vals={}
  for c in r:
   v=c.find('s:v',ns);inline=c.find('s:is',ns);vals[re.sub(r'\d','',c.attrib['r'])]=ss[int(v.text)] if v is not None and c.attrib.get('t')=='s' else v.text if v is not None else ''.join(inline.itertext()) if inline is not None else ''
  yield int(r.attrib['r']),vals;r.clear()
usa=collections.defaultdict(list)
for p in places:
 if p[5]=='United States':usa[(norm(p[4]),norm(p[1]))].append(p)
alias={'newyork':'newyorkcity','washington':'washingtondc'};out=[];audit={'sources':[],'rejected':collections.Counter(),'unmatched_samples':[],'ambiguous_samples':[],'matches':[]}
for year in range(2020,2026):
 path=src/f'comfy-fbi-offenses-{year}.zip';z=zipfile.ZipFile(path);table=next(n for n in z.namelist() if re.search(r'Table_8_.*by_State_by_City_'+str(year)+r'\.xlsx$',n,re.I));table_data=z.read(table);method=next(n for n in z.namelist() if 'methodolog' in n.lower() and n.lower().endswith('.pdf'));pdf=src/f'comfy-fbi-methodology-{year}.pdf';pdf.write_bytes(z.read(method));text=subprocess.check_output(['pdftotext',str(pdf),'-'],text=True);flat=re.sub(r'\s+',' ',text);rule=re.search(r'To be included in Tables 8.{0,250}',flat)
 assert rule and '12 months of complete data' in rule.group(0),f'Missing completeness rule {year}'
 raw=list(rows_xlsx(table_data));assert any(f'by State by City, {year}' in v.get('A','') for _,v in raw[:8]);header=next(v for _,v in raw[:10] if v.get('B')=='City');assert 'Murder' in header['E'] and header['C']=='Population'
 footnotes={}
 for _,v in raw:
  if re.match(r'^\d+ ',v.get('A','')):footnotes[re.match(r'^\d+',v['A'])[0]]=v['A']
 state='';state_flag='';accepted=[];seen_source=set()
 for row,v in raw:
  if v.get('A') and not re.match(r'^\d',v['A']):
   m=re.match(r'^(.*?)(\d*)$',v['A']);state=m[1].strip();state_flag=m[2]
  if not v.get('B') or not re.fullmatch(r'\d+',v.get('C','')) or not re.fullmatch(r'\d+',v.get('E','')):continue
  pop=int(v['C']);count=int(v['E']);name=re.sub(r'\d+$','',v['B']).strip();key=(norm(state),norm(name));key=(key[0],alias.get(key[1],key[1]));candidates=usa.get(key,[])
  if pop<=0:audit['rejected']['invalid_population']+=1;continue
  if len(candidates)!=1:
   audit['rejected']['unmatched' if not candidates else 'ambiguous']+=1
   dest='unmatched_samples' if not candidates else 'ambiguous_samples'
   if len(audit[dest])<50:audit[dest].append({'year':year,'state':state,'city':name,'candidates':[p[0] for p in candidates]})
   continue
  p=candidates[0]
  if p[6] and not .5<=pop/p[6]<=2:audit['rejected']['population_sanity']+=1;continue
  if key in seen_source:raise ValueError('Duplicate FBI city/state source key '+str(key))
  seen_source.add(key);warning='; '.join(footnotes[f] for f in [state_flag,*re.findall(r'\d+$',v['B'])] if f in footnotes)
  r={'id':p[0],'year':year,'value':count/pop*100000,'count':count,'population':pop,'source':'FBI','area':name+', '+p[4],'geography':'municipal agency service area','reporting_months':12,'coverage':'12 complete months required by FBI Table 8 methodology','source_row':row,'warning':warning}
  accepted.append(r);audit['matches'].append({'id':p[0],'year':year,'source':'FBI','state':state,'city':name,'source_row':row,'method':'unique state + normalized city name; exact catalog ID; population sanity 0.5–2.0'})
 out.extend(accepted);audit['sources'].append({'source':'FBI','year':year,'key':f'cius/{year}/offenses-known-to-le-{year}.zip','zip_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'table':table,'table_sha256':hashlib.sha256(table_data).hexdigest(),'methodology_sha256':hashlib.sha256(z.read(method)).hexdigest(),'coverage_rule':rule.group(0).split('To be included in Table 20')[0].strip(),'accepted':len(accepted)})
# Explicit city-code/country/name crosswalk; no proximity or country-capital fallback.
config={'BG001C':('Bulgaria','Sofia'),'CZ001C':('Czechia','Prague'),'DK001C':('Denmark','Copenhagen'),'DE001C':('Germany','Berlin'),'EL001C':('Greece','Athens'),'ES001C':('Spain','Madrid'),'FR001C':('France','Paris'),'HR001C':('Croatia','Zagreb'),'IT001C':('Italy','Rome'),'CY001C':('Cyprus','Nicosia'),'LV001C':('Latvia','Riga'),'LT001C':('Lithuania','Vilnius'),'LU001C':('Luxembourg','Luxembourg'),'HU001C':('Hungary','Budapest'),'MT001C':('Malta','Valletta'),'NL001C':('The Netherlands','Amsterdam'),'AT001C':('Austria','Vienna'),'PL001C':('Poland','Warsaw'),'PT001C':('Portugal','Lisbon'),'SI001C':('Slovenia','Ljubljana'),'SK001C':('Slovakia','Bratislava'),'FI001C':('Finland','Helsinki'),'IS001C':('Iceland','Reykjavik'),'NO001C':('Norway','Oslo'),'CH001C':('Switzerland','Bern'),'CH002C':('Switzerland','Zürich'),'BA001C1':('Bosnia and Herzegovina','Sarajevo'),'ME001C':('Montenegro','Podgorica'),'MK001C':('North Macedonia','Skopje'),'AL001C':('Albania','Tirana'),'RS001C':('Serbia','Belgrade'),'TR012C':('Turkey','Istanbul'),'XK001C':('Kosovo','Pristina')}
path=src/'comfy-localcrime-eurostat.txt';j=json.loads(path.read_text());assert j['id']==['freq','sex','unit','cities','time'];dim=j['dimension'];assert dim['sex']['category']['index']=={'T':0} and dim['freq']['category']['index']=={'A':0};units=dim['unit']['category']['index'];cities=dim['cities']['category']['index'];years=dim['time']['category']['index'];size=j['size'];flags=j.get('status',{});values=j['value'];labels=dim['cities']['category']['label'];euro=0
for code,ci in cities.items():
 country,name=config[code];candidates=[p for p in places if p[5]==country and norm(p[1])==norm(name)]
 if len(candidates)!=1:audit['rejected']['eurostat_ambiguous_or_unmatched']+=1;continue
 p=candidates[0]
 for year,ti in years.items():
  idx=(units['P_HTHAB']*size[3]+ci)*size[4]+ti;nr=(units['NR']*size[3]+ci)*size[4]+ti;value=values.get(str(idx));flag=flags.get(str(idx),'')
  if value is None:continue
  if flag:audit['rejected']['eurostat_flagged']+=1;continue
  assert value>=0;count=values.get(str(nr));assert count is None or count>=0
  out.append({'id':p[0],'year':int(year),'value':value,'count':count,'population':None,'source':'Eurostat','area':labels[code],'geography':'greater city' if 'greater' in labels[code].lower() else 'city','reporting_months':None,'coverage':'Official annual rate; monthly reporting completeness not published','city_code':code,'source_index':idx,'warning':''});euro+=1;audit['matches'].append({'id':p[0],'year':int(year),'source':'Eurostat','city_code':code,'area':labels[code],'method':'explicit city-code + country + unique normalized catalog name'})
audit['sources'].append({'source':'Eurostat','dataset':'crim_hom_vcit','updated':j['updated'],'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'unit':'P_HTHAB','sex':'T','accepted':euro,'flags_excluded':True});out.sort(key=lambda r:(r['id'],r['year']));assert len({(r['id'],r['year']) for r in out})==len(out)
coverage={str(y):dict(collections.Counter(r['source'] for r in out if r['year']==y)) for y in range(2020,2026)}
result={'retrieved_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'metric':'FBI murder/nonnegligent manslaughter and Eurostat intentional homicide victims','unit':'per 100,000 population','default_year':2024,'coverage_by_year':coverage,'source_urls':{'FBI':'https://cde.ucr.cjis.gov/LATEST/webapp/#/pages/downloads','Eurostat':'https://ec.europa.eu/eurostat/databrowser/view/crim_hom_vcit/default/table?lang=en'},'columns':['id','year','value','count','population','source','area','geography','reference','warning'],'rows':[[r['id'],r['year'],r['value'],r['count'],r['population'],r['source'],r['area'],r['geography'],r.get('source_row',r.get('city_code')),r['warning']] for r in out]};data=json.dumps(result,separators=(',',':')).encode();(dist/'assets/homicide-city.json.gz').write_bytes(gzip.compress(data,mtime=0));audit['coverage_by_year']=coverage;audit['rejected']=dict(audit['rejected']);audit['rows']=len(out);audit['json_bytes']=len(data);audit['compressed_bytes']=(dist/'assets/homicide-city.json.gz').stat().st_size;(dist.parent/'docs/city-homicide-import-audit.json').write_text(json.dumps(audit,indent=2));print(json.dumps({k:v for k,v in audit.items() if k not in ['sources','matches','unmatched_samples','ambiguous_samples']},indent=2))
