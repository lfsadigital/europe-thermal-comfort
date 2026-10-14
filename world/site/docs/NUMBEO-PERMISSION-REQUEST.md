# Numbeo integration permission request — 2026-10-14

Status: drafted, NOT SENT. No subscription purchased; no dataset imported.

Recipient: contact@numbeo.com
Subject: Permission and pricing for a personal city comparison website

Hello Numbeo team,

I run Comfy Days (https://comfy.lfsadigital.com/), a free personal project with no subscriptions or advertisements. It compares cities using historical weather data.

I would like to add optional city filters for your cost-of-living and quality-of-life indices, with a clear link back to Numbeo. Could you confirm the permitted access method and whether this personal use qualifies for free access or needs a paid API/data license?

Please also confirm whether we may cache a limited city snapshot, deliver those values to visitors' browsers for filtering and PNG exports, and how often it must be refreshed. We would keep your dataset out of our public GitHub repository and would not offer a public data API or feed.

If browser-delivered snapshots are not permitted, which integration pattern would you authorize? Are any free or discounted arrangements available for this kind of personal project?

Thank you,
Luiz

## Verified public conditions
- Personal websites: use allowed with a link back; this alone does not authorize scraping.
- Automated scraping/crawling: requires written permission.
- Commercial API license: use in applications permitted, but public API/data-feed redistribution requires consent.
- Published Basic API price: USD260/month, before applicable tax; no plan purchased.
- The permissibility of our exact browser-delivered workflow is UNKNOWN until clarified.

Sources checked 14 October 2026:
https://www.numbeo.com/common/terms_of_use.jsp
https://www.numbeo.com/common/api.jsp
https://www.numbeo.com/premium/commercial-license

## Open-Meteo recommendation
Keep the existing monthly-chart API for now under the personal-project conditions, without claiming definitive provider confirmation of commercial classification. Alternative: remotely derive monthly chart data from the same licensed ERA5 AWS Open Data archive and serve those aggregates ourselves. This removes dependence on the hosted free API without changing source/model. No implementation or publication performed in this investigation.
https://open-meteo.com/en/terms
https://github.com/open-meteo/open-data
