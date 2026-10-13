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

This records the local source in `dist/styles.css`, `dist/lfsa-brand.css`, `dist/index.html`, `dist/monthly-charts.js`, `dist/city-filters.js`, `dist/city-map.js`, and `dist/discovery.js`. The city homicide source contract is recorded in `docs/CITY-HOMICIDE.md`. The brand stylesheet loads last. This is a source inspection; rendered behavior is not certified here.

**Creative North Star: "Clear climate data within the LFSA visual identity."**

Keep the established navy page, white work surfaces, gold actions, blue secondary accents, and compact information hierarchy. The new city filters and monthly views extend this system.

## Colors

Primary navy carries headings and text on light surfaces. Deep navy anchors the page gradient and region controls. Gold marks primary actions, selected regions, focus, and temperature comfort shading. Blue identifies secondary metrics and precipitation. White panels use pale borders and muted blue text. Climate map colors encode data independently of brand action colors.

**The Data Color Rule.** Preserve climate encoding. Do not assign a brand color a new weather meaning.

## Typography

Space Grotesk serves headings, the brand, and strong metric values. Inter serves body text, controls, notes, and tables. Numeric values use tabular figures where the source sets them. Keep the existing heading scale and compact supporting labels.

Monthly tiles use month labels (12px) and values (15px). Chart notes and table values use compact text (12px). Keep units and missing-data text readable.

## Layout

Header, main, and footer share a centered maximum width (1320px), with horizontal padding (32px desktop; 16px at widths up to 800px). White sections use the section spacing token. The map has a fixed detail column (280px, then 240px up to 900px); it stacks below 650px. Ranking rows use two columns, then one below 650px.

Monthly plots use two columns, then one up to 850px. Line/bar SVGs retain a minimum width (620px) inside a horizontally scrollable, focusable container. They must not shrink until labels become unreadable. Native monthly heatmap tiles use six columns on desktop and four up to 650px, with compact gaps. Filters use three columns, then one up to 850px.

Region tabs remain sticky near the top (8px). City filter fields, selects, buttons, and summary use scroll margins (100px top; 20px bottom). The focus guard checks focused controls against the tab bottom plus a clearance (12px) and the viewport bottom (16px). It centers a control when needed so focused fields remain visible below the tabs. The adjust action opens the filter panel and focuses its first toggle; scrolling follows the reduced-motion preference.

## Elevation & Depth

Panels are primarily flat white surfaces separated by borders. Region tabs use a restrained shadow; search results use a stronger shadow to sit above the map. The map HUD has a small shadow. Preserve this limited elevation vocabulary. Do not add decorative depth to charts or ranking rows.

## Shapes

Large sections have soft panel corners. Fieldsets and metric cards use the fieldset radius. Inputs and standard buttons use their own smaller radii. City shortcuts and badges are pill shaped. Heatmap tiles use the tile radius. Borders separate sections and table rows without creating heavy frames.

## Components

Buttons retain navy text on white, gold primary actions, and navy active switches. Selected region controls use gold on deep navy. Preserve visible focus outlines (3px gold, offset 3px); chart points use their existing focused mark treatment. Primary actions and region controls have a minimum height (44px). Disabled fields use pale fill and muted text.

**The Weather Boundary Rule.** City context filters affect the city ranking and optional city markers. Keep the climate raster, climate selection, comfort formula, and weather rules unchanged. Matching markers use the weather palette; excluded markers are gray; missing required data uses white outlined markers. Hover explains status; clicking selects the city. Map mode defaults to ranking only and is shared in the URL. Native sliders complement exact numeric fields and share their enabled state. Slider ranges are Nomads (0–5), monthly budget (0–10,000 USD), and homicide (0–30 per 100,000). Exact fields retain the wider limits for budget (1,000,000 USD) and homicide (300 per 100,000). Shared URLs retain enabled filters, exact values, crime year, homicide geographic level, and marker mode. Enabled homicide filters write `homgeo=city` or `homgeo=country`. Old URLs with `crime=1` and no `homgeo` retain country mode.

