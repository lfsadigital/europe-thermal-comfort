# Current state · 2026-11-18

The canonical site is https://comfy.lfsadigital.com/. Latest confirmed application publication is Sites **v45**, source `3102b6c55d9da056327f08777a47fde8d566db35`. See [the machine-readable receipt](SUPPORT-RELEASE.json).

## Source authority

GitHub `main` is the source of truth. The migration merged on 2026-11-18 in [PR #2](https://github.com/lfsadigital/europe-thermal-comfort/pull/2). ChatGPT Sites hosts production. Publish reviewed GitHub revisions using the [manual release workflow](PUBLISHING.md).

Frontend: `world/site/dist/`. Backend: `world/query-service/worker.mjs`. Local full preview: `node world/query-service/local-server.mjs`; build: `npm run build`. Static HTML alone does not provide the custom climate/monthly routes. The [root README](../README.md) describes current defaults and commands; [query service](../world/query-service/README.md) covers backend verification.

## Final support design

- Header: Lab, Sponsor (email), and Ko-fi support.
- Hero: one small dashed sponsor space beside the title on desktop; stacks under the introduction at 900px and below.
- Sponsor contact: `mailto:lfsa.business@gmail.com?subject=Comfy%20Days%20sponsorship`; no sponsorship link opens X.
- Support: direct Ko-fi link, official locally hosted cup mark, no extra JS or payment embed.
- Footer: LFSA Digital Lab and existing social/source credits. X remains a social link.
- Expanded map hides the header, hero and lower support section.

## Verification and limits

Custom-domain HTTPS returned HTTP 200 and its HTML matched v45 source byte for byte on 2026-11-17. Provider status and SSL were active, with no last error. Local Chromium presentation was checked at 320/390/768/1440px; no horizontal overflow, one sponsor placement, correct mailto destinations and visible keyboard focus. Impeccable detector returned no findings. Build and diff checks passed. Live browser rendering, physical touch, other browser engines and email-client launch were not verified by those checks.

Impeccable Doctor setup was repaired in this checkout, including a local engine and hook manifests, and returned no findings. Developer tooling, local consent and binaries are checkout-local; the harness may require a reload. This is not a claim that another workstation has the same installation.

## Documentation precedence

Use this file, README and current source for present behavior. DESIGN describes the final interface. OPERATIONS is chronological. Older feature docs, preview reports, JSON test outputs and release receipts retain their dates and scopes; their old formulas, UI states and results must not override current implementation. In particular, AIR-QUALITY.md describes the previous median-based city filter; AIR-QUALITY-DAILY.md describes the current daily scoring rule.
