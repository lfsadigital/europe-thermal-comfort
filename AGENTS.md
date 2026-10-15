# Comfy Days working instructions

## Scope and source of truth

- The current application is in **`world/site`**; serve `world/site/dist`.
- The Europe-only implementation in the repository root is historical. Do not use its formula, dependencies or defaults for the current application.
- Start with [docs/CONTINUITY.md](docs/CONTINUITY.md). Use [current rules](world/site/docs/COMFORT-RULES.md), [design](world/site/DESIGN.md) and [release operations](world/site/OPERATIONS.md). Historical reports are evidence of their dated state, not current requirements.
- Current UI defaults come from `uiDefaults()` in `world/site/dist/app.js`. `metadata.json` retains the older archive baseline for compatibility; it is not the live UI-default authority.

## Change control and verification

- Verify before reporting. Distinguish observed results from expectations; call unverifiable information unknown.
- Do not send messages, publish posts, push, deploy, delete resources or change production without explicit, specific maintainer authorization. Execute only the authorized action.
- Limit changes to Comfy Days. Do not modify unrelated projects or shared infrastructure.
- Prefer reproducible source and command-line checks. Do not assume browser tools exist in the selected Cloud environment.
- Preserve the LFSA visual identity and accessibility. Test real Apply clicks, immersive mode, mobile layout and PNG export when changing map controls.

## Data, storage and credentials

- Keep raw ERA5 archives, bulk climate arrays and large build outputs off local workstations. Do not download or create files approaching 1 GB locally.
- Use existing remote data endpoints and compact presets. The optional legacy baseline restore is about 18 MB, not a raw-data import.
- Do not launch import scripts, remote processing workflows, release uploads or infrastructure changes without separate authorization for that work. Running a workflow can write remote resources.
- Never commit tokens, authentication files, private notes, local environment files or personal vault exports. Obtain authorized service access through the environment; do not copy workstation credentials.
- Preserve daily source alignment, UTC aggregation, coverage checks, source credits and licenses. Do not silently substitute data sources or treat missing values as passing.

## Validation and handoff

- Run the relevant commands in [docs/CONTINUITY.md](docs/CONTINUITY.md) from the repository root. Do not install the root historical Python requirements for frontend-only work.
- Run the pure calculation checks for formula changes. Browser checks require a local server, network access and a working Playwright browser; report unavailable checks rather than claiming success.
- Browser tests can write PNGs and JSON reports. Inspect `git status` afterward and review generated changes before including them.
- Keep work on a separate branch. Review the diff, report tests and limitations, and obtain authorization before push or publication. A push to this repository is a code backup, not a Sites deployment.
