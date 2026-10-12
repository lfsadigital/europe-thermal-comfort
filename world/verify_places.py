import gzip,json,math
from pathlib import Path
p=json.loads(gzip.decompress(Path('site/dist/assets/places.json.gz').read_bytes()))
assert len(p)>130000 and len({r[0] for r in p})==len(p)
assert all(-90<=r[2]<=90 and -180<=r[3]<=180 for r in p)
for name,lat,lon,state in [('São Paulo',-23.55052,-46.633308,'São Paulo'),('Porto',41.14961,-8.61099,'Porto'),('Cape Town',-33.92584,18.42322,'Western Cape')]:
 def km(r):
  a,b=map(math.radians,[lat,r[2]]);dlat=b-a;dlon=math.radians(r[3]-lon);return 6371.0088*2*math.asin(min(1,math.sqrt(math.sin(dlat/2)**2+math.cos(a)*math.cos(b)*math.sin(dlon/2)**2)))
 row=min(p,key=km);assert row[1]==name,(name,row);assert state in row[4],row;print(name,row[4],row[5],round(km(row),3),'km')
print('PASS GeoNames unique IDs, geographic coordinates, nearest city and state checks')
