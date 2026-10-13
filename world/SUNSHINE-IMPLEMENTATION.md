# Optional sunshine rules — accepted specification

Luiz selected this rule on 2026-10-12. Status: implemented, tested and published as Sites v14 at https://comfy.lfsadigital.com/ on 2026-10-13 UTC.

- Sunshine is hours of sunshine, not daylight hours. Use explicit ERA5, UTC days, 2020–2025, and the same source coordinates and sampling policy as temperature and rain.
- Enabled default: minimum 6 hours/day, no upper limit. This is a user preference, not a validated physiological comfort threshold.
- Disabled by default. Disabled calculations and existing data-coverage rules must remain unchanged.
- When enabled, let H be the selected minimum hours per day and S be daily sunshine hours. Additional penalty = 0.5 × max(0, H − S).
- Apply the zero floor after adding temperature, rainfall and sunshine penalties: max(0, 10 − temperaturePenalty − rainfallPenalty − sunshinePenalty).
- Comfortable days require all three daily limits, inclusively: temperature in range, rainfall at or below the shared limit, sunshine at or above H.
- Missing sunshine is not zero sunshine. Enabled results must use paired three-variable records, disclose coverage, and apply a documented coverage threshold.
- Show average sunshine hours/day in the details panel. Recalculate scores, days/year, city rankings and PNGs from the same rules.
- Do not approximate joint daily conditions by combining annual averages.
- Existing temperature/rain statistics remain unchanged. A separate remote sunshine dataset supplies paired daily triples and precomputed default maps.

## Storage constraint

Do not download or build the worldwide sunshine archive on Luiz's Mac. The authorized build runs on a standard GitHub-hosted Linux runner in the public repository. The raw source stays on that runner and is removed after upload. Keep only source code, tests, reports and small metadata locally. Audit global coverage and cross-tab equality before the authorized deployment.

## Examples (illustrations, not observed city results)

With H=6 hours, 22°C and rainfall ≤1 mm: S=6 gives 10 points and a comfortable day; S=4 gives 9 points and does not count as comfortable. With 28°C, rain of 12 mm and S=4: temperature penalty 1, rain penalty 1, sunshine penalty 1, giving 7 points.

Definition source: https://open-meteo.com/en/docs/historical-weather-api

## Build design

The remote import pins temperature and precipitation archive ETags to the current ERA5 release. It aggregates all three variables into the same indexed UTC dates and sampled cells. Sunshine uses the published Open-Meteo method applied to ERA5 direct radiation, with the pinned NREL SPA lookup. It does not substitute daylight hours.

Default temperature/rain settings support all 49 sunshine minimums from 0 to 24 in 0.5-hour steps through small map files. Custom combinations stream daily chunks through the browser worker. Sunshine HTTP responses use no-store; decoded memory holds at most four chunks. No large local data directory is created.

The source builder requires all 14 original score/day map SHA-256 hashes to match. The independent JavaScript audit runs remotely against every packed daily chunk and all cells in seven periods. Small API reference samples and browser checks complete the release validation.

## Build correction

The first batch stopped after packaging because its Cape Town reference was offshore. It did not publish a site version. The corrected batch validates all reference land cells before any download and records completed source objects with their source fingerprint. A failure step preserves recovery files on GitHub rather than on the Mac. Progress writes are bounded to avoid excess KV writes.
