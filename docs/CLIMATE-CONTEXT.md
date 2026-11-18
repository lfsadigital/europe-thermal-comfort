# Additional climate and urban context — local preview

Implemented 2026-10-14. Publication and GitHub update explicitly authorized by Luiz; deployment verification recorded separately.

## Scope

Humidity, daily minima / warm nights and urban density are informational context. No weather scores, qualifying-day rules, climate map arrays, city eligibility or ranking calculations change. Existing monthly values were compared with the prior implementation and remained identical for synthetic complete records with sunshine on/off.

## Monthly climate

Same Open-Meteo archive endpoint and ERA5 model, exact selected climate cell, `elevation=nan`, `cell_selection=nearest`, UTC dates, 2020–2025; selected year is filtered before aggregation.

Additional daily fields: `temperature_2m_min` (°C), `relative_humidity_2m_mean` (%). API date arrays and all units are checked. Monthly low and humidity use the mean of valid daily records. At least 90% of each year's month must be valid; otherwise that monthly metric is missing. A missing humidity/minimum does not suppress the other existing metrics.

Warm nights is explicitly a proxy: UTC days with daily minimum >=20°C, including equality. It does not isolate local nighttime hours. Monthly count = qualifying valid minima / all valid minima × calendar days / selected years. With complete records this is exact count / years; otherwise it is scaled. No claim of simultaneous humidity at the daily high. Definition is in a keyboard/tap information disclosure.

Six charts and an eight-column table; new metrics do not affect either comfort output. Requests happen only after location selection. Existing 12-cell worker memory cache and cancellation remain. No new paid API.

## Urban density

Source: European Commission JRC, GHSL GHS-UCDB R2024A V1.2 GENERAL_CHARACTERISTICS thematic package, reference year 2025 estimates.

Source directory:
https://jeodpp.jrc.ec.europa.eu/ftp/jrc-opendata/GHSL/GHS_UCDB_GLOBE_R2024A/GHS_UCDB_THEME_GLOBE_R2024A/GHS_UCDB_THEME_GENERAL_CHARACTERISTICS_GLOBE_R2024A/V1-2/

Exact file: GHS_UCDB_THEME_GENERAL_CHARACTERISTICS_GLOBE_R2024A_V1_2.zip (about 6.6 MiB).
SHA256: bc879d82320504f89df2041b7936221c8239cd808abe93980493aed062b4f3d6
The directory's copyright.txt explicitly licenses the dataset CC BY 4.0. Credit European Union / JRC, indicate transformations; no endorsement. Only original GHSL polygon geometry and urban-centre attributes are used. GADM country names/boundaries and other thematic third-party fields are not redistributed.

Density = GC_POP_TOT_2025 / GC_UCA_KM2_2025 (estimated residents per km² of the entire GHSL urban centre). This is not municipality density, neighbourhood density, or density at the climate cell. The UI states the urban-centre name and 2025 year independently of weather year.

`city-data/import_urban_density.py` projects GeoNames coordinates into EPSG:54009 (Mollweide, radius 6378137), parses actual source multipolygons including holes, and performs point-in-polygon matching. No nearest or name-only fallback. Multiple matches would remain Unknown. Geography applies to the listed city point, not an arbitrary map click or the municipal boundary.

Coverage with current 161,031-place catalogue: 21,642 matches; 139,389 Unknown; zero ambiguous; 11,422 urban centres indexed. The urban-centre dataset does not cover every small town or rural location.

Output `dist/assets/urban-density.json.gz`: 296,807 bytes, lazy-loaded on the first selected location. No backend, KV or Worker execution added. Source ZIP and extracted GeoPackage were temporary, not shipped; the global 1.7 GB package was not downloaded.

Rebuild:
`python3 city-data/import_urban_density.py /path/to/source.zip site/dist/assets/places.json.gz site/dist/assets/urban-density.json.gz`

## Verification

- `node city-data/climate-context-check.cjs`: old monthly outputs identical; inclusive minimum 20°C; zero humidity; missing records; all derived density ratios checked.
- Parser/projection tests: origin, polygon interior, hole and exterior.
- Real Miami ERA5 API response: 2,192 daily records, expected units and cell; all monthly extra metrics available. January six-year mean: minimum 18.54785°C, humidity 73.5%, warm-night proxy 12.83333 days/month.
- `node city-data/climate-context-browser.cjs`: browser uses a small real Miami response fixture from `/private/tmp/comfy-context-miami.json`; six charts, 12 months, eight columns, series/heatmaps, desktop/mobile, no viewport overflow, Unknown density, no JS errors.
- Captures: `share/context-charts-desktop.png`, `share/context-charts-mobile.png`.
- Impeccable detector ran with degraded parser support, reported incumbent chart colors #167aaf and #967300; these were retained from the existing chart identity. Computed contrast was not covered by that detector. Screenshots inspected separately.
- Publication and GitHub update authorized on the next user turn. See CLIMATE-CONTEXT-LIVE.json and release receipt for completed production checks.
