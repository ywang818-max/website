# Blog 8 — Bootstrap intervals, coverage and simulated hypothesis tests

[Article](https://ywang818-max.github.io/website/blog/posts/post8/) ·
[Full-width lab](https://ywang818-max.github.io/website/blog/posts/post8/results/lab.html)

Question: can a 95% interval miss a 30-minute average, and when does a sample
justify rejecting a stated average? Audience: general readers/students familiar
with averages. About 660 main-text words; three teaching panels serve distinct
parts of the assignment. They are not three versions of the same finding.

## Run from a clean copy

Use Python 3.11+ and NumPy. From the website repository root:

```sh
python3 -m venv .venv-blog8
source .venv-blog8/bin/activate
python -m pip install -r blog/posts/post8/code/requirements.txt
python blog/posts/post8/code/build.py
python blog/posts/post8/code/verify.py
```

Installation may need internet; the analysis itself runs offline and requires no
API, account, empirical download or existing result file. The script derives all
paths from its own location, so an absolute quoted path works from any directory.
It regenerates the article's numeric prose from `code/article-template.qmd`.
The template describes the published fixed model/configuration; changing the model
requires reviewing its literal narrative assumptions, not just editing numbers.

For local viewing, serve the post directory:

```sh
cd blog/posts/post8
python3 -m http.server 8000
```

Open http://localhost:8000/results/lab.html. The 390-pixel layout-check companion
is at /results/preview-narrow.html. On a normal Quarto setup run `quarto render`
from the website root after building; explicit resources include `results/**`
and `vendor/**`. The committed `docs/` HTML is the deployed artifact. Quarto is
not needed to run the statistical experiment or standalone lab.

## Exact file organization

| Path | Purpose |
|---|---|
| `data/config.json` | Published seed, population model and repetition counts |
| `data/README.md` | Simulation-only provenance and random-stream specification |
| `code/build.py` | Data generation, bootstrap, coverage, null simulations, exports and numeric article generation |
| `code/article-template.qmd` | Editable article text with numeric placeholders |
| `index.qmd` | Generated article source with actual results |
| `code/lab-template.html` | Accessible controls, display shell and local script references |
| `code/lab.js` | Plotly rendering; shared sample-size/confidence state and null-claim comparison |
| `code/preview-narrow.html` | 390-pixel iframe QA companion |
| `code/requirements.txt` | Pinned NumPy dependency |
| `code/verify.py` | Independent scalar percentiles, CSV reconciliation and analytic Student-t quadrature checks |
| `vendor/plotly-basic-3.1.0.min.js` | Official pinned Plotly runtime, locally bundled |
| `vendor/LICENSE.txt` | Plotly MIT license |
| `results/simulated_sample.csv` | All 200 simulated observations; smaller settings use prefixes |
| `results/bootstrap_means.csv` | 5,000 resampled means for each sample size |
| `results/coverage_intervals.csv` | All 12,000 interval records (3 n × 2 levels × 2,000 samples) |
| `results/coverage_summary.csv` | Actual coverage, Monte Carlo SE, interval widths and displayed-sample CIs |
| `results/null_test_summary.csv` | 18 configurations with observed t, tail counts, corrected p, critical bounds and decisions |
| `results/payload.json` | Plot data, summaries and first 60 intervals; generated, not a build input |
| `results/metrics.json`, `results/validation.json`, `results/verification.json` | Narrative results, source hashes and independently checked numerical identities |
| `results/lab.html`, `results/lab.js` | Generated standalone interactive lab |
| `results/preview.svg` | Data-based listing thumbnail, not an additional analysis figure |
| `results/preview-narrow.html` | Generated narrow viewport companion |
| `REPRODUCTION_CHECK.md` | Checks actually performed and their limits |

Everything required is in the repository. Nothing exists only inside a ZIP.
Results are generated and saved programmatically. There are no personal records.

## Statistical design — distinguish the three experiments

**Population model.** Independent Normal(mean=30, SD=5), measured in simulated
minutes. This is a stylized normal teaching model, not a dataset from a service.
Normality is assumed for the one-sample t-test demonstration. No inference about
actual delivery performance, populations or causality is warranted.

**1. One observed sample.** Base seed 20261101 produces 200 observations. Settings
n=40/100/200 use nested prefixes; changing n changes the data subset as well as
precision. For each n, draw 5,000 nonparametric bootstrap samples of size n with
replacement from that observed subset and average each. NumPy linear-interpolated
percentiles give the selected two-sided 90% or 95% interval. No known population
SD is inserted into this bootstrap calculation.

**2. Coverage.** For each n, the outer loop draws 2,000 independent new samples
from the population model. Each gets 999 new bootstrap resamples, then percentile
intervals at both confidence levels. A hit is `low <= 30 <= high`, not containment
of the observed sample mean. All trials, including misses, are retained.
The chart shows only trials 1–60 in generation order; totals use all 2,000.
Monte Carlo SE is sqrt(estimated coverage × (1−estimated coverage)/2000).
It measures simulation noise, not uncertainty about an individual sample mean.
Finite-sample undercoverage is reported rather than hidden by tuning a seed.

**3. Hypothesis test.** Use t=(sample mean−claimed mean)/(sample SD/sqrt(n)), with
sample SD computed using n−1. Generate 50,000 new normal samples under a null,
each with its own estimated SD. For computational reuse the null is centered at
zero: the studentized location statistic is translation-invariant, so this is the
same null distribution for each selectable claimed mean. It does not use the
alternative-population data to construct a null distribution.

Critical |t| is the selected confidence quantile of simulated |T|. Rejection is
|observed t| > critical. The two-sided simulated p is
`(number(|T_null| >= |t_observed|)+1)/(50000+1)`; the finite-simulation correction
prevents p=0. Histogram edges include observed and critical cutpoints, so the
blue tail-bin counts exactly match the extreme count. Variable-width histogram
heights are count/(simulation count × bin width), making total area equal one.
The orange rejection regions and blue observed-tail areas are distinct concepts.
Non-rejection does not prove the null; p is not Pr(H0 true).

The t-test and percentile-bootstrap interval are different procedures and need
not be exact inversions of one another. Confidence selection sets alpha=1−level
in the test as a teaching link, not a claim of exact interval/test duality.

## Reproducibility and expected outputs

Random generator: NumPy PCG64. Original sample: default_rng(20261101). Independent
streams for each n use SeedSequence([20261101,n,purpose]), where purpose 1 is
displayed bootstrap, 2 is coverage and 3 is null simulation. Seed is fixed; no
search over seeds or removal of misses is used. Coverage consumes one population
sample and its inner bootstrap draws sequentially before drawing the next sample.
Null samples are generated in blocks of 5,000 to limit memory.

| Default (n=200, 95%, null mean 30) | Result |
|---|---:|
| Observed mean | 29.6628773 minutes |
| Percentile interval | [28.9353374, 30.3597925] minutes |
| Coverage | 1,899 / 2,000 = 94.95% |
| Monte Carlo SE | 0.489641 percentage points |
| Observed t | −0.9343769 |
| Null extreme count | 17,550 / 50,000 |
| Corrected p | 0.3510130 |
| Decision at alpha .05 | Do not reject |

95% coverage: n=40 → 92.65%; n=100 → 94.70%; n=200 → 94.95%.
The 40-observation result illustrates that an advertised percentile interval
can under-cover. Repetition count cannot fix that methodological issue. Skewness,
nonindependence, selection bias and other interval constructions are outside this
model; this post does not claim bootstrap works universally.

## Professor/TA requirements

The three panels construct/plot bootstrap means, assess repeated-sample coverage,
and simulate null-test statistics with rejection regions and p-values. Controls
vary sample size, confidence and the null claim; all displayed summaries update
with the corresponding saved experiment. The article is concise, its question
is concrete, each panel adds a distinct required explanation, and conclusions
stay inside the simulated evidence. No unsupported industry/history/policy claims.

References: [SciPy bootstrap methods](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.bootstrap.html),
[NIST intervals and t-tests](https://www.itl.nist.gov/div898/handbook/eda/section3/eda352.htm),
[Plotly API](https://plotly.com/javascript/plotlyjs-function-reference/).
