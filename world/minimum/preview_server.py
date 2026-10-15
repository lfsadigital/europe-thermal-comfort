"""Local preview only. Relay small remote minima chunks; never save bulk data to disk."""
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlsplit
from urllib.request import Request,urlopen
import re,threading,collections,argparse,time
ROOT=Path(__file__).resolve().parents[1]/'site/dist'
cache=collections.OrderedDict();lock=threading.Lock();slots=threading.BoundedSemaphore(2);budget=16*1024*1024
class Handler(SimpleHTTPRequestHandler):
 def __init__(self,*args,**kw):super().__init__(*args,directory=str(ROOT),**kw)
 def do_GET(self):
  path=urlsplit(self.path).path
  if not path.startswith('/minimum-data/'):return super().do_GET()
  parts=path.split('/')
  if len(parts)!=4 or not re.fullmatch(r'comfy-minimum-preview-\d+',parts[2]) or not re.fullmatch(r'(minimum-20\d\d-\d+|min-(score|days|coverage)-(mean|20\d\d))\.gz',parts[3]):self.send_error(404);return
  with lock:data=cache.get(path)
  if data is None:
   try:
    with slots:
     url=f'https://github.com/lfsadigital/europe-thermal-comfort/releases/download/{parts[2]}/{parts[3]}'
     for attempt in range(4):
      try:
       with urlopen(Request(url,headers={'User-Agent':'ComfyDays-LocalPreview/1.0'}),timeout=90)as response:data=response.read(8*1024*1024+1)
       if len(data)>8*1024*1024:raise ValueError('Chunk too large')
       break
      except Exception:
       if attempt==3:raise
       time.sleep(attempt+1)
    with lock:
     cache[path]=data;cache.move_to_end(path)
     while sum(map(len,cache.values()))>budget:cache.popitem(last=False)
   except Exception:self.send_error(502,'Remote daily-low data unavailable; retry');return
  self.send_response(200);self.send_header('Content-Type','application/octet-stream');self.send_header('Content-Length',str(len(data)));self.send_header('Cache-Control','no-store');self.end_headers()
  try:self.wfile.write(data)
  except(BrokenPipeError,ConnectionResetError):pass
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--port',type=int,default=8777);a=p.parse_args();print(f'Comfy preview: http://127.0.0.1:{a.port}/',flush=True);ThreadingHTTPServer(('127.0.0.1',a.port),Handler).serve_forever()
