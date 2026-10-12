from pathlib import Path
import gzip,struct,json
root=Path(__file__).resolve().parent/'site/dist/assets'
a=b=0
for p in root.glob('climate-*.gz'):
 raw=gzip.decompress(p.read_bytes());h=list(struct.unpack('<11I',raw[:44]));n,nt=h[3:5];offset=44+2*n+4*(n+1)+12*nt
 # Marginal temperature tables are unused: the joint tables retain all exact statistics.
 compact=struct.pack('<11I',*(h[:4]+[0]+h[5:]))+raw[44:44+2*n]+bytes(4*(n+1))+raw[offset:]
 assert compact[44+2*n+4*(n+1):]==raw[offset:]
 packed=gzip.compress(compact,compresslevel=9,mtime=0);a+=p.stat().st_size;b+=len(packed);p.write_bytes(packed)
print(a,b,'saved',a-b)
