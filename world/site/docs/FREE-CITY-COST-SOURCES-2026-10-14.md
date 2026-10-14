# Free city cost data candidates — 14 October 2026

Research only: no site edits, import, deploy, GitHub push, paid API, or contact to any provider.

## Assessment
No broad global monthly-cost source has been cleared as a production-ready replacement. Available data differ in geographic unit, household assumptions, time and provenance. License permission and data reliability are separate questions. Do not combine sources into a uniform global USD budget without an explicit common basket.

### WhereToEmigrate — global candidate, not cleared for production
Publisher licenses compilation CC BY 4.0. CSV read directly in memory: 3,418 bytes, 76 rows, 76 unique city/country pairs in 26 countries. Every row has a single-person monthly cost. Data dictionary defines this as EUR/month including rent. Family budget and central/peripheral one-bedroom rent also present. README snapshot July 2026 and quarterly refresh claim. Exact observation date and original price provenance per city were not available in the inspected CSV/dictionary; methodology page primarily describes visa claims, not cost sampling. Full basket and statistical validation remain unknown. The declared license is suitable for attributed reuse, but independent rights/provenance of input prices were not verified.

Coverage counted from file:
- Europe: 36 rows, 12 countries (Germany, Portugal, United Kingdom, Netherlands, Spain, Ireland, Sweden, Switzerland, Estonia, Austria, Czech Republic, Denmark).
- Americas: 18 rows (Canada, Mexico, Costa Rica, Panama, Chile, Uruguay).
- Asia including UAE: 16 rows (UAE, Thailand, Japan, Malaysia, South Korea, Singapore).
- Oceania: 6 rows (Australia, New Zealand).
- USA, Brazil and Africa: zero rows.

https://github.com/0brien18/global-emigration-dataset
https://github.com/0brien18/global-emigration-dataset/blob/main/cost-of-living-global-2026.csv
https://github.com/0brien18/global-emigration-dataset/blob/main/data-dictionary.csv
https://github.com/0brien18/global-emigration-dataset/blob/main/LICENSE

### Economic Policy Institute — strongest USD monthly-budget candidate for USA
2026 documentation: all 3,143 US counties/county equivalents and 613 HUD FMR metropolitan areas; 10 household types. 2025 dollar basis, with some older source items inflated to 2025. Includes housing, food, transport, childcare, healthcare, taxes and other necessities; one-adult zero-child profile available. A modeled modest local household budget, not a nomad short-stay budget. City matching would require a county/metro geographic crosswalk; no neighborhood/city-proper claims.

Explicit CC BY-NC-SA 4.0 reuse: attribution, noncommercial use, shared adaptations under the same license. Current personal/noncommercial project use is the applicable condition; this is not an unrestricted commercial license. License for data adaptation does not automatically require changing the unrelated site's entire source-code license. Primary publisher expressly supports download of full data. Exact joined coverage in our GeoNames catalog not calculated in this research.

https://www.epi.org/resources/budget/
https://www.epi.org/publication/family-budget-calculator-documentation/

### US BEA Regional Price Parities — strongest license, different metric
Official statistics; BEA FAQ states public domain unless otherwise specified. RPP is an index relative to US average=100, not a monthly USD budget. Metro series historical; February 19, 2026 release discontinued metro and metro/nonmetro portions while continuing state data for2024. Do not call current 2024 state figures city figures or invent USD/month conversions. Exact archived metro count and latest year not independently enumerated here.

https://www.bea.gov/help/faq/147
https://www.bea.gov/data/prices-inflation/regional-price-parities-state-and-metro-area
https://www.bea.gov/news/2026/real-personal-consumption-expenditures-state-and-real-personal-income-state-2024

## Candidates excluded or pending
- ReloMap: claims208cities/73countries and monthly updates, but README derives from Numbeo/Expatistan; README data license BY-NC contradicts repository-level BY license. Upstream redistribution authority not established. Not cleared.
- AverageCostOfLiving: claims1003cities/174countries, BY-NC4.0; underlying crowdsourced price databases unnamed, no precise observation date/download process confirmed. Not cleared.
- Nostos:500city records are not500observed city-cost records; cost fields use WhereToEmigrate plus country-estimate fallback. Country estimates must not be presented as city observations. No improvement over source coverage proved.
- Zenodo7833285:2023dataset explicitly says scraped from Expatistan; uploader's BY-NC-SA license does not establish rights to republish proprietary source. Not cleared.
- MIT/Living Wage Institute: permits direct use for10or fewer locations, but larger use requires license request and prohibits scraping/export. Not suitable for this unpaid bulk integration.

https://github.com/Alessandro114/cost-of-living-api
https://www.averagecostof.living/sources
https://nostos.navoy.io/data
https://zenodo.org/records/7833285
https://livingwage.mit.edu/pages/faqs

## Recommendation
For USA monthly-budget functionality, EPI is the best candidate under noncommercial attribution/share-alike conditions, with clearly labeled county/metro data and one-adult/no-children assumptions. For global coverage, keep cost unavailable until the76-city candidate has verified basket/provenance, or keep it explicitly experimental rather than treating it as validated global cost data. Do not pay, scrape restricted websites or silently impute country budgets into cities.
