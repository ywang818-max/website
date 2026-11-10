# Executed verification, November 9, 2026

- Inspected all 45 supplied Excel pairs, their column meanings in the supplied R script, missingness and numeric types. No missing cells or identifiers. Independent R paired t-test matched Python: mean difference 1908.8908889 dollars, interval [-379.7180054,4197.4997831], two-sided p=.09985230.
- Froze the 2022–2025 Yahoo snapshot and recorded request URLs and hashes. 95 stocks plus SPY have identical 963-session calendars, positive prices, complete OHLC/volume/adjusted fields and no duplicate symbol-date keys. BK failed before fitting and was excluded.
- Four improved candidates selected strictly on 2024 RMSE, not investment returns. Both fitted models use identical 2022–23 training labels; training and validation future labels end strictly before the next split.
- Independently recalculated all 17,955 saved targets from frozen entry/exit adjusted prices; all saved RMSEs; all forty strategy/window returns; every model weight sum and selected top-ten set; and all twelve investment-cost scenarios. Tolerance 1e-12.
- Primary observed results: revised RMSE about 8.84 pp vs original 9.50 pp and constant 8.86 pp. With 10 bp each side, cumulative revised return about 38.7%, original 33.3%, equal-weight 11.7%, matched-window SPY 8.5%; endpoint buy-and-hold SPY about 14.2%.
- Figures and article are generated directly from saved outputs. Main prose is within the requested 600–800-word range. Clean-copy execution from an unrelated working directory recreated all ten computational result files byte-for-byte. All three SVG figures were visually reviewed; public browser checks follow publication.

The original R script is preserved; the Python baseline is a reconstruction with corrected evaluation timing, not a bitwise R reproduction. Ten nonoverlapping portfolio windows, a retrospective universe and historical adjusted-price vintage limit generalization. No claim of persistent alpha or future investment profitability is made.
