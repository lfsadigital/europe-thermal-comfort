
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

## 2026-10-14 — EPI budget published

Sites version23 source dd6ff5c3a1a107849f9a41c3dba4f61955dd7abf, deployment appgdep_6ad006d5b3f48191a3e128c40a0ba75e succeeded2026-10-14T22:49:13.203760+00:00. GitHub code5cbc6c4 pushed. Anonymous custom-domain EPI browser checks passed: lazy USA-only data, county/profile/year context, Miami source5047USD/month, unknown cities retained, original score/day arrays exact across regions, known failures excluded, true city hover, two PNGs, reload/mobile/invalid/reset, simulated source outage and retry. Scientific core/worker hashes unchanged. Temporary source workbook, GeoNames input and deployment archive removed. No new Cloudflare resources/KV or DNS changes.

## 2026-10-14 — climate and urban context published

Explicit authorization received for comfy.lfsadigital.com publication and GitHub update. Sites v24 source afaaa61f910675d1d37531f97c04c558fe8a40f0; deployment appgdep_6ad00ef6c2a08191968787e27ecb12bf succeeded 2026-10-14T23:23:52.562002+00:00. GitHub code commit 860ccb7. Humidity, daily lows and warm-night proxy appear in monthly charts/table; GHSL urban-centre density is in a folded location detail. Informational only; scoring, qualifying days, ranking and filters unchanged. Anonymous live checks passed with real monthly API: six charts,12months,eight table columns,series/heatmaps,Miami density2059people/km²,World/Europe/USA exact map arrays and parameters equal predeploy baseline,390px no overflow,zero JS errors. Initial30-second external-API test timed out; correct90-second test passed without production changes. Test fixture freezes prechange monthly core independently of repository HEAD. No DNS or Cloudflare service/KV changes. Temporary publication archive removed.

## 2026-10-14 — floating controls and optional daily lows

Luiz authorized publication after correcting the preview's full-width Highlights bar and oversized help spacing. Highlights now uses content width on desktop and a constrained responsive width on mobile. Field help lives at the fieldset header; inherited disclosure padding is reset. Keyboard/tap disclosure and reduced-transparency fallback remain. Desktop/mobile screenshot and actual-width/disclosure/overflow checks passed.

Optional daily minima remain off by default (initial 12–22°C). Temperature uses 0.5 times the greater high/low deviation, never their sum. Both active ranges must pass for a comfortable day. All 514,194 cell/year audits passed. Default-off maps restore exactly; global tab equality and PNG checks passed. Data import and 315 MB derived minimum archive remain remote. Existing sunshine Worker gained only an allowlisted minimum-v1 route to immutable release assets, with edge cache, public CORS and browser no-store; existing static sunshine assets retained. No KV, new Worker, DNS or other-project changes. Browser verified the production-ready endpoint before Site publication. See docs/DAILY-LOW-PREVIEW.md and audit JSON evidence.

Published Sites v25, source 7ee3d6e7a103972865047676b2f079fcde020bff; deployment appgdep_6ad0239a410c819192ca19b6f7db7398 succeeded at 2026-10-15T00:51:54.996307+00:00 (October 14 in São Paulo). Anonymous https://comfy.lfsadigital.com checks passed for content-sized Highlights, help disclosure, mobile overflow, World/Europe/USA values, default-off exact restoration, PNG export and zero page errors. Temporary publication archive removed after successful save and live checks. No GitHub main push in this publication turn.

## 2026-10-14 — Apply obstruction and revised defaults

Reproduced Luiz's immersive-map obstruction. The weather form's scroll area and footer could exceed the sheet, and mobile navigation wrapped over Apply. The sheet now budgets its complete height, keeps Apply outside the scrolling fields, and reserves the measured navigation height. Mobile map actions stay in one horizontally scrollable row. Actual hit tests and clicks passed at 1920×930 immersive, 1440×1000 normal and 390×844 immersive; see docs/WEATHER-APPLY-CHECK.json.

New fresh-link defaults: highlight score ≥7 and days/year ≥120; high 18–28°C; optional low 14–28°C, still off; rain ≤4 mm. Sunshine remains optional, off, with 6 h initial minimum. Explicit URL selections remain respected. Weather Reset uses the new weather defaults. Formula and source are unchanged.

