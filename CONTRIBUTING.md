# Contributing

Issues and pull requests are welcome. Describe the problem and the proposed
change. For numerical changes, include an independently calculated example
and verify inclusive limits, leap days, annualization, missing values and
NOAA interpolation. Keep sources and native resolution visible to visitors.

Run the static site with `python3 -m http.server 8000 --directory site/dist`.
Run `cd site && node verify-dynamic.cjs` to check the browser calculation.
Rebuild the data with `python rebuild_site.py` after installing requirements.
Do not commit `.cache`, `.venv`, credentials, Sites identity or raw climate
archives. Preserve third-party attribution and data terms in DATA_LICENSE.md.
