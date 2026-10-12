# ERA5 versus NOAA CPC — 2020–2025

Read-only benchmark. Production site and source files were not changed.

## Method

- 12 city locations; same production NOAA cell selection, then ERA5 requested at that exact cell centre. Returned coordinates were checked.
- Fixed ERA5 model through Open-Meteo; GMT daily aggregation, elevation=nan, cell_selection=nearest. No model mixing or elevation downscaling.
- Daily maximum temperature and total precipitation (rain + snow water equivalent). No sunshine penalty in this comparison.
- Score: max(0, 10 − 0.5 × distance outside inclusive 18–26°C − precipitation penalty). Rain ≤1 mm: 0; >1–10: 0.5; >10–20: 1; >20: 1.5.
- Comfortable days: temperature within 18–26°C inclusive and precipitation ≤1 mm. Annual count = qualifying / valid × 2192 / 6.
- Eligibility: ≥90% paired valid days in every calendar month. Missing days are excluded, never filled.
- Every NOAA result checked against production score/days binary assets; ineligible Cape Town checked to be missing in those assets. Scalar and NumPy formulas agreed.

## Results

| City | NOAA score | ERA5 score | Δ score | NOAA days/year | ERA5 days/year | Δ days/year | NOAA paired days |
|---|---:|---:|---:|---:|---:|---:|---:|
| Porto | 8.69 | 8.59 | -0.10 | 104.8 | 99.7 | -5.2 | 2192/2192 |
| Madrid | 7.76 | 7.72 | -0.04 | 73.0 | 68.3 | -4.7 | 2192/2192 |
| London | 7.69 | 7.49 | -0.19 | 82.3 | 74.0 | -8.3 | 2192/2192 |
| Rome | 8.34 | 8.29 | -0.05 | 84.2 | 68.0 | -16.2 | 2192/2192 |
| Los Angeles | 8.73 | 8.62 | -0.11 | 141.5 | 136.2 | -5.3 | 2192/2192 |
| New York | 7.13 | 7.15 | +0.02 | 62.2 | 65.0 | +2.8 | 2192/2192 |
| Miami | 7.65 | 8.66 | +1.02 | 33.2 | 75.2 | +42.0 | 2192/2192 |
| Chicago | 6.53 | 6.67 | +0.14 | 55.0 | 60.5 | +5.5 | 2192/2192 |
| Nairobi | 9.57 | 9.61 | +0.04 | 162.9 | 159.8 | -3.1 | 2191/2192 |
| Nguruka | 8.20 | 8.60 | +0.40 | 5.2 | 3.7 | -1.5 | 2192/2192 |
| Cape Town | Unavailable | 8.91 | — | Unavailable | 132.7 | — | 2174/2192 |
| Marrakech | 7.39 | 7.78 | +0.38 | 109.0 | 109.0 | +0.0 | 2192/2192 |

All ERA5 samples had 2192/2192 paired days. Nairobi NOAA had 2191; common-date comparison changes Δ days from −3.1 to −3.0. Cape Town NOAA had 2174 but failed at least one monthly coverage test; its raw diagnostic mean is not a publishable result.

## Interpretation and limits

- Miami changes by about +1.02 score and +42 days/year. ERA5 mean daily Tmax is 2.27°C lower at the sampled cell. This is a material change, not proof ERA5 is more accurate.
- Rome changes by −16.2 days/year despite a small score difference. Near-threshold temperature/precipitation changes can alter binary comfortable-day counts.
- These are grid-cell estimates near cities, not city weather station measurements. Equal centre coordinates do not make the two cell footprints equal (NOAA 0.5°, ERA5 supplied at 0.25°).
- NOAA observing-day windows have not been verified to match ERA5 UTC-day aggregation. Results compare the products as available; they are not a fully harmonized accuracy test.
- Neither product was checked against independent weather station truth. Accuracy winner remains unknown.
- Nguruka uses its catalog city coordinates (−5.10917, 31.04194) and production-selected cell (−5.25, 31.25). It is not the older user click at cell (−5.25, 30.75).
- This sample does not establish global coverage or global ranking agreement.

Raw API responses, exact coordinates, common-date deltas, temperature biases and configuration: share/era5-comparison/results.json. Reproduce: ../europe-comfort/.venv/bin/python compare_era5_noaa.py (NumPy required). Cached responses are reused.

Official API specification: https://open-meteo.com/en/docs/historical-weather-api
NOAA source files: https://downloads.psl.noaa.gov/Datasets/cpc_global_temp/ and https://downloads.psl.noaa.gov/Datasets/cpc_global_precip/