GitHub Actions run 38666386588 generated four standard combinations (high only, high+low, each with/without 6h sunshine) for every year and the full period remotely. Passed 2,056,776 cell/year/mode checks, including score bounds and comfortable-day subset checks. Compact maps are served through the existing Comfy data endpoint; no bulk Mac files, KV, new Worker or other-project changes. Browser fresh-default, all-four-mode, Reset and PNG checks passed; see docs/REQUESTED-DEFAULTS-CHECK.json. Publication result follows.

Published v26: source 21431679fb0275a5481db4d86c0e1c704e1fa529; deployment appgdep_6ad02ed083488191b837b32ba94afeae succeeded 2026-10-15T01:39:44.767652+00:00 (October 14 São Paulo). Live anonymous fresh-default/all-mode/Reset/PNG checks and actual Apply clicks in all three sizes passed. No page errors. Explicit older URLs retain their selections; root URL uses revised defaults. Temporary publication archive removed.

## 2026-10-14 — daily-low default enabled

Luiz explicitly authorized publication. Fresh visits and Weather Reset now enable daily lows at 14–28°C, while sunshine remains off. Explicit lows=0 is preserved in share URLs so users can still disable and reload. Existing precomputed low maps are reused; source and formulas are unchanged. The daily-low monthly chart shows its selected band; sunshine has no band while disabled. Local default/reset/chart/PNG checks passed. Live publication verification follows.


## 2026-10-25 — optional AQI publication candidate

User explicitly requested production publication. Applied the reviewed AQI feature to current Sites v31 source 2be68ec9a477e052566959c8dbf09cdb25cd07da, preserving its newer temperature controls, climate query service, monthly service and cross-request isolation fixes. No previous source version was restored. AQI is off by default, informational, with complete 2023–2025 CAMS global years and independent period/coverage; comfort scores, days, ranking and exports remain unchanged.

The four-width real-application browser suite passed against this integrated source, including keyboard, URL reload, data races, unavailable/error/retry states, computed text contrast and identical climate arrays/parameters/ranking under AQI changes. Query-service canonicalization, compact-response, annualization, cache isolation and request-concurrency tests passed. Build succeeded with the existing locked dependencies. Previous real-source six-probe CI remains https://github.com/lfsadigital/europe-thermal-comfort/actions/runs/40235522951. Deployment receipt follows after publication.

## 2026-10-25 — AQI control moved into Weather

User corrected the placement: AQI belongs with optional Sunshine in Weather. The single opt-in and AQI period selector now live immediately after Sunshine and use Weather draft/Apply/Reset behavior. Applied history appears in the summary; below-map results link back to Weather. AQI-only Apply compares climate values semantically and preserves the exact score/day arrays without climate recalculation. Browser regression passed at 1440/768/390/320px with keyboard, pending state, reset, errors/retry/cancellation, URL restoration, exact initial array identity and no page errors. Existing LFSA styling preserved; scoped review's material comparison fix resolved. The control is explicitly labeled Show air quality history; pollution-based exclusion of cities/map results is a separate unanswered clarification, not a shipped claim.


## 2026-10-25 — real AQI map and Top 10 filtering candidate

User explicitly confirmed excluding places above the chosen AQI limit from map and Top 10 while retaining Confi10. Implemented inclusive historical-median threshold, default100, independent2023–2025 period and conservative missing-data exclusion. Only AQI-verified qualifying city points show while continuous climate shading is hidden; original climate arrays/parameters/day counts remain unchanged and disable restores them. Ranking checks sorted cities until ten qualifying representatives, including alternative cities within a shared climate cell; bounded40-candidate scans expose provisional/continue controls. Visible-city verification uses8-city batches. Source summary endpoint validates full annual records, caches compact aggregates, and bounds request-owned concurrency.

Backend/core/filter and full browser→actual backend→synthetic provider→map/ranking tests passed. Four widths1440/768/390/320, inclusive100, relaxed500 restores exact original ranking, strict50+continuation, missing/sourcefailure/retry/stale cancellation, default-off/no fetch, URL/reset,44px/nooverflow/no pageerrors and exact original score/day array objects. Review found timeout honesty and shared-cell representative defects; both fixed, regression-tested and scored resolved. Original climate query regression and build passed. Publication and real-source route probe follow.


