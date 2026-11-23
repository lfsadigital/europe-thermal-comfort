# Comfy Days · World, Europe & USA

Live site: [comfy.lfsadigital.com](https://comfy.lfsadigital.com/).

Last confirmed application publication: **Sites v46**, source `fc92c4ff49a2fda2406dd2b55a9f34ccea1530eb`, on 2026-11-23. The platform hostname is an alias for this project; use the custom domain in user-facing links. See [current state](docs/CURRENT-STATE.md), [release receipt](docs/MAP-FIRST-RELEASE.json) and [operations](OPERATIONS.md).

GitHub `main` is the source of truth. ChatGPT Sites hosts production at the custom domain above. Each release is published manually from a reviewed GitHub revision. See [publishing from GitHub](docs/PUBLISHING.md).

## Application and development

The frontend source is `world/site/dist/`. Production also requires the same-origin climate and monthly APIs in `world/query-service/worker.mjs`. The site is deployed as a Worker with static assets; a static-only deployment is insufficient.

From this repository root, with Node.js and the locked dependencies installed:

```sh
npm ci
node world/query-service/local-server.mjs
```

The full development server listens on `http://127.0.0.1:8778`. A Python static server can inspect presentation but cannot validate custom-rule or monthly API flows. API checks require access to the configured public data sources. Keep raw climate archives remote.

```sh
node world/query-service/check.mjs
node world/city-data/temperature-bounds-check.cjs
npm run build
git diff --check
```

Build output is `dist/server/index.js`, `dist/server/wrangler.json`, `dist/client/` and `dist/.openai/hosting.json`. Packaging includes the root `.openai/hosting.json` with the existing project identity, plus `dist/server` and `dist/client`. Use the existing Sites project; preserve its custom domain and public audience. No data rebuild is needed for UI or documentation edits. See [query service](world/query-service/README.md).

## Current rules

Live defaults come from `uiDefaults()` in `world/site/dist/app.js`, not archived defaults in `assets/metadata.json` or old preset manifests. The current temperature controls share a **14–30°C** band, with daily lows enabled; rainfall is **≤4 mm/day**. Sunshine is off (6 h/day minimum when enabled), AQI is off (initial limit 100). Highlights use score ≥7 and comfortable days/year ≥120.

Each UTC day starts at 10. Temperature loses 0.5 point per degree using the larger high/low deviation, never their sum. Subtract rain and enabled sunshine/AQI penalties, then floor the daily result at zero before averaging. Comfortable days must meet the enabled weather limits on the same date. Monthly weather coverage, matched-date alignment, calendar annualization and explicit unknown-data behavior are preserved. AQI uses a common 2023–2025 period or a year within it; unknown AQI adds no penalty. See [daily AQI rules](docs/AIR-QUALITY-DAILY.md), the application and the query core for the full current implementation.

World, Europe and USA are views over the same climate source and calculation. ERA5 supplies weather; CAMS supplies optional AQI. Map tiles, GeoNames, urban context and optional city filters retain their individual credits and licenses. Keep the full credits in the application. Historical scientific/import checks are preserved under [documentation](docs/README.md), with their original scope and date.

## Support, sponsorship and navigation

The header links to [LFSA Digital Lab](https://lfsadigital.com/lab/), sponsorship email and [Ko-fi](https://ko-fi.com/luizalmeida). A small sponsor space sits to the right of the hero on desktop and below the rankings at 760px and below. Both sponsor links use `mailto:lfsa.business@gmail.com?subject=Comfy%20Days%20sponsorship`. Ko-fi support remains below city rankings. Sponsors do not influence scores or rankings.

Styling is in `world/site/dist/project-support.css`; the official Ko-fi cup mark is local in `kofi-cup.svg`. There is no support JavaScript, floating widget or embedded payment panel. See [design](DESIGN.md).

## Evidence and historical records

The v46 HTML was fetched successfully over HTTPS from the custom domain and matched the published application source byte for byte. Domain and SSL status were active with no reported error. Earlier certificate/network failures were limitations of those verification attempts; they were not evidence of a confirmed site certificate defect.

The v46 HTML matched the release build over HTTPS on the custom domain. Local Chromium checks at 390 and 1440 CSS pixels confirmed map visibility in the first viewport, the default metric, score selection after reload, and mobile region selection.

Prior implementation notes are retained in [the archive](docs/ARCHIVE-IMPLEMENTATION.md). Historical release receipts and dated tests remain evidence of their own versions; do not treat them as fresh checks of v46.
