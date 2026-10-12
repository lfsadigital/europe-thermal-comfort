"""Rebuild the temperature base, paired rain assets, then verify the browser engine."""
import subprocess,sys
from pathlib import Path
steps=[['build_comfort.py'],['country_table.py'],['export_site.py','--temperature-only'],['audit_dynamic.py'],['export_dynamic_map.py'],['verify_raw_ranges.py'],['verify_final.py'],['extend_temperature.py'],['rain_data.py'],['export_site.py'],['verify_rain_ranges.py'],['verify_2025.py']]
for step in steps:subprocess.run([sys.executable,*step],check=True)
subprocess.run(['node','verify-rain.cjs'],cwd=Path('site'),check=True)
