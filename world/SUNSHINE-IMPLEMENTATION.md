# Optional sunshine rules — accepted specification

Luiz selected this rule on 2026-10-12. Status: specified, not implemented or published.

- Sunshine is hours of sunshine, not daylight hours. Use explicit ERA5, UTC days, 2020–2025, and the same source coordinates and sampling policy as temperature and rain.
- Planned enabled default: minimum 6 hours/day, no upper limit. This is a user preference, not a validated physiological comfort threshold.
- Disabled by default. Disabled calculations and existing data-coverage rules must remain unchanged.
- When enabled, let H be the selected minimum hours per day and S be daily sunshine hours. Additional penalty = 0.5 × max(0, H − S).
- Apply the zero floor after adding temperature, rainfall and sunshine penalties: max(0, 10 − temperaturePenalty − rainfallPenalty − sunshinePenalty).
- Comfortable days require all three daily limits, inclusively: temperature in range, rainfall at or below the shared limit, sunshine at or above H.
- Missing sunshine is not zero sunshine. Enabled results must use paired three-variable records, disclose coverage, and apply a documented coverage threshold.
- Show average sunshine hours/day in the details panel. Recalculate scores, days/year, city rankings and PNGs from the same rules.
- Do not approximate joint daily conditions by combining annual averages.
- Existing stored statistics contain temperature/rain only. New daily sunshine pairing and a compatible joint-statistics format are required before enabling worldwide rules.

## Storage constraint

Do not download or build the worldwide sunshine archive on Luiz's Mac. Select and authorize a remote batch-processing environment first. Cost and runtime are currently unknown. Keep only source code, tests, reports and small metadata locally. Audit global coverage and cross-tab equality before requesting deployment approval.

## Examples (illustrations, not observed city results)

With H=6 hours, 22°C and rainfall ≤1 mm: S=6 gives 10 points and a comfortable day; S=4 gives 9 points and does not count as comfortable. With 28°C, rain of 12 mm and S=4: temperature penalty 1, rain penalty 1, sunshine penalty 1, giving 7 points.

Definition source: https://open-meteo.com/en/docs/historical-weather-api
