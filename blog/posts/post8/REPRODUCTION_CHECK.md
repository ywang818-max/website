# Blog 8 validation — November 1, 2026

## Numerical and clean-copy checks actually performed

- Ran the build and independent verifier from an unrelated working directory using a fresh copy without `results/` or generated `index.qmd`.
- All 13 result files and the generated article were byte-identical to the original build. Main prose: approximately 658 words, excluding code, equation and sources.
- Independently checked all three sample means and SDs using scalar sums; manually interpolated all six percentile intervals rather than importing the build's helper.
- Regenerated the first three resampled means at each sample size with the separate `choice` API and scalar summation; nine values agreed.
- Reconciled every one of the 12,000 coverage rows, six group totals, and all 360 first-60 interval records used in the plotting payload.
- Checked all 18 null-test result rows. Independent numerical integration of the analytic Student-t density agreed with every simulated p-value and critical-area estimate within five Monte Carlo standard errors. Maximum p-value discrepancy: 0.00150.
- Verified every histogram integrates to one, totals equal its simulation count, and blue null-tail bin counts exactly match the unbinned extreme count.
- Verified default results: mean 29.6628773; 95% bootstrap interval [28.9353374, 30.3597925]; coverage 1,899/2,000=94.95%; t=−0.9343769; corrected p=0.3510130.
- Input/config/runtime hashes are saved; all observations are simulated. JavaScript controller syntax checked independently.

## Browser checks

The generated lab is being checked in a real browser before final delivery. Browser outcomes will be recorded here after observation; numerical checks alone do not establish rendered usability.

## Limits

This is a fixed independent-normal teaching model, not empirical delivery-service data. Percentile bootstrap coverage is approximate and under-covers at n=40 in this experiment. Monte Carlo SE describes simulation noise. The t-test and percentile interval are not exact inverses. No universal coverage, real-service performance, significance-search or causal claims are warranted.
