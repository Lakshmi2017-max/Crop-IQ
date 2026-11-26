"""Model selection, top-3 crop ranking, and plain-language explanations."""

import json
from pathlib import Path
import joblib
import pandas as pd

from app.economics import (
    ECONOMICS_CSV,
    PRICES_DIR,
    get_crop_economics,
    load_crop_economics_table,
)
from app.schemas import CropRecommendation, ReasonDetail, RecommendRequest

BACKEND_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BACKEND_DIR / "data" / "Crop_recommendation.csv"
MODELS_PATH = BACKEND_DIR / "models" / "mode_models.joblib"
PROFILES_PATH = BACKEND_DIR / "models" / "crop_profiles.json"

# Fixed order for soil keys and feature ordering.
SOIL_FEATURES = ["N", "P", "K", "ph"]
WEATHER_FEATURES = ["temperature", "humidity", "rainfall"]
ALL_FEATURES = SOIL_FEATURES + WEATHER_FEATURES

# Map API lowercase field names to dataset feature names.
API_TO_FEATURE = {
    "n": "N",
    "p": "P",
    "k": "K",
    "ph": "ph",
    "temperature": "temperature",
    "humidity": "humidity",
    "rainfall": "rainfall",
}
FEATURE_TO_API = {v: k for k, v in API_TO_FEATURE.items()}

# Human-readable labels and units for plain-language reason sentences.
FEATURE_DISPLAY = {
    "N": ("Nitrogen", ""),
    "P": ("Phosphorus", ""),
    "K": ("Potassium", ""),
    "ph": ("Soil pH", ""),
    "temperature": ("Temperature", "C"),
    "humidity": ("Humidity", "%"),
    "rainfall": ("Rainfall", "mm"),
}


def _format_num(value: float) -> str:
    """Format numbers cleanly without noisy trailing .0 when exact."""
    rounded = round(float(value), 2)
    if rounded.is_integer():
        return str(int(rounded))
    return f"{rounded:g}"


def compute_feature_bounds(csv_path: Path = DATA_PATH) -> dict[str, tuple[float, float]]:
    """Compute allowed [min, max] bounds per feature from the dataset widened by 10%."""
    if not csv_path.exists():
        raise FileNotFoundError(f"Missing dataset for validation bounds: {csv_path}")

    df = pd.read_csv(csv_path)
    bounds: dict[str, tuple[float, float]] = {}

    for feat in ALL_FEATURES:
        col_min = float(df[feat].min())
        col_max = float(df[feat].max())
        span = col_max - col_min
        low = col_min - 0.10 * span
        # Keep non-negative agricultural measurements (N, P, K, humidity, rainfall, pH) >= 0.
        if col_min >= 0:
            low = max(0.0, low)
        high = col_max + 0.10 * span
        bounds[feat] = (round(low, 2), round(high, 2))

    return bounds


def select_model_key(soil_inputs: dict[str, float | None]) -> tuple[str, list[str], str]:
    """Return (model_key, soil_values_used, mode_label) for the provided soil features."""
    soil_used = [feat for feat in SOIL_FEATURES if soil_inputs.get(feat) is not None]
    model_key = "+".join(soil_used) if soil_used else "none"

    if len(soil_used) == 4:
        mode_label = "A (full soil data)"
    elif len(soil_used) >= 1:
        mode_label = "B (partial soil data)"
    else:
        mode_label = "C (no soil data)"

    return model_key, soil_used, mode_label


