# Blog 2 reproducibility check — October 19, 2026

This revision addresses the two half-point deductions visible in the supplied rubric: repository organization (README/file paths) and reproducibility/coding practices. It does not claim or guarantee a revised grade.

Verified locally with R 4.6.1 and installed package versions recorded in `results/session-info.txt`:

1. Copied the public Blog 2 inputs and scripts into a clean directory, omitting the entire `results/` folder and the original HTML cache.
2. Ran `Rscript` on the script's absolute path from `/private/tmp`, with spaces in the project path. No source-page download was used in default mode.
3. The script recreated all four output files. `skill_counts.csv` and `sample_summary.csv` exactly matched the original submitted CSV records: 253 posts, Python 68, React 51, TypeScript 51, PostgreSQL 40, AWS 34; co-mentions 20 and 34.
4. Tested the rvest extraction branch using the locally archived October 6 HTML fixture, substituting only the network read with the fixture and omitting the wait in the test copy. All 16 extracted skill counts matched the fixed indicator dataset. This checks parsing and extraction; a new live network collection was not performed.
5. The refresh branch saved separate inputs and outputs and left the submitted indicator dataset unchanged. Inspected the saved chart.

Default analysis no longer reads any existing `results/` files or silently switches to a local HTML cache. The fixed source metadata is under `data/`, checksums verify the input snapshot, every output is saved in code, and refresh uses a collection-date-specific caption.

The article's findings and sample period have not been changed. The project README documents installation, working directories, relative and absolute commands, the complete folder map, expected outputs, and the difference between reproducing a frozen snapshot and scraping a new page.
