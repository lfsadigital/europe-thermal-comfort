# Optional historical air quality

Air quality is separate location context below the climate map. It starts off on a clean URL and makes no air-quality request until enabled and a point is selected. Visitors can choose 2023, 2024, 2025, or the pooled 2023–2025 period independently of the weather period. All regions use the same US AQI scale and CAMS global source. Air quality does not change climate arrays, comfort scores, comfortable-day counts, rankings, map colors, weather controls, or PNG content.

## Source, terms, and limits

The browser requests `us_aqi` and `pm2_5` from the [Open-Meteo Air Quality API](https://open-meteo.com/en/docs/air-quality-api), with `domains=cams_global`, full calendar-year dates, and `timezone=UTC`. The underlying source is [CAMS global atmospheric composition forecasts, ECMWF](https://ads.atmosphere.copernicus.eu/datasets/cams-global-atmospheric-composition-forecasts?tab=overview). Global history begins in August 2022; offering complete years 2023–2025 gives every region the same period choices.

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

- [air-quality-core.js](../dist/air-quality-core.js) validates and aggregates records without weather dependencies.
- [air-quality.js](../dist/air-quality.js) loads selected-point data, renders summaries and the folded monthly table, and manages loading, failure, retry, and stale-request cancellation. Requests have a 45-second timeout per year. A bounded, in-memory cache retains up to 12 point/period summaries; no persistent air-quality archive is created.
- [index.html](../dist/index.html), [air-quality.css](../dist/air-quality.css), and [app.js](../dist/app.js) provide the optional section and selection/URL integration. `aqi=1` restores opt-in; `aqiyear=2023`, `2024`, or `2025` selects one year. The default pooled period omits `aqiyear`.

The existing [DESIGN.md](../DESIGN.md) remains the visual authority. This is an ordinary extension: the section inherits LFSA heading/body fonts and navy text, reuses white/pale surfaces and borders, and follows the existing 24px section rhythm. Compact 13/14px supporting text already exists in incumbent styles. Category dots have a specific data meaning; labels and numeric ranges convey that meaning without color. Distribution bars use navy and leave the climate palette untouched.

The section preserves the Quiet Surface Rule through folded source methods and monthly values. Native web checkbox, select, disclosure, and table semantics support keyboard use. Controls have 44px minimum targets, visible focus treatment, responsive wrapping, and a focusable horizontal table scroller. No new visual system, design seed, or native platform conventions are introduced, and DESIGN.md is unchanged.

## Verification and evidence limits

Run from the repository root:

```sh
node world/air-quality/check.cjs
node world/air-quality/browser-check.cjs
node world/air-quality/live-check.cjs
```

The browser check needs Playwright and Chromium (`CHROMIUM_PATH` can select the executable); the workflow installs its isolated dependency. The live check needs network access to the API host.

The core check passed category boundaries (including fractional AQI and values above 500), leap-year denominators, exact 90% monthly thresholds, missingness, independent PM2.5 coverage, malformed payload rejection, and comparison of the existing climate/ranking engine files against `origin/main`.

The real application browser check uses synthetic weather and hourly air-quality records. Verified cases include 1440, 768, 390, and 320px widths, no page overflow, keyboard interaction, 44px targets, unchanged climate arrays/parameters/rankings, opt-in requests, caching, request races, coverage failure, source errors, retry, URL reload, and invalid URL values. Computed heading, note, range, and metric-label text contrast passed 4.5:1; the suite reported no page errors. Screenshots under the repository's `.impeccable/review/` directory explicitly label synthetic QA data. Synthetic captures establish interface behavior, not real pollution values.

Real-source Lisbon and Miami 2025 probes passed in [GitHub Actions run 40235210442](https://github.com/lfsadigital/europe-thermal-comfort/actions/runs/40235210442). The expanded [run 40235522951](https://github.com/lfsadigital/europe-thermal-comfort/actions/runs/40235522951) passed deterministic checks, real Chrome integration at all four widths, and all six source probes for Lisbon and Miami across 2023–2025. Both locations returned 26,304 / 26,304 AQI hours. Direct access to the API host was blocked in the local execution environment, so real-source evidence comes from CI. The workflow is [air-quality-check.yml](../../../.github/workflows/air-quality-check.yml).

Independent finish review returned “ship” with no material findings. The local Impeccable detector reported 12 advisories (seven colors and five font steps), with no warnings or errors. These advisories do not establish a new token system. Existing unrelated DESIGN.md drift and inherited compact typography were not repaired or promoted into new design rules. This document records a reviewed candidate, not a production deployment or merge.
