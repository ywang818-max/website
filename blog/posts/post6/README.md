# Blog 6: Python + SQL parent–child matching and income measurement

[Article](https://ywang818-max.github.io/website/blog/posts/post6/)

## Start here

This is an empirical tutorial using the locally supplied PSID extract J366555
and FIMS biological-parent map fim16218_gid_BO_2_UBL. It uses real observations,
not simulated data. It compares income definitions and age windows on the same
3,108 child–biological-father pairs. The 1,679 distinct fathers define the clusters
for confidence intervals. Estimates are descriptive and unweighted, not causal
effects or nationally representative IGE estimates.

## Folder map

| Path | Content |
|---|---|
| `index.qmd` | Tutorial source with the actual SQL operations and findings |
| `code/analyze.py` | Fixed-width import, validation, SQLite tables, OLS and programmatic exports |
| `code/requirements.txt` | Pinned numerical and plotting packages |
| `sql/match.sql` | Version-controlled aggregation and generational matching queries |
| `data/variable_map.json` | Every interview wave's income, age, family ID, sequence and relationship variables |
| `data/cpi_annual.csv` | Public annual CPI values for income years 1967–2022 |
| `data/README.md` | Acquisition, input identities, privacy and codebook rules |
| `results/estimates.csv` / `.json` | Four OLS results, pair counts, clustered standard errors and intervals |
| `results/audit.json` | Source checksums, sample flow and age/window coverage |
| `results/figures/figure1.svg` | Same-sample single-year/multi-year comparison |
| `results/figures/figure2.svg` | Early-adult/prime-age child comparison |
| `REPRODUCTION_CHECK.md` | Checks actually performed and limits |

No raw microdata, person IDs, individual matches or database are in this
repository. Those files are not needed to view the article, but are needed to
rerun the empirical analysis. An aggregate table cannot reconstruct this sample.

## Reproduce with your own authorized local inputs

Use Python 3.11 or newer. From the repository root:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r blog/posts/post6/code/requirements.txt
python blog/posts/post6/code/analyze.py \
  --data /your/local/J366555.txt \
  --statements /your/local/J366555.do \
  --fims /your/local/fim16218_gid_BO_2_UBL.txt
```

The path arguments are examples; use the locations of your local downloads.
The script derives output paths from its location and works from any working
directory. It uses no credentials or network calls. Do not send microdata to
GitHub or publish your download links. Follow the current PSID Conditions of Use.

Installing packages requires a connection. Once packages and authorized inputs
are available, the complete analysis runs offline and writes all outputs. The
data files must match the documented 261-variable extract. For a differently
named but equivalent extract, supply the corresponding .do file and compare the
generated mapping and codebooks; the adapter fails on incompatible fields.

To regenerate the website from the repository root on a normal Quarto setup:

```sh
quarto render
```

Run the analysis before rendering to regenerate figures. The deployed file is
`docs/blog/posts/post6/index.html`; SVGs and the aggregate CSV are copied to that
post's results directory. The site requires no access to private inputs.

## Matching and selection, explicitly

1. Read the Stata `infix` positions directly; parse numeric fixed-width fields,
   including decimal-valued income. Never guess CSV separators.
2. Construct `pid = ER30001*1000 + ER30002`, a collision-free encoding for the
   documented 4-digit family ID and 3-digit person number. Assert uniqueness.
3. For each wave, retain valid age (1–125), family interview ID, sequence 1–20,
   and a current head/spouse/partner relationship: 1/2/9 through 1982, and
   10/20/22 from 1983. This avoids measuring an adult child through their
   parents' household when they are only listed as a co-resident child.
4. Exclude missing/nonpositive and historically bottom-coded incomes <=$1.
   Exclude documented upper boundaries: $99,999 for 1969–1979; $999,999 for
   1980/1984/1985; $9,999,999 for other 1981–1995 waves; >=$9,999,998 from
   1996 onward. The latter is a conservative common upper-bound screen, including
   special sample/missing codes. The 1968 variable has no upper-code screen.
   These choices are explicit; zero/bottom-coded income cannot enter logs.
5. Verify equal income within each (wave, family interview ID), create separate
   family and membership tables with unique primary keys, and join on both keys.
   Assert the person-wave row count is unchanged by the join.
6. Read FIMS's exact fixed-width layout. Use PTYPE F (biological father), encode
   both permanent IDs, remove links to people absent from the extract, exclude
   three parent-type/recorded-sex inconsistencies, and reject self-parent links
   or multiple distinct fathers for the same child.
7. Use interview ages 35–44 for both prime-age averages, requiring >=3 observed
   income years for each. Select one prime-age observation nearest age 40,
   and one early-adult observation nearest 27 within 25–29; ties use earlier wave.
8. Aggregate income in levels before taking logs. An average of logs would be a
   different estimand. All four regressions use the intersection of these same
   complete child–father pairs; no outcome-driven window selection is used.

Income belongs to the previous calendar year. Ages are interview ages, not
exact tax-year ages. Annual CPI ratios convert nominal values to 2022 dollars;
the input table is the publicly published Minneapolis Fed series rounded to one
decimal. Ratios, rather than the arbitrary CPI base, determine the conversion.

## Models and interpretation

OLS includes an intercept, with log child family income on log father family
income. Covariance uses a father-cluster sandwich with the standard finite-sample
factor G/(G-1)*(N-1)/(N-2). Reported intervals are normal 95% intervals. A separate
least-squares solver verifies every coefficient against the normal-equation
calculation. No survey weights, cohort controls or household-size adjustments
are included; these are classroom descriptive estimates for the selected sample.

| Model | IGE |
|---|---:|
| Single prime-age year for both generations | 0.4354194924 |
| Prime-age multi-year averages for both | 0.5743378288 |
| Early-adult child year / father prime-age average | 0.4531726752 |
| Prime-age child year / father prime-age average | 0.6005337419 |

Same N=3,108 in every model; G=1,679 fathers. Mean prime-age observations:
child 5.2548, father 8.1190. Mean selected interview ages: child prime 39.5486,
father prime 40.0254, child early 26.8642. Unequal panel spacing means these are
observed years, not ten consecutive annual income measurements for everyone.

Income averaging reduces some transitory fluctuations; it does not guarantee
unbiased permanent income. The age comparison demonstrates age sensitivity,
not a causal identification of life-cycle bias. Household composition and
calendar/cohort differences can also contribute. Requiring coverage at several
ages creates a selected surviving panel. Father clustering handles siblings,
but is not a full complex-survey or extended-dynasty variance estimator.

## Sources

- PSID Data Center: https://simba.isr.umich.edu/default.aspx
- PSID FIMS: https://simba.isr.umich.edu/FIMS/default.aspx
- Identifier guidance: https://psidonline.isr.umich.edu/Guide/FAQ.aspx?Type=1
- CPI table (1967–2022 values transcribed at published one-decimal precision):
  https://www.minneapolisfed.org/about-us/monetary-policy/inflation-calculator/consumer-price-index-1913-
- Life-course matching research: https://pmc.ncbi.nlm.nih.gov/articles/PMC3692297/
- Python sqlite3: https://docs.python.org/3/library/sqlite3.html
- Data conditions: https://simba.isr.umich.edu/U/CondUse.aspx

Required citation: Panel Study of Income Dynamics, public use dataset. Produced
and distributed by the Survey Research Center, Institute for Social Research,
University of Michigan, Ann Arbor, MI (2026).
