# Optional historical air quality

The optional Weather air-quality filter limits city points and Top 10 results by historical median US AQI. It starts off on a clean URL. Visitors choose a maximum of 50, 100 (default), 150, 200, 300, or 500 and either 2023, 2024, 2025 (default), or pooled 2023–2025, independently of the weather period. The limit is inclusive: median 100 passes maximum 100. All regions use the same US AQI scale and CAMS global source. Climate scores, comfortable-day counts, source arrays, and climate-rule values remain unchanged.

## Source, terms, and limits

The browser directly requests `us_aqi` and `pm2_5` from the public [Open-Meteo Air Quality API](https://open-meteo.com/en/docs/air-quality-api), with `domains=cams_global`, full calendar-year dates, and `timezone=UTC`. One request covers the entire chosen period; annual splits are validated before aggregation. There is no AQI proxy endpoint. The underlying source is [CAMS global atmospheric composition forecasts, ECMWF](https://ads.atmosphere.copernicus.eu/datasets/cams-global-atmospheric-composition-forecasts?tab=overview). Global history begins in August 2022; offering complete years 2023–2025 gives every region the same period choices.

These are archived model forecasts, approximately 0.4° (~45 km), with 3-hourly source output interpolated by the provider to hourly values. They are regional estimates for the requested point, not city monitoring-station observations, an ERA5 climate cell, or current conditions. Source model versions can change over time. The displayed **Provider-returned coordinates** are response metadata and do not guarantee the precise pollutant grid-cell centre.

Data distributed by Open-Meteo are attributed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); Comfy Days performs the aggregations. Providers do not endorse this site. The API service has separate [terms](https://open-meteo.com/en/terms): its free endpoint is for non-commercial use and is subject to usage limits. A data license does not remove those service restrictions. This implementation adds no API key, subscription, billing account, or paid service. Commercial use requires checking and meeting the provider's applicable service terms.

## Calculation and availability

The provider supplies hourly US AQI as the highest pollutant sub-index, using pollutant-specific averaging windows. Comfy Days does not derive AQI from mean PM2.5. The headline measures are the median of available hourly AQI and the arithmetic mean of available hourly PM2.5, in µg/m³. The pooled view uses all available hours across the three years; it does not average three yearly summaries.

Category shares classify each unrounded hourly AQI value, then divide category hours by available AQI hours:

| US AQI category | Hourly range |
| --- | --- |
| Good | 0–50 |
| Moderate | >50–100 |
| Unhealthy for sensitive groups | >100–150 |
| Unhealthy | >150–200 |
| Very unhealthy | >200–300 |
| Hazardous | >300 |

Values above 500 remain hazardous. These are [US AQI health category names](https://www.airnow.gov/aqi/aqi-basics/), not a guarantee of individual safety. Shares describe available hours, not days, and do not measure simultaneous comfortable weather.

AQI and PM2.5 availability are evaluated independently. Each metric requires at least 90% valid hours in **every month of every selected year**. A deficient month in one year cannot be hidden by pooling it with two complete years. Overall summaries require all selected year-months to pass; each monthly table row requires that calendar month to pass in each selected year. Failed metrics display “Not available”; valid zero values remain valid and missing values are never filled.

Expected denominators follow UTC calendar hours, including leap day: 8,760 in 2023, 8,784 in 2024, 8,760 in 2025, and 26,304 pooled. The interface shows available/expected counts for both metrics overall and in the monthly table. Payload validation checks coordinates, UTC offset, units, complete ordered hourly timestamps, array lengths, and nonnegative finite numeric values or explicit nulls.

## Implementation and interaction

- [air-quality-core.js](../dist/air-quality-core.js) splits the combined response with `fromRange`, validates each complete annual time axis, and aggregates records without weather dependencies.
- [air-quality-filter.js](../dist/air-quality-filter.js) progressively verifies candidates, excludes unverified or ineligible AQI, bounds client work to two concurrent jobs and summary memory to 2,000 entries, and cancels stale generations. The request timeout is 145 seconds. Source failures and timeouts expose Retry rather than silently completing a ranking.
- Source starts are spaced by at least 4,500ms multiplied by the number of requested years: 4.5 seconds for one year and 13.5 seconds for pooled history. HTTP 429 retries honor `Retry-After` seconds or HTTP dates, with a 60-second fallback when unavailable, and at most three attempts. Quota waits are cancellable and display a source-wait status. The free API and this pacing can make verification gradual; neither guarantees immediate completion or prevents all source limits.
- [air-quality.js](../dist/air-quality.js) owns draft/applied settings and selected-point history, including the folded monthly table. Its separate selected-point cache holds up to 12 summaries.
- [index.html](../dist/index.html), [air-quality.css](../dist/air-quality.css), and [app.js](../dist/app.js) provide controls, selection, and URLs. `aqi=1` enables filtering; `aqmax` stores the applied maximum; `aqiyear=2023` or `2024` selects those years and `aqiyear=mean` selects pooled history. The default 2025 period omits `aqiyear`. The original climate and monthly backend routes are unchanged; the AQI proxy service and route have been removed. There is no persistent or global AQI archive.

When active, AQI hides the climate raster and shows only verified qualifying city points on a neutral basemap. Unknown AQI, insufficient AQI coverage, and failed source checks do not qualify. PM2.5 remains independent context and does not decide threshold eligibility. This is progressive city-point verification, not a global AQI raster archive or comprehensive monitoring-station coverage.

[discovery.js](../dist/discovery.js) keeps the climate metric sort order and verifies leading candidates until ten qualifying results are found or the candidate list is exhausted. With Avoid nearby duplicates enabled, these represent distinct climate cells; a failed city does not prevent another city in that cell from qualifying. The initial scan checks at most 40 candidates, with **Check next 40 ranking candidates** to continue. Incomplete scans and failures leave results provisional. [city-map.js](../dist/city-map.js) separately verifies visible candidates in batches of eight, with **Check more cities in this view**. Existing population, city, zoom, and climate-highlight limits still apply to visible points.

Disabling the AQI filter restores the original climate raster and ranking behavior. Reset also restores AQI off, maximum 100, and 2025 while resetting the other weather rules as usual. AQI-only Apply preserves climate array identities and does not recalculate climate. PNG export uses the current map canvas and includes the applied AQI limit, period, and verified-city-point context.

The existing [DESIGN.md](../DESIGN.md) remains the visual authority. This is an ordinary extension: the section inherits LFSA heading/body fonts and navy text, reuses white/pale surfaces and borders, and follows the existing 24px section rhythm. Compact 13/14px supporting text already exists in incumbent styles. Category dots have a specific data meaning; labels and numeric ranges convey that meaning without color. Distribution bars use navy and leave the climate palette untouched.

The section preserves the Quiet Surface Rule through folded source methods and monthly values. Native web checkbox, select, disclosure, and table semantics support keyboard use. Controls have 44px minimum targets, visible focus treatment, responsive wrapping, and a focusable horizontal table scroller. No new visual system, design seed, or native platform conventions are introduced, and DESIGN.md is unchanged.

## Verification and evidence limits

Run from the repository root:

```sh
node world/air-quality/filter-check.cjs
node world/air-quality/browser-check.mjs
```

The browser check needs Playwright and Chromium (`CHROMIUM_PATH` can select the executable). It runs the real application, direct-source request path, and client aggregation against a synthetic provider. The pacing gate is disabled only for synthetic browser tests; production pacing remains active. These tests do not establish live global source coverage.

Updated unit checks passed combined-range annual validation, quota spacing, `Retry-After` seconds/date handling, cancellation, inclusive thresholds, missing/invalid exclusion, duplicate-cell representatives, and bounded provisional scans. Existing timeout/retry and review fixes remain covered. Original backend regression checks also passed. Historical core checks covered fractional AQI boundaries, values above 500, leap-year denominators, and exact 90% per-year monthly thresholds. Ranking and map integration intentionally apply AQI eligibility; climate calculations remain unchanged.

The updated direct-source fixture pipeline passed 1440, 768, 390, and 320px widths. Coverage includes inclusive maximum 100, relaxed maximum 500 restoring baseline Top 10, strict maximum 50, missing/error/retry/stale handling, URL restoration, Reset, continuation, 44px targets, no page overflow or page errors, and exact unchanged climate arrays and parameters. Screenshots under `.impeccable/review/` use synthetic QA data. The earlier proxy-backed synthetic suite also passed, but that was not evidence of successful live delivery.

Earlier real-source Lisbon and Miami 2025 probes passed in [run 40235210442](https://github.com/lfsadigital/europe-thermal-comfort/actions/runs/40235210442). Historical [run 40235522951](https://github.com/lfsadigital/europe-thermal-comfort/actions/runs/40235522951) passed all six Lisbon/Miami source probes across 2023–2025; both locations returned 26,304 / 26,304 AQI hours. These remain valid source-data probes. Actual v34 live proxy integration failed: logs confirmed Open-Meteo HTTP 429 on the shared Cloudflare origin. The replacement direct-browser path is pending publication and real-browser verification; no live filter success is claimed.

Independent review assessed both earlier material fixes as resolved and returned scoped “ship”; this does not certify live source delivery. The Impeccable detector reported seven inherited font-size advisories. These do not establish a new token system. Existing unrelated DESIGN.md drift and compact typography were not repaired or promoted into new design rules. The direct-path correction remains a candidate pending live verification.


## Weather controls

The single Filter by air quality checkbox, maximum selector, and independent period selector live directly after Sunshine in Weather. Changes remain drafts until Apply weather. The applied AQI limit and period appear in an editable Weather summary chip. The historical-results section retains its information and an Edit in Weather action, which opens Weather and focuses the checkbox. The form compares climate parameter values before recalculating, so an AQI-only Apply does not run a climate recalculation.

This extends existing Weather fieldsets, draft/Apply, summary chips, edit links, and visible loading/retry patterns. It retains LFSA typography, navy/muted text, and 44px AQI controls; DESIGN.md remains unchanged. The active map explicitly labels verified points and hidden climate shading so a sparse or provisional view cannot imply comprehensive clean-air coverage.


## Published filter verification

Sites v35 source7ea8fb2718037cab8b39d9dfbd8bf1e891ff44e0, deploymentappgdep_6ade89cead248191949c1ddeaa8339f1, succeeded2026-10-25T22:59:40Z. The [real public-browser CI](https://github.com/lfsadigital/europe-thermal-comfort/actions/runs/40242719997) passed after publication: real direct CAMS history, Lisbon median47 for2023–2025 qualifies at100, New Delhi median169 for2025 is excluded, ten Europe results all within100, verified map features, restored raster and exact Confi10 arrays on disabling, zero page errors. The earlier shared-origin v34 candidate failed source429 and was superseded; it is not counted as a successful live test. Details are in AIR-QUALITY-FILTER-RELEASE.json.
