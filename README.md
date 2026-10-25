# Comfy Days

Live worldwide site: https://comfy.lfsadigital.com/

**Current worldwide ERA5 source is in [world/](world/).** The Europe-only code below is an archived implementation, with a different source and historical scoring formula. It does not describe the live site.

Current live defaults: minimum **≥14°C**, maximum **≤30°C**, rain **≤4 mm/day**, sunshine **off**, AQI **off**. Highlights: **≥7 points and ≥120 days/year**. [Rules and examples](world/site/docs/COMFORT-RULES.md).

The live interface is hosted by Sites and climate statistics by Cloudflare. GitHub stores this public code backup; it does not host the current Comfy Days site.

## Archived Europe-only implementation

[Open the archived website](https://conforto-termico-europa.lfsadigital.chatgpt.site)

A real Natural Earth map of Europe with two measures based on daily maximum
temperatures and daily rain totals from 2020–2025. Choose integer temperature limits from −30 to 50 °C.
The default interval is 18–26 °C. Both endpoints are included.

## Run locally

This repository contains code only. Derived climate data and maps are not
redistributed here. For local development, download the published assets
from the website (non-commercial research/education terms still apply):

```sh
python3 download_site_assets.py
```

Or rebuild from the official sources (see below). Then run:

```sh
python3 -m http.server 8000 --directory site/dist
```

Open http://localhost:8000. Use a recent browser with Web Workers and gzip
DecompressionStream. Calculations run locally without weather API calls.
The URL preserves the interval, year and view for sharing. First use of a
custom interval loads about 20 MB for six years or 12–13 MB for one year.

## Calculation

For each daily maximum T, lower limit L and upper limit U:

`score = 100 - max(L - T, 0) - max(T - U, 0) - (rain > 1 mm ? 1 : 0)`

The period score averages **2,192 daily scores**, not the mean temperature.
Comfortable days count `L <= T <= U AND rain <= 1 mm`. Exactly 1 mm qualifies.
The rain penalty is one extra point, independent of the temperature penalty.
For example, 17 °C with 2 mm rain scores 98 for an 18–26 °C interval. For 2020–2025 divide the total by
**six years**, not by 2,192 days. Individual years show actual counts.
Leap years 2020 and 2024 each contain 366 days.

Sparse histograms store joint dry-day temperature counts, wet-day counts,
paired-record validity, original fractional temperature sums and exact
integer-boundary counts. They are sufficient for integer endpoints without
storing all daily series in the browser. E-OBS sums use a lossless int16 residual around each bucket midpoint,
reconstructed with the original NetCDF scale; NOAA sums remain float64. Browser arithmetic uses float64.

## Data and map

E-OBS v33.0e ensemble daily Tmax and rainfall (TX/RR), native 0.1° (roughly 11 km north–south),
plus NOAA CPC daily Tmax and Global Unified Precipitation, native 0.5°, in eastern gaps. Compute score and day
counts on the original NOAA grid **before** bilinear interpolation. Do not
interpolate temperatures first. Cells need all paired daily records. Six-year coverage:
110,182 of 117,065 land cells (94.12%). Missing rain is never treated as dry. Source provenance remains visible.

E-OBS station report days and NOAA 06–06 UTC days differ. These estimates are
not street-level observations. Wind, humidity and nighttime temperatures
are excluded. Precipitation is aligned by its recorded date; source reporting
windows may differ. This is a preference score, not a physiological index.

Natural Earth 1:10 million borders and coasts; Lambert Conformal projection.
Fixed palette across ranges and years: score 76–98; days 0–150+.
Out-of-scale values use the endpoint color; queries show the actual number.
Coastal display may use the nearest complete cell within 0.2°.

## Rebuild and verify

```sh
cd site
node verify-dynamic.cjs
```

Run this after rebuilding. It checks all valid cells in seven periods against the served data and six custom
intervals against independent raw E-OBS and NOAA temperature/rain references.

Rebuild derived assets (several GB of source downloads on the first run):

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python rebuild_site.py
```

`rain_data.py` checks all 2,192 paired daily fields, inclusive boundaries,
additive penalties, annualization and leap-day weighting. `verify-rain.cjs` checks
all 14 served numeric grids and 84 raw-data custom-range references.
The report is `site/dist/assets/rain-audit.json`.
`verify_rain_ranges.py` recreates independent references even when caches are reused.
`verify_2025.py` independently recalculates all 365 paired 2025 daily fields,
checks the native NOAA grid, the six-year denominators and unchanged 2020–2024
annual values. `period_config.py` defines the published period and default limits.

Contributions: [CONTRIBUTING.md](CONTRIBUTING.md). Code: MIT.
**Climate data are not MIT-licensed.** E-OBS is restricted to non-commercial
research and education. See [DATA_LICENSE.md](DATA_LICENSE.md) for attribution
and source policies.
