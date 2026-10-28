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

Observed on the published standalone explorer and inside the article iframe:

- Initial view: 67 table rows, 1,496,561 computed-burden households, 48.2% pooled burden; real Plotly SVG marks and axes visibly rendered.
- $1,000 / all sizes: 43 rows, 297,858 households, 43.6%; article iframe also updated correctly.
- $1,000 / minimum 20,000: 2 rows, 62,296 households, 44.7%; plotted dots, table and summary agreed.
- Selected Centre outside those filters: profile explicitly warned of exclusion; its actual $1,207 rent and 57.0% burden remained visible in the profile.
- Clicked Erie's plotted dot: selected Erie, displayed $904 ±$20, 49.2%, and 16,159 / 32,863 with 2,448 not-computed ratios.
- Enabled rent margins: horizontal error bars visibly rendered for the selected subset.
- Empty $600 state: zero rows and households, pooled rate shown as —, explanatory message; no stale previous pooled rate.
- Reset restored 67 rows and all default controls. $1,200 produced 54 rows and 45.4%.
- Activated Cameron's table button using Enter: keyboard-accessible profile displayed $689 ±$116 and the published income margin.
- Inspected the article iframe, auto-fit height, full-width link, and 390-pixel nested-viewport companion. Narrow controls stacked, statistics wrapped, axes remained readable, and $1,000 filtering returned the same 43 counties. The exact-data table intentionally scrolls horizontally on narrow displays.

The hover template and underlying displayed values were checked in source; automated interaction evidence above covers point clicks, controls and keyboard/table access, rather than claiming a separate pointer-hover test. These observations do not establish accessibility compliance for every browser or assistive technology.

## Interpretation limits

Five-year survey estimates in 2024 dollars, not current listings. Household counts are represented households, not survey sample sizes. Point-estimate filters do not imply a statistical difference or a personally affordable/safe home. Published rent margins are 90% margins for county medians; no derived burden-rate interval is claimed. The dataset is intentionally reused from Blog 5, while the interactive comparison is new.
