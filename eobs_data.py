"""Read official E-OBS NetCDF through verified, cached HTTP byte ranges."""
import io
import time
from pathlib import Path
import requests

URL = 'https://knmi-ecad-assets-prd.s3.amazonaws.com/ensembles/data/Grid_0.1deg_reg_ensemble/tx_ens_mean_0.1deg_reg_v33.0e.nc'

class HTTPRangeFile(io.RawIOBase):
    def __init__(self, url=URL, cache=Path('.cache/eobs-v33'), block_size=4*1024*1024):
        self.url, self.cache, self.block_size = url, Path(cache), block_size
        self.cache.mkdir(parents=True, exist_ok=True)
        self.session = requests.Session()
        response = self.session.head(url, timeout=60)
        response.raise_for_status()
        self.size = int(response.headers['Content-Length'])
        self.etag = response.headers.get('ETag')
        self.position = 0
        self.memory = {}
        self.downloaded = 0

    def readable(self): return True
    def seekable(self): return True
    def tell(self): return self.position

    def seek(self, offset, whence=0):
        position = offset if whence == 0 else self.position+offset if whence == 1 else self.size+offset
        if position < 0: raise ValueError('Negative seek')
        self.position = position
        return position

    def block(self, number):
        if number in self.memory:
            return self.memory[number]
        start = number*self.block_size
        end = min(self.size, start+self.block_size)-1
        path = self.cache/f'{self.block_size}-{number}.bin'
        if path.exists() and path.stat().st_size == end-start+1:
            data = path.read_bytes()
        else:
            for attempt in range(4):
                try:
                    r = self.session.get(self.url, headers={'Range':f'bytes={start}-{end}','If-Match':self.etag}, timeout=(20,120))
                    r.raise_for_status()
                    if r.status_code != 206 or r.headers.get('Content-Range') != f'bytes {start}-{end}/{self.size}' or len(r.content) != end-start+1:
                        raise ValueError('Server did not return the requested byte range')
                    data = r.content
                    temporary = path.with_suffix('.tmp')
                    temporary.write_bytes(data)
                    temporary.replace(path)
                    self.downloaded += len(data)
                    break
                except requests.RequestException:
                    if attempt == 3: raise
                    time.sleep(2**attempt)
        if len(self.memory) >= 16:
            self.memory.pop(next(iter(self.memory)))
        self.memory[number] = data
        return data

    def read(self, size=-1):
        if size < 0: size = self.size-self.position
        end = min(self.size, self.position+size)
        pieces = []
        while self.position < end:
            number, offset = divmod(self.position,self.block_size)
            data = self.block(number)
            length = min(len(data)-offset,end-self.position)
            pieces.append(data[offset:offset+length])
            self.position += length
        return b''.join(pieces)

    def readinto(self, buffer):
        data = self.read(len(buffer)); buffer[:len(data)] = data; return len(data)
