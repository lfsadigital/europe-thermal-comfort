# Miami source validation — 2020–2025

Production site unchanged. Same default filters: 18–26°C inclusive, precipitation ≤1 mm for comfortable days, daily score max(0, 10 −0.5/°C outside range − rain penalty 0/0.5/1/1.5).

## Observed result

NOAA CPC represents daily maximum temperature and derived comfort results much better than the tested ERA5 coastal cell for the two airport station records examined. This does not establish worldwide accuracy, and precipitation results are mixed.

| Dataset | Mean daily Tmax °C | Score | Comfortable days/year |
|---|---:|---:|---:|
| Station | 29.78 | 7.69 | 33.0 |
| NOAA CPC | 29.78 | 7.65 | 33.2 |
| ERA5 grid UTC | 27.52 | 8.66 | 75.2 |
| ERA5 grid local | 27.46 | 8.66 | 75.5 |

## Evidence

- Miami International Airport: GHCND USW00012839, coordinates 25.78805, −80.31694, elevation 1.4 m. All 2192 days valid paired TMAX/PRCP. Quality flagged records excluded; values decoded from tenths °C/mm; traces retained as zero per supplied record. Independent scalar parsing/scoring matched vectorized results.
- Miami Opa Locka Airport: GHCND USW00012882, 2162 valid paired days. Observed score 7.69 and estimated 34.5 days/year. Against the same Miami grid samples, Tmax MAE NOAA 0.36°C versus ERA5 2.45°C. These are nearby station observations, not an independent withheld validation set; CPC may use these observations.
- Miami International Tmax MAE: NOAA 0.37°C versus ERA5 UTC 2.34°C; ERA5 is on average 2.26°C colder. Monthly means show the discrepancy throughout the year.
- Original NOAA 2020–2025 NetCDF cell (25.75, 279.75°E) checked against cached raw arrays; all daily values matched. Tmax attributes state max_period 6z to 6z. No indexing, longitude, or units error found.
- Local timezone ERA5 changes score from 8.66 to 8.66 and days/year from 75.2 to 75.5; it does not resolve the temperature discrepancy. NOAA/observing station exact windows are not fully harmonized; same-date precipitation errors remain sensitive to timing.
- Requesting ERA5 at actual airport coordinates returns the same (25.75, −80.25) cell. Explicit cell_selection=land also returns that cell and does not improve the result.
- Western ERA5 cell (25.75, −80.50) improves Tmax MAE against Miami International to 0.69°C, mean Tmax to 29.31°C, score 7.83, days/year 42.8. This suggests coastal cell representativeness as an explanation; actual land fraction/model attribution not verified. That western cell is a different location and cannot be silently substituted just because it matches a station better.
- Holding NOAA temperature and swapping only ERA5 precipitation yields score 7.64 and 32.2 days/year. Holding ERA5 temperature with NOAA precipitation yields 8.67 and 81.0 days/year. The large original difference is mainly temperature-driven.

## Precipitation is not a clear NOAA win

- Airport observed annual precipitation mean: 1822.6 mm; CPC 1503.1; ERA5 1364.5. CPC annual total is closer.
- Same date-label precipitation MAE: CPC 5.50 mm/day; ERA5 UTC 4.63; ERA5 local 4.44. ERA5 is closer on that metric.
- Dry threshold classification agreement: CPC 71.8%; ERA5 UTC 77.4%; ERA5 local 78.8%. Spatial averaging of convective precipitation and daily windows affect these comparisons.
- Agreement of final scores does not prove all component weather variables are accurate.

## Decision

Do not replace current global CPC with the tested ERA5 extraction method yet. First audit coastal spatial selection and benchmark representative coastal/inland stations across regions. Higher resolution or one source alone does not guarantee better city climate representation. ERA5 remains a candidate, not validated as a universal improvement.

## Files and official sources

- Scripts: investigate_miami.py and miami_followup.py; cached original station records and API responses: share/miami-audit/.
- Main results: share/miami-audit/results.json; sensitivity checks: followup-results.json.
- Station: https://www.ncei.noaa.gov/cdo-web/datasets/GHCND/stations/GHCND%3AUSW00012839/detail
- Data specification: https://www.ncei.noaa.gov/pub/data/ghcn/daily/readme.txt
- Station raw files: https://www.ncei.noaa.gov/pub/data/ghcn/daily/all/USW00012839.dly and https://www.ncei.noaa.gov/pub/data/ghcn/daily/all/USW00012882.dly
- ERA5 documentation: https://confluence.ecmwf.int/pages/viewpage.action?pageId=388500357
