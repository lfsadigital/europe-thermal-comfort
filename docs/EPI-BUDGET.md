# EPI regional budget — tested 2026-10-14

User authorized implementation, tests, public deployment and GitHub update. USA tab only; off by default; initial ceiling USD5,000/month, adjustable. Does not change climate scores, comfortable-day counts or raster colors. The existing matching-city/ranking rules apply. Missing regional data is Unknown, retained in ranking and never presented as a verified map match.

## Source, profile and geography
Economic Policy Institute. 2026. Family Budget Calculator. Published March2026, in2025USD. Exact County-sheet family code1p0c: one adult, no children. Monthly Total columnM retained; Annual Total columnU used as an independent unit check. Total includes housing, food, transportation, healthcare, other necessities and taxes; childcare is zero. This is a modest local household budget including taxes, not a nomad short-stay budget, average city spending or neighborhood measurement. EPI assumes a studio for one adult.

GeoNames city ID+US state+county FIPS joins to EPI county FIPS. Existing catalog coordinates must agree within0.02° with the current source; state names must agree. No nearest-city, metro, state or national fallback. For cities spanning counties the GeoNames associated county is a regional reference only. New York City lacks a unique county code in this source and stays Unknown. Alaska/Connecticut boundary/code changes are not guessed.

3,143 county rows imported;16,418of16,629USA catalog cities linked;211Unknown. See EPI-IMPORT-AUDIT.json for unmatched reasons, input hashes and sample source rows. Source totals match annual/12. Component figures are separately rounded in the workbook; their monthly sum differs from Total by at most $0.166667 ($2/year). We preserve the published Total rather than recomputing it.

## Behavior
The budget panel and filtering are active only in USA. Switching to World/Europe hides and suspends it; returning to USA restores the selection. URL keys epi=1 and epimax represent only an active USA filter. Data loads lazily on the first USA visit; no new backend, KV writes or external API calls per interaction. Error/missing data remain Unknown, with retry. Invalid budget blocks export; loading budget blocks a budget-filtered PNG until classification completes. Source year is independent of the selected climate year.

Regional county name, amount, profile and price-year appear in city context; hover includes regional attribution. PNG filter line and credit identify EPI, profile,2025USD and CC BY-NC-SA4.0. No Nomads or UNODC country data restored.

## License
EPI data and Comfy Days county/city adaptation: CC BY-NC-SA4.0. Attribution and license metadata embedded in epi-budget.json.gz; the adapted data must retain this license. GeoNames identifiers/administrative joins: CC BY4.0. These data licenses are separate from the application source-code license. Neither EPI nor GeoNames endorses Comfy Days.

https://www.epi.org/resources/budget/
https://www.epi.org/publication/family-budget-calculator-documentation/
https://files.epi.org/uploads/fbc_data_2026.xlsx
https://creativecommons.org/licenses/by-nc-sa/4.0/
https://www.geonames.org/export/

## Reproduce
Run python3 city-data/import_epi.py --workbook /path/fbc_data_2026.xlsx --geonames /path/cities1000.zip --site /path/site. Inputs are small temporary files, not tracked. No global ERA5 files downloaded for this feature. Tests: epi-check.cjs, epi-browser-check.cjs plus existing climate/monthly/mask checks.

Local tests passed: all3,143county unit/total checks,16,418joins, Miami source value, unknown NYC retained, exact budget boundary, USA-only scope, unchanged climate arrays across tabs, real map hover, URL reload, score/day PNGs,360px layout, invalid-input guard, reset, outage/retry. Scientific core/worker SHA-256 hashes match the prior production manifest. Publication receipt follows separately.
