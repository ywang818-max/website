# Blog 5: Lower Rents, Lighter Burden?

[Published article](https://ywang818-max.github.io/website/blog/posts/post5/)

This analysis asks whether lower-rent Pennsylvania counties have lower rental burdens. It uses all 67 counties, 2020–2024 ACS five-year estimates, and real Census TIGERweb county polygons. The article is descriptive; it does not estimate causal effects of employment or measure neighborhood safety.

## File guide

| Path | Purpose |
|---|---|
| `index.qmd` | Article source, figures and source links |
| `code/acquire_data.py` | Optional online refresh of the public inputs |
| `code/analyze.py` | Offline calculations, validation, CSV and figure generation |
| `code/requirements.txt` | Pinned Python plotting dependencies |
| `data/raw/acs_reporter.json` | Archived Census estimates and margins of error, obtained through Census Reporter |
| `data/raw/pa_counties_5070.json` | Archived official TIGERweb geometry, EPSG:5070 |
| `data/raw/provenance.json` | Exact download URLs, UTC timestamp, SHA-256 hashes and boundary metadata |
| `results/county_analysis.csv` | One row per county; rent, renter income, population counts and burden percentages |
| `results/metrics.json` | State benchmarks and selected descriptive comparisons |
| `results/validation.json` | Programmatically generated integrity checks |
| `results/figures/figure1.svg` | Median gross rent map |
| `results/figures/figure2.svg` | Rental burden map |
| `results/figures/figure3.svg` | County rent-versus-burden scatterplot |
| `REPRODUCTION_CHECK.md` | Clean-copy replication procedure and recorded result |

Generated PNG companions are optional review files; the website uses SVG. Code, data and results are separated and every input needed for the published numerical results is archived here. No private paths, Census API key, network access, manual spreadsheet changes or copying of results is needed to rerun the analysis.

## Reproduce the published analysis

From the repository root, using Python 3.11 or newer:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r blog/posts/post5/code/requirements.txt
python blog/posts/post5/code/analyze.py
```

Installing the dependencies requires a connection; after installation the analysis runs entirely offline. The script resolves its paths from its own location, so it also works from another working directory. It verifies the source hashes before calculating results, creates output folders and saves all tables and figures itself. Avoid changing `data/raw` to preserve the published snapshot.

To rebuild the Quarto website, install Quarto and, from the repository root, run:

```sh
quarto render
```

The website configuration writes rendered pages to `docs/`. The deployed article is `docs/blog/posts/post5/index.html`. Rendering alone uses the saved figures; run the analysis first to regenerate them. If dependencies are already installed, no account or key is required for replication.

## Optional acquisition of a new snapshot

```sh
python blog/posts/post5/code/acquire_data.py
python blog/posts/post5/code/analyze.py
```

This intentionally replaces the archived inputs and provenance. It requires internet access and should be done on a copy if retaining the exact published snapshot matters. The acquisition pins Census Reporter release `acs2024_5yr`; it does not silently substitute the latest release. The official Census API returned a Missing Key page, so the ACS download uses Census Reporter’s public API, which republishes Census data. TIGERweb is the official Census boundary service. A GitHub working-branch acquisition run successfully archived these inputs before publication.

## Definitions and calculations

- B25064, column 001: median monthly gross rent, including utilities (2024 dollars).
- B25119, column 003: median annual income of renter-occupied households (2024 inflation-adjusted dollars). This is not median income of all households, hourly pay, or a measure of job vacancies.
- B25070, column 001: cash-rent renter-occupied households; 011: ratio not computed.
- Burden numerator: B25070 columns 007 + 008 + 009 + 010 (30% or more). Denominator: 001 minus 011. Multiply by 100 for a percentage.
- Severe burden: column 010 (50% or more), divided by that same computable denominator.
- State figures come directly from the statewide Census record, not from averages of county medians or rates.
- Ratio-of-medians is not used as a substitute for the household-based burden measure. Zero-income or otherwise noncomputable ratios are not silently treated as affordable.

Expected state results: median rent **$1,209**; median renter income **$47,506**; computable cash-rent households **1,496,561**; burdened households **721,590**; burden share **48.2165444643%**. Excluded not-computed households: **121,321**. Erie: $904 rent, $34,870 income, 49.1708% burden; Montgomery: $1,683, $65,931, 49.0203%.

## Quality, uncertainty and geography

The script requires 67 unique Pennsylvania county FIPS codes and an exact one-to-one match with 67 county geometries. It verifies nonnegative counts, positive medians, category totals, source hashes and county count reconciliation to the direct state record. Null or Census sentinel values fail validation rather than becoming zero. ACS median rent/income margins of error are retained in the CSV and all original count margins of error remain in the archive. The article makes no significance claims about small county differences; burden percentages do not include computed confidence intervals.

Maps use the current TIGERweb county layer downloaded with this snapshot, with coordinates in NAD83 / Conus Albers (EPSG:5070), simplified to 250 metres by the service for presentation. This is a boundary-service vintage, not a claim that the polygons are a 2024 boundary extract. State/county FIPS matching is verified. County area is not renter population; county summaries cannot resolve within-county inequality or safety. Gross rent reflects occupied units, not advertised vacancies; the five-year estimates do not describe October 2026 market conditions.

Source metadata and table labels: [B25064](https://api.census.gov/data/2024/acs/acs5/groups/B25064.html), [B25070](https://api.census.gov/data/2024/acs/acs5/groups/B25070.html), [B25119](https://api.census.gov/data/2024/acs/acs5/groups/B25119.html), [Census Reporter](https://censusreporter.org/about/), [TIGERweb](https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/State_County/MapServer/1).
