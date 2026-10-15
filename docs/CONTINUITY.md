# Comfy Days: continuation in Codex Cloud

Prepared on 2026-10-15 from GitHub backup commit `c3ae1402d70bd778cbc973e6321d06b25c337023`. This is a handoff document, not authorization to push, deploy or run a data rebuild.

## Open the correct project

The active application is **`world/site`**, with static output in **`world/site/dist`**. The Europe-only application and Python pipeline at the repository root are historical. Do not start a new Europe implementation or apply its old 100-point formula.

The code baseline is `lfsadigital/europe-thermal-comfort`, branch `main`. This handoff is on `docs/cloud-continuity`; select that branch to read these new instructions until they are merged. The last verified publication is Sites **v27**, source commit `53b536eddf21e04382027f81cc5174365c3b5ee4`, at https://comfy.lfsadigital.com/. The GitHub and Sites commit IDs differ because they are separate repositories. [PUBLISHED-SOURCE.json](../world/site/docs/PUBLISHED-SOURCE.json) records hashes for 60 published application files; all 60 matched the backup during the migration analysis. No Cloud environment or Cloud browser validation has been completed yet.

## Read these existing records first

1. [COMFORT-RULES.md](../world/site/docs/COMFORT-RULES.md): current formula, defaults, examples, annualization, chart bands and missing-data behavior.
2. [world/site/README.md](../world/site/README.md): frontend and data architecture.
3. [DESIGN.md](../world/site/DESIGN.md): LFSA visual system.
4. [world/site/OPERATIONS.md](../world/site/OPERATIONS.md): publication and live-check history, including v27.
5. [ERA5 migration](../world/site/docs/ERA5-MIGRATION.md), [Miami validation](../world/site/docs/MIAMI-SOURCE-VALIDATION.md) and [daily-low preview audit](../world/site/docs/DAILY-LOW-PREVIEW.md): source decisions and scientific caveats. The preview report's earlier defaults are historical.
6. [Data license update](../world/site/docs/DATA-LICENSE-UPDATE.md), [municipal homicide](../world/site/docs/CITY-HOMICIDE.md) and [EPI budget](../world/site/docs/EPI-BUDGET.md): permitted sources and coverage limits.

Current defaults: high **18–28°C**, low **enabled at 14–28°C**, precipitation **≤4 mm/day**, sunshine **off** with 6 h/day initial minimum when enabled. Highlights require score **≥7** and comfortable days/year **≥120**. The temperature penalty is 0.5 times the greater high/low deviation, never their sum. Do not duplicate or revise the full specification here; maintain COMFORT-RULES.md.

## Infrastructure record that was only in the Mac operations log

The local `world-comfort/OPERATIONS.md`, entry dated **2026-10-13, “obsolete NOAA Worker removed”**, records maintainer-authorized deletion of only the unused Comfy Worker **`comfy-days-climate-v5`**. The deletion returned HTTP 200. Read-back identified the retained Comfy data Workers as **`comfy-days-climate-era5`** and **`comfy-days-climate-sunshine`**. This removed the old NOAA rollback endpoint; it is not a usable rollback target.

The same record reports post-removal anonymous checks passing for filters, missing-data handling, region parity, mobile and both PNG views, with zero page errors. It also records a 404 for an exploratory `/era5-v1/manifest.json` request because that was not a deployed asset. Do not diagnose service failure from that nonexistent path. These are historical observations, not a fresh infrastructure inventory. No other project's resources were changed in that operation.

The interface is hosted by Sites; GitHub is its code backup. Climate data uses the existing Cloudflare endpoints. Do not migrate hosting, recreate the retired Worker or change DNS as part of environment setup.

## Prepare a small Cloud development environment

Run commands below from the **repository root**. The frontend is buildless; no application package installation or root Python scientific stack is needed to serve it. Use Node.js and Python 3. Network access is needed for data, map tiles and monthly charts. Allow the actual hosts used by the app, including `comfy.lfsadigital.com`, the two Comfy data Worker hostnames in the metadata, `archive-api.open-meteo.com` and `tiles.openfreemap.org`. Dependency installation needs its package/browser download hosts too. Validate connectivity rather than assuming a domain setting supplies authorization.

### Source and pure calculation checks

```sh
git status --short
node --check world/site/dist/app.js
node --check world/site/dist/climate-worker.js
node --check world/site/dist/monthly-charts.js
node world/city-data/daily-low-check.cjs
node world/city-data/climate-context-check.cjs
git diff --check
```

These checks were used before the handoff; rerun them in the actual Cloud environment. The first calculation check covers 10,000 direct-reference cases. The context check reads the included small urban-density table and historical monthly-core fixture.

### Restore only legacy map baselines, then serve

```sh
python3 world/restore_default_maps.py
python3 -m http.server 8777 --directory world/site/dist
```

