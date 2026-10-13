# Map-first controls — local candidate

Weather and Cities panels share the map toolbar. Only one opens at a time. Each scrolls within the map; Escape closes it and restores focus. Top 10 remains below and its Edit city filters button opens the map panel.

Weather changes require Apply. Pending changes do not affect the map and block export. City limits update immediately with a short debounce. Invalid city drafts preserve the last valid state and block export. Loading and failure remain visible; missing optional records are retained as unknown, not filled with zero.

Marker legend: weather color = known match; gray fill = known failure; hollow navy ring = missing optional data, kept. A known failure excludes even if a different field is unknown. All statuses use the same zoom/population visibility rules. Catalog population eligibility is separate from optional-data status.

PNG captures the actual rendered MapLibre camera and city layer, at the current view/period and applied rules. The posting frame is 2400×1800, with rule summary, palette, attribution and socials. Exports wait for rendering; a timeout reports failure. Pending weather, invalid city inputs and active calculation/data loading block export.

Verification: 20 climate/monthly checks; 21 independent filter cases; real mobile weather apply; desktop/tablet/390px/320px controls; markers rendered; unknown ranking retained; region values unchanged; both PNG views matched 81 independent canvas pixels exactly. See map-first-browser.json and ../city-data/map-first-*.cjs. No weather archive or formula changed. Publication has not occurred for this candidate.
