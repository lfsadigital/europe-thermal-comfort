"""Extract national total victim rates only; never regional estimates or subgroups."""
import argparse, collections, datetime, gzip, hashlib, json, pathlib, re, zipfile
import xml.etree.ElementTree as ET

parser=argparse.ArgumentParser()
parser.add_argument('workbook')
parser.add_argument('--dist',default=str(pathlib.Path(__file__).resolve().parent.parent/'site/dist'))
args=parser.parse_args();dist=pathlib.Path(args.dist)
ns={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
archive=zipfile.ZipFile(args.workbook)
strings=[''.join(s.itertext()) for s in ET.fromstring(archive.read('xl/sharedStrings.xml'))]
rates={};counts={}
for _,row in ET.iterparse(archive.open('xl/worksheets/sheet1.xml'),events=['end']):
    if not row.tag.endswith('}row'):continue
    values={}
    for cell in row:
        value=cell.find('s:v',ns)
        if value is not None:
            values[re.sub(r'\d','',cell.attrib['r'])]=strings[int(value.text)] if cell.attrib.get('t')=='s' else value.text
    if (values.get('E')=='Victims of intentional homicide' and all(values.get(c)=='Total' for c in ['F','G','H','I']) and values.get('J') in ['2020','2021','2022','2023','2024','2025']):
        target=rates if values.get('K')=='Rate per 100,000 population' else counts if values.get('K')=='Counts' else None
        if target is not None:
            key=(values['A'],int(values['J']))
            if key in target:raise ValueError('Duplicate total '+str(key))
            target[key]={'iso3':values['A'],'country':values['B'],'year':int(values['J']),'value':float(values['L']),'national_source':values.get('M','')}
    row.clear()
aliases={'United States of America':'United States','United Kingdom of Great Britain and Northern Ireland':'United Kingdom','United Republic of Tanzania':'Tanzania','Republic of Korea':'South Korea','Democratic People\u2019s Republic of Korea':'North Korea','Russian Federation':'Russia','Türkiye':'Turkey','Viet Nam':'Vietnam','Iran (Islamic Republic of)':'Iran','Bolivia (Plurinational State of)':'Bolivia','Venezuela (Bolivarian Republic of)':'Venezuela','Republic of Moldova':'Moldova','Lao People\u2019s Democratic Republic':'Laos','Syrian Arab Republic':'Syria','Côte d’Ivoire':'Ivory Coast','State of Palestine':'Palestinian Territory','Netherlands (Kingdom of the)':'The Netherlands','China, Hong Kong Special Administrative Region':'Hong Kong','China, Macao Special Administrative Region':'Macao','Kosovo under UNSCR 1244':'Kosovo'}
place_countries={p[5] for p in json.load(gzip.open(dist/'assets/places.json.gz'))}
rows=[]
for key,rate in rates.items():
    assert rate['value']>=0
    name=aliases.get(rate['country'],rate['country'])
    rows.append({**rate,'place_country':name if name in place_countries else None,'count':counts.get(key,{}).get('value')})
rows.sort(key=lambda r:(r['iso3'],r['year']))
coverage=collections.Counter(r['year'] for r in rows if r['place_country'])
default_year=2023 if 2023 in coverage else max(coverage)
result={'source':'https://data.unodc.org/datareport/hom-victim','download':'https://data.unodc.org/sites/dataportal.unodc.org/files/2026-07/data_cts_intentional_homicide.xlsx','source_updated':'2026-07-12','retrieved_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'geographic_level':'country','metric':'Victims of intentional homicide, all sexes and ages','unit':'per 100,000 population','default_year':default_year,'coverage_by_year':dict(sorted(coverage.items())),'rows':rows}
(dist/'assets/homicide-country.json').write_text(json.dumps(result,separators=(',',':')))
audit={'workbook_sha256':hashlib.sha256(pathlib.Path(args.workbook).read_bytes()).hexdigest(),'rate_rows':len(rows),'coverage_by_year':result['coverage_by_year'],'default_year':default_year,'unmapped_countries':sorted({r['country'] for r in rows if not r['place_country']}),'selected_sheet':'data_cts_intentional_homicide','excluded_sheet':'data_cts_homicide_reg_estimates','filters':{'indicator':'Victims of intentional homicide','dimension':'Total','category':'Total','sex':'Total','age':'Total','unit':'Rate per 100,000 population'},'sample_rows':[r for r in rows if r['iso3'] in ['USA','PRT','BRA','TZA'] and r['year']==2023]}
(dist.parent/'docs/homicide-import-audit.json').write_text(json.dumps(audit,indent=2))
print(json.dumps({k:v for k,v in audit.items() if k not in ['filters','sample_rows']},indent=2))