class CropRecommender:
    """Loads trained subset models, crop profiles, bounds, and economics tables."""

    def __init__(
        self,
        models_path: Path = MODELS_PATH,
        profiles_path: Path = PROFILES_PATH,
        data_path: Path = DATA_PATH,
        prices_dir: Path = PRICES_DIR,
        econ_csv_path: Path = ECONOMICS_CSV,
    ) -> None:
        if not models_path.exists():
            raise FileNotFoundError(f"Missing trained models: {models_path}")
        if not profiles_path.exists():
            raise FileNotFoundError(f"Missing crop profiles: {profiles_path}")

        self.models: dict[str, dict] = joblib.load(models_path)
        with profiles_path.open("r", encoding="utf-8") as f:
            self.profiles: dict[str, dict[str, list[float]]] = json.load(f)
        self.bounds: dict[str, tuple[float, float]] = compute_feature_bounds(data_path)
        self.prices_dir = prices_dir
        self.econ_table = load_crop_economics_table(econ_csv_path)

    def validate_inputs(self, req: RecommendRequest) -> list[dict]:
        """Check provided values against dataset bounds widened by 10%. Returns error list."""
        provided = {
            "N": req.n,
            "P": req.p,
            "K": req.k,
            "ph": req.ph,
            "temperature": req.temperature,
            "humidity": req.humidity,
            "rainfall": req.rainfall,
        }
        errors: list[dict] = []
        for feat, value in provided.items():
            if value is None:
                continue
            low, high = self.bounds[feat]
            if value < low or value > high:
                api_field = FEATURE_TO_API[feat]
                errors.append(
                    {
                        "field": api_field,
                        "feature": feat,
                        "value": value,
                        "min": low,
                        "max": high,
                        "msg": (
                            f"{api_field} ({value}) is out of allowed range "
                            f"[{low}, {high}]"
                        ),
                    }
                )
        return errors

    def _build_explanations(
        self, crop: str, provided_inputs: dict[str, float]
    ) -> tuple[str, list[str], list[ReasonDetail]]:
        """Compare every provided input against the crop's 5th-95th percentile range."""
        profile = self.profiles[crop]
        reasons: list[str] = []
        details: list[ReasonDetail] = []
        in_range_count = 0

        for feat in ALL_FEATURES:
            if feat not in provided_inputs:
                continue
            val = float(provided_inputs[feat])
            lo, hi = profile[feat]
            if val < lo:
                status = "below"
            elif val > hi:
                status = "above"
            else:
                status = "within"
                in_range_count += 1

            name, unit = FEATURE_DISPLAY[feat]
            sentence = (
                f"{name} {_format_num(val)}{unit} is {status} the typical range "
                f"for {crop} ({_format_num(lo)}-{_format_num(hi)}{unit})"
            )
            reasons.append(sentence)
            details.append(
                ReasonDetail(
                    feature=feat,
                    value=val,
                    low=float(lo),
                    high=float(hi),
                    status=status,
                )
            )

        conditions_in_range = f"{in_range_count} of {len(provided_inputs)}"
        return conditions_in_range, reasons, details

    def recommend(self, req: RecommendRequest) -> dict:
        """Select the matching soil-subset model and return top 3 crop recommendations."""
        soil_inputs = {
            "N": req.n,
            "P": req.p,
            "K": req.k,
            "ph": req.ph,
        }
        model_key, soil_used, mode_label = select_model_key(soil_inputs)
        model_entry = self.models[model_key]
        clf = model_entry["model"]
        model_features: list[str] = model_entry["features"]
        cv_accuracy = round(float(model_entry["cv_accuracy"]), 4)

        provided_inputs: dict[str, float] = {
            "temperature": float(req.temperature),
            "humidity": float(req.humidity),
            "rainfall": float(req.rainfall),
        }
        for feat in soil_used:
            provided_inputs[feat] = float(soil_inputs[feat])  # type: ignore[arg-type]

        # Build a one-row DataFrame in the exact feature order expected by the model.
        row_df = pd.DataFrame(
            [[provided_inputs[feat] for feat in model_features]],
            columns=model_features,
        )

        # predict_proba gives the fraction of trees in the Random Forest voting for each crop
        # (not a calibrated probability).
        probs = clf.predict_proba(row_df)[0]
        classes = clf.classes_
        ranked_indices = probs.argsort()[::-1][:3]

        recommendations: list[CropRecommendation] = []
        for idx in ranked_indices:
            crop = str(classes[idx])
            prob = round(float(probs[idx]), 3)
            conditions_str, reasons, details = self._build_explanations(crop, provided_inputs)
            econ = get_crop_economics(
                crop,
                prices_dir=self.prices_dir,
                econ_table=self.econ_table,
            )
            recommendations.append(
                CropRecommendation(
                    crop=crop,
                    probability=prob,
                    conditions_in_range=conditions_str,
                    reasons=reasons,
                    reason_details=details,
                    economics=econ,
                )
            )

        excluded_from_profit_ranking: list[str] = []
        if req.rank_by == "profit":
            with_profit = [
                rec
                for rec in recommendations
                if rec.economics is not None and rec.economics.profit_expected is not None
            ]
            without_profit = [
                rec
                for rec in recommendations
                if rec.economics is None or rec.economics.profit_expected is None
            ]
            with_profit.sort(
                key=lambda rec: (
                    rec.economics.profit_expected,  # type: ignore[union-attr]
                    rec.probability,
                ),
                reverse=True,
            )
            excluded_from_profit_ranking = [rec.crop for rec in without_profit]
            recommendations = with_profit + without_profit

        return {
            "mode": mode_label,
            "soil_values_used": soil_used,
            "expected_accuracy": cv_accuracy,
            "recommendations": recommendations,
            "excluded_from_profit_ranking": excluded_from_profit_ranking,
        }
