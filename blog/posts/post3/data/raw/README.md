# Raw-data access and extract specification

Raw IPUMS microdata are not committed or uploaded. IPUMS terms require permission for redistribution; this project shares only grouped totals and counts, with no person or household identifiers.

1. Register/sign in at https://cps.ipums.org/cps/ and select **July 2026 Basic Monthly** (not the annual ASEC).
2. Add YEAR, MONTH, AGE, EDUC99, EMPSTAT, LABFORCE, and WTFINL. Download a CSV extract, optionally gzip-compressed. Extract numbers and filenames vary by account.
3. Keep the extract in a local location. From the website root run:

```sh
Rscript blog/posts/post3/code/analyze.R --microdata "/your/path/to/cps_extract.csv.gz"
```

Replace the quoted example path; do not change any paths in the script. Outputs go to `blog/posts/post3/results/microdata/`, not over the published aggregate snapshot. If a future IPUMS extract revises observations or weights, results can differ from the archived aggregate snapshot.

The author's original local extract has 90,719 rows, of which 44,881 satisfy the analysis filters. Its checksum and selected population are recorded in `data/provenance.csv`. A fresh public clone can reproduce all published tables and charts directly from `data/processed/education_status_cells.csv` without needing the raw extract.

To identify caregiving separately in a future extension, add NILFACT and follow its universe/codes; do not treat EMPSTAT=34 as a caregiving code. EMPSTAT=32 means unable to work, 34 means other NILF, and 36 means retired. NILF means not in the labor force. The current extract does not include NILFACT.
