# Published comfort rules and defaults

Applies to Sites v27, source `53b536eddf21e04382027f81cc5174365c3b5ee4`, published October 14, 2026 (São Paulo), at https://comfy.lfsadigital.com/ . This GitHub repository is the code backup; it is not the website host.

## Fresh visits and Weather Reset

| Setting | Default |
|---|---|
| Main measure | Comfort score, 0–10 |
| Daily high | 18–28°C, inclusive |
| Daily low | **Enabled**, 14–28°C, inclusive |
| Comfortable rain limit | ≤4 mm per UTC day |
| Rain loss, >4–10 mm | 0.5 point |
| Rain loss, >10–20 mm | 1 point |
| Rain loss, >20 mm | 1.5 points |
| Sunshine | **Disabled**; initial minimum 6 h/day when enabled |
| Climate Highlights | Enabled; score ≥7 **and** ≥120 comfortable days/year |
| Population | At least 50,000 catalog residents |
| Period | 2020–2025, all six years |

Explicit URL settings override defaults. `lows=0` preserves a disabled low rule across reloads. Weather Reset restores the weather defaults; it does not reset the separate city filters or Highlights.

## Daily calculation

For a daily value `T` and inclusive interval `[L,U]`:

```text
deviation(T,L,U) = max(L − T, 0, T − U)
high_deviation = deviation(Tmax, high_min, high_max)
low_deviation  = deviation(Tmin, low_min, low_max) if lows enabled, otherwise 0
temperature_loss = 0.5 × max(high_deviation, low_deviation)
sunshine_loss = 0.5 × max(sun_min − sunshine_hours, 0) if enabled, otherwise 0
daily_score = max(0, 10 − temperature_loss − rain_loss − sunshine_loss)
```

High and low losses are **not added**. Rain and optional sunshine losses are added to the greater temperature loss. The zero floor is applied to each daily score before averaging.

With default rules, high 16°C and low 10°C give deviations 2°C and 4°C: temperature loss is 2 points, not 3. With rain ≤4 mm, the score is 8. High 33°C, low 24°C and 11 mm precipitation score 6.5 (2.5 heat loss + 1 rain loss).

A comfortable day must meet **every enabled daily limit**: high interval, low interval when enabled, precipitation ≤the shared rain limit, and sunshine minimum when enabled. Exactly 4 mm qualifies under the default limit. Missing data is not interpreted as passing.

## Period score and days/year

2020–2025 has 2,192 calendar days. We score each matched day and then average those daily scores. We do not score the six-year mean temperature.

```text
period_score = sum(valid daily scores) / matched valid days
comfortable_days_per_year = comfortable matched days / matched valid days
                            × calendar days in selected period / years in period
```

With complete records, the six-year day measure is the qualifying-day total divided by **6**, not by 2,192. For one year, it is the actual qualifying count. Missing records require at least 90% matched coverage in **every month**; eligible partial day counts are annualized estimates and are labeled. Optional disabled variables do not add a coverage requirement.

## Source and charts

World, Europe and USA use the same ERA5 cells, source and formulas. Native supplied resolution is 0.25°; the map samples exact cells every 0.5° (about 55 km north–south), without elevation downscaling. Values describe climate cells, not neighborhoods.

High and low are the maximum and minimum of the same 24 hourly 2 m temperatures over 00:00–23:00 UTC. Precipitation is the UTC daily total, including snow as water equivalent. Sunshine is estimated sunshine duration, not daylight duration. Models can differ from local station measurements, especially near coasts and mountains.

Monthly temperature charts also aggregate hourly ERA5 temperatures from the selected cell. Open-Meteo's daily-extreme fields are not interchangeable with reductions of its hourly series; see the historical daily-low audit. API display rounding can cause small differences from the map archive.

The high chart shades its selected interval. The low chart shades its interval only while enabled. Sunshine shades its minimum only when enabled. Monthly averages inside a band do **not** prove that every daily value qualifies. The precipitation chart is mm/month: the daily rain limit is not drawn as a monthly threshold. Humidity and warm-night charts are informational; they add no score penalty.

## Interface and export

Highlights colors climate areas passing both aggregate thresholds. Climate colors do not encode homicide or budget. City markers highlight verified matches; missing optional city data stays in the ranking and is labeled. Region tabs change the camera and ranking region, not the underlying climate value.

Weather edits require Apply. The footer stays outside the scrolling fields and reserves the actual immersive map-navigation height. PNG is disabled while weather edits are pending or calculation is running. Export captures the current camera, applied filters, rule ranges and credits.

## Implementation and verification

- `dist/app.js` → `uiDefaults()` is the current UI-default authority.
- `dist/assets/metadata.json` → original archive baseline (18–26°C, rain 1 mm), retained for old precomputed maps; **not the live UI defaults**.
- `dist/assets/defaults-v2.json` → remote compact maps for current high/low settings, with/without 6h sunshine.
- `dist/daily-temperature-core.js` → max-of-high/low daily calculation.
- `dist/climate-worker.js` → custom-range streaming, bounded memory and no-store daily responses.
- `world/minimum/` → remote processing and preset generation. Raw arrays stay on remote runners; do not run bulk imports on a personal Mac.

The live v27 check passed fresh defaults, all four standard high/low/sun combinations, Reset, low chart band, absent sunshine band when off, PNG and zero page errors. Explicit `lows=0` also survived live reload. Earlier validation covered 514,194 cell/year comparisons with the original off-state maps; the new default preset build checked 2,056,776 cell/year/mode results. See `REQUESTED-DEFAULTS-CHECK.json`, `WEATHER-APPLY-CHECK.json`, `minimum-javascript-audit.json` and the operations log for scope. Personal preference score; not a validated physiological comfort index.
