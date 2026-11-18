# Data usage review — 2026-10-14

## Local cleanup
107 obsolete review PNGs and NOAA station review input files removed: 129,825,544 bytes (129.8 MB decimal). Code, documentation, JSON/CSV audit results, current quiet-*.png and logo-header.png preserved. Site dist file hashes were identical before and after cleanup. Final allocated folder sizes: world-comfort 59,796 KiB; comfy-days-github 34,424 KiB; combined approximately 96.5 MB decimal / 92.0 MiB. No push, deploy or remote resource deletion occurred.

## Nomads: permission unresolved; current redistribution needs correction
Actual importer uses the public /api/cities snapshot, retaining score/cost for 1,165 matched cities. assets/nomads-cities.json exists in both local deployed bundle and GitHub backup. Public access is not proof of a redistribution license. Current /api redirects to v3 documentation with paid API licensing. That license allows use in products during an active subscription, limits caches to 30 days, and prohibits giving away raw data as a dataset/public API/data feed or building a competing city database. General terms require a link back on the screen using their data.

The original snapshot came from the older public endpoint, not paid v3. Applicability of v3 terms to this legacy snapshot and existence of separate written permission are UNKNOWN. Thus no definitive legal violation is asserted, but current publication is not cleared. Earlier documentation claiming that an endpoint being intended for maps plus attribution sufficed was incomplete.

Recommended action: obtain explicit written permission covering browser-distributed score/cost snapshot and GitHub redistribution, or remove Nomads snapshot and filters from the public site/repository. A paid subscription alone does not authorize public dataset distribution under these terms. Do not purchase a plan or contact the provider without user authorization.

Sources:
- https://nomads.com/api/v3 (License section)
- https://nomads.com/faq/nomadscom-terms-of-service-privacy-policy-8279217
- https://nomads.com/api/cities (legacy endpoint still accessible)

## Other active data
| Source | Observed reuse rules | Status / limitations |
|---|---|---|
| Open-Meteo AWS open data, ERA5 temperature/rain/solar | Open data repository specifies CC BY 4.0; ECMWF archive datasets describe open archive access | Reuse permitted with source/license/change attribution. Site credits Copernicus ERA5/ECMWF and Open-Meteo; weather-specific license and derived-data notice should be made explicit rather than relying on GeoNames adjacent license link. |
| Open-Meteo Historical API, monthly charts | Data CC BY 4.0; free hosted API limited to noncommercial use; less than 10,000/day, 5,000/hour, 600/min | Free personal/nonprofit website with no ads/subscriptions is an allowed example. Promotional/commercial use is excluded. Classification of branded Lab as promotional is not conclusively established; request clarification or replace chart API with remotely processed monthly aggregates if used commercially. API-service rules differ from AWS dataset reuse. |
| GeoNames | Attribution license, commercial use allowed | Source and CC BY link present in footer; reuse supported. |
| Natural Earth | Public domain | Reuse supported. |
| Eurostat homicide statistics | Commercial/noncommercial statistical reuse with attribution; exceptions for third-party material | Dataset links and source labels present. No restriction specific to our homicide table found; do not generalize to every Eurostat dataset. |
| FBI public UCR crime data | FBI data-quality guidelines explicitly call publicly released UCR data public domain | Reuse supported; preserve geographic/year/coverage labels. |
| UNODC country homicide workbook | Official aggregate workbook provenance confirmed; applicable aggregate dataset reuse license not successfully verified | UNKNOWN. Do not apply unrelated microdata restrictions or UNdata portal license automatically. Needs dataset-specific reuse confirmation. |
| OpenFreeMap / OpenStreetMap basemap | OpenFreeMap free public service; OSM attribution/licensing still applies | Basemap attribution exists in UI and export. ODbL conditions must be retained; this review does not clear every third-party software dependency. |

Sources:
- https://github.com/open-meteo/open-data (License)
- https://www.ecmwf.int/en/forecasts/access-forecasts/access-archive-datasets
- https://open-meteo.com/en/terms
- https://www.geonames.org/export/
- https://www.naturalearthdata.com/about/terms-of-use/
- https://ec.europa.eu/eurostat/help/copyright-notice
- https://ucr.fbi.gov/cjis/ucr/data_quality_guidelines
- https://data.unodc.org/datareport/hom-victim
- https://openfreemap.org/
- https://www.openstreetmap.org/copyright

This is a source-permission review, not a blanket legal clearance. No live data was changed. A direct HTTP post-cleanup check received 403 from hosting, so it did not establish interactive live-site health. All local published assets are unchanged by hashes; deletion was confined to local review files.
