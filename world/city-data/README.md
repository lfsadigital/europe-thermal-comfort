# City context import and tests

`import_nomads.py` and `import_homicide.py` use Python standard-library parsing and retain only curated small tables. Pass local source files as arguments; they do not fetch global climate archives. Source URLs, matching, units and coverage are in `../site/docs/CITY-CONTEXT-AND-MONTHLY.md`.

Run `node check.cjs` for synthetic monthly aggregation and source-table invariants. Browser checks require `npm install --no-save playwright` and `npx playwright install chromium`, or set `COMFY_CHROME_PATH` for an installed Chrome. Start `python3 -m http.server 8777 --directory ../site/dist`. Run `node map-check.cjs` for filters, shared URLs, region consistency, hover/click and PNG export checks. Set `COMFY_TEST_URL=https://comfy.lfsadigital.com/` for the public-site check. Screenshots and reports are saved in `../share/`, excluded from the code backup.

`browser-check.cjs` also compares monthly API charts against small independently processed Porto/Miami/Nairobi ERA5 fixtures. Set `COMFY_REFERENCE_FILE` to that audit input. Raw validation fixtures are not included in this code-only backup. The local original checks and their results are recorded in the site documentation.
