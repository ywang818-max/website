# Blog 3 — Education and labor-market outcomes: start here

**Published article:** https://ywang818-max.github.io/website/blog/posts/post3/

This project uses July 2026 IPUMS CPS Basic Monthly data for civilian adults ages 25–64. The article uses three core figures: participation, unemployment, and nonparticipation status. Employment-to-population ratios remain in the prose; the script also saves a supplementary employment chart for inspection. Every population estimate uses the person weight **WTFINL**.

## Quick start: reproduce the published results offline

Download this website repository using **Code → Download ZIP** on GitHub and unzip it, or clone `https://github.com/ywang818-max/website.git`. Keep the folder structure intact. Open a **Terminal** in the extracted website root (`website` or `website-main`; RStudio's Terminal tab also works).

Requires R 4.1 or newer. Run these terminal commands, not R Console expressions:

```sh
Rscript blog/posts/post3/code/install_packages.R
Rscript blog/posts/post3/code/analyze.R
```

Installation needs internet only for missing packages. The analysis itself runs offline using committed, grouped CPS totals. It creates the results directory and saves every table and figure automatically; previous results and raw microdata are not required for this mode.

If already inside `blog/posts/post3`, use `Rscript code/analyze.R`. The script locates all project files relative to its own file, not your working directory. Absolute script paths work too; quote a path containing spaces:

```sh
Rscript "/your/path/to/website/blog/posts/post3/code/analyze.R"
```

Replace only the example path; do not edit file paths in the R code.

## Exact folder map

All paths below are relative to `blog/posts/post3/`:

```text
post3/
├── README.md                              # Start here
├── REPRODUCTION_CHECK.md                  # Verification and feedback response
├── index.qmd                              # Article; references saved charts
├── .gitignore                             # Keeps raw data/rebuild outputs local
├── code/
│   ├── install_packages.R                 # Installs missing readr/ggplot2/scales
│   └── analyze.R                          # Full microdata and aggregate pipelines
├── data/
│   ├── processed/
│   │   └── education_status_cells.csv     # Fixed INPUT: 28 grouped CPS cells
│   ├── provenance.csv                     # Input period, sample size and checksum
│   ├── snapshot_checksums.csv             # Verifies the fixed aggregate inputs
│   └── raw/
│       └── README.md                      # Exact IPUMS download specification
└── results/                               # OUTPUTS; never used as inputs
    ├── education_status_cells.csv         # Cells used in the current run
    ├── education_rates.csv                # Participation/employment/unemployment
    ├── nonparticipation_status.csv        # Three NILF categories and denominators
    ├── participation_gap_accounting.csv   # Lowest vs highest education gap
    ├── participation.png                  # Figure 1
    ├── employment.png                     # Supplementary diagnostic
    ├── unemployment.png                   # Figure 2
    ├── nonparticipation.png               # Figure 3
    └── session-info.txt                   # Versions used for the run
```

The input cells contain four education groups × seven employment statuses, with respondent counts and sums of WTFINL. They are grouped totals, not person-level records. The default script verifies their checksums and derives all rates, tables and charts from them. It does not read saved rates or manually entered article numbers.

## Expected checks

The raw local extract contained 90,719 rows. The analysis retained 44,881 eligible adults.

| Education | Unweighted n | Participation | Employment | Unemployment |
| --- | ---: | ---: | ---: | ---: |
| Less than high school | 2,902 | 61.4% | 58.3% | 5.0% |
| High school | 12,094 | 73.6% | 70.4% | 4.2% |
| Some college / Associate | 11,045 | 78.9% | 76.0% | 3.7% |
| Bachelor's or higher | 18,840 | 85.6% | 83.0% | 3.1% |

The script checks employment = participation × (1 − unemployment), and checks that the three nonparticipation shares sum to one minus participation. For the lowest versus highest education group, contributions sum to the participation gap: unable to work 12.8199 percentage points, other NILF 11.0749 points, and retired 0.3467 points. These are accounting contributions, not causal effects.

The default run recreates the nine files above even after deleting `results/`. Graphics/fonts can differ slightly across package versions; compare numeric CSV results for statistical replication. `REPRODUCTION_CHECK.md` records the clean-copy and full-microdata checks.

## Rebuild from authorized IPUMS microdata

See [data/raw/README.md](data/raw/README.md) for exact sample/variable selection and [IPUMS CPS](https://cps.ipums.org/cps/) for access. The extract must contain YEAR, MONTH, AGE, EDUC99, EMPSTAT, LABFORCE, and WTFINL.

From the website root:

```sh
Rscript blog/posts/post3/code/analyze.R --microdata "/your/path/to/cps_extract.csv.gz"
```

This reads the raw CSV, applies filters, computes the 28 grouped cells, and regenerates every statistic and chart. Outputs are isolated in `results/microdata/` and do not overwrite the fixed inputs or default results. The public aggregate-input route allows readers to reproduce the article without an IPUMS account; the microdata route verifies the underlying derivation. The raw extract is not redistributed. See [IPUMS terms](https://cps.ipums.org/cps/terms.shtml).

## Definitions and methodology

- Sample: YEAR=2026, MONTH=7; ages 25–64; valid education and civilian employment/participation codes; finite positive WTFINL. Armed forces (EMPSTAT=1), NIU, missing and invalid codes are excluded.
- Education: EDUC99 codes 1,4–9 = less than high school; 10 = high school; 11,13,14 = some college/associate; 15–18 = bachelor's or higher. Code 0 is excluded.
- Employed: EMPSTAT 10 or 12. Unemployed: 21 or 22. Labor force: LABFORCE=2; the script checks consistency with these employment codes.
- Nonparticipants: EMPSTAT **32 = unable to work; 34 = other NILF; 36 = retired**. NILF means not in the labor force. These are recorded statuses, not experimentally identified mechanisms.
- Participation denominator: all eligible adults in the education group. Employment denominator: the same adults. Unemployment denominator: employed plus unemployed adults in the group.
- Figure 4 denominator: **all adults in the education group**, so its segments sum to the group's nonparticipation rate. `nonparticipation_status.csv` also saves within-nonparticipant shares with that different denominator clearly named.
- All weighted numerators and denominators sum WTFINL; do not use the household weight, ASECWT, or EARNWT. Rates are invariant to a common scaling of person weights.
- The extract does not include NILFACT, so EMPSTAT=34 cannot be split into caregiving, education, and other activities. A future extension can add NILFACT while following its universe. The article explicitly discloses this limit.

These one-month, non-seasonally-adjusted estimates are descriptive. Age composition, health and family circumstances can differ across education groups. No causal or statistical-significance claims are made; the figures do not include survey-design confidence intervals.

## Sources and website rendering

- [IPUMS CPS](https://cps.ipums.org/cps/), University of Minnesota, July 2026 Basic Monthly sample.
- [EDUC99](https://cps.ipums.org/cps-action/variables/EDUC99), [EMPSTAT](https://cps.ipums.org/cps-action/variables/EMPSTAT), [WTFINL](https://cps.ipums.org/cps-action/variables/WTFINL), [NILFACT](https://cps.ipums.org/cps-action/variables/NILFACT).
- [IPUMS citation information](https://cps.ipums.org/cps/citation.shtml).

The article is `blog/posts/post3/index.qmd`; generated website output is `docs/blog/posts/post3/index.html`. From the website root run `quarto render blog/posts/post3/index.qmd` to render with the existing site theme. Quarto is optional for analysis reproduction. Render only after regenerating the saved figures. The article includes a direct link to this README so readers do not have to search the whole website repository.
