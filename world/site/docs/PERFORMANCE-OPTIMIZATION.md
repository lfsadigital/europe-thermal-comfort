# Browser performance optimization

User authorized measurement, local optimization, testing and publication; hosting migration deferred.

Candidate lists cache the same region/population/distance/finite-weather eligibility before optional filters are assessed. Ranking and marker code reuse that candidate set. Rank result retention is bounded to 64 entries, candidate lists to 12 combinations and invalidated when weather arrays change. Climate results are keyed by period and exact weather parameters, held only in browser RAM with a 16 MiB retained-result budget. No disk database, KV, server calculation, new cloud resources or large local weather archive. Existing bounded sunshine file cache remains.

## Before/after measurement

Same local app, Chrome headless, 1440×1000, CPU throttled 4×. Each row is the median of nine synchronous ranking + marker refresh calls, including threshold changes. This measures main-thread refresh work, not INP or time until map pixels finish drawing. The fingerprint of score/day arrays, ranking rows and marker counts was identical. No page errors.

| Region | Nomads filter | Before ms | After ms |
|---|---|---:|---:|
| world | False | 394.7 | 61.9 |
| world | True | 1931.6 | 304.4 |
| europe | False | 560.1 | 9.7 |
| europe | True | 2586.3 | 61.3 |
| usa | False | 405.6 | 5.1 |
| usa | True | 2016.8 | 28.9 |

Initial ready: 4597 ms before, 4211 ms after, one run per version. Network and startup variability are not controlled enough to claim an initial-load gain. Returning to previously loaded mean/2025 eliminates three prepared score/day/coverage requests each time; period values match exactly. First visits still download required data. Timing files retain raw samples, scripts reproduce the measurements.

Climate formulas, raw data, coverage handling, palette and PNG workflow are unchanged. All savings are browser work or avoided requests; existing remote services are unchanged. Small static downloads for tests may occur; no server-side bulk processing or new account workloads were created. Current application scope only: Comfy.

Publication and anonymous verification identifiers will follow in OPERATIONS.md.
