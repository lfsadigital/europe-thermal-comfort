---
name: Comfy Days · LFSA
description: Climate comparison with LFSA branding and readable data views.
colors:
  navy: "#0a2463"
  deep: "#061640"
  gold: "#f5c518"
  blue: "#2da0e0"
  surface: "#ffffff"
  line: "#d8dfeb"
  muted: "#50617d"
  dark-text: "#f4f4f5"
  dark-muted: "#cbd5e1"
  panel: "#f5f7fb"
  empty: "#eef2f8"
typography:
  display:
    fontFamily: "Space Grotesk, Inter, sans-serif"
    fontSize: "clamp(34px, 4vw, 48px)"
    lineHeight: 1.08
    letterSpacing: "-.035em"
  headline:
    fontFamily: "Space Grotesk, Inter, sans-serif"
    fontSize: "22px"
    letterSpacing: "-.5px"
  body:
    fontFamily: "Inter, system-ui, sans-serif"
    fontSize: "16px"
    lineHeight: 1.5
rounded:
  panel: "20px"
  fieldset: "12px"
  button: "10px"
  input: "8px"
  tile: "5px"
spacing:
  compact: "6px"
  field: "16px"
  section: "24px"
components:
  button-primary:
    backgroundColor: "{colors.gold}"
    textColor: "{colors.deep}"
    rounded: "{rounded.button}"
    padding: "10px 16px"
  panel:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.navy}"
    rounded: "{rounded.panel}"
    padding: "24px"
---

## Overview

This records the local source in `dist/styles.css`, `dist/lfsa-brand.css`, `dist/index.html`, `dist/monthly-charts.js`, `dist/city-filters.js`, `dist/city-map.js`, `dist/discovery.js`, `dist/workspace-ui.css`, `dist/workspace-ui.js`, `dist/geo-map.js`, `dist/map-tiles-worker.js`, and `dist/app.js`. The city homicide source contract is recorded in `docs/CITY-HOMICIDE.md`. The workspace stylesheet loads after the base and brand stylesheets. `dist/index.html` records the narrow map refinement direction. This document records source behavior; `docs/MAP-FIRST-FILTERS.md` records the candidate verification and its scope. No PRODUCT.md was found in this scoped documentation pass; the incumbent LFSA identity is retained.

**Creative North Star: "Clear climate data within the LFSA visual identity."**

Keep the established navy page, white work surfaces, gold actions, blue secondary accents, and compact information hierarchy. The map controls, city filters, and monthly views extend this system. The local header mark is a gold sun over a blue horizon on deep navy (`dist/logo.svg`). The favicon uses a simpler version of that mark (`dist/favicon.svg`), with local PNG companions at 32px and 180px. These assets replace the prior smile mark; keep their LFSA palette and native SVG shapes.

## Colors

Primary navy carries headings and text on light surfaces. Deep navy anchors the page gradient and region controls. Gold marks primary actions, selected regions, focus, and temperature comfort shading. Blue identifies secondary metrics and precipitation. White panels use pale borders and muted blue text. Climate map colors encode data independently of brand action colors.

**The Data Color Rule.** Preserve climate encoding. Do not assign a brand color a new weather meaning.

## Typography

Space Grotesk serves headings, the brand, and strong metric values. Inter serves body text, controls, notes, and tables. Numeric values use tabular figures where the source sets them. Keep the existing heading scale and compact supporting labels.

Monthly tiles use month labels (12px) and values (15px). Chart notes and table values use compact text (12px). Keep units and missing-data text readable.

## Layout

Header, main, and footer share a centered maximum width (1320px), with horizontal padding (32px desktop; 16px at widths up to 800px). White sections use the section spacing token. The map fills its work surface. Location details float over the map only after selection, with a close button; empty metric cards stay hidden. The panel is narrower on mobile and moves toward the bottom. Ranking rows use two columns, then one below 650px.

Monthly plots use two columns, then one up to 850px. Line/bar SVGs retain a minimum width (620px) inside a horizontally scrollable, focusable container. They must not shrink until labels become unreadable. Native monthly heatmap tiles use six columns on desktop and four up to 650px, with compact gaps. Map filter fields use one column inside the overlay panels.

Region tabs remain sticky near the top (8px). Weather, Colors, Cities, and Export PNG share a toolbar over the map. The map is 580px high on desktop and 520px up to 650px. The toolbar sits 12px from the map edges, then 10px on mobile. Panel width is capped at 360px and its height stays within the map. City controls scroll inside the panel. Weather fields scroll between the fixed panel heading and visible Apply footer. Top 10 remains below the map and monthly views; its Edit city filters action opens the Cities panel, centers the map, and focuses the panel summary. Panel scrolling must not pan or zoom the map.

