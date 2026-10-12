# Remote sunshine build

Run only through the GitHub Actions `Remote ERA5 sunshine build` workflow. The bulk builder refuses local execution. Standard public-repository runners process ERA5 archives in bounded remote disk space. A temporary authenticated Cloudflare control worker exchanges scoped asset-upload credentials; no account-wide Cloudflare token is stored in GitHub.

Temperature/rain source objects are pinned to the production import ETags, and every original default score/day array must retain its SHA-256. Sunshine uses ERA5 direct radiation and Open-Meteo's published NREL SPA method. The initial 72-day API pilot spans 12 cities in June/December, including polar night/day. Small floating-point differences are recorded in the pilot report. Sunshine is calculated at the same sampled cells and uses the same UTC hourly labels as the existing data. Radiation duration and precipitation are preceding-hour sums.

The enabled rule subtracts 0.5 point per hour below the selected minimum, with the floor applied to each daily score. Comfortable days require temperature, rain and sunshine limits on the same day. Missing sunshine is not zero. The disabled path retains the original data and calculations.

Default temperature/rain rules are precomputed for minimum sunshine from 0 to 24 hours in 0.5-hour steps. Other rules use exact daily triples, streamed by year/chunk. Temperature dictionaries preserve Float32 values; rainfall bins match the existing 0.1 mm controls; sunshine seconds retain Float32 daily sums. Bulk responses must use no-store in the browser, with a bounded decoded cache.

`solar.py` adapts the Open-Meteo solar method and is licensed AGPL-3.0-only; the included license and pinned source are retained. Generated astronomical lookup values and derived climate data are distinct from application code. Climate data attribution is Copernicus/ECMWF ERA5 via Open-Meteo. Other project files retain their existing licenses.