Keep the server in a separate terminal/session. Open port 8777 through the Cloud environment's supported preview mechanism. The restore command fetches 21 SHA-256-checked baseline arrays, about **18 MB**. Current defaults use compact remote presets; do not fetch the full ERA5 archive. If restore gets 403 or a hash mismatch, stop and report the network/version issue. Do not disable its hash checks.

### Browser checks, only if supported by the selected environment

Install test dependencies outside the repository in the Cloud VM:

```sh
npm install --prefix /tmp/comfy-cloud-browser --no-save --package-lock=false playwright
export COMFY_PLAYWRIGHT_PATH=/tmp/comfy-cloud-browser/node_modules/playwright
node "$COMFY_PLAYWRIGHT_PATH/cli.js" install --with-deps chromium
node world/city-data/requested-defaults-check.cjs
node world/city-data/weather-apply-check.cjs
node world/city-data/daily-low-global.cjs
git status --short
```

Run the export and test commands in the same shell, or configure `COMFY_PLAYWRIGHT_PATH` as an environment variable. The shared browser launcher first checks installed Playwright, then this override; its Mac fallback is not a Cloud installation. Do not set the Mac Chrome path on Linux. Browser execution and visual inspection in the selected Cloud mode remain **unverified**; if unavailable, report the limitation and arrange a separate authorized UI check.

The default test checks the four standard low/sun combinations, Reset, low chart band, sunshine off and PNG. The Apply test clicks the button at 1920×930 immersive, 1440×1000 normal and 390×844 immersive. The global check compares region-tab values and restores the explicit low-off baseline. The tests use the local server by default; do not point them at production unless live verification is specifically requested. They write reports under `world/site/docs` and images under `world/share` or `.impeccable/review`; review generated diffs. Older test scripts can assert obsolete defaults or require missing audit inputs; do not use them as a blanket current-release gate.

## Local material worth preserving

These are candidate records to review, not instructions to copy whole folders:

| Local project-relative location | What to retain |
|---|---|
| `world-comfort/OPERATIONS.md` | The obsolete-Worker deletion record summarized above; retain the original locally for provenance. |
| `world-comfort/site/.openai/hosting.json` | Preserve locally for future authorized publication. Do **not** copy the file into this public repository; confirm the existing Sites project through authorized tools when needed. |
| `world-comfort/cloudflare-plan-verification.md` and `cloudflare-kv-audit-2026-10-13.md` | Historical operational findings; review/redact before extracting Comfy-only facts. They are not a current billing check and can mention other projects. |
| `world-comfort/city-data/ui-polish-check.cjs` and selected recent UI captures | Optional regression evidence for floating Highlights and help spacing; review paths and fixtures before promoting a test. |
| `world-comfort/share/current-defaults.png` and selected current exports | Optional examples, regenerable from the application; not required for code execution. |
| Project instruction and design references | Project rules are captured in root AGENTS.md and the existing DESIGN.md. Install only required skills through an approved method; workstation-specific skills are not repository dependencies. |

The separate Mac source folder can have older READMEs and older test expectations than this backup. Do not overwrite the updated GitHub documentation with those copies. If additional notes are found later, extract only reviewed public project decisions into this handoff or the existing domain document. Do not copy private notebooks or unrelated notes.

## Not needed to continue

- Mac `.git` directories, source checkout history duplicates, caches, `__pycache__`, installed packages and temporary publication archives.
- Old PNGs/screenshots, intermediate references and exploratory source downloads, unless a specific regression requires them.
- The local 21 baseline arrays: restore the small verified copies when needed.
- Raw ERA5 files and the complete derived daily archive: use remote data; bulk rebuilds need separate authorization and a remote batch environment.
- Retired NOAA service files as an active dependency, or the root European implementation as the current app.
- Tokens, OAuth state, authentication configs, private notes or unrelated project material. Never put these in the public backup.

## Branch-push deployment check (2026-10-15)

Before publishing this documentation branch, the repository and Comfy build settings were read back: all three GitHub workflows use only `workflow_dispatch`; repository webhooks were empty; GitHub Pages was disabled; and both retained Comfy Workers had no Workers Builds triggers. Sites uses a separate source repository. A push of these two documentation files has no deployment trigger in the checked configuration. Recheck these settings if deployment integrations are added later; this is not permanent authorization to publish.

## First Cloud task and publication boundary

Start from `docs/cloud-continuity` at the reviewed continuation commit (or the corresponding `main` commit after a separately approved merge), read root AGENTS.md and this file, verify current source hashes, run pure checks, serve the app and assess browser-test support. Report missing network access or tools before proposing product changes. Do not rebuild climate data for setup.

Deployment needs fresh authorized Sites access and the **existing** project identity; GitHub push alone does not publish the app. Do not assume the workstation's authenticated connectors or this chat's available tools exist in the new session. Keep deployment access out of the initial environment unless required and authorized. Reuse existing docs and append dated evidence rather than replacing history.