Only one filter panel can be open. Escape closes the open panel and returns focus to its summary; a pointer action outside the toolbar also closes panels. Opening through an edit link respects reduced motion when centering the map. Mobile number fields and selects use 16px text and a minimum height of 44px; panel summaries, export, toggles, and nested disclosure summaries also use 44px targets.

## Elevation & Depth

Panels are primarily flat white surfaces separated by borders. Region tabs use a restrained shadow; search results use a stronger shadow to sit above the map. The map HUD has a small shadow. Map toolbar controls use a small shadow (`0 3px 10px #06164018`); open filter panels use a stronger shadow (`0 8px 28px #06164030`) above the map. Preserve this limited elevation vocabulary. Do not add decorative depth to charts or ranking rows.

## Shapes

Large sections have soft panel corners. Fieldsets and metric cards use the fieldset radius. Inputs and standard buttons use their own smaller radii. Badges are pill shaped. Heatmap tiles use the tile radius. Borders separate sections and table rows without creating heavy frames.

## Components

Buttons retain navy text on white, gold primary actions, and navy active switches. Selected region controls use gold on deep navy. Preserve visible focus outlines (3px gold, offset 3px); chart points use their existing focused mark treatment. Base primary actions and region controls have a minimum height (44px); map toolbar controls and Apply use 42px on desktop and the toolbar uses 44px on mobile. Disabled fields use pale fill and muted text.

**The Weather Boundary Rule.** City context filters affect the city ranking and optional city markers. City context must not change climate values, climate selection, the comfort formula, or weather rules. Weather edits remain drafts until Apply weather; a blue dot and Changes not applied text expose that state. Pending weather edits block PNG export. City limits update immediately with a short debounce. Invalid city drafts preserve the last valid state and block export. Loading and failure status stay visible. Applying weather closes the Weather panel.

The On the map select has two modes: Matching cities (`results`, default) and No city highlights (`ranking`). Old `citymap=markers` URLs normalize to `results`. Matching cities shows only cities that pass every active city filter with known data and satisfy the enabled climate highlight limits. Missing optional data stays eligible in the ranking but receives no map highlight. No city highlights removes the city-filter marker layer while keeping ranking filters active. Changing map mode or climate highlight limits does not change ranking eligibility. Native sliders complement exact numeric fields and share their enabled state. Slider ranges are Nomads (0–5), monthly budget (0–10,000 USD), and homicide (0–30 per 100,000). Exact fields retain the wider limits for budget (1,000,000 USD) and homicide (300 per 100,000). Shared URLs retain enabled filters, exact values, crime year, homicide geographic level, and marker mode. Enabled homicide filters write `homgeo=city` or `homgeo=country`. Old URLs with `crime=1` and no `homgeo` retain country mode.

City filters are independent optional controls: minimum Nomads score (0–5), maximum nomad monthly cost (USD estimate), and maximum homicide rate (per 100,000) with an explicit geographic level and crime year. The geographic selector offers City / municipal area and Country / area. City mode and 2024 are the defaults; all three filters start off on a clean URL. Saved URL parameters can restore enabled filters. Missing optional Nomads score, monthly cost, or homicide values remain unknown and stay in ranking results when the corresponding filter is active. A known failed limit excludes a city even when another optional value is unknown. Missing local homicide never falls back to a country rate; a published zero remains valid. The crime year is separate from the weather period. Use explicit unavailable text and loading/error status.

Local homicide uses FBI municipal agency service areas in the USA and Eurostat city or greater-city areas in Europe. Source areas can differ from named city boundaries, and the two sources use different definitions. The 2024 matched coverage is 6,900 USA cities and 11 European city/greater-city areas; coverage changes by year. Country mode uses UNODC national context, shared by the country’s cities. Show source links for FBI, Eurostat, and UNODC, the Nomads retrieval date, and the UNODC release date in country mode. Selected-city details show local and country rows separately, with year, rate, source, local area, geographic boundary label, available count, and source warnings. FBI rows also show the source population and the Table 8 requirement for 12 complete reporting months. Eurostat rows state that monthly reporting completeness is unknown. Homicide is not a complete safety measure.

