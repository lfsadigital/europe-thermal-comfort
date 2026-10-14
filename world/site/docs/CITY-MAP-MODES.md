# City map modes and identity update

Highlight results (markers) is the default: known matches retain weather colors, known failures have gray fill, unknown optional values use hollow navy rings and remain eligible. Only results (results) removes known failures but keeps unknowns. Do not apply (ranking) removes the filter layer; all three modes keep the same filtered ranking. Prior markers/ranking URLs remain valid; results mode persists in citymap. PNG identifies the applied mode and captures the real viewport.

Population below the selected minimum is a known failure. Hover and selected-city detail explain the actual population and minimum. Optional Nomads/cost/homicide missing values do not fail. A known population failure still excludes a city even if another field is unknown. The displayed population is the GeoNames catalog value, not a new demographic estimate.

Marker universe is cities with at least 1000 residents, valid finite weather values, cell distance at most 0.75°, and selected regional membership. Known catalog population zero remains outside this universe. Counts cover this full regional universe. Rendering materializes the current camera with 25% padding; moveend refreshes. Existing declutter thresholds remain: zoom below3, ≥500k; below5, ≥100k; at5+, all catalog candidates. This avoids sending the entire 161k catalog to the renderer. Climate raster, raw files and formulas stay unchanged.

Status remains visible independently of legend: empty match set offers Adjust Cities filters; empty camera/zoom offers zoom or movement. No new Cloudflare resources, KV or server computation introduced.

Logo is an authored SVG sun and blue horizon using LFSA navy/gold/blue. Favicon is a simplified SVG plus a 32px PNG fallback; 180px Apple icon is rendered from logo.svg with local headless Chrome. Source vector and generated raster are retained in dist. Assets total under 6KB. No external imagery or fonts were introduced.

Verification: independent 21 city filter cases, 20 climate/monthly cases; map modes/population/unknown retention/URL/ranking independence/zoom/320px/empty-state checks; Only results PNG; full map-first regression with 81 exact canvas pixel samples per metric. Performance measured in docs/performance-map-modes.json; reflects synchronous ranking+marker update work, not INP. Visual reviewer found one material empty-status defect; its fix scored resolved. DESIGN.md documents final built UI. Publication evidence follows in OPERATIONS.md.
