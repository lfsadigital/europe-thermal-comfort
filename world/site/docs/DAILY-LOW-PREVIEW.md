> Historical preview report. Current published rules and defaults: [COMFORT-RULES.md](COMFORT-RULES.md). Statements below describe the earlier preview, not the current defaults.

# Optional daily lows — local preview

Production is unchanged. Publishing requires Luiz's approval after preview.

## Rule

Daily highs keep the default inclusive 18–26°C interval. Daily lows are optional, off by default, initially 12–22°C. Both bounds are editable.

For each day, compute the distance outside each active interval in °C. Temperature loss is 0.5 × the **greater** distance, not their sum. Add the existing rain loss and optional sunshine loss, then floor the daily score at zero. Average valid daily scores. A comfortable day must meet both active temperature intervals plus rain and optional sunshine limits. Missing low records never pass.

## Comparable temperature source

The existing maximum archive uses the maximum of 24 ERA5 hourly temperatures, 00:00–23:00 UTC, at the existing sampled cells. New minima use the minimum of those exact same records. Source object sizes and ETags are pinned to the published maximum import inventory.

Open-Meteo API daily extrema are not identical to reducing its hourly series. A six-year Porto check found a maximum 2.4°C minimum-temperature difference. Therefore independent validation uses API **hourly** temperatures over identical UTC windows, not its daily-extreme fields. Monthly charts now also reduce hourly temperatures for daily high, low and mean. API daily precipitation, sunshine and humidity remain their existing fields.

## Storage and scope

Processing occurs on GitHub Actions, branch `preview/daily-lows`. Raw arrays remain on the remote runner. Derived minima are in the preview GitHub release `comfy-minimum-preview-38659046289` (315,130,605 compressed bytes). No bulk climate download to the Mac and no new Cloudflare resources or KV operations.

The local preview relay keeps at most 16 MiB in memory and does not write these chunks to disk. Compact default maps are generated remotely to avoid scanning six years for the standard optional-low selection. Custom ranges still require daily data and can take longer.

## Verification so far

- 10,000 direct-reference formula cases passed, including missing values, inclusive bounds, temperature max-loss rule and daily zero floor.
- One-cell, real Miami fixture passed end-to-end worker calculation, optional sunshine, URL, default-off restoration, mobile overflow and PNG rule metadata. This fixture is a wiring test, not the new global source validation.
- Remote import passed independent 2,192-day comparisons for Porto, Miami, Nairobi and Oslo. Largest difference from API's rounded hourly values: 0.050001°C.
- Existing monthly/context checks passed.
- Scoped UI finish review passed after mobile target fixes; design notes are in DAILY-LOW-FILTER-DESIGN.md.
- Full global audit and real preview verification are recorded separately when complete. Do not claim they passed from this file alone.

## Completed global checks

Remote JavaScript audit run 38659938524 passed all 514,194 year/cells, including default-off comparison with SHA-256-pinned production maps. The real local preview passed World/Europe/USA equality at Porto, Miami, Nairobi and Oslo; default-off arrays restored exactly; PNG export passed. Evidence: `minimum-javascript-audit.json` and `DAILY-LOW-GLOBAL-CHECK.json`. Optional low defaults remain off; 12–22°C applies only when enabled. Local preview: http://127.0.0.1:8777/. Production remains unchanged.

A real custom 14–22°C low interval for 2025 also passed through the full browser worker and remote relay, with 365 paired Miami records, no browser errors, score 8.5110273923 and 68 comfortable days. Evidence: DAILY-LOW-CUSTOM-CHECK.json. This custom one-year recalculation took about 45 seconds on this test connection; custom six-year runs can take longer. No bulk chunks were written to local disk.
