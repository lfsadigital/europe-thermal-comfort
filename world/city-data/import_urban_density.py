"""Join GeoNames points to GHSL 2025 urban-centre polygons; no nearest fallback.
Input: the small GENERAL_CHARACTERISTICS thematic ZIP (CC BY 4.0).
No GADM boundaries or attributes are redistributed.
"""
import argparse,gzip,json,math,sqlite3,struct,tempfile,zipfile,hashlib
from pathlib import Path

def project(lat,lon):
    phi=math.radians(lat);theta=phi
    for _ in range(20):
        den=2+2*math.cos(2*theta)
        if den<1e-12: break
        delta=(2*theta+math.sin(2*theta)-math.pi*math.sin(phi))/den
        theta-=delta
        if abs(delta)<1e-12:break
    return 2*math.sqrt(2)*6378137/math.pi*math.radians(lon)*math.cos(theta),math.sqrt(2)*6378137*math.sin(theta)

def polygons(blob):
    flags=blob[3]; offset=8+{0:0,1:32,2:48,3:48,4:64}[(flags>>1)&7]
    def read(pos):
        endian='<' if blob[pos]==1 else '>';typ=struct.unpack_from(endian+'I',blob,pos+1)[0];pos+=5
        n=struct.unpack_from(endian+'I',blob,pos)[0];pos+=4
        if typ==6:
            out=[]
            for _ in range(n):
                child,pos=read(pos);out+=child
            return out,pos
        assert typ==3,typ
        rings=[]
        for _ in range(n):
            count=struct.unpack_from(endian+'I',blob,pos)[0];pos+=4
            rings.append([struct.unpack_from(endian+'dd',blob,pos+i*16)for i in range(count)]);pos+=count*16
        return [rings],pos
    return read(offset)[0]

def ring_contains(x,y,ring):
    inside=False
    for (ax,ay),(bx,by) in zip(ring,ring[1:]+ring[:1]):
        if (ay>y)!=(by>y) and x<(bx-ax)*(y-ay)/(by-ay)+ax:inside=not inside
    return inside

def contains(x,y,polys):
    return any(ring_contains(x,y,p[0]) and not any(ring_contains(x,y,r)for r in p[1:])for p in polys)

def build(archive,places_path,output):
    raw=Path(archive).read_bytes(); assert len(raw)<15_000_000
    with zipfile.ZipFile(archive)as z,tempfile.TemporaryDirectory(prefix='comfy-density-')as tmp:
        name=next(n for n in z.namelist()if n.endswith('.gpkg'))
        path=Path(tmp)/'density.gpkg';path.write_bytes(z.read(name));con=sqlite3.connect(path)
        table=con.execute("select table_name from gpkg_geometry_columns where geometry_type_name='MULTIPOLYGON'").fetchone()[0]
        rows=con.execute(f'SELECT geom,ID_UC_G0,GC_UCN_MAI_2025,GC_UCA_KM2_2025,GC_POP_TOT_2025 FROM "{table}"').fetchall()
        grid={};centres={};step=100000
        for geom,id,name,area,pop in rows:
            if not area or not pop or area<=0 or pop<0:continue
            poly=polygons(geom);pts=[xy for p in poly for r in p for xy in r]
            xs,ys=zip(*pts);bbox=min(xs),min(ys),max(xs),max(ys)
            centres[id]=(name,area,pop,poly,bbox)
            for i in range(math.floor(bbox[0]/step),math.floor(bbox[2]/step)+1):
                for j in range(math.floor(bbox[1]/step),math.floor(bbox[3]/step)+1):grid.setdefault((i,j),[]).append(id)
        places=json.load(gzip.open(places_path,'rt'));matches={};ambiguous=0
        for p in places:
            x,y=project(p[2],p[3]);found=[]
            for id in grid.get((math.floor(x/step),math.floor(y/step)),[]):
                name,area,pop,poly,b=centres[id]
                if b[0]<=x<=b[2]and b[1]<=y<=b[3]and contains(x,y,poly):found.append(id)
            if len(found)==1:
                id=found[0];name,area,pop,_,_=centres[id];matches[str(p[0])]=[id,name,round(pop/area,2),area,round(pop,2)]
            elif len(found)>1:ambiguous+=1
        data={'source':'European Commission JRC · GHSL UCDB R2024A V1.2','year':2025,'license':'CC BY 4.0','url':'https://human-settlement.emergency.copernicus.eu/ghs_ucdb_2024.php','definition':'Estimated urban-centre residents per km²; not municipal density. Point-in-polygon join; no nearest fallback.','fields':['urbanCentreId','urbanCentreName','residentsPerKm2','areaKm2','estimatedResidents'],'cities':matches}
        with gzip.GzipFile(output,'wb',mtime=0)as f:f.write(json.dumps(data,ensure_ascii=False,separators=(',',':')).encode())
        audit={'catalogCities':len(places),'matched':len(matches),'unknown':len(places)-len(matches),'ambiguous':ambiguous,'urbanCentres':len(centres),'inputSha256':hashlib.sha256(raw).hexdigest(),'bytes':Path(output).stat().st_size}
        print(json.dumps(audit));return audit
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('archive');p.add_argument('places');p.add_argument('output');a=p.parse_args();build(a.archive,a.places,a.output)
