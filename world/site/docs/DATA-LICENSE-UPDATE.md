# Data license update — 14 October 2026

## Nomads withdrawn
Removed public score/cost snapshot, both controls, per-city context values and network fetch. Legacy nomads/nomadmin/cost/budget URL flags are stripped on startup and serialization. No replacement data installed. City population and homicide filters retain their rules. Historical documentation is retained with a withdrawal notice; matching audit retains counts only.

Nomads current API terms prohibit distributing its raw data as a dataset/feed and limit paid caching to 30 days. Separate permission for the older public snapshot was not verified. Removal is precautionary, not a definitive legal finding about that historical endpoint. No paid subscription purchased and no provider contacted.
https://nomads.com/api/v3#license

## UNODC
The actual data portal HTML was fetched on 14 October. Its footer links https://www.unodc.org/unodc/legal.html and https://www.un.org/en/about-us/copyright. The legal notice permits personal noncommercial copying but grants no redistribution or derivative-work right. The July 2026 homicide metadata gives a suggested citation, not a redistribution license. No dataset-specific override was found. We cannot label the current directly downloaded workbook CC BY based only on its public accessibility.

Removal of country data pending user choice. Municipal FBI UCR and Eurostat data have separate reuse permissions and are unaffected.

Potential replacement, not installed: https://data.worldbank.org/indicator/VC.IHR.PSRC.P5 explicitly labels the country homicide series CC BY 4.0 and cites UNODC. Import only that licensed distribution, retaining its vintage/coverage and crediting both organizations. Do not relabel the existing July 2026 workbook as World Bank data or assume identical coverage.

## Open-Meteo
The map/scientific archive comes from AWS Open Data, CC BY 4.0: https://github.com/open-meteo/open-data . MonthlyCharts calls the free Historical API only for a selected grid cell: ERA5 daily maximum/mean temperature, precipitation sum and sunshine duration for 2020–2025, UTC and no elevation correction. These charts do not supply or change the map score. The provider permits private/nonprofit sites without subscriptions/ads; promotional/commercial uses are excluded even if free to visitors. Classification depends on purpose, not simply whether anyone is charged. No classification confirmation from provider was obtained. https://open-meteo.com/en/terms

## Numbeo replacement assessment
https://www.numbeo.com/common/terms_of_use.jsp permits personal website reuse with link attribution, but prohibits automated scraping/crawling without prior written permission. Commercial API/data subscriptions do not grant republication via public APIs/data feeds without consent. This is not an unrestricted open database substitute. Cost-of-living/quality-of-life indices are different metrics from Nomads score and its nomad monthly USD budget. A future integration needs permission for the exact workflow and clearly defined cost components. No Numbeo data downloaded.

## Credits and validation
Added explicit weather CC BY source/license/change attribution in folded About the data, plus GeoNames, Natural Earth, FBI, Eurostat and OSM credits. PNG footer credits the weather provider/license and identifies derived scores. Scientific core and worker SHA-256 hashes match the pre-edit manifest; climate files/cells/period/formula unchanged. Local tests passed monthly aggregation, zero-floor sunshine rules, pixel mask rendering, missing homicide data/year retention, population eligibility, Miami count/rate, and browser Nomads removal/URL cleanup/filter invariance/World-Europe-USA numeric parity/two PNGs/mobile width.

GitHub removal targets the current branch. Older commits can retain the retired snapshot; history rewriting requires separate authorization. Old Sites saved versions can retain former assets too. No history rewrite or deletion of saved versions is included.
