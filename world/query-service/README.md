# Compact climate query service

Keeps raw daily archives off the browser, preserves the existing ERA5 daily formula, and caches aggregate responses. The static app requires both same-origin routes for custom rules and monthly charts; `python -m http.server` alone serves only the standard-map preset.

From the repository root:

```sh
node world/query-service/check.mjs
node world/city-data/temperature-bounds-check.cjs
node world/query-service/local-server.mjs
```

The preview listens on `127.0.0.1:8778`. It uses curl for the configured environment proxy/CA and bounds its memory cache to 8 MiB. `worker.mjs` is the Cloudflare/Sites entrypoint; it uses one decoded climate job and one monthly job per isolate, cache expiration and in-flight sharing, with no new storage bindings. Build with an externally installed esbuild:

```sh
COMFY_ESBUILD_PATH=/path/to/esbuild node world/query-service/build-site.mjs /tmp/comfy-site-build
```

The output is `server/index.js`, `server/wrangler.json`, `client/`, and `.openai/hosting.json`. It was validated in Miniflare/workerd with an ASSETS binding. To publish it on Sites, use the existing Comfy Days project/source repository; preserve its public audience and custom domain. Do not publish a static-only artifact after this migration.

`build-defaults.mjs` streams the public daily archives with two bounded jobs and writes only the two compact standard presets, not the raw archives. Running it is a remote data-processing operation and requires authorization. The currently generated presets need not be rebuilt to test or publish this change.

Browser checks (Playwright and a Chromium executable must already be available):

```sh
COMFY_PLAYWRIGHT_PATH=/path/to/playwright COMFY_CHROME_PATH=/path/to/chromium node world/city-data/performance-flow-check.cjs
COMFY_PLAYWRIGHT_PATH=/path/to/playwright COMFY_CHROME_PATH=/path/to/chromium node world/city-data/temperature-controls-check.cjs
```

The performance check uses real public data through the local query backend and records its timings under `world/site/docs/PERFORMANCE-LATEST.json`. A first unseen custom rule can still take about a minute to complete globally on this local backend; the selected spatial part is prioritized and cached rules complete much faster. Local timings are not production edge latency. The default six-year map uses a ~1.13 MB preset and requires no query request.
