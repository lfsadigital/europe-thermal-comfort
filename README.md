# Europe thermal comfort map

[Open the website](https://conforto-termico-europa.lfsadigital.chatgpt.site)

A real Natural Earth map of Europe with two measures based on daily maximum
temperatures from 2020–2024. Choose integer temperature limits from −30 to 50 °C.
The default interval is 20–25 °C. Both endpoints are included.

## Run locally

This repository contains code only. Derived climate data and maps are not
redistributed here. Rebuild them from the official sources first (see below).
Then run:

```sh
python3 -m http.server 8000 --directory site/dist
```

Open http://localhost:8000. Use a recent browser with Web Workers and gzip
DecompressionStream. Calculations run locally without weather API calls.
The URL preserves the interval, year and view for sharing. First use of a
custom interval loads about 13 MB for five years or 9–10 MB for one year.

## Calculation

For each daily maximum T, lower limit L and upper limit U:

`score = 100 - max(L - T, 0) - max(T - U, 0)`

The period score averages **1,827 daily scores**, not the mean temperature.
Comfortable days count `L <= T <= U`. For 2020–2024 divide the total by
**five years**, not by 1,827 days. Individual years show actual counts.
Leap years 2020 and 2024 each contain 366 days.

Sparse histograms store counts, original fractional temperature sums and exact
integer-boundary counts. They are sufficient for integer endpoints without
storing all daily series in the browser. E-OBS sums use a lossless int16 residual around each bucket midpoint,
reconstructed with the original NetCDF scale; NOAA sums remain float64. Browser arithmetic uses float64.

## Data and map

E-OBS v33.0e ensemble daily Tmax, native 0.1° (roughly 11 km north–south),
plus NOAA CPC daily Tmax, native 0.5°, in eastern gaps. Compute score and day
counts on the original NOAA grid **before** bilinear interpolation. Do not
interpolate temperatures first. Cells need all daily records. Coverage:
116,101 of 117,065 land cells (99.18%). Source provenance remains visible.

E-OBS station report days and NOAA 06–06 UTC days differ. These estimates are
not street-level observations. Rain, wind, humidity and nighttime temperatures
are excluded. This is a temperature preference score, not a physiological index.

Natural Earth 1:10 million borders and coasts; Lambert Conformal projection.
Fixed palette across ranges and years: score 76–98; days 0–150+.
Out-of-scale values use the endpoint color; queries show the actual number.
Coastal display may use the nearest complete cell within 0.2°.

## Rebuild and verify

```sh
cd site
node verify-dynamic.cjs
```

Run this after rebuilding. It checks all valid cells in six periods against the served data and five custom
intervals against independent raw NOAA references.

Rebuild derived assets (several GB of source downloads on the first run):

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python rebuild_site.py
```

`audit_dynamic.py` checks all 1,827 original daily fields, inclusive boundaries,
annualization, leap-day weighting and all 12 served numeric grids. The generated report
is `site/dist/assets/audit.json`. `verify_raw_ranges.py` creates independent
raw-data references for the browser engine.

Contributions: [CONTRIBUTING.md](CONTRIBUTING.md). Code: MIT.
**Climate data are not MIT-licensed.** E-OBS is restricted to non-commercial
research and education. See [DATA_LICENSE.md](DATA_LICENSE.md) for attribution
and source policies.
