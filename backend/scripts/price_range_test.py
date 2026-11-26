"""Reproduce historical 4-month price range and 12-month walk-forward coverage check."""

from pathlib import Path
import numpy as np
import pandas as pd

BACKEND_DIR = Path(__file__).resolve().parent.parent
PADDY_CSV = BACKEND_DIR / "data" / "prices" / "paddy.csv"
HORIZON_MONTHS = 4
EVAL_WINDOW = 12


def run_coverage_test(
    price_csv: Path = PADDY_CSV,
    horizon: int = HORIZON_MONTHS,
    eval_months: int = EVAL_WINDOW,
) -> dict:
    """Evaluate how often actual prices H months later fall inside the historical 5-95% range.

    For each evaluation month t, only log changes c_k = ln(p[k+H] / p[k]) whose
    outcome p[k+H] was already known at month t (k + H <= t) are used.
    """
    if not price_csv.exists():
        raise FileNotFoundError(f"Missing price file: {price_csv}")

    df = pd.read_csv(price_csv)[["date", "modal"]].dropna().copy()
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").reset_index(drop=True)

    prices = df["modal"].astype(float).to_numpy()
    dates = df["date"].dt.strftime("%Y-%m-%d").to_list()
    n = len(prices)

    # Full-history range from latest modal price
    all_changes = np.log(prices[horizon:] / prices[:-horizon])
    latest_modal = float(prices[-1])
    full_low = float(latest_modal * np.exp(np.quantile(all_changes, 0.05)))
    full_high = float(latest_modal * np.exp(np.quantile(all_changes, 0.95)))

    # Last `eval_months` origin months whose t + horizon outcome is observed
    start_t = n - horizon - eval_months
    end_t = n - horizon

    hits = 0
    rows = []
    for t in range(start_t, end_t):
        # Changes known by time t satisfy k + horizon <= t -> k <= t - horizon
        known_end = t - horizon + 1
        known_changes = np.log(prices[horizon : known_end + horizon] / prices[:known_end])
        low = float(prices[t] * np.exp(np.quantile(known_changes, 0.05)))
        high = float(prices[t] * np.exp(np.quantile(known_changes, 0.95)))
        actual = float(prices[t + horizon])
        inside = low <= actual <= high
        if inside:
            hits += 1
        rows.append(
            {
                "origin_date": dates[t],
                "target_date": dates[t + horizon],
                "origin_modal": round(float(prices[t]), 2),
                "low": round(low, 2),
                "high": round(high, 2),
                "actual_4m": round(actual, 2),
                "inside": inside,
            }
        )

    coverage = hits / eval_months
    return {
        "months_of_history": n,
        "latest_date": dates[-1],
        "latest_modal": round(latest_modal, 2),
        "current_low": round(full_low, 2),
        "current_high": round(full_high, 2),
        "hits": hits,
        "total": eval_months,
        "coverage": coverage,
        "rows": rows,
    }


def main() -> None:
    res = run_coverage_test()
    print(f"Price file: {PADDY_CSV.name} ({res['months_of_history']} months, latest {res['latest_date']})")
    print(
        f"Latest modal: Rs {res['latest_modal']:.2f}/q | "
        f"4-month historical range (5th-95th): Rs {res['current_low']:.2f} to Rs {res['current_high']:.2f}/q\n"
    )
    print(
        f"{'Origin':<12} {'Target':<12} {'Origin Modal':>12} "
        f"{'Low':>10} {'High':>10} {'Actual 4m':>10} {'Inside':>8}"
    )
    print("-" * 78)
    for row in res["rows"]:
        print(
            f"{row['origin_date']:<12} {row['target_date']:<12} "
            f"{row['origin_modal']:>12.2f} {row['low']:>10.2f} {row['high']:>10.2f} "
            f"{row['actual_4m']:>10.2f} {'YES' if row['inside'] else 'NO':>8}"
        )
    print(
        f"\nWalk-forward coverage (last {res['total']} months): "
        f"{res['hits']} of {res['total']} ({res['coverage'] * 100:.1f}%)"
    )


if __name__ == "__main__":
    main()