## 2026-10-25 — direct-source correction after live quota failure

Native v34 deployment succeeded but live source verification failed: the shared Cloudflare origin received Open-Meteo429, producing an honest unavailable response. This is not counted as successful live filter verification. Removed the new AQI proxy and restored the pre-existing climate/monthly Worker source. City checks now use the same public API directly from each visitor browser, with at most2jobs, year-weighted4500ms start pacing, cancellable waits and Retry-After honored even on exhausted retries. No proxy/IP rotation or paid service added. Latest full year2025 is the default, with explicit2023–2025 still available. Combined-range input is split into validated annual records; yearly UTC axes/coverage/statistics stay exact. Fixture end-to-end, range, quota, cancellation and existing climate regressions passed; real direct-path verification follows publication.

## 2026-10-26 · Keep missing AQI without a penalty

User policy correction: exclude only known above-limit historical AQI; retain missing, pending, insufficient and failed checks in map/Top 10 with explicit unknown labels and hollow map/export markers. Climate scores and day counts remain unchanged. The AQI-specific neutral basemap behavior remains unchanged.

## 2026-10-26 · Daily AQI integration candidate

User approved optional AQI in the shared comfort calculation, largest contiguous 3-hour mean per UTC day (at least 22 valid hourly values), 1 point per 50 above an inclusive user limit (100 initially), common 2023–2025 period, and no penalty/exclusion for absent AQI. New query engine, coverage wire field, checksum-verified daily archive delivery, Weather control, map/ranking, selected history, URL, cancellation and PNG are implemented. Four-width synthetic browser checks and 10,000 exact off-state parity checks passed. The global remote source build and real API checks must finish before publication. See docs/AIR-QUALITY-DAILY.md.

Global AQI archive now validated: run40391731987, dataset cams-global-max3h-425950138cae91b1,126annualchunks,85699nodes,1096dates,93921747/93926104valid dailyvalues. All6winter/summer APIcomparisons passed within integer-displayrounding. Checkpoint restored without reimport after upload-path correction; source TLS retries recovered. The installed descriptor matches the node-gridSHA256. Preparing native publication and real-site checks.


## 2026-11-17 — support, sponsorship and custom-domain verification

Published support work through v42–v45. Final application v45 source is `3102b6c55d9da056327f08777a47fde8d566db35`; saved version `appgprj_6acc3bb3fcd4819181f55b4757d282a8~appgver_1f047c0d78a88191881ba37285550c35`, deployment `appgdep_6afc8a1cba588191899032a6b6e0fdaf`, native status succeeded at 2026-11-17T17:09:00.642403+00:00.

Canonical URL: https://comfy.lfsadigital.com/. Platform URL is an alias for the same existing project. Final design has compact header links, official Ko-fi branding and a small sponsor space beside the desktop hero. Both sponsor actions open email, not X. The lower support area retains Ko-fi and sponsor-independence copy. No climate computation, data, DNS, audience or infrastructure was changed by the support work.

Custom domain recheck: HTTPS HTTP 200; fetched HTML matched v45 source byte for byte; domain/provider/SSL active, last error null. Early browser certificate and tunnel failures were verification-environment limitations, not a diagnosed production certificate fault. No DNS or certificate repair was required.

Scoped local Chromium checks passed at 320/390/768/1440px, with no horizontal overflow, one sponsor slot, correct mailto destinations and keyboard focus. Scoped Impeccable detector and build/whitespace checks passed. Physical touch, other browser engines and external email-client launch were not tested. Doctor setup was fixed locally and returned no findings; hook delivery may require harness reload. No development credentials, local consent or binaries were added to production.

Documentation reconciliation updated current entrypoints, preserved historical reports and added `docs/SUPPORT-RELEASE.json` with frontend source hashes. Documentation-only updates do not republish or increment the application version.


## 2026-11-18 — GitHub source migration

Imported the current application into GitHub `main` in [PR #2](https://github.com/lfsadigital/europe-thermal-comfort/pull/2). Verified 92 frontend hashes against the v45 receipt and ran the query checks and production build. The live application remains Sites v45. See [publishing](docs/PUBLISHING.md) for future releases.
