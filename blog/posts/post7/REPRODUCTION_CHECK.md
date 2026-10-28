# Blog 7 verification — October 27, 2026

## Numerical and build checks performed

- Fresh copy excluded the complete results folder; ran build.py from an unrelated directory with spaces in its script path, using Python's standard library only.
- All six generated artifacts (county CSV, metrics, validation, explorer HTML, explorer JS and preview SVG) were byte-identical to the first build.
- Independently recomputed all 67 burden rates directly from the raw B25070 category values, outside the build's extraction function; agreement within 1e-10.
- Verified category sums, 67 unique county FIPS, positive medians, valid denominators and all relevant household totals reconciling to the directly estimated state.
- Verified fixed plot ranges include every county estimate and median-rent margin of error.
- Checked the documented scenario counts and pooled rates, including no-result $600 and the two-county $1,000/20,000-household state.
- Verified source checksum, local pinned Plotly runtime, MIT license, article iframe path and local assets. No credentials, private records, transient download URLs or external CDN runtime are required.

## Browser verification

The initial publication is being checked in a real browser; interaction results will be recorded here once observed. Numerical checks alone do not certify the controls or layout.

## Interpretation limits

Five-year survey estimates in 2024 dollars, not current listings. Household counts are represented households, not survey sample sizes. Point-estimate filters do not imply a statistical difference or a personally affordable/safe home. Published rent margins are 90% margins for county medians; no derived burden-rate interval is claimed. The dataset is intentionally reused from Blog 5, while the interactive comparison is new.
