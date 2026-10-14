"""EPI 2026 county budgets: exact 1p0c rows joined through GeoNames county codes."""
import argparse, collections, datetime, gzip, hashlib, json, math, pathlib, re, zipfile
import xml.etree.ElementTree as ET

p = argparse.ArgumentParser()
p.add_argument('--workbook', required=True)
p.add_argument('--geonames', required=True)
p.add_argument('--site', default=str(pathlib.Path(__file__).resolve().parents[1] / 'site'))
a = p.parse_args()
site = pathlib.Path(a.site)
ns = {'s': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
z = zipfile.ZipFile(a.workbook)
ss = [''.join(t.itertext()) for t in ET.fromstring(z.read('xl/sharedStrings.xml'))]
counties, states, coverage = {}, {}, collections.Counter()
component_deltas = []
for _, row in ET.iterparse(z.open('xl/worksheets/sheet2.xml'), events=['end']):
    if not row.tag.endswith('}row'):
        continue
    values = {}
    for cell in row:
        v = cell.find('s:v', ns)
        if v is not None:
            values[re.sub(r'\d', '', cell.attrib['r'])] = ss[int(v.text)] if cell.attrib.get('t') == 's' else v.text
    if row.attrib['r'] == '2':
        assert values['C'] == 'county_fips' and values['E'] == 'Family' and values['M'] == 'Total'
    if values.get('E') == '1p0c':
        fips = str(int(values['C'])).zfill(5)
        assert fips not in counties
        components = [float(values[c]) for c in 'FGHIJKL']
        monthly, annual = float(values['M']), float(values['U'])
        assert all(math.isfinite(v) and v >= 0 for v in components)
        assert monthly > 0 and abs(monthly * 12 - annual) < 1e-7
        component_deltas.append(abs(sum(components) - monthly))
        # Published component amounts and totals are separately rounded to annual dollars.
        assert component_deltas[-1] <= 2 / 12 + 1e-7 and components[5] == 0
        state = values['B']
        assert state not in states or states[state] == fips[:2]
        states[state] = fips[:2]
        counties[fips] = [values['D'], state, monthly, annual, *components]
        coverage[state] += 1
    row.clear()
assert len(counties) == 3143
places = json.load(gzip.open(site / 'dist/assets/places.json.gz'))
catalog = {p[0]: p for p in places if p[5] == 'United States'}
state_names = {f['properties']['abbr']: f['properties']['name'] for f in json.load(gzip.open(site / 'dist/assets/us-states.geojson.gz'))['features']}
def norm(s):
    return re.sub('[^a-z]', '', s.lower())
joins, rejected = {}, collections.Counter()
with zipfile.ZipFile(a.geonames).open('cities1000.txt') as src:
    for line in src:
        fields = line.decode().rstrip('\n').split('\t')
        ident = int(fields[0])
        if fields[8] != 'US' or ident not in catalog:
            continue
        city, state, county = catalog[ident], fields[10], fields[11]
        if state not in states or len(county) != 3 or not county.isdigit():
            rejected['missing_county_code'] += 1
            continue
        if norm(city[4]) != norm(state_names.get(state, '')) and not (state == 'DC' and city[4] in ['Washington, D.C.', 'District of Columbia']):
            rejected['state_mismatch'] += 1
            continue
        if abs(city[2] - float(fields[4])) > .02 or abs(city[3] - float(fields[5])) > .02:
            rejected['catalog_coordinate_changed'] += 1
            continue
        fips = states[state] + county
        if fips not in counties:
            rejected['county_not_in_epi'] += 1
            continue
        joins[str(ident)] = fips
source = 'https://www.epi.org/resources/budget/'
result = {'source': source, 'download': 'https://files.epi.org/uploads/fbc_data_2026.xlsx',
          'edition': 2026, 'price_year': 2025, 'profile': '1 adult, no children', 'family_code': '1p0c',
          'currency': 'USD', 'unit': 'monthly', 'geography': 'county',
          'license': 'CC BY-NC-SA 4.0',
          'adaptation': 'County/city join by Comfy Days, CC BY-NC-SA 4.0',
          'geonames_credit': {'source': 'https://www.geonames.org/', 'license': 'CC BY 4.0', 'license_url': 'https://creativecommons.org/licenses/by/4.0/'}, 'license_url': 'https://creativecommons.org/licenses/by-nc-sa/4.0/',
          'citation': 'Economic Policy Institute. 2026. Family Budget Calculator.',
          'retrieved_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
          'join_method': 'Exact GeoNames ID, state and county FIPS; catalog coordinate check; no nearest-city, metro or state fallback.',
          'columns': ['name', 'state', 'monthly', 'annual', 'housing', 'food', 'transport', 'healthcare', 'other', 'childcare', 'taxes'],
          'counties': counties, 'city_counties': joins}
payload = json.dumps(result, separators=(',', ':'), ensure_ascii=False).encode()
(site / 'dist/assets/epi-budget.json.gz').write_bytes(gzip.compress(payload, mtime=0))
audit = {'source': source, 'workbook_sha256': hashlib.sha256(pathlib.Path(a.workbook).read_bytes()).hexdigest(),
         'geonames_sha256': hashlib.sha256(pathlib.Path(a.geonames).read_bytes()).hexdigest(),
         'county_rows': len(counties), 'catalog_usa_cities': len(catalog), 'matched_cities': len(joins),
         'unknown_cities': len(catalog) - len(joins), 'rejected': dict(rejected), 'max_component_total_difference_usd_month': max(component_deltas), 'county_rows_by_state': dict(coverage),
         'samples': {str(i): {'city': catalog[i][1], 'fips': joins.get(str(i)), 'record': counties.get(joins.get(str(i)))}
                     for i in [4164138, 5128581, 5391959, 5368361, 4180439]},
         'checks': ['county tab only', '1p0c only', 'monthly equals annual /12', 'published component/total difference at most $2/year; original total retained',
                    'zero childcare', 'unique county FIPS', 'exact state/code join', 'no nearest fallback']}
(site / 'docs/EPI-IMPORT-AUDIT.json').write_text(json.dumps(audit, indent=2) + '\n')
print(json.dumps({k: audit[k] for k in ['county_rows', 'catalog_usa_cities', 'matched_cities', 'unknown_cities', 'rejected', 'samples']}))
