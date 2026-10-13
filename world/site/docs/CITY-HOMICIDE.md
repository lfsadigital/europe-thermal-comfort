# City homicide: sources and limits

City filters remain optional and do not change weather scores, weather map colors or comfortable-day calculations. Local homicide and national homicide are distinct modes. Missing local data remains eligible as unknown when the local filter is enabled; it never falls back to a country value. A known rate above the limit excludes the city. A published zero is a valid value, not missing.

Default when enabled: city/municipal area, 2024, maximum 5 per 100,000. The year is independent of the weather period. Old URLs with crime=1 and no homgeo retain country mode. New URLs write homgeo=city or homgeo=country.

## USA

Source: FBI Crime Data Explorer annual Offenses Known to Law Enforcement, Table 8, by State by City, 2020–2025. Metric: murder and nonnegligent manslaughter. Rate = reported count × 100,000 / the FBI table's same-year population. GeoNames population is never the denominator.

The methodology for each imported year requires 12 complete reporting months for agencies included in Table 8. This is the FBI publication inclusion requirement; the application does not independently reconstruct monthly agency submissions. Included areas represent municipal agency service areas. County, university and other agency tables are excluded to avoid overlap. Agency service areas can differ from city boundaries. State or city source footnotes remain visible.

Joins require a unique normalized city name and state in GeoNames. Explicit aliases: New York → New York City; Washington → Washington DC. Saints, forts, mounts and accents are normalized. No fuzzy or nearest-city matching. A same-year FBI population outside 0.5–2 times the catalog population is excluded as a conservative identity check. This can exclude legitimate cities whose populations changed; exclusions are not assigned guessed values. Ambiguous and unmatched rows remain unavailable.

## Europe

Source: Eurostat crim_hom_vcit, total-sex intentional homicide victims, published P_HTHAB rates, 2020–2024, update 2026-04-29. An explicit city-code/country/name crosswalk joins each area to one catalog city. The published rate is used directly. Counts alone do not produce a guessed rate. Flagged rates are excluded. Greater-city labels remain visible. Monthly reporting completeness is unknown, not claimed as 12 months.

This dataset has rates for only 19 distinct European city/greater-city areas over the period, and 11 in 2024. It does not cover every European city. There is no imported European city data for 2025. Local FBI and Eurostat definitions and geographic areas are not perfectly equivalent; homicide is not a complete measure of safety.

## Matched coverage

| Year | USA | Europe |
|---|---:|---:|
| 2020 | 6,130 | 18 |
| 2021 | 4,879 | 17 |
| 2022 | 6,265 | 17 |
| 2023 | 6,562 | 16 |
| 2024 | 6,900 | 11 |
| 2025 | 6,859 | 0 |

37,674 unique city/year rates. The compressed public asset is 601,231 bytes. The audit records every accepted catalog ID and source row/code, source hashes, annual coverage and rejected matches. Download acquisition is bounded; no climate archive is downloaded. Temporary source files can be deleted after verification without affecting the published site.

Reproduce with Python standard library plus pdftotext: run city-data/fetch_city_homicide.py, import_city_homicide.py and verify_city_homicide.py. Source acquisitions are small temporary files, not application runtime requests. Run homicide-browser-check.cjs against a preview, then COMFY_TEST_URL=https://comfy.lfsadigital.com/ after publication.

Official sources:
- https://cde.ucr.cjis.gov/LATEST/webapp/#/pages/downloads
- https://ec.europa.eu/eurostat/databrowser/view/crim_hom_vcit/default/table?lang=en
- https://ec.europa.eu/eurostat/cache/metadata/en/crim_sims.htm
