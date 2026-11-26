"""Validate user-supplied CropIQ datasets before training or serving."""

from pathlib import Path
import sys
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
CROP_CSV = DATA_DIR / "Crop_recommendation.csv"
PRICES_DIR = DATA_DIR / "prices"

EXPECTED_COLUMNS = [
    "N",
    "P",
    "K",
    "temperature",
    "humidity",
    "ph",
    "rainfall",
    "label",
]

EXPECTED_CROPS = {
    "rice",
    "maize",
    "chickpea",
    "kidneybeans",
    "pigeonpeas",
    "mothbeans",
    "mungbean",
    "blackgram",
    "lentil",
    "pomegranate",
    "banana",
    "mango",
    "grapes",
    "watermelon",
    "muskmelon",
    "apple",
    "orange",
    "papaya",
    "coconut",
    "cotton",
    "jute",
    "coffee",
}


def check_crop_dataset(path: Path = CROP_CSV) -> pd.DataFrame:
    """Verify Crop_recommendation.csv structure, completeness, and crop labels."""
    if not path.exists():
        raise FileNotFoundError(f"Missing required dataset: {path}")

    df = pd.read_csv(path)
    if list(df.columns) != EXPECTED_COLUMNS:
        raise ValueError(
            f"Unexpected columns in {path.name}: {list(df.columns)} != {EXPECTED_COLUMNS}"
        )

    if len(df) != 2200:
        raise ValueError(f"Expected 2200 rows in {path.name}, found {len(df)}")

    missing_total = int(df.isna().sum().sum())
    if missing_total != 0:
        raise ValueError(f"Found {missing_total} missing values in {path.name}")

    labels = set(df["label"].astype(str).unique())
    if labels != EXPECTED_CROPS:
        raise ValueError(
            f"Crop labels mismatch. Missing={EXPECTED_CROPS - labels}, Extra={labels - EXPECTED_CROPS}"
        )

    counts = df["label"].value_counts()
    bad_counts = counts[counts != 100]
    if not bad_counts.empty:
        raise ValueError(f"Expected 100 rows per crop, got: {bad_counts.to_dict()}")

    return df


def check_paddy_prices(prices_dir: Path = PRICES_DIR) -> Path:
    """Verify paddy price CSV exists and inspect its modal series."""
    standard_path = prices_dir / "paddy.csv"
    alt_path = prices_dir / "paddy_prices.csv"
    if standard_path.exists():
        price_path = standard_path
    elif alt_path.exists():
        price_path = alt_path
    else:
        raise FileNotFoundError(
            f"Missing paddy price CSV in {prices_dir} (expected paddy.csv or paddy_prices.csv)"
        )

    df = pd.read_csv(price_path)
    required = ["date", "modal", "min", "max"]
    if list(df.columns) != required:
        raise ValueError(f"Unexpected columns in {price_path.name}: {list(df.columns)}")
    if len(df) != 61:
        raise ValueError(f"Expected 61 rows in {price_path.name}, found {len(df)}")
    if int(df["modal"].isna().sum()) != 0:
        raise ValueError(f"Found missing modal prices in {price_path.name}")

    print(
        f"Paddy prices ({price_path.name}): {len(df)} rows, "
        f"{df['date'].iloc[0]} to {df['date'].iloc[-1]}, "
        f"latest modal={df['modal'].iloc[-1]}"
    )
    if price_path.name != "paddy.csv":
        print(
            "Note: file is named paddy_prices.csv; Phase 2 expects data/prices/paddy.csv "
            "or a paddy alias."
        )
    return price_path


def main() -> int:
    df = check_crop_dataset()
    print(f"Crop dataset OK: {len(df)} rows, {df['label'].nunique()} crops, 0 missing values.")
    print("\nFeature min/max summary:")
    for col in EXPECTED_COLUMNS[:-1]:
        print(f"  {col:12s}: min={df[col].min():.4f}, max={df[col].max():.4f}")
    print()
    check_paddy_prices()
    return 0


if __name__ == "__main__":
    sys.exit(main())
