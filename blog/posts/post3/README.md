# Blog 3: Education and labor-market outcomes in July 2026

## Source and input

Source: IPUMS CPS, University of Minnesota, July 2026 Basic Monthly sample. https://cps.ipums.org/cps/

Create an IPUMS CPS account and select the July 2026 Basic Monthly sample (not ASEC). Include YEAR, MONTH, AGE, EDUC99, EMPSTAT, LABFORCE, and WTFINL. Download a CSV extract. Save it locally as `cps_00001.csv.gz` in this folder, or supply its actual path to the script. The original local extract has 90,719 rows; the analysis retains 44,881 eligible respondents. IPUMS access is required to obtain the raw input; the repository includes code and aggregate results rather than redistributing microdata. The raw CSV is already excluded by the website's `.gitignore`.

Source documentation:
- Education: https://cps.ipums.org/cps-action/variables/EDUC99
- Employment status: https://cps.ipums.org/cps-action/variables/EMPSTAT
- Basic monthly person weights: https://cps.ipums.org/cps-action/variables/WTFINL
- Citation information: https://cps.ipums.org/cps/citation.shtml
- Redistribution terms: https://cps.ipums.org/cps/terms.shtml

## Files and reproduce

- `index.qmd`: article with three connected, labeled figures.
- `code/analyze.R`: reads raw data, applies sample/education definitions and weights, and saves aggregates and all figures.
- `results/education_rates.csv`: four education groups, sample sizes, weighted totals, and three rates.
- `results/participation.png`, `employment.png`, `unemployment.png`: substantive visualizations generated from these estimates.
- `results/session-info.txt`: R/package versions used.

Requires R plus dplyr, readr, ggplot2, and scales. Install with `install.packages(c('dplyr','readr','ggplot2','scales'))`.

From the website repository root:

```sh
cd blog/posts/post3
Rscript code/analyze.R
# Or:
Rscript code/analyze.R /absolute/path/to/your/cps.csv.gz
```

To render only the article, from the website root run `quarto render blog/posts/post3/index.qmd`. Rendering uses saved figures and does not execute the analysis or expose raw microdata.

## Definitions and weights

Restrict to YEAR=2026, MONTH=7, ages 25–64, valid education and civilian employment/participation codes, and finite positive WTFINL.

EDUC99 groups: codes below 10 (valid codes 1,4–9) = less than high school; 10 = high school; 11,13,14 = some college/associate; 15–18 = bachelor's or higher. Code 0 is excluded. EMPSTAT 10/12 are employed, 21/22 unemployed, and 32/34/36 not in the labor force. LABFORCE=2 identifies participants. The script checks that this agrees with employment status.

Use WTFINL for every population rate. Its common scaling cancels in weighted proportions; do not substitute the household weight or the ASEC/earnings weights. The downloaded CSV already contains fractional weights.

- Participation = sum of person weights for participants / sum of person weights for all eligible adults in the education group.
- Employment-to-population ratio = weighted employed / weighted eligible adults in the group.
- Unemployment = weighted unemployed / weighted participants in the group.

The script verifies employment = participation × (1 − unemployment) before saving the results. Estimates are not seasonally adjusted. They are descriptive, not causal, and no confidence intervals or significance claims are made. Replication with an independently regenerated extract may differ if IPUMS revises the input data.
