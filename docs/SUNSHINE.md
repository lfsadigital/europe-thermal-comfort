# Optional sunshine

The default minimum is 6 hours/day. The rule is disabled until the visitor enables it and applies the controls. Minimums use 0.5-hour steps, from 0 to 24; there is no upper sunshine penalty.

For each UTC day, additional penalty = 0.5 × max(0, selected minimum − sunshine hours). Apply the zero floor after temperature, rain and sunshine penalties. Comfortable days require all enabled daily limits on the same date. Scores average daily values; comfortable days/year are annualized using matched record coverage. Missing sunshine is not zero sunshine. Every month needs at least 90% matched days.

ERA5 radiation, temperature and precipitation use the same sampled source cells and indexed UTC days for 2020–2025. Sunshine is derived from direct radiation using the published Open-Meteo solar method around the WMO 120 W/m² threshold. The pinned solar lookup uses NREL SPA. This is estimated sunshine duration, not daylight length and not a station measurement at a named city.

All regional tabs, both metrics, rankings and PNGs use the same rules and arrays. When disabled, temperature/rain scores and day counts use the unchanged original data and engine. The details panel can show mean sunshine without enabling a penalty.

The build and full-data JavaScript audit run remotely on GitHub Actions. Raw source archives are never downloaded to the Mac. The optional daily dataset is served from a separate Cloudflare asset Worker with `Cache-Control: no-store`. Browser recalculation keeps at most four decoded chunks. Default temperature/rain settings use small prepared maps for each sunshine minimum.

See the public repository's `world/sunshine` folder for the build, algorithm provenance, AGPL license for solar adaptations, and remote validation workflow.
