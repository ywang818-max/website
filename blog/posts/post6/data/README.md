# Data inputs and provenance

Only public variable names/mapping and the public CPI table are stored here.
The empirical input files remain on the analyst's local computer and are NOT
committed. Supply them explicitly to `code/analyze.py`.

## PSID input manifest

- `J366555.txt`: 261-variable, 85,536-person All Individuals ASCII extract,
  job 366555, generated October 21, 2026. Fixed-width length is 798 characters.
- `J366555.do`: exact fixed-width column positions and variable labels. Required
  by the Python importer, not executed as Stata code.
- `J366555_codebook.pdf`: codebook used to check age, relationship, sequence,
  income reference years, bottom codes and upper-code boundaries.
- `J366555_formats.do`: value-label reference; not needed by the numeric parser.
- `fim16218_gid_BO_2_UBL.txt`: biological-only, long, individual-to-parents,
  unbalanced FIMS GID map, 145,347 rows according to its reading statements.
- The FIMS layout is: ID68 columns 1–4, PN 5–7, GID 8, ID68P 9–12,
  PNP 13–15, PTYPE 16–17. F is father, M is mother. Empty parent rows are
  retained in the original unbalanced map but cannot become father matches.

Checksums of the three files actually used by the importer are saved in
`results/audit.json`. They identify the analyzed snapshot without publishing it.

## Acquire an equivalent extract

Using your own PSID registration, select Total Family Income and Individual Age
for all available 1968–2023 interview waves. Select the individual-file interview
ID and sequence number for each year, plus permanent ER30001 and ER30002. The
Data Center includes release/relationship/sex variables in the documented export;
verify these against `variable_map.json` and your reading statements. Export
All Individuals as ASCII with Stata statements and PDF codebook; do not subset
to current heads, because the analysis applies its documented wave-specific
head/spouse filter itself.

FIMS options: Inter-generational GID, biological only, individual to parents,
long format, unbalanced map, ASCII with Stata statements. Job and generated file
names may differ. Column identities and coding must match the adapter.

Readers must obtain their own authorized local files and follow PSID's current
Conditions of Use. This repository provides neither microdata nor individual
derived extracts. Published outputs are aggregate counts, regressions and figures.

## CPI

`cpi_annual.csv` contains annual published values for 1967–2022, transcribed from
the Minneapolis Fed historical CPI table on October 21, 2026. Values are rounded
to one decimal as on that page. Income in interview year t is assigned calendar
year t-1 and multiplied by CPI(2022)/CPI(t-1). The script makes no network calls.
