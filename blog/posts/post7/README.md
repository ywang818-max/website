# Blog 7 — Plotly rent-budget explorer

[Published article](https://ywang818-max.github.io/website/blog/posts/post7/)

Question: which Pennsylvania counties remain in a median-rent-budget comparison,
and what does the shortlist conceal about local renter burden? Audience: students
and early-career renters. This post deliberately reuses Blog 5's verified ACS
snapshot; Blog 7 does not require a new dataset. Its contribution is interactive
filtering, county identification, linked detail and uncertainty inspection.

## Reproduce from a fresh clone

Requires Python 3.9+ (standard library only). No package installation, account,
API key, current website download or prior output files are required.
From the website repository root:

    python3 blog/posts/post7/code/build.py

Or, from any directory, run the absolute script path, quoted if it contains spaces.
The script derives every input/output path from its own location. To inspect the
result locally, from this post's folder run:

    python3 -m http.server 8000

Open http://localhost:8000/results/explorer.html in a modern browser. Some browser
file policies restrict file://; a local server avoids that. To regenerate the
Quarto website normally, run `quarto render` from the repository root after the
analysis build. The existing site renders into `docs/`; the committed deployed
HTML and local runtime make the interaction usable without Python in the browser.

## Exact folder map

- `index.qmd`: article source, embeds the explorer iframe and full-width link.
- `code/build.py`: verifies source hash, reconstructs all county statistics,
  checks reconciliations, exports CSV/JSON, explorer HTML/JS and preview SVG.
- `code/explorer-template.html`: readable control, accessibility, table and style template.
- `code/explorer.js`: Plotly controller, common filtering predicate and linked views.
- `data/raw/acs_reporter.json`: complete fixed Census Reporter response (68 geographies,
  counties plus state); the input, not a previously calculated output.
- `data/raw/source_provenance.json`: source URL, date, release, units and checksum.
- `vendor/plotly-basic-3.1.0.min.js`: official pinned Plotly basic bundle, downloaded
  from the Plotly GitHub release tag v3.1.0; no CDN dependency during viewing.
- `vendor/LICENSE.txt`: Plotly MIT license.
- `results/county_analysis.csv`: 67 county observations, medians, margins, denominators.
- `results/metrics.json`: state comparator, documented filter scenarios and examples.
- `results/validation.json`: input/runtime hashes and numerical validation rules.
- `results/explorer.html`, `results/explorer.js`: generated interactive artifact.
- `results/preview.svg`: static blog-listing thumbnail; not a second analysis figure.
- `REPRODUCTION_CHECK.md`: numerical and rendered interaction checks actually performed.

No files are available only inside a ZIP. The original response, all code and the
runtime needed to view the chart are committed in this folder.

## Definitions and calculation order

Source: 2020–2024 ACS five-year estimates, in 2024 inflation-adjusted dollars,
archived October 20, 2026 UTC. This is not current apartment-listing data.
B25064_001 is median gross monthly rent, B25119_003 is median annual household
income for renter-occupied units. Do not divide these medians and call the result
a household burden rate: their universes differ and medians do not pair households.

B25070_001 is total cash-rent households; _011 is ratios not computed. The burden
numerator is _007 + _008 + _009 + _010 (30% or more); denominator is _001 - _011.
The script verifies the categories sum to total, unique county FIPS, 67 county
coverage and all relevant county counts sum to directly published state counts.
The published statewide burden is 721,590 / 1,496,561 = 48.2165%.

Filter: median gross rent <= selected ceiling AND computed-burden households >=
selected minimum. Both comparisons are inclusive. The pooled rate recomputes
sum(numerators)/sum(denominators); no unweighted averaging of county rates occurs.
The subset is a selection of counties, not a sample of listings or households
whose own rent necessarily falls below the ceiling.

The dashed horizontal reference stays at the statewide rate as filters change;
it is not mislabeled as the filtered average. Axes remain fixed for comparisons.
All dots have equal size. Selected counties use a diamond as well as a different
color; the dropdown and exact table provide keyboard alternatives. Filtering,
summary and table share the same predicate. An inspected county outside filters
gets a warning and is not drawn in the filtered plot or table.

The rent-error toggle shows published symmetric 90% margins of error on median
rent, not a spread of individual rents. Income margins appear in the pinned
county profile. Burden confidence intervals are not calculated here. No ranking
or filter is interpreted as a statistical-significance result. The market-size
filter uses estimated represented households, not survey respondent counts.

## Expected checks

| Rent ceiling | Minimum computed households | Counties | Pooled burden |
|---|---:|---:|---:|
| $1,800 | 0 | 67 | 48.216544% |
| $1,200 | 0 | 54 | 45.403261% |
| $1,000 | 0 | 43 | 43.607692% |
| $1,000 | 20,000 | 2 | 44.691473% |
| $600 | 0 | 0 | Not defined (displayed as —) |

Erie: rent $904 ±$20, burden 49.1708%; Centre: $1,207 ±$27, 57.0361%;
Cameron: $689 ±$116. Displayed medians are survey estimates, not availability,
quality, safety, personal affordability or causal evidence.

## Course rubric

Six common criteria: motivated question, accessible explanation, interpretation/
takeaway, data/presentation, organized repository/README and reproducible saved
outputs. Blog 7-specific: actual Plotly visualization; functioning usable controls;
substantive interactive exploration beyond one static graph; discussion of the
patterns and information revealed. There is no three-figure quota for Blog 7.

Sources: [Census Reporter tables](https://censusreporter.org/),
[Census five-year guidance](https://www.census.gov/programs-surveys/acs/guidance/estimates.html),
[Plotly API](https://plotly.com/javascript/plotlyjs-function-reference/).
