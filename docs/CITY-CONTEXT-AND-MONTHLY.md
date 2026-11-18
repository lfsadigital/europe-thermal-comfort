> Update 2026-10-14: Nomads score/cost filters and the redistributed snapshot are removed. The description below is historical. See DATA-LICENSE-UPDATE.md for current source permissions.

# City filters and monthly climate charts

City context and monthly chart release. Publication identifiers and live verification are recorded in the operations log.

## Independent city filters

All optional filters start off. Weather and Cities panels sit over the map; Top 10 stays below. Map + list is the default effect; List only hides the optional city markers. Weather-colored markers match known limits, gray filled markers fail a known limit, and hollow navy markers lack optional data but remain eligible. A known failure takes priority over another unknown field. The climate raster and weather formula stay unchanged. Population eligibility still uses GeoNames populations and the selected minimum; no population is guessed. Optional missing Nomads, cost or homicide values are never treated as zero or as failed limits. Cost zero is unavailable; published homicide zero is valid.

Weather drafts require Apply and disable PNG export until applied. City filters update the ranking and markers without a climate download. Shared URLs retain the population threshold, filter values, scope/year and map effect. PNG export captures the current rendered map camera and markers, with the applied weather/city settings and source credits. It does not reset to the region preset.

- **Nomads score:** minimum on its native 0–5 scale. Their current composite already includes weather, cost and other factors; it is separate from our 2020–2025 comfort score.
- **Nomad cost:** maximum monthly USD estimate for the nomad lifestyle. This is not a universal average cost or guaranteed budget.
- **Homicide rate:** city/municipal or country/area mode, explicitly selected crime year and maximum rate. City mode defaults to 2024 and 5 when enabled. Coverage and geographic boundaries vary; missing local rates never use a country fallback. See CITY-HOMICIDE.md. Old shared URLs without homgeo retain country mode.

Nomads public `/api/cities` returned 1,375 cities. Matching uses the same country, normalized name and coordinates within 15 km. The validated snapshot matches 1,165 records to our catalog. No proximity-only fallback is used. Only city identity, coordinates, score and cost are retained; no member credentials or private data are used. Retrieval date and source links appear in the interface. No automatic refresh or API proxy has been deployed. The supplied public endpoint is explicitly for maps; other documented endpoints have 60 requests/hour/IP and no bulk-scraping support. Their endpoint returned duplicate CORS headers during inspection, so the tested interface uses the small dated snapshot rather than depending on direct browser access. Later refreshes require a reviewed refresh process.

Crime source: UNODC's July 2026 workbook, national sheet only. Filters select Victims of intentional homicide, Total dimension/category/sex/age, Rate per 100,000 population. Arrests, convictions, subgroups and regional/global estimates are excluded. Duplicate ISO/year records stop the import. 584 rates are present for 2020–2024. Mapped countries/areas by year: 2020 131; 2021 121; 2022 115; 2023 104; 2024 94. Missing 2025 is not filled. Separate England/Wales, Scotland and Northern Ireland records are not relabeled as an entire UK rate; partial central-Iraq records are not relabeled as Iraq. Read `homicide-import-audit.json` for provenance, source checksum and sample values.

Country context comes from the selected nearest listed city's country. It is not a determination of the jurisdiction of an arbitrary click. Place-name distance remains visible in the location panel.

## Monthly charts

Use Bklit examples as interaction inspiration, implemented with native SVG and a lightweight month grid inside the existing buildless app. No React or chart framework is added.

Only after inspecting a location, one small Open-Meteo Historical API request fetches 2,192 daily records for the original selected ERA5 climate-cell coordinates, 2020–2025. Parameters pin `models=era5`, `timezone=UTC`, `cell_selection=nearest`, `elevation=nan` (no elevation downscaling). Returned coordinates, units, UTC offset and every calendar date are verified; mismatches fail rather than silently using another cell or source. No Best Match or ERA5-Land substitution occurs.

Variables: `temperature_2m_max`, `temperature_2m_mean`, `precipitation_sum`, `sunshine_duration`. Chart values use API display precision. Existing weather scores retain original archive precision and are not recalculated from these API arrays. In Porto, daily API high-temperature rounding differs by up to about 0.05°C; precipitation differs only by floating-point precision. This small precision difference is disclosed in the chart.

- Temperature: solid line averages daily highs; dashed line averages daily means. The selected daily-high comfort band is shaded in line mode. A monthly average within that band does not mean every day qualifies.
- Precipitation: sum of daily precipitation per calendar month; in the six-year view, average those six monthly totals. Includes snow water equivalent. A month with any missing precipitation records is shown as a gap rather than inventing a total.
- Sunshine: average daily sunshine seconds divided by 3,600, not daylight hours. Temperature and sunshine require at least 90% observations in each corresponding year/month; available daily values are weighted by their actual record counts.
- Heatmap: readable month/value tiles, with intensity relative to each chart's values, no numeric positional y-axis. The table retains daily means as well as highs. Line charts scroll horizontally on small screens rather than shrinking text.

Charts use a separate Web Worker. A new location cancels the previous request. Up to 12 small cell datasets are held in memory; no persistent cache is written. Region changes reuse the same selected cell. Year changes reuse the six-year cell request. API failure clears chart values and allows retry without disabling the weather map. The old rainfall bins preserve threshold decisions, so they are deliberately not used for monthly rainfall totals.

Snow already contributes to the weather score through total precipitation, measured as melted-water equivalent. There is no separate snowfall-depth, snow-cover or icy-surface rule.

## Sources and reproducible imports

- https://nomads.com/api — documented city-list endpoint for maps
- https://nomads.com/mcp — public access and score/cost fields
- https://nomads.com/faq/what-is-the-nomad-score-8335629 — score meaning and changing seasons
- https://nomads.com/faq/nomadscom-terms-of-service-privacy-policy-8279217 — link-back requirement
- https://data.unodc.org/datareport/hom-victim — official download and metadata
- https://open-meteo.com/en/docs/historical-weather-api — ERA5, variables, units and request controls
- https://bklit.com/docs/components/composed-chart
- https://bklit.com/docs/components/heatmap-chart
- https://bklit.com/docs/components/scatter-chart
- https://bklit.com/docs/utility/reference-area

Local importer code is in `world-comfort/city-data/import_nomads.py` and `import_homicide.py`. They retain only small derived city/country tables. The 7.8 MB UNODC input and 1.6 MB public Nomads response are temporary inputs, not added to Git history. No global weather archive is downloaded for this feature.
