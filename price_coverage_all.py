"""Walk-forward check of the historical price range for every crop price file.

For each crop: use only information available at month t, build the 5th-95th
percentile range for the price H months later, and count how often the real
price landed inside it (last 12 testable months). Pairs are matched by calendar
date, so crops with missing months are handled correctly.

Run from the cropiq folder:
    .venv\\Scripts\\python.exe price_coverage_all.py
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

H = 4
TEST_N = 12
LO, HI = 0.05, 0.95
MIN_MONTHS, MIN_PAIRS = 36, 30
MIN_KNOWN = 10          # need at least this many past changes to build a range

folder = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("backend/data/prices")
off = pd.DateOffset(months=H)
rows = []

for f in sorted(folder.glob("*.csv")):
    name = f.stem
    if name == "ragi":          # not one of the 22 crops in the recommender
        continue
    df = pd.read_csv(f, parse_dates=["date"])
    df["date"] = df["date"].dt.to_period("M").dt.to_timestamp()
    s = (df.drop_duplicates("date").sort_values("date")
           .set_index("date")["modal"].astype(float))
    pairs = [t for t in s.index if t + off in s.index]

    if len(s) < MIN_MONTHS or len(pairs) < MIN_PAIRS:
        rows.append({"crop": name, "months": len(s), "pairs": len(pairs),
                     "tested": 0, "inside": 0, "coverage_pct": "",
                     "naive_mape_pct": "", "note": "below minimum, no range shown"})
        continue

    inside = tested = 0
    naive_errors = []
    for t in pairs[-TEST_N:]:
        # only changes whose outcome was already known at month t
        known = [np.log(s[u + off] / s[u]) for u in pairs if u + off <= t]
        if len(known) < MIN_KNOWN:
            continue
        lo = s[t] * np.exp(np.quantile(known, LO))
        hi = s[t] * np.exp(np.quantile(known, HI))
        actual = s[t + off]
        tested += 1
        inside += int(lo <= actual <= hi)
        naive_errors.append(abs(actual - s[t]) / actual)

    rows.append({"crop": name, "months": len(s), "pairs": len(pairs),
                 "tested": tested, "inside": inside,
                 "coverage_pct": round(100 * inside / tested) if tested else "",
                 "naive_mape_pct": round(100 * np.mean(naive_errors), 1) if naive_errors else "",
                 "note": ""})

out = pd.DataFrame(rows)
print(out.to_string(index=False))
out.to_csv("price_range_coverage.csv", index=False)
print("\nSaved price_range_coverage.csv")
