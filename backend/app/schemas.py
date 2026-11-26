"""Pydantic request and response schemas for the CropIQ API."""

from typing import Literal
from pydantic import BaseModel, Field


class RecommendRequest(BaseModel):
    """Input payload for POST /recommend."""

    temperature: float = Field(..., allow_inf_nan=False, description="Temperature in Celsius")
    humidity: float = Field(..., allow_inf_nan=False, description="Relative humidity in %")
    rainfall: float = Field(..., allow_inf_nan=False, description="Rainfall in mm")

    # Soil nutrients and pH are optional; missing or null selects a partial/weather-only model.
    n: float | None = Field(default=None, allow_inf_nan=False, description="Nitrogen (N)")
    p: float | None = Field(default=None, allow_inf_nan=False, description="Phosphorus (P)")
    k: float | None = Field(default=None, allow_inf_nan=False, description="Potassium (K)")
    ph: float | None = Field(default=None, allow_inf_nan=False, description="Soil pH")

    rank_by: Literal["suitability", "profit"] = Field(
        default="suitability",
        description="Rank top 3 recommendations by ML suitability or expected profit",
    )


class ReasonDetail(BaseModel):
    """Structured comparison between one input feature and a crop's typical range."""

    feature: str
    value: float
    low: float
    high: float
    status: Literal["within", "below", "above"]


class CropEconomics(BaseModel):
    """Historical price range and estimated per-acre profit for one crop."""

    price_low: float
    price_expected: float
    price_high: float
    profit_low: float | None = None
    profit_expected: float | None = None
    profit_high: float | None = None
    price_months_of_history: int
    source: str


class CropRecommendation(BaseModel):
    """Single recommended crop with model vote share, explanations, and economics."""

    crop: str
    probability: float
    conditions_in_range: str
    reasons: list[str]
    reason_details: list[ReasonDetail]
    economics: CropEconomics | None = None


class RecommendResponse(BaseModel):
    """Response payload for POST /recommend."""

    mode: str
    soil_values_used: list[str]
    expected_accuracy: float
    recommendations: list[CropRecommendation]
    excluded_from_profit_ranking: list[str]
