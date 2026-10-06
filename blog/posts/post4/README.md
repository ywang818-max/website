# Blog 4: Did U.S. Wages Catch Up With the Cost of Living?

A descriptive analysis of private-sector average hourly earnings, consumer prices, and rents in the United States. All figures are generated programmatically. No regressions or causal claims are made.

## Organization

- `code/analyze.py`: data acquisition, transformations, metrics, and all three figures.
- `data/raw/`: archived FRED CSV inputs retrieved October 6, 2026.
- `data/processed/`: aligned monthly levels and transformed indices.
- `results/figures/`: three substantive figures in PNG and SVG formats.
- `results/metrics.json`: programmatically calculated article statistics.
- `article.md`: English article with sources and figures.
- `dist/`: static published blog assets and downloadable replication package.

## Reproduce the submitted results

Requires Python 3.10 or newer. From the website repository root, first run `cd blog/posts/post4`. Then:

```sh
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python code/analyze.py
```

This uses the archived inputs to reproduce the submitted results without a network connection. To fetch the same observation window again:

```sh
python code/analyze.py --download
```

FRED can revise past observations, so downloading again may change results. The archived files preserve the submitted snapshot. No API key is required for FRED's CSV download URLs.

## Data

All three series are monthly and seasonally adjusted. Source: U.S. Bureau of Labor Statistics via FRED.

| Name | Series | Original units | Source |
| --- | --- | --- | --- |
| Private-sector average hourly earnings, all employees | CES0500000003 | Dollars/hour | https://fred.stlouisfed.org/series/CES0500000003 |
| All-items CPI-U | CPIAUCSL | 1982–84 = 100 | https://fred.stlouisfed.org/series/CPIAUCSL |
| CPI-U, rent of primary residence | CUSR0000SEHA | 1982–84 = 100 | https://fred.stlouisfed.org/series/CUSR0000SEHA |

Download format: `https://fred.stlouisfed.org/graph/fredgraph.csv?id=SERIES&cosd=2019-01-01&coed=2026-08-01`.

Period: January 2019–August 2026, 92 calendar months; 91 complete observations. September earnings are available, but excluded to match the latest CPI month available as of October 6, 2026. Join series by observation month; convert missing strings to missing values; preserve the monthly calendar. October 2025 CPI and rent are missing in the source; no interpolation is performed, and the affected chart lines have gaps. Each baseline is the arithmetic mean of the twelve 2019 monthly observations.

## Transformations

For each series X: index_X(t) = 100 * X(t) / mean(X in 2019).

Real wage index = 100 * index_wage / index_cpi.

Wage purchasing power against rent = 100 * index_wage / index_rent.

Cumulative percent change = index_X - 100. Real wage change is calculated as a ratio, rather than subtracting cumulative growth rates. The normalized real wage index uses the ratio of the series-specific 2019 means as its reference; it is not separately divided by the mean of twelve monthly wage/price ratios.

## Scope and interpretation

Earnings refer to all private nonfarm payroll employees, not government workers, self-employed people, or a panel of identical workers. They are an average, not a median. Workforce composition affects this measure, especially in 2020. CPI describes urban consumer price changes, not every household's exact cost of living. Rent CPI is not new-lease asking rent, home prices, mortgage payments, or rent/income burden. Rent is part of all-items CPI and must not be added to it again. National movements are descriptive and do not establish a causal mechanism.

Rent measurement reference: https://www.bls.gov/cpi/factsheets/owners-equivalent-rent-and-rent.htm

## Submission

Submit both the published blog URL and a GitHub repository URL. This package contains the files required for the repository; a Sites source repository is not automatically a GitHub repository. Confirm that this dataset has not already been used in an earlier blog assignment before submitting.
