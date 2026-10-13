
## 2026-10-12 — local city context and monthly charts

Prepared, not pushed or deployed. Browser verification passed 133 checks with zero page errors across region tabs, filters, shared URLs, and Porto/Miami/Nairobi monthly comparisons. Separate checks passed for missing US crime data, monthly-request failure and retry, mobile overflow, and both 2400×1800 PNG exports. Independent design review passed after three chart fixes. Production weather calculations and original climate arrays remain unchanged. Temporary Nomads and UNODC source downloads were removed; curated small tables remain in dist/assets.

## 2026-10-13 — city map interaction checks

User authorized publication and GitHub backup. Optional map mode, shared URL, debounced native sliders and exact values, city hover reasons, click-to-inspect and marker-inclusive PNG exports implemented. Climate raster and score/day arrays do not change. At overview zoom only larger cities appear; smaller and unknown-data cities become visible with zoom. Local marker suite passed 47 checks with no page errors. The first hover test was outside the browser viewport; bringing the map into view resolved the test without a product change. Monthly/filter suite passed 133 checks; independent missing-data and API retry checks passed. City-level crime import is proposed in docs/LOCAL-CRIME-NEXT.md, not included. The independent reviewer scored the mobile field-occlusion fix resolved (ship at that narrow scope). Publication IDs and live checks follow after verification.
