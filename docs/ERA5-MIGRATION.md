# ERA5 migration

Luiz approved ERA5 for the existing temperature/precipitation dataset and explicitly approved publication after tests. Sunshine is not included in this release.

## Data and calculation

- Source: Copernicus ERA5 / ECMWF, distributed through Open-Meteo AWS Open Data. No ERA5-Land, IFS, NOAA or E-OBS fallback.
- Period: 2020–2025, 2,192 UTC days. Daily temperature is the maximum of 24 hourly 2 m temperatures. Daily precipitation is the sum of 24 hourly precipitation values, including snow water equivalent.
- Supplied source grid: 0.25°. Existing map sampling: exact source points every 0.5°, approximately 55 km north–south. No spatial interpolation or elevation downscaling in the calculations. ERA5 values are model estimates informed by observations, not local station measurements.
- Original hourly temperature precision: 0.05°C. No API display rounding is applied before scoring. Rain thresholds keep the source float32 comparison precision.
- Defaults unchanged: 18–26°C inclusive; precipitation ≤1 mm for comfortable days and no rain penalty; >1–10 mm loses 0.5, >10–20 loses 1, >20 loses 1.5.
- Daily score: max(0, 10 − 0.5 × degrees outside the temperature range − rain penalty). Floor zero applies to each day before averaging.
- Average score: daily score sum / valid paired days. Comfortable days/year: qualifying days / valid paired days × calendar days / years. With complete records this is the actual count / years.
- Missing hours propagate to missing daily values. At least 90% paired daily coverage in every month is required; no missing-day imputation.
- World, Europe and USA share the same arrays, cell selection, controls and engine. Tabs change the geographic viewport only. Colors, design, city/state search, details and MapLibre navigation are preserved.

## Import and provenance

`import_era5_local.py` downloads public OM archive files with verified byte ranges, Content-Range, lengths and ETag pinning. The large 2020/2021 objects were imported one at a time. `import_era5_parallel.py` processes at most four small 21-day source objects concurrently. Temporary source objects are deleted after data flush and checkpoint. The transfer inventory totals about 35.63 GB; the two retained daily arrays total about 1.5 GB. All 47,808 file/variable/row tasks completed.

Initial remote row-by-row ingestion was stopped because it was slow. Resumable completion checkpoints prevent partial source records from being published. `era5-import.json` records the full source object inventory and ETags. `era5-data-manifest.json` records SHA-256 hashes of the release data.

`build_era5_statistics.py` builds default map binaries and exact format-4 joint statistics from those daily arrays. The production JavaScript calculation engine was not changed.

## Verified local checks

| Check | Result |
|---|---|
| All map cells | 85,699 cells, each with all 2,192 paired days |
| Raw data range | Tmax −77.75 to 53.5°C; precipitation 0 to 442.8 mm/day |
| All defaults, all periods | 85,699 cells × 7 periods; score and comfortable-day counts match original daily calculations; maximum score difference zero before Float32 map storage |
| Independent scalar vs production engine | 1,134 comparisons across all 7 periods, including custom rain/temperature and zero-floor cases; maximum difference zero |
| Bulk vs API | All 12 reference locations match within API temperature rounding; maximum temperature difference 0.050002°C and precipitation float difference 0.000003052 mm |
| Browser values across tabs | 126 metric comparisons, default/custom and six-year/2025 views; pass |
| Search and ranking | 11 ranking checks; city/state searches, accents, country, keyboard, missing data, custom rules and mobile checks; pass |
| Navigation | Wheel, drag/inertia, keyboard, pinch, zoom anchor, street-level labels/roads, US state labels and crosshair cursor; pass |
| PNGs | All six exports generated at 2400 × 1800; period, defaults and ERA5 source included |
| Preserved components | Ten calculation, tile rendering, geometry, design, discovery, logo and bundled MapLibre files byte-identical |

Evidence is in `validation/`. The browser run reported no JavaScript errors or HTTP failures. Initial local readiness was 2.325 seconds; measured tab switches were 52–84 ms. These are local test measurements, not production performance guarantees.

The earlier API comparison used temperatures rounded to one decimal. At the 12 reference locations, original bulk precision changes the final six-year score by at most 0.01123 points and comfortable days/year by at most 1.334. The final site is checked against original data. See `ERA5-REFERENCE-CITIES.md`.

## Delivery and rollback

New ERA5 statistics are served from `https://comfy-days-climate-era5.lfsalmeida92.workers.dev/era5-v1/`. Default maps and interface are packaged through Sites for `https://comfy.lfsadigital.com`. Browser asset version 12 prevents cached NOAA defaults/metadata/worker code from being mixed with ERA5.

All 294 dynamic files must pass live size/hash and CORS checks before the Site is published. Public-site verification follows publication. Deployment IDs and final status are recorded in the local operations log.

Original NOAA daily arrays, the `comfy-days-climate-v5` worker and the previous Sites version 11 are retained for rollback. This migration makes no DNS changes and does not modify the main GitHub Pages site.

## Known limits

ERA5 is selected for consistent global sourcing; it is not claimed to be more accurate at every location. The coastal Miami discrepancy against airport stations was measured and reviewed before Luiz chose ERA5. See `MIAMI-SOURCE-VALIDATION.md`. Climate resolution remains 0.5° sampling even when the vector basemap is zoomed to street level. Smooth map colors are visual interpolation; numeric readouts use original sampled cells.
