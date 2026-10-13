
## 2026-10-12 — local city context and monthly charts

Prepared, not pushed or deployed. Browser verification passed 133 checks with zero page errors across region tabs, filters, shared URLs, and Porto/Miami/Nairobi monthly comparisons. Separate checks passed for missing US crime data, monthly-request failure and retry, mobile overflow, and both 2400×1800 PNG exports. Independent design review passed after three chart fixes. Production weather calculations and original climate arrays remain unchanged. Temporary Nomads and UNODC source downloads were removed; curated small tables remain in dist/assets.

## 2026-10-13 — city map interaction checks

User authorized publication and GitHub backup. Optional map mode, shared URL, debounced native sliders and exact values, city hover reasons, click-to-inspect and marker-inclusive PNG exports implemented. Climate raster and score/day arrays do not change. At overview zoom only larger cities appear; smaller and unknown-data cities become visible with zoom. Local marker suite passed 47 checks with no page errors. The first hover test was outside the browser viewport; bringing the map into view resolved the test without a product change. Monthly/filter suite passed 133 checks; independent missing-data and API retry checks passed. City-level crime import is proposed in docs/LOCAL-CRIME-NEXT.md, not included. The independent reviewer scored the mobile field-occlusion fix resolved (ship at that narrow scope). Publication IDs and live checks follow after verification.

## 2026-10-13 — published city context and monthly charts

Published Sites version 15 at https://comfy.lfsadigital.com/ . Source be4a87a8c180d8d85761aa6b0b2447a715093bb9; saved version appgprj_6acc3bb3fcd4819181f55b4757d282a8~appgver_f6a7624415188191be457ee8e1c85967; deployment appgdep_6acda07b121881919d19a94e11a897e5 succeeded at 03:07:56 UTC. Code backup pushed to GitHub and read back: 8bd36ef002a6f086a8a3efb2224f1d1e0afb1a6c.

Anonymous custom-domain browser checks passed: 133 chart/filter/source comparisons, 47 marker/hover/click/tab/shared-URL/mobile/export checks, zero page errors. Separate public missing-data, API failure/retry and PNG checks passed. All 11 sampled public code/data files match the tested source by SHA-256. Curated city tables total 302,946 bytes. No global climate archive was downloaded. Crime remains country/area context with selected years; no local FBI or Eurostat import is claimed. Weather raster and original score/day data are unchanged. DNS and main GitHub Pages site were not modified.

Release metadata and public evidence are under site/docs/CITY-CONTEXT-RELEASE.json and city-*-public-*.json. The temporary publication tar was removed after the saved-version deployment succeeded. Local source is retained; bulk weather data remains remote.

## 2026-10-13 — city homicide prepared

User explicitly authorized publication and GitHub backup. FBI Table 8 (2020–2025) and Eurostat crim_hom_vcit victim rates (2020–2024) imported with conservative unique catalog joins and same-source denominators. 37,674 city/year rows rechecked against every original rate/count/population. Scope selector distinguishes city/municipal from country; missing local data never falls back. Coverage labels include 12-month FBI table inclusion rule and unknown Eurostat monthly completeness. Historical URLs retain national semantics. City-specific filter/URL/mobile/export checks passed; 133 chart/filter, 47 map and independent failure/missing-data regression checks passed. Weather arrays and formula unchanged. Corrected Netherlands catalog country spelling for Europe ranking. Publication and anonymous live evidence follow.

## 2026-10-13 — city homicide published

Published Sites version 16, source 36f72884c74391fefb66045e2c72de9e80696cce, deployment appgdep_6acdaab021d88191885362fc15816931, succeeded 2026-10-13T03:51:30.846286+00:00. Anonymous custom-domain city/scope/year/missing-data/tab/shared-link/mobile/PNG checks passed with zero page errors. All seven changed public code/data assets match the tested source by SHA-256. Miami 2024: 28 murders / 460,392 FBI population × 100,000 = 6.081773792767902; Amsterdam greater city 2024: published Eurostat 1.68. Both unchanged across tabs. Python HTTP asset client received 403; anonymous browser verification succeeded. Independent design verdict scored its sole documentation fix resolved.

Temporary official source downloads, extraction files and the saved publication archive were removed: 45,325,456 bytes across 25 files, no application assets removed. The imported city table and source hashes/audit remain. No bulk climate download occurred. GitHub backup verification follows this release.

## 2026-10-13 — map-first candidate, not published

Weather and Cities controls moved onto the map. Optional missing city data stays eligible as unknown; known failures exclude. PNG uses the actual current camera and rendered city markers. Local functional/mobile/export checks passed; climate assets and formulas unchanged. Live Lab technical SEO checked separately: canonical, title, description, robots, sitemap and normal project links passed. Google index status and external backlinks unknown. This candidate has not been pushed or deployed; explicit approval is required.

## 2026-10-13 — map-first published

Explicitly authorized. Sites version 17, source 58548cc15bf3b02ca3f3a6d5b0f1f1f34e200b33, deployment appgdep_6ace9c91e5888191842f5fff6e9c6ba4 succeeded at 2026-10-13T21:03:32.114069+00:00. Anonymous custom-domain filters, unknown retention, markers, URL state, mobile, tab parity and both PNG checks passed with zero page errors. Each PNG matched 81 actual canvas samples with maximum difference zero. No climate data/formula changed.