City filters are independent optional controls: minimum Nomads score (0–5), maximum nomad monthly cost (USD estimate), and maximum homicide rate (per 100,000) with an explicit geographic level and crime year. The geographic selector offers City / municipal area and Country / area. City mode and 2024 are the defaults; all three filters start off on a clean URL. Saved URL parameters can restore enabled filters. Missing required values exclude a city only when the corresponding filter is active. Missing local homicide never falls back to a country rate; a published zero remains valid. The crime year is separate from the weather period. Use explicit unavailable text and loading/error status.

Local homicide uses FBI municipal agency service areas in the USA and Eurostat city or greater-city areas in Europe. Source areas can differ from named city boundaries, and the two sources use different definitions. The 2024 matched coverage is 6,900 USA cities and 11 European city/greater-city areas; coverage changes by year. Country mode uses UNODC national context, shared by the country’s cities. Show source links for FBI, Eurostat, and UNODC, the Nomads retrieval date, and the UNODC release date in country mode. Selected-city details show local and country rows separately, with year, rate, source, local area, geographic boundary label, available count, and source warnings. FBI rows also show the source population and the Table 8 requirement for 12 complete reporting months. Eurostat rows state that monthly reporting completeness is unknown. Homicide is not a complete safety measure.

**The Marker Visibility Rule.** Markers require an active city filter, loaded city data, and marker mode. Matching cities keep weather colors; failed filters use gray fill; unavailable required data uses white fill with a dark outline. Hover shows the city, weather values, match status, exclusion reasons, and available city context. Selected-city context also states the active-filter result.

Overview decluttering affects visibility only. At zoom below 3, show known-data cities with at least 500,000 residents; from 3, show known-data cities with at least 100,000; from 4.5, allow missing-data cities with at least 100,000; from 5, show all eligible points. Status counts cover the full eligible catalog, not only visible points or the top ten. Eligibility uses selected region and population size, climate-cell distance at most 0.75°, and finite score/day values. Missing-data counts are a subset of excluded counts.

Marker-aware PNG drawing uses the eligible point set inside the export bounds and preserves match, excluded, and unknown styling. The export drawing does not apply the live zoom decluttering thresholds. This describes the source export method, not a verified exported image.

**The Cell Fidelity Rule.** Monthly views follow the selected exact ERA5 cell and selected weather period. Display cell coordinates, period, UTC-day basis, and Open-Meteo daily API attribution. Disclose API display rounding differences from the score archive. Keep the monthly data table available.

Temperature uses average daily high as a solid line and daily mean as a dashed line. The shaded band reflects the actual selected temperature limits in line mode. A monthly average inside that band does not mean every day qualifies. Precipitation uses monthly totals, including snow water equivalent, and bars in series mode. Sunshine uses average hours per day; its minimum shading appears only when the sunshine rule is enabled in series mode.

Monthly heatmaps use native tiles without a y-axis. Each chart normalizes intensity within its own values; darker means higher, not better or more comfortable. Show numerical values, units, missing values, and accessible labels. Temperature tiles show daily highs; daily means remain in the table. Do not show comfort-band shading in heatmap mode.

## Do's and Don'ts

- **Do** preserve LFSA tokens and the existing map and rules hierarchy.
- **Do** keep source, time basis, units, and missing-data meaning close to the relevant data.
- **Do** keep monthly charts readable through scrolling and provide table access.
- **Don't** mix independent city context with weather scoring or label national homicide as city crime.
- **Don't** treat relative heatmap intensity as an absolute comfort scale.
- **Do** keep focused filter controls clear of the sticky tabs and preserve the scroll margins.
- **Don't** claim a complete page audit from these source observations. The reported follow-up independent review found one mobile focus occlusion issue, marked it resolved, and gave a ship disposition within that narrow scope. This document does not independently verify that review or certify the whole page.
