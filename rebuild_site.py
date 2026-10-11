"""Rebuild site assets and run numerical checks from a clean checkout."""
import subprocess,sys
from pathlib import Path
for script in ['build_comfort.py','country_table.py','export_site.py','audit_dynamic.py','export_dynamic_map.py','verify_raw_ranges.py','verify_final.py']:
 subprocess.run([sys.executable,script],check=True)
subprocess.run(['node','verify-dynamic.cjs'],cwd=Path('site'),check=True)
