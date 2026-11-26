"""Build typical per-crop feature ranges (5th-95th percentiles) in crop_profiles.json."""

import json
from pathlib import Path
import numpy as np
import pandas as pd

BACKEND_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BACKEND_DIR / "data" / "Crop_recommendation.csv"
MODELS_DIR = BACKEND_DIR / "models"
OUTPUT_PATH = MODELS_DIR / "crop_profiles.json"

ALL_FEATURES = ["N", "P", "K", "temperature", "humidity", "ph", "rainfall"]


def build_profiles(data_path: Path = DATA_PATH, output_path: Path = OUTPUT_PATH) -> dict:
    """Compute [5th percentile, 95th percentile] per feature for each crop."""
    if not data_path.exists():
        raise FileNotFoundError(f"Missing dataset: {data_path}")

    df = pd.read_csv(data_path)
    profiles: dict[str, dict[str, list[float]]] = {}

    for crop, group in df.groupby("label", sort=True):
        crop_ranges: dict[str, list[float]] = {}
        for feat in ALL_FEATURES:
            p5, p95 = np.percentile(group[feat].to_numpy(), [5, 95])
            crop_ranges[feat] = [round(float(p5), 1), round(float(p95), 1)]
        profiles[str(crop)] = crop_ranges

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(profiles, f, indent=2)

    return profiles


def main() -> None:
    profiles = build_profiles()
    print(f"Saved {len(profiles)} crop profiles to {OUTPUT_PATH}")
    if "rice" in profiles:
        print(f"Sample profile (rice): {profiles['rice']}")


if __name__ == "__main__":
    main()
