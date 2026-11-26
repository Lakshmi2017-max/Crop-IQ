"""Historical price range and per-acre profit engine for CropIQ."""

from pathlib import Path
import numpy as np
import pandas as pd

from app.schemas import CropEconomics

BACKEND_DIR = Path(__file__).resolve().parent.parent
PRICES_DIR = BACKEND_DIR / "data" / "prices"
ECONOMICS_CSV = BACKEND_DIR / "data" / "crop_economics.csv"

# Map ML dataset crop names to price/economics file names where they differ.
CROP_ECONOMICS_ALIASES = {
    "rice": "paddy",
}

HORIZON_MONTHS = 4

# Minimum-data rule: below this, a price range would look precise but is not
# trustworthy, so no range is shown ("price data not available").
MIN_MONTHS = 36   # months of price history in the file
MIN_PAIRS = 30    # pairs where BOTH month t and month t+4 have a price


def resolve_crop_economics_key(crop: str) -> str:
    """Resolve an ML crop label to its price/economics lookup key."""
    normalized = crop.strip().lower()
    return CROP_ECONOMICS_ALIASES.get(normalized, normalized)


def _parse_optional_float(raw_value: object) -> float | None:
    """Parse a CSV cell into float, returning None for TODO_SOURCE or empty cells."""
    if raw_value is None or pd.isna(raw_value):
        return None
    text = str(raw_value).strip()
    if not text or text.upper() == "TODO_SOURCE":
        return None
    return float(text)


def load_crop_economics_table(econ_csv_path: Path = ECONOMICS_CSV) -> dict[str, dict]:
    """Load per-crop yield and cultivation cost rows from crop_economics.csv."""
    if not econ_csv_path.exists():
        return {}

    df = pd.read_csv(econ_csv_path)
    table: dict[str, dict] = {}
    for _, row in df.iterrows():
        crop_key = str(row["crop"]).strip().lower()
        source_val = str(row.get("source", "TODO_SOURCE")).strip()
        year_val = str(row.get("year", "TODO_SOURCE")).strip()
        table[crop_key] = {
            "yield_quintal_per_acre": _parse_optional_float(row.get("yield_quintal_per_acre")),
            "cost_rs_per_acre": _parse_optional_float(row.get("cost_rs_per_acre")),
            "source": source_val if source_val else "TODO_SOURCE",
            "year": year_val if year_val else "TODO_SOURCE",
        }
    return table


def compute_price_range(
    price_csv_path: Path,
    horizon_months: int = HORIZON_MONTHS,
) -> dict | None:
    """Historical H-month price range from MODAL prices (5th-95th percentile of
    log price changes).

    - Pairs are matched by CALENDAR DATE (month t and month t+H), never by row
      position, because some crops have missing months.
    - Returns None when the file fails the minimum-data rule (MIN_MONTHS, MIN_PAIRS).
    - Ignores min/max columns: recent Agmarknet rows have inconsistent min/max.
    """
    if not price_csv_path.exists():
        return None

    df = pd.read_csv(price_csv_path)
    if "date" not in df.columns or "modal" not in df.columns:
        return None

    df = df[["date", "modal"]].dropna().copy()
    # normalise every date to the first of its month, keep one price per month
    df["date"] = pd.to_datetime(df["date"]).dt.to_period("M").dt.to_timestamp()
    df = df.drop_duplicates(subset="date", keep="last").sort_values("date")

    series = pd.Series(df["modal"].astype(float).to_numpy(), index=pd.DatetimeIndex(df["date"]))
    if len(series) < MIN_MONTHS:
        return None

    # price H calendar months after each month (NaN where that month is missing)
    later = series.reindex(series.index + pd.DateOffset(months=horizon_months)).to_numpy()
    valid = ~np.isnan(later)
    if int(valid.sum()) < MIN_PAIRS:
        return None

    # c_t = ln(price[t + H] / price[t]) over all months where both exist
    log_changes = np.log(later[valid] / series.to_numpy()[valid])
    q05 = float(np.quantile(log_changes, 0.05))
    q95 = float(np.quantile(log_changes, 0.95))

    latest_modal = float(series.iloc[-1])
    price_low = float(latest_modal * np.exp(q05))
    price_high = float(latest_modal * np.exp(q95))

    return {
        "price_low": round(price_low, 2),
        "price_expected": round(latest_modal, 2),
        "price_high": round(price_high, 2),
        "price_months_of_history": int(len(series)),
    }


def _find_price_csv(crop: str, prices_dir: Path) -> Path | None:
    """Find <crop>.csv or its mapped alias CSV inside prices_dir."""
    normalized = crop.strip().lower()
    direct_path = prices_dir / f"{normalized}.csv"
    if direct_path.exists():
        return direct_path

    alias_key = resolve_crop_economics_key(normalized)
    alias_path = prices_dir / f"{alias_key}.csv"
    if alias_path.exists():
        return alias_path
    return None


def get_crop_economics(
    crop: str,
    prices_dir: Path = PRICES_DIR,
    econ_table: dict[str, dict] | None = None,
) -> CropEconomics | None:
    """Build CropEconomics for a crop.

    The PRICE range needs only a price file that passes the minimum-data rule.
    The PROFIT needs real yield and cost in crop_economics.csv; until then the
    profit fields are None (never invented).
    Returns None when there is no usable price file for the crop.
    """
    if econ_table is None:
        econ_table = load_crop_economics_table()

    normalized = crop.strip().lower()
    alias_key = resolve_crop_economics_key(normalized)

    price_csv = _find_price_csv(normalized, prices_dir)
    if price_csv is None:
        return None

    price_stats = compute_price_range(price_csv)
    if price_stats is None:
        return None

    # a missing economics row is NOT an error: it just means no yield/cost yet
    econ_row = (
        econ_table.get(normalized)
        or econ_table.get(alias_key)
        or {
            "yield_quintal_per_acre": None,
            "cost_rs_per_acre": None,
            "source": "TODO_SOURCE",
            "year": "TODO_SOURCE",
        }
    )

    yield_q = econ_row["yield_quintal_per_acre"]
    cost_rs = econ_row["cost_rs_per_acre"]

    profit_low: float | None = None
    profit_expected: float | None = None
    profit_high: float | None = None

    if yield_q is not None and cost_rs is not None:
        profit_low = round(yield_q * price_stats["price_low"] - cost_rs, 2)
        profit_expected = round(yield_q * price_stats["price_expected"] - cost_rs, 2)
        profit_high = round(yield_q * price_stats["price_high"] - cost_rs, 2)

    raw_source = econ_row["source"]
    raw_year = econ_row["year"]
    if raw_source == "TODO_SOURCE":
        source_label = "CEDA Agmarknet modal prices; yield/cost: TODO_SOURCE"
    elif raw_year and raw_year != "TODO_SOURCE":
        source_label = f"CEDA Agmarknet modal prices; {raw_source} ({raw_year})"
    else:
        source_label = f"CEDA Agmarknet modal prices; {raw_source}"

    return CropEconomics(
        price_low=price_stats["price_low"],
        price_expected=price_stats["price_expected"],
        price_high=price_stats["price_high"],
        profit_low=profit_low,
        profit_expected=profit_expected,
        profit_high=profit_high,
        price_months_of_history=price_stats["price_months_of_history"],
        source=source_label,
    )
