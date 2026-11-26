"""Phase 1 tests for CropIQ backend core: model selection, validation, and /recommend."""

from itertools import combinations
import re
import joblib
import pandas as pd
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.recommender import DATA_PATH, MODELS_PATH, SOIL_FEATURES, select_model_key


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(scope="module")
def trained_models():
    return joblib.load(MODELS_PATH)


@pytest.fixture(scope="module")
def dataset_df():
    return pd.read_csv(DATA_PATH)


def test_health_endpoint(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert resp.json() == {"status": "CropIQ API running"}


def test_all_16_soil_subset_keys():
    """Verify select_model_key maps every one of the 16 subsets in N, P, K, ph order."""
    seen_keys = set()
    for r in range(len(SOIL_FEATURES) + 1):
        for subset in combinations(SOIL_FEATURES, r):
            soil_inputs = {f: (50.0 if f in subset else None) for f in SOIL_FEATURES}
            key, used, mode = select_model_key(soil_inputs)
            expected_key = "+".join(subset) if subset else "none"
            assert key == expected_key
            assert used == list(subset)
            if r == 4:
                assert mode == "A (full soil data)"
            elif r == 0:
                assert mode == "C (no soil data)"
            else:
                assert mode == "B (partial soil data)"
            seen_keys.add(key)

    assert len(seen_keys) == 16


def test_modes_and_expected_accuracy(client, trained_models):
    """Modes A, B, C return the expected mode label and matching CV accuracy."""
    base_weather = {"temperature": 21.0, "humidity": 82.0, "rainfall": 203.0}

    # Mode A: all 4 soil values
    resp_a = client.post("/recommend", json={**base_weather, "n": 90, "p": 42, "k": 43, "ph": 6.5})
    assert resp_a.status_code == 200
    data_a = resp_a.json()
    assert data_a["mode"] == "A (full soil data)"
    assert data_a["soil_values_used"] == ["N", "P", "K", "ph"]
    assert data_a["expected_accuracy"] == pytest.approx(
        round(trained_models["N+P+K+ph"]["cv_accuracy"], 4), abs=1e-4
    )

    # Mode B: partial soil values (N + K)
    resp_b = client.post("/recommend", json={**base_weather, "n": 90, "k": 43})
    assert resp_b.status_code == 200
    data_b = resp_b.json()
    assert data_b["mode"] == "B (partial soil data)"
    assert data_b["soil_values_used"] == ["N", "K"]
    assert data_b["expected_accuracy"] == pytest.approx(
        round(trained_models["N+K"]["cv_accuracy"], 4), abs=1e-4
    )

    # Mode C: no soil values
    resp_c = client.post("/recommend", json=base_weather)
    assert resp_c.status_code == 200
    data_c = resp_c.json()
    assert data_c["mode"] == "C (no soil data)"
    assert data_c["soil_values_used"] == []
    assert data_c["expected_accuracy"] == pytest.approx(
        round(trained_models["none"]["cv_accuracy"], 4), abs=1e-4
    )


def test_rice_sanity_check_and_explanations(client):
    """Sanity check from spec section 14 and explanation formatting."""
    resp = client.post(
        "/recommend",
        json={
            "temperature": 21,
            "humidity": 82,
            "rainfall": 203,
            "n": 90,
            "p": 42,
            "k": 43,
            "ph": 6.5,
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    recs = data["recommendations"]
    assert len(recs) == 3
    assert recs[0]["crop"] == "rice"
    assert recs[0]["conditions_in_range"].endswith(" of 7")
    assert len(recs[0]["reasons"]) == 7
    assert len(recs[0]["reason_details"]) == 7

    pattern = re.compile(
        r"^(Nitrogen|Phosphorus|Potassium|Soil pH|Temperature|Humidity|Rainfall) "
        r".+ is (within|below|above) the typical range for [a-z]+ \(.+-.+\)$"
    )
    for sentence in recs[0]["reasons"]:
        assert pattern.match(sentence), f"Unexpected reason format: {sentence}"


@pytest.mark.parametrize("missing_field", ["temperature", "humidity", "rainfall"])
def test_missing_weather_returns_422(client, missing_field):
    payload = {"temperature": 21.0, "humidity": 82.0, "rainfall": 203.0}
    del payload[missing_field]
    resp = client.post("/recommend", json=payload)
    assert resp.status_code == 422


def test_out_of_range_values_return_422(client, dataset_df):
    base = {"temperature": 21.0, "humidity": 82.0, "rainfall": 203.0}

    # Well above max + 10% for temperature
    temp_max = float(dataset_df["temperature"].max())
    resp_high = client.post("/recommend", json={**base, "temperature": temp_max * 1.5})
    assert resp_high.status_code == 422

    # Negative soil nutrient (below min)
    resp_low = client.post("/recommend", json={**base, "n": -5.0})
    assert resp_low.status_code == 422

    # Out-of-range pH (above max + 10%)
    ph_max = float(dataset_df["ph"].max())
    resp_ph = client.post("/recommend", json={**base, "ph": ph_max * 1.5})
    assert resp_ph.status_code == 422