**The Map Highlight Rule.** Colors starts enabled with inclusive minimum score (8 / 10) AND minimum comfortable days (180 / year). Both limits are adjustable. These limits control map display only; original score/day arrays, scoring formulas, ranking, and selected-cell values stay unchanged. Each raster pixel uses the nearest original climate cell to decide whether it passes both limits. Failed or missing cells have transparent raster alpha over the neutral base. Smooth interpolation affects displayed values only and cannot make a failed cell qualify. Grid display uses the original cell values.

**The Marker Visibility Rule.** The map city universe starts at 1,000 residents in the selected region, with climate-cell distance at most 0.75° and finite score/day values. Only verified matches become visible points. Active population, optional city limits, and enabled climate highlight limits must all pass. No gray failure markers or unknown rings appear in this view. The old marker legend is hidden. Hover exposes city values and available context; clicking selects the city.

Overview decluttering applies to matching points. At zoom below 3, show cities with at least 500,000 residents; from 3 to below 5, show cities with at least 100,000; from 5, use the full eligible map city universe. Materialize points within the current bounds plus 25% padding on each axis and refresh after moveend. Regional match, excluded, and retained-unknown counts appear in the information popover, together with loading and empty-view status. Ranking independently retains the chosen population minimum and labels missing optional data.

**The Quiet Surface Rule.** Put technical explanations behind information controls or About the data. Information works on hover, keyboard focus, and tap. Keep sources available inside these disclosures. Remove the old quick-city buttons and hero eyebrow. Show selected-location details only when a location has been selected; closing the panel clears its visible selection state. Do not fill the resting map with empty cards.

**The Expanded Workspace Rule.** Expand map opens a fixed full-window workspace, with region, metric, period, search, filters, and PNG export available. It uses the page workspace rather than native browser fullscreen. Escape exits; Tab and Shift+Tab wrap focus inside the expanded workspace. Entry and exit focus the expand/exit control. The responsive map uses the remaining workspace height; local desktop and mobile captures document a map height above 400px in the checked viewports.

**The Export Fidelity Rule.** PNG uses the actual rendered MapLibre canvas at the current camera, weather metric, period, and applied filters. It preserves the selected map mode, visible matching city points, climate highlight mask, and live decluttering. It does not reconstruct the climate raster or use the legacy geographic marker drawing method. The 2400×1800 frame includes the applied rule summary, city mode and missing-data policy, inclusive climate highlight thresholds, palette, attribution, and social handles. Neutral land is labeled as outside highlight limits or missing weather records. Export metadata records the applied climate highlight settings. Export waits for map rendering and reports a timeout as failure. Pending weather, invalid city drafts, and active calculation or required city-data loading block export.

**The Cell Fidelity Rule.** Monthly views follow the selected exact ERA5 cell and selected weather period. Display cell coordinates, period, UTC-day basis, and Open-Meteo daily API attribution. Disclose API display rounding differences from the score archive. Keep the monthly data table available.

Temperature uses average daily high as a solid line and daily mean as a dashed line. The shaded band reflects the actual selected temperature limits in line mode. A monthly average inside that band does not mean every day qualifies. Precipitation uses monthly totals, including snow water equivalent, and bars in series mode. Sunshine uses average hours per day; its minimum shading appears only when the sunshine rule is enabled in series mode.

Monthly heatmaps use native tiles without a y-axis. Each chart normalizes intensity within its own values; darker means higher, not better or more comfortable. Show numerical values, units, missing values, and accessible labels. Temperature tiles show daily highs; daily means remain in the table. Do not show comfort-band shading in heatmap mode.

## Do's and Don'ts

- **Do** preserve LFSA tokens and the existing map and rules hierarchy.
- **Do** keep source, time basis, units, and missing-data meaning close to the relevant data.
- **Do** keep monthly charts readable through scrolling and provide table access.
- **Don't** mix independent city context with weather scoring or label national homicide as city crime.
- **Don't** treat relative heatmap intensity as an absolute comfort scale.
- **Do** keep filter scrolling inside the map, Apply visible, and Escape focus restoration intact.
- **Do** label retained unknown optional data in ranking and information; highlight only verified matches on the map.
- **Don't** claim a complete page audit from this scoped refinement. Only the three review fixes were reported resolved. Current local captures are `../share/quiet-immersive-desktop.png`, `../share/quiet-colors-desktop.png`, and the other `../share/quiet-*` desktop/mobile captures, with `../share/quiet-map.png` for PNG export. The refinement is published as version20; deployment and live verification evidence are recorded in QUIET-MAP-RELEASE.json and OPERATIONS.md.
