# Sunshine data build and tests

Bulk climate processing runs only on a GitHub-hosted Linux runner. `remote_build.py` rejects local execution. The Mac keeps source code, small reference samples and audit reports. Sunshine bulk HTTP responses use `Cache-Control: no-store`; browser recalculation uses bounded memory and does not save the daily archive to disk.

Sunshine is derived from hourly ERA5 direct radiation using the published Open-Meteo solar algorithm, pinned in `sources.json`. It is an estimate of sunshine duration, not astronomical daylight or an observation at a city. Temperature, precipitation and sunshine use the same ERA5 archive, source cells and indexed UTC dates, 2020–2025.

The optional rule is off by default. Its initial minimum is 6 hours/day, adjustable from 0 to 24 in 0.5-hour steps. Score penalty: 0.5 × max(0, minimum − daily sunshine hours). Apply the daily zero floor after all penalties. Comfortable days require temperature, rain and sunshine to meet their limits on the same day. Missing sunshine is not zero: at least 90% matched days must exist in every month.

The remote builder recreates the original temperature/rain maps and requires their SHA-256 hashes to match before release. It validates every default sunshine result against direct daily arithmetic. A separate remote JavaScript audit decodes all daily files with the browser engine and checks every cell for each year and the six-year mean. Default temperature/rain rules support small cached map downloads for every sunshine minimum; custom combinations stream daily files into a worker.

Solar calculation adaptations retain the upstream AGPL-3.0 license. See `AGPL-3.0.txt`. Other project code retains its existing license. Preserve source attribution when redistributing the climate data.
