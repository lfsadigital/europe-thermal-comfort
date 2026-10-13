# Current worldwide ERA5 version

Source backup for https://comfy.lfsadigital.com/ . World, Europe and USA share ERA5, dates and calculation rules.

## Run locally without a large import

```sh
python3 world/restore_default_maps.py
python3 -m http.server 8777 --directory world/site/dist
```

Open http://localhost:8777 . The restore step downloads only the 21 default map arrays (about 18 MB), checks their saved SHA-256 hashes, and reuses valid existing files. Geographic assets and front-end source are included. Custom recalculations fetch versioned statistics from the existing Cloudflare endpoint on demand; they do not require a raw climate archive on disk. Remote service availability is a dependency.

## Storage and contribution

This repository excludes raw climate records, bulk statistics, caches, credentials and local Git history. Do not run the import scripts on a personal Mac unless you deliberately accept their substantial storage use. Use a separately authorized remote batch environment for future climate-data builds. Python processing scripts are preserved for reproducibility; they require scientific dependencies and the layouts described in the import documentation. Local absolute paths in older browser-check launchers must be adjusted for your installed Playwright and Chrome.

Current scoring and metadata: [site/README.md](site/README.md). Scientific validation and source limitations: [ERA5-MIGRATION.md](ERA5-MIGRATION.md). Optional sunshine is now live: off by default, 6 hours/day minimum, adjustable in 0.5-hour steps. Scores lose 0.5 point per missing hour; comfortable days must meet all enabled daily limits. See [sunshine/README.md](sunshine/README.md). The population-filter update has 48 passing region/metric/threshold checks.

Code inherits the repository MIT license except the solar adaptations, which retain AGPL-3.0; see `sunshine/AGPL-3.0.txt`. ERA5, Open-Meteo, Natural Earth, GeoNames, OpenStreetMap, map libraries and fonts have their own attribution and license conditions; see the interface and bundled license files. The old E-OBS restrictions in the root DATA_LICENSE.md concern the archived Europe pipeline, not an authorization to redistribute any data without checking its own terms.
