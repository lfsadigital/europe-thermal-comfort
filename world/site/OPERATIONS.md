
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

## 2026-10-13 — browser performance candidate

User explicitly authorized optimizing, comparing, testing and publishing Comfy before deciding hosting migration. Browser-only candidate eligibility reuse and bounded result cache implemented. CPU-throttled (4×) local median ranking/marker refresh: World Nomads on 1931.6 → 304.4 ms, Europe 2586.3 → 61.3 ms, USA 2016.8 → 28.9 ms. Exact arrays/rank rows/marker count fingerprint identical. Initial-ready timings 4597 versus 4211 ms are single observations, no initial-load improvement claimed. Returning to cached periods removes three prepared-map requests. Independent climate/filter, mobile/custom-temperature and map/PNG checks passed. Sunshine/cache-specific checks and publication follow. No cloud service, DNS, KV or other project changes in this optimization.

## 2026-10-13 — browser optimization published

Sites version 18, source f6e9f5d7f4903c20f604b5eccc03c3b690aeebc2, deployment appgdep_6acea9263a708191bfd86f6bd96c7b83 succeeded 2026-10-13T21:57:11.704063+00:00. Anonymous custom-domain map/filter/mobile/tab/PNG and period/sunshine cache checks passed with zero page errors. Each PNG matched 81 canvas samples with max difference zero. Returning to cached mean/2025 required zero prepared-map requests; values identical. Sunshine 6→7→6 and off restored exact arrays; cache budget checks passed. No hosting migration, KV operations, server calculation service or other project changes introduced. Public GitHub not pushed in this request; local backup prepared. Temporary publication archive removed after successful save/deploy.

## 2026-10-14 — city map modes and logo candidate

User authorized three map modes, population classification, retained optional unknowns and zoom behavior, testing/publication; added improved logo/favicon to same scope. Candidate browser checks and PNG regression passed. Default highlight, results-only keeps unknowns, ranking-only leaves climate layer unchanged. Population fails are gray; 1k+ catalog rendered by existing zoom thresholds and camera padding. Counts region-wide. Authored native SVG sun/horizon and simplified favicon with 32px/180px raster fallbacks. Reviewer empty-status fix scored resolved. No scientific dataset/formula changes and no cloud resources outside Comfy altered. Publication follows.

## 2026-10-14 — city map modes and identity published

Sites version 19, source 7a7de1ebcfff3330b286b9d722ec6f75f14d968b, deployment appgdep_6acfc4f2447881918d7895aa623e7533 succeeded 2026-10-14T18:08:11.416512+00:00. Anonymous custom-domain mode/population/unknown/empty/URL/zoom/320px/PNG checks passed. Full regression passed zero page errors; each score/day PNG matches 81 canvas samples exactly. Logo rendered; all four public logo/favicon files match tested local SHA-256 and return200. No dataset/formula, DNS or other-project resource changed. No public GitHub push in this request. Local publication archive removed after successful deployment and checks.

## 2026-10-14 — quiet map candidate, not published

User asked neutral nonmatching areas, verified city highlights, immersion, much less visible copy and removal of quick-city chips; chose adjustable score and days limits together. Candidate defaults score≥8 and days/year≥180 as map-only highlight limits. Source numerical arrays/formula/data unchanged. Unknown metadata remains ranking eligible but is not highlighted; no socioeconomic region masking inferred from city records. Local tests verify exact original-cell mask, transparency/full-color restoration, no failed or unknown highlighted points, removal of chips, PNG threshold state, immersion/Escape/height and320px overflow. Three review fixes scored resolved (mobile info/Exit overlap, neutral export legend, eyebrow removal); final DESIGN documented. No new deploy, GitHub push, Cloudflare service/DNS or other-project changes. Awaiting explicit publication approval.

## 2026-10-14 — quiet map published

Explicit approval for publishing and GitHub update received. Sites version20, source17988d9ce8de8a519b9b1c49db738324f79af7a2, deployment appgdep_6acfd46f8a7c81918dc5f2f0ec0433f6 succeeded 2026-10-14T19:14:10.987907+00:00. Anonymous custom-domain exact-mask/unchanged-array/verified-city/immersion/Escape/320px/PNG/invalid-input tests passed. Eight public code/style SHA-256 hashes match tested local files. No hosting/DNS/data-source or other-project changes. GitHub backup includes prior performance and logo changes as well as this refinement; no raw climate archives included. Temporary publication archive removed after successful deploy/verification.

## 2026-10-14 — license update candidate

Explicit user authorization: remove Nomads from public site/GitHub, audit UNODC, correct credits, test and publish without changing climate calculations. Nomads removed from runtime bundle; legacy flags normalized. Scientific core/worker hashes unchanged. Country-source permission requires follow-up; municipal data retained. Local browser and unit tests passed. No DNS/Cloudflare resource changes.

## 2026-10-14 — country source withdrawn

User chose withdrawal of UNODC country data pending permission. Removed country snapshot, fetch, selector option and context values. Retained municipal FBI/Eurostat values and no-fallback behavior. Old country-filter links disable the retired filter. Broader country coverage is lost; municipal Unknown values stay eligible. Weather data and calculations unchanged.

## 2026-10-14 — data license update published

Sites version22 source0f50cf75911f2936bea82cc9c666eeb6f8e0ffc1, deployment appgdep_6acfe31719a4819182acb9a226899dae succeeded 2026-10-14T20:16:40.060037+00:00. Nomads and UNODC country snapshots and filters withdrawn with explicit user authorization. FBI/Eurostat municipal values, population and all climate calculations preserved; scientific core/worker hashes unchanged. GitHub code08d566f pushed. No DNS/Cloudflare account resource changes. Historical repository commits/Sites saved versions not removed.

Anonymous custom-domain license-update browser checks passed with zero JavaScript errors: retired JSON endpoints serve no dataset; legacy flags normalized; exact weather arrays stable under city filters and region tabs; municipal Miami rate/count retained; score/day PNG2400×1800 exclude retired fields;360px no overflow. Temporary publication archives removed.

## 2026-10-14 — EPI USA budget candidate

Authorized free EPI integration, tests/publication and GitHub update. Exact1p0c county totals,2025USD, joined to GeoNames county FIPS.16,418cities linked;211unknown. Budget is USA-only,off by default,USD5,000 initial ceiling. Scientific core/worker hashes unchanged. Lazy178KiB data asset, no new Cloudflare services or KV. Tests/publication follow.
