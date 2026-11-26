"""Train all 16 soil-subset Random Forest models and save mode_models.joblib."""

from itertools import combinations
from pathlib import Path
import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import StratifiedKFold, cross_val_score

BACKEND_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BACKEND_DIR / "data" / "Crop_recommendation.csv"
MODELS_DIR = BACKEND_DIR / "models"
OUTPUT_PATH = MODELS_DIR / "mode_models.joblib"

# Fixed order required for model keys and feature vectors.
SOIL_FEATURES = ["N", "P", "K", "ph"]
WEATHER_FEATURES = ["temperature", "humidity", "rainfall"]


def mode_name_for_soil_count(count: int) -> str:
    """Map number of soil features provided to the CropIQ mode label."""
    if count == 4:
        return "A (full soil data)"
    if 1 <= count <= 3:
        return "B (partial soil data)"
    return "C (no soil data)"


def train_all_modes(data_path: Path = DATA_PATH, output_path: Path = OUTPUT_PATH) -> dict:
    """Train and cross-validate one RandomForestClassifier per soil-feature subset."""
    if not data_path.exists():
        raise FileNotFoundError(f"Missing dataset: {data_path}")

    df = pd.read_csv(data_path)
    y = df["label"]
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

    models: dict[str, dict] = {}
    summary_rows: list[tuple[str, int, str, float]] = []

    for r in range(len(SOIL_FEATURES) + 1):
        for subset in combinations(SOIL_FEATURES, r):
            key = "+".join(subset) if subset else "none"
            features = list(subset) + WEATHER_FEATURES
            X = df[features]

            clf = RandomForestClassifier(
                n_estimators=100,
                random_state=42,
                n_jobs=-1,
            )
            cv_scores = cross_val_score(clf, X, y, cv=cv, scoring="accuracy")
            cv_accuracy = float(cv_scores.mean())

            # Fit final model on all rows after measuring 5-fold CV accuracy.
            final_clf = RandomForestClassifier(
                n_estimators=100,
                random_state=42,
                n_jobs=-1,
            )
            final_clf.fit(X, y)

            models[key] = {
                "model": final_clf,
                "features": features,
                "cv_accuracy": cv_accuracy,
            }
            summary_rows.append((key, len(subset), mode_name_for_soil_count(len(subset)), cv_accuracy))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(models, output_path, compress=3)

    summary_rows.sort(key=lambda row: row[3], reverse=True)
    print(f"Saved {len(models)} models to {output_path}\n")
    print(f"{'Model Key':<16} {'Soil#':<6} {'Mode':<24} {'5-Fold CV Accuracy':>18}")
    print("-" * 68)
    for key, soil_count, mode_label, acc in summary_rows:
        print(f"{key:<16} {soil_count:<6} {mode_label:<24} {acc * 100:>17.2f}%")

    return models


def main() -> None:
    train_all_modes()


if __name__ == "__main__":
    main()
