# Local crime data: next validated import

The current release contains country/area homicide rates only. It does not contain local US or European crime measurements. A country rate is not reused as a local estimate.

## USA

Official FBI UCR/NIBRS Crime Data Explorer includes municipal and other agency submissions. Match municipal agencies to catalog cities and the agency population for the same year. Require complete annual reporting and distinguish reporting coverage from a zero count. County, university and tribal agencies are not interchangeable with city police; overlapping populations must not be summed blindly. Start with comparable intentional homicide rates, then assess other violent crime categories separately.

https://www.fbi.gov/news/press-releases/fbi-releases-2024-reported-crimes-in-the-nation-statistics
https://nibrs.fbi.gov/2025/

## Europe

Eurostat supplies intentional homicide offences and victims for selected largest cities. Coverage is not every European city. Match the reporting geography (city or greater city) and its same-year population before computing a rate. Victims and offences must not be interchanged. Keep missing cities explicit and do not substitute a national rate without an explicit geography label.

https://ec.europa.eu/eurostat/en/web/crime
https://ec.europa.eu/eurostat/databrowser/view/crim_hom_ocit/default/table?lang=en
https://ec.europa.eu/eurostat/documents/3859598/18846431/KS-GQ-24-010-EN-N.pdf/ef737587-085e-6018-8038-e41f59222020

Local source imports have not been implemented or published in this release. Release dates, latest complete year, licensing, city matching and coverage must be read from the actual selected files before publication.
