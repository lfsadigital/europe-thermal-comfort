"""Recheck every exported rate against its original official table and catalog join."""
import gzip,json,zipfile,pathlib,io,re,xml.etree.ElementTree as ET,hashlib,collections
base=pathlib.Path(__file__).resolve().parent.parent;dist=base/'site/dist';src=pathlib.Path('/private/tmp')
j=json.load(gzip.open(dist/'assets/homicide-city.json.gz'));rows=[dict(zip(j['columns'],r)) for r in j['rows']];places={p[0]:p for p in json.load(gzip.open(dist/'assets/places.json.gz'))};audit=json.loads((base/'site/docs/city-homicide-import-audit.json').read_text());matches={(r['id'],r['year']):r for r in audit['matches']}
assert len(rows)==len({(r['id'],r['year']) for r in rows})==37674
# Independent cell reader: each export's stored reference points back to its source row.
def cells(blob):
 z=zipfile.ZipFile(io.BytesIO(blob));ns={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'};ss=[''.join(e.itertext()) for e in ET.fromstring(z.read('xl/sharedStrings.xml'))] if 'xl/sharedStrings.xml' in z.namelist() else [];out={}
 for row in ET.fromstring(z.read('xl/worksheets/sheet1.xml')).find('s:sheetData',ns):
  d={}
  for c in row:
   v=c.find('s:v',ns);i=c.find('s:is',ns);d[re.sub(r'\d','',c.attrib['r'])]=ss[int(v.text)] if v is not None and c.attrib.get('t')=='s' else v.text if v is not None else ''.join(i.itertext()) if i is not None else ''
  out[int(row.attrib['r'])]=d
 return out
fbi={}
for source in audit['sources']:
 if source['source']!='FBI':continue
 path=src/f"comfy-fbi-offenses-{source['year']}.zip";assert hashlib.sha256(path.read_bytes()).hexdigest()==source['zip_sha256'];z=zipfile.ZipFile(path);blob=z.read(source['table']);assert hashlib.sha256(blob).hexdigest()==source['table_sha256'];assert '12 months of complete data' in source['coverage_rule'];fbi[source['year']]=cells(blob)
e=json.loads((src/'comfy-localcrime-eurostat.txt').read_text());dims=e['dimension'];sizes=e['size'];checked=collections.Counter()
for r in rows:
 p=places[r['id']];m=matches[r['id'],r['year']];assert r['value']>=0
 if r['source']=='FBI':
  assert p[5]=='United States'
  assert re.sub('[^a-z]','',p[4].lower())==re.sub('[^a-z]','',m['state'].lower())
  raw=fbi[r['year']][r['reference']];assert int(raw['C'])==r['population']>0;assert int(raw['E'])==r['count'];assert abs(r['value']-int(raw['E'])*100000/int(raw['C']))<1e-12;assert r['geography']=='municipal agency service area'
 else:
  code=r['reference'];ci=dims['cities']['category']['index'][code];ti=dims['time']['category']['index'][str(r['year'])];ui=dims['unit']['category']['index']['P_HTHAB'];idx=(ui*sizes[3]+ci)*sizes[4]+ti;assert e['value'][str(idx)]==r['value'];assert not e.get('status',{}).get(str(idx));assert r['area']==dims['cities']['category']['label'][code];assert r['population'] is None
 checked[r['source']]+=1
miami=next(r for r in rows if r['id']==4164138 and r['year']==2024);assert miami['count']==28 and miami['population']==460392
assert not any(r['id']==2988507 and r['year']==2024 for r in rows) # Paris missing, not zero
zeros=sum(r['value']==0 for r in rows);assert zeros>0
report={'result':'PASS','rows_checked':len(rows),'by_source':dict(checked),'known_zero_rates':zeros,'coverage_by_year':j['coverage_by_year'],'compressed_bytes':(dist/'assets/homicide-city.json.gz').stat().st_size,'sha256':hashlib.sha256((dist/'assets/homicide-city.json.gz').read_bytes()).hexdigest(),'checks':['unique city/year','all source counts, denominators and rates','catalog IDs and USA state matches','official annual completeness rules','Eurostat published rates and flags','unknown distinct from zero']};(base/'site/docs/city-homicide-data-verification.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
