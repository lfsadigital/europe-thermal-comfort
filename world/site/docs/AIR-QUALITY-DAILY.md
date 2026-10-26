# Optional daily AQI in comfort

AQI is a Weather scoring rule, off by default, like Sunshine. It changes Confi10, Comfy Days, continuous map colors, climate highlights and the ranking through the shared calculation. It no longer gates city eligibility by a historical median or hides climate shading. Population, homicide and budget remain city filters.

## Agreed calculation

For each UTC date, require at least 22 valid, nonnegative hourly US AQI values. Calculate the arithmetic mean of each complete, contiguous 3-hour window contained within that day; take the largest mean. Do not bridge missing hours or midnight. If fewer than 22 valid hours exist, that date’s AQI is unknown.

The default user limit is 100, inclusive. Other provided limits are 50, 150, 200, 300 and 500. The personal comfort penalty is `max(0, (dailyAQI - limit) / 50)`. This weight and aggregation are Comfy Days preference rules, not an official daily AQI health definition.

```text
dailyScore = max(0, 10 - temperatureLoss - rainLoss
                    - optionalSunshineLoss - optionalAQILoss)
Confi10 = mean(dailyScore across valid matched weather dates)
ComfyDay = all enabled daily weather limits pass
           AND (AQI is disabled OR unknown OR dailyAQI <= limit)
```

Temperature retains the larger high/low deviation, at 0.5 point/°C. Rain and sunshine retain the published rules. The score’s zero floor is applied on each date before averaging. Comfortable-day frequencies retain calendar annualization and the weather coverage requirement of 90% matched days in every month. AQI availability does not reduce weather denominators or exclude places.

Unknown AQI adds zero penalty and leaves that date’s weather-only comfortable status intact. Counts expose how many matched weather dates considered AQI. Unknown dates are never described as verified clean air. Mixed coverage is disclosed in the map status, point details, ranking and selected AQI history. Failed archives cannot enter the immutable archive cache or be mistaken for valid zero AQI.

## Common period

The map supports 2023–2025 pooled and individual 2023, 2024 or 2025 with AQI enabled. Applying AQI in an incompatible period switches all weather metrics to 2023–2025, with advance notice in Weather. Incompatible period choices are disabled while AQI is applied. Disabling AQI retains the chosen common period for comparison. Old `aqiyear` links migrate to the single global period and are rewritten canonically.

## Source and data preparation

CAMS global atmospheric composition forecasts, ECMWF, distributed by Open-Meteo AWS Open Data, CC BY 4.0. These are regional modeled estimates on a 0.4° grid, not monitoring-station or minute measurements. Each existing ERA5 0.5° climate-cell centre is explicitly matched to its nearest CAMS grid point, with longitude wrap.

The remote build downloads pinned public concentration objects for PM2.5, PM10, NO2, O3, SO2 and CO. Hourly US AQI follows Open-Meteo’s pollutant-specific preceding-hour windows, units and index breakpoints, checked against upstream commit `03d62919c419f1eccad8dcbbcf7f92a2dd7069b4`. A 24-hour source lookback supplies the first date’s pollutant averages. Native S3 hourly estimates are used; no hourly city queries are extrapolated across the map. Missing pollutant data stays unknown.

The largest daily 3-hour mean is packed as Float64 without display rounding, in 2,048-node annual chunks with UTC/year/grid headers and SHA-256 checksums. Leap year 2024 has 366 days. The source inventory, file hashes, node-grid hash, method and independent API comparisons accompany an immutable prerelease data archive. Only remote runners perform bulk ingestion; no raw global archives enter Git or a visitor’s browser.

The public API rounds hourly AQI to integers. Independent comparisons allow at most 0.501 AQI difference per hour and daily value for that rounding, rather than treating the displayed integer as the original precision. Validation covers Lisbon, New Delhi and Sydney in winter and summer; publication requires those checks to pass.

## Delivery and UI

The existing same-origin climate service reads the small annual daily AQI chunks server-side, verifies hashes and date/grid alignment, then calculates the same daily formula used in tests. It uses explicitly named caches; compressed verified archive responses may persist, never request-owned promises or raw arrays. Compact map responses add AQI-considered date counts. A dataset identity is part of cache isolation.

Weather uses the existing checkbox, select, draft/Apply/Reset, focus and summary-chip patterns. The selected-point history uses the same archive and map period, reporting daily coverage and a folded monthly table. Monthly weather charts also use the common period. PNG captures the recalculated map, applied rules and missing-data treatment. LFSA styling and the established visual authority remain intact.

## Verification

- `node world/air-quality/daily-check.cjs`: isolated/sustained spikes, contiguous windows, 22-hour minimum, thresholds/zero, score floor, missing-date fallback and 10,000 exact off-state comparisons with the published v36 engine.
- `node world/air-quality/archive-check.mjs`: checksums/cache/corruption, common periods, leap weighting, per-date fallback, binary coverage and monthly point summaries.
- `node world/query-service/check.mjs`: original service behavior, canonical rules, failures, coverage and named-cache concurrency.
- `node world/air-quality/daily-browser-check.mjs`: actual query engine/browser with synthetic daily archives at 1440/768/390/320px, draft/apply/reset/URL, changed continuous field, ranking, missing-source fallback, restored off values, shared period, cancellation, PNG, 44px controls and no overflow/page errors.

Fixture screenshots are synthetic-source QA and cannot establish real global data coverage. Native deployment and actual real-source verification are recorded separately after successful ingestion; this source document alone is not a publication receipt.

## Validated global archive

[Run 40391731987](https://github.com/lfsadigital/europe-thermal-comfort/actions/runs/40391731987) passed all six real January/July comparisons for Lisbon, New Delhi and Sydney. Dataset `cams-global-max3h-425950138cae91b1` covers all 85,699 climate nodes across 1,096 calendar dates, with 93,921,747 / 93,926,104 valid daily AQI values (99.99536%). [Data release and full source audit](https://github.com/lfsadigital/europe-thermal-comfort/releases/tag/comfy-aqi-daily-max3h-v1). The initially completed import lost its final validation to an API timeout; the replacement saved a durable checkpoint and successfully resumed it, including retries for another transient source timeout. These data checks establish archive readiness; real deployed-site checks are recorded separately.

## Published and verified

Published as Sites v37 at [comfy.lfsadigital.com](https://comfy.lfsadigital.com), source `58031c366f219f082e0057a8958630af8fe00e7e`. [Live verification](https://github.com/lfsadigital/europe-thermal-comfort/actions/runs/40393231689) passed with real data and no interception: independent three-year calculations agreed with the deployed API and browser at all three reference locations; all 85,699 climate cells considered AQI; the raster remained visible; the ranking used integrated values; disabling AQI restored weather-only results; no page errors occurred. The tested settings were 11–30°C, rain ≤4mm, sunshine ≥6h and daily AQI ≤100. Receipt and reference values are in `AQI-DAILY-RELEASE.json`.
