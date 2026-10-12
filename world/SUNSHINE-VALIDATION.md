# Sunshine data compatibility audit (historical NOAA baseline)

Date: 2026-10-12. This audit preceded the ERA5 migration. Production now uses ERA5 for temperature and rain; sunshine is not yet included. The NOAA baseline and recommendation below describe the earlier state.

## Existing dataset, observed locally

The published site uses NOAA CPC daily Tmax and precipitation, 2020–2025, 2,192 dates, 360 × 720 grid, 0.5° point spacing. All regions share this dataset. Native cell coordinates include 41.25/-8.25 (Porto area), -1.25/36.75 (Nairobi area), 34.25/-118.25 (Los Angeles area). The build pairs temperature and precipitation by recorded date; it does not demonstrate identical observing-hour windows. README already documents that reporting windows can differ.

## Candidate source and resolution

Open-Meteo Historical Weather API, explicitly `models=era5`, supplies global hourly data on its 0.25° grid, including daily sunshine duration in seconds. This is model/reanalysis-derived sunshine estimated from direct normal irradiance above 120 W/m², not a station sunshine recording and not daylight duration. ERA5 is a different product from NOAA CPC; the same coordinates and date labels do not establish equivalent methodology or spatial support.

The three tested NOAA coordinates were returned exactly by ERA5. Therefore these sampled locations need no coordinate interpolation. Selecting ERA5 values at 0.5° spacing is possible, but downsampling spacing does not turn a 0.25° source into the same underlying analysis as CPC. Any spatial aggregation/resampling policy must be explicit and applied consistently to all variables.

## API checks performed

- Full period 2020-01-01 to 2025-12-31, all 2,192 dates, at each of the three cells above.
- Requested sunshine_duration, daylight_duration, temperature_2m_max and precipitation_sum together.
- Fixed model ERA5, timezone GMT/UTC, nearest-cell selection; disabled elevation downscaling (`elevation=nan` for each coordinate).
- No missing sunshine, temperature or precipitation in these three samples. This is 6,576 sampled location-days, not a full worldwide coverage audit.
- Sunshine units seconds; every sample nonnegative, below 24 hours and no longer than returned daylight (1-second tolerance).
- Separate 3-day hourly check at Porto: daily sunshine matches sum of 24 hourly values within 0.01 second; daily Tmax matches maximum of the 24 returned hourly temperatures.
- These checks validate API availability, indexing, units and aggregation, not agreement with measured station sunshine or worldwide accuracy.

Evidence:
- `share/sunshine-api-samples.json`: metadata and sample summary.
- `share/sunshine-api-response.json`: returned full daily sample.
- `share/sunshine-hourly-check.json`: hourly/daily consistency.
- `validate_sunshine_api.py`, `validate_sunshine_hourly.py`: reproducible requests.

## Recommendation

For one coherent model/day/grid convention, first benchmark an alternative using explicitly ERA5 for all three variables. Keep the existing production dataset unchanged until comparison with CPC is measured and reviewed. Fix one common timezone definition and one shared spatial sampling policy; apply the same choices to every region and both metrics. The API's default Best Match can mix models, so do not use it for this consistency test.

Adding ERA5 sunshine alone to CPC temperature/rain is technically possible, but requires a reporting-window and spatial-support audit. This audit has not established exact 24-hour alignment of CPC with ERA5. It must not be described as a fully homogeneous three-variable dataset.

Before any sunshine filter publication: audit global coverage, ensure all three variables exist for each scored day, document the definition of a day and grid sampling, rebuild joint daily statistics, compare temperatures/rain/scores/rankings against production, and leave the new sunshine option disabled by default unless the user chooses otherwise. Changing the source can change scores; this audit did not quantify that difference.

Sources:
- https://open-meteo.com/en/docs/historical-weather-api
- https://psl.noaa.gov/data/gridded/tables/att.daily.html
