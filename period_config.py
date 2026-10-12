"""One authoritative period for the published paired temperature/rain maps."""
from datetime import date
YEARS=tuple(range(2020,2026))
YEAR_DAYS=tuple((date(y+1,1,1)-date(y,1,1)).days for y in YEARS)
TOTAL_DAYS=sum(YEAR_DAYS)
N_YEARS=len(YEARS)
PERIOD=f'{YEARS[0]}–{YEARS[-1]}'
DEFAULT_RANGE=(18,26)
assert YEAR_DAYS==(366,365,365,365,366,365) and TOTAL_DAYS==2192 and N_YEARS==6
