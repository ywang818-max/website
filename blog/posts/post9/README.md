# Blog 9: stock forecasting outside the classroom

Article: https://ywang818-max.github.io/website/blog/posts/post9/

## Reproduce the analysis offline

Python 3.12 and the pinned packages in `code/requirements.txt` are required. On macOS XGBoost also needs an OpenMP runtime (`brew install libomp`, or an existing compatible libomp). No network access, Yahoo account or R installation is required for the frozen analysis.

```sh
python -m venv .venv
source .venv/bin/activate
python -m pip install -r code/requirements.txt
python code/build.py
python code/verify.py
```

These commands resolve paths relative to their scripts, so they also work from another working directory. `build.py` writes predictions, validation scores, holdings, portfolio windows, model binaries and summaries into `results/`. `verify.py` independently checks saved prices, every test target, ranking selections, weights, compounded investment results and RMSE. The class paired statistics were also checked with R independently.

`code/render.py` regenerates the article's numerical prose and SVG figures. It also updates this repository's prebuilt `docs` site using its existing article shell and Pandoc (or the Pandoc bundled with RStudio). This step expects the complete website repository. The computational commands above work with just this post directory. Standard Quarto can instead render `index.qmd` after the figures exist.

## Files

- `index.qmd`: generated 600–800-word article.
- `code/build.py`: frozen-data analysis and model fitting.
- `code/verify.py`: independent output checks.
- `code/render.py`: figures, numerical prose and committed-site rendering.
- `code/download.py`: optional Yahoo snapshot refresh, separate from offline reproduction. A refresh changes evidence and requires rerunning validation; do not treat it as the original snapshot.
- `code/classroom_original.R`: professor's stock-model script preserved unchanged.
- `code/classroom_results.R`: professor's results-comparison script preserved unchanged; its original local path must be edited to run it elsewhere.
- `code/extract_class.R`: optional extraction from the supplied Excel file and independent paired t-test, using `readxl`. It takes an input XLSX path and output CSV path as two arguments.
- `data/class_results.csv`: all 45 anonymous numeric portfolio pairs from `Full_Results-1.xlsx`, Sheet1 A1:B46. No missing values or participant identifiers. Means and differences are dollars; no initial-capital assumption is needed.
- `data/prices.csv.gz`: frozen Yahoo daily OHLC, volume and adjusted-close snapshot for 95 stocks and SPY. CSV can be decompressed with standard gzip tools. Original precision retained to nine significant digits before analysis.
- `data/manifest.json`: retrieval URLs, counts and original JSON SHA256 checksums, including the failed BK request. Original individual JSON files are not required by the offline analysis; the provided compressed snapshot is the controlling input.
- `data/design.json`: training/validation/test boundaries, candidate grid, timing and cost assumptions specified before fitting.
- `results/summary.json`: article numbers, date boundaries, versions and compressed snapshot hash.
- `results/validation_selection.csv`: all four candidates; selection solely by 2024 pooled RMSE.
- `results/test_predictions.csv.gz`: all 17,955 test stock-date targets and three forecasts.
- `results/prediction_metrics.csv`: RMSE, MAE and direction accuracy.
- `results/holdings.csv`: ten selected stocks, weights and realized targets per model/window.
- `results/portfolio_windows.csv`: gross/net block returns and wealth paths for both models, all-stock equal weight and matched-window SPY.
- `results/investment_metrics.csv`: cumulative return under 0, 10 and 25 basis points each side.
- `results/original.ubj`, `results/revised.ubj`: fitted XGBoost models.
- `results/classroom.svg`, `prediction.svg`, `investment.svg`: three substantive figures.
- `results/verification.json`: scope and outcome of executed independent checks.

## What is reproduced and what changes

The professor's recipe uses every numeric field except the target, treating symbol/date as IDs. The reconstructed baseline retains OHLC, volume, adjusted close, same-day returns, SPY returns, inverted momentum ratios as written, 22-observation lagged volatility and market-adjusted return. It uses 300 trees, depth 5, learning rate .05, min-child-weight 10 and gamma 0, with a fixed seed and histogram tree construction. A training-mean initial prediction is explicit. This is a Python reconstruction, not a claim of bitwise equivalence to an unavailable fitted R model or its original Yahoo vintage.

The extension uses lagged price ratios in the usual momentum direction (prior close divided by older close minus one), lagged excess return and volatility. It removes nominal price/volume levels and current-day raw-return fields. Lambda=10, depth in {2,3} and trees in {100,300} were the four candidates. Both final models train on the same 33,725 rows. Validation contains 22,040 rows. Neither model is refitted on 2024.

Training labels must finish before January 2024. Validation labels must finish before January 2025. The date cutoffs alone in the original script did not purge labels crossing the split. Here the final training signal is November 30, 2023 and its last label ends December 29. All predictors are available by signal close; entry is the NEXT close. Both models use the same target `adjusted[t+20]/adjusted[t+1]-1`, which is 19 close-to-close return intervals, although the classroom script calls it a 20-day forecast.

The baseline's original compounding, SPY aggregation and annualized Sharpe/alpha code are not used uncritically: monthly returns were annualized with daily factors and the original SPY window differed from the model target. The corrected comparison uses identical nonoverlapping entry/exit windows for all arms. It reports cumulative, unannualized performance only. There are ten model windows January 3–October 21, 2025; the remaining data permit evaluating all eligible daily forecasts through October 3 but not a complete eleventh portfolio block. Signals are spaced 20 trading days, entry t+1 and exit t+20. The next entry is t+21, creating a one-close cash interval. Cash earns zero. The market-timing gaps apply equally to matched-window comparators. A genuine passive SPY comparison over the endpoints, with only one entry and exit, is also reported separately in `summary.json`.

Model portfolio weights normalize positive predictions among the top ten. If all ten predictions are nonpositive, they receive equal weights. All-stock equal weight avoids arbitrary top-ten tie-breaking for the constant-forecast benchmark. Each strategy is liquidated at each window end; the conservative cost convention charges its entire capital 0.1% on each purchase and sale (0.25% sensitivity). Net gross factors are `(1-c)^2 * (1+r)`; costs are assumptions, not measured broker charges. Adjusted prices approximate reinvested corporate-action/dividend returns. Taxes, market impact, borrowing, risk-free return and liquidity limits are not modeled.

## Interpretation limits and sources

The supplied universe is retrospective and excludes failed ticker BK, so survivorship/selection bias remains. Data downloaded in November 2026 are not a point-in-time corporate-action database. No test-tuned settings or economic-performance selection were used. Lower global RMSE does not imply better stock ranking; higher portfolio return in ten windows does not establish persistent risk-adjusted alpha. Class pairs share market shocks, so the paired confidence interval is descriptive, conditional on the usual pair-independence assumption, not evidence from 45 independent markets. We do not attribute classroom outcomes to XGBoost without portfolio identities.

Sources: professor-supplied spreadsheets/scripts; Yahoo Finance chart endpoint (individual URLs in manifest); XGBoost parameter documentation https://xgboost.readthedocs.io/en/stable/parameter.html ; time-ordered validation https://scikit-learn.org/stable/modules/cross_validation.html#time-series-split . Professor's example WSJ article was consulted for concise, figure-led presentation; it supplies no stock data or claims.
