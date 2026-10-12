"""Remote-only recovery storage for a failed batch; never copies data to the Mac."""
import os,subprocess,tarfile,json
from pathlib import Path
assert os.environ.get('GITHUB_ACTIONS')=='true'
root=Path(os.environ['RUNNER_TEMP']);cache=root/'comfy-sunshine-cache';out=root/'comfy-sunshine-output';tag='comfy-sunshine-recovery-v1'
if not cache.exists() and not out.exists():raise SystemExit(0)
if subprocess.run(['gh','release','view',tag],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL).returncode:
 subprocess.run(['gh','release','create',tag,'--prerelease','--title','Temporary remote sunshine recovery','--notes','Temporary remote batch checkpoints. Removed after successful publication. No climate files were copied to the local Mac.'],check=True)
for path in list(cache.glob('*.npy'))+list(cache.glob('completed.json')):
 subprocess.run(['gh','release','upload',tag,str(path),'--clobber'],check=True)
if out.exists():
 bundle=root/'sunshine-recovery-output.tar'
 with tarfile.open(bundle,'w') as tar:
  for path in out.iterdir():
   if path.is_file():tar.add(path,arcname=path.name)
 subprocess.run(['gh','release','upload',tag,str(bundle),'--clobber'],check=True)
print('Saved recovery files remotely; no bulk files moved to the Mac')
