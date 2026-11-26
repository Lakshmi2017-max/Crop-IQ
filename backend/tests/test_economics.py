"""Phase 2 tests for historical price range, profit calculation, and rank-by behavior."""

import shutil
import pandas as pd
import pytest
from fastapi.testclient import TestClient

from app.economics import ECONOMICS_CSV, PRICES_DIR, compute_price_range, get_crop_economics
from app.main import app
from app.recommender import CropRecommender
from app.schemas import RecommendRequest
from scripts.price_range_test import run_coverage_test


def test_paddy_price_range_matches_expected_band():
    """Supplied paddy.csv should yield latest ~2297 and range ~2035 to ~2629 (+/- 5%)."""
    stats = compute_price_range(PRICES_DIR / "paddy.csv")
    assert stats is not None
    assert stats["price_months_of_history"] == 61
    assert stats["price_expected"] == pytest.approx(2296.75, abs=0.5)
    assert stats["price_low"] == pytest.approx(2035.0, rel=0.05)
    assert stats["price_high"] == pytest.approx(2629.0, rel=0.05)


def test_paddy_walk_forward_coverage():
    """Coverage check over the last 12 months should reproduce ~9 of 12 (75%)."""
    res = run_coverage_test()
    assert res["total"] == 12
    assert res["hits"] >= 8  # expected ~9 of 12 (75%)


def test_rice_uses_paddy_prices_and_keeps_unprovided_profit_null():
    """With TODO_SOURCE yield/cost, rice returns real prices and null profit (never invented)."""
    econ = get_crop_economics("rice")
    assert econ is not None
    assert econ.price_expected == pytest.approx(2296.75, abs=0.5)
    assert econ.profit_low is None
    assert econ.profit_expected is None
    assert econ.profit_high is None
    assert "TODO_SOURCE" in econ.source


def test_price_range_needs_only_a_price_file_not_an_economics_row():
    """Price range shows whenever a price file passes the minimum-data rule.
    Profit stays None until real yield and cost exist."""
    for crop in ("watermelon", "pomegranate"):
        econ = get_crop_economics(crop)
        assert econ is not None
        assert econ.price_low < econ.price_expected < econ.price_high
        assert econ.profit_expected is None

    # mango has 35 months and 21 pairs (below the minimum); chickpea has no file
    assert get_crop_economics("mango") is None
    assert get_crop_economics("chickpea") is None

    with TestClient(app) as client:
        resp = client.post(
            "/recommend",
            json={"temperature": 21, "humidity": 82, "rainfall": 203,
                  "n": 90, "p": 42, "k": 43, "ph": 6.5},
        )
    assert resp.status_code == 200
    by_crop = {r["crop"]: r for r in resp.json()["recommendations"]}
    assert by_crop["rice"]["economics"] is not None
    for crop in ("watermelon", "pomegranate"):
        assert by_crop[crop]["economics"] is not None
        assert by_crop[crop]["economics"]["profit_expected"] is None


def test_profit_ranking_excludes_crops_without_data_and_sorts_by_profit(tmp_path):
    """When numeric yield/cost exist for a subset of crops, rank_by='profit' sorts and excludes others."""
    prices_dir = tmp_path / "prices"
    prices_dir.mkdir()
    shutil.copy(PRICES_DIR / "paddy.csv", prices_dir / "paddy.csv")

    # Synthetic watermelon file: 40 consecutive months, so it passes the
    # minimum-data rule (36 months, 30 pairs). Latest price is exactly 1250.
    months = pd.date_range("2022-01-01", periods=40, freq="MS")
    lines = ["date,modal,min,max"]
    for i, d in enumerate(months):
        lines.append(f"{d.strftime('%Y-%m-%d')},{1000 + 250 * i / 39:.2f},0,0")
    (prices_dir / "watermelon.csv").write_text("\n".join(lines) + "\n", encoding="utf-8")

    econ_csv = tmp_path / "crop_economics.csv"
    econ_csv.write_text(
        "crop,yield_quintal_per_acre,cost_rs_per_acre,source,year\n"
        "paddy,20,25000,Test Fixture,2025\n"
        "watermelon,100,20000,Test Fixture,2025\n",
        encoding="utf-8",
    )

    recommender = CropRecommender(prices_dir=prices_dir, econ_csv_path=econ_csv)
    req = RecommendRequest(
        temperature=21, humidity=82, rainfall=203,
        n=90, p=42, k=43, ph=6.5, rank_by="profit",
    )
    res = recommender.recommend(req)
    crops_order = [r.crop for r in res["recommendations"]]

    # watermelon: 100 * 1250 - 20000 = 105000; rice: 20 * 2296.75 - 25000 = 20935
    assert crops_order[0] == "watermelon"
    assert crops_order[1] == "rice"
    # pomegranate has no price file in this temporary folder, so it is excluded
    assert res["excluded_from_profit_ranking"] == ["pomegranate"]
    assert res["recommendations"][0].economics.profit_expected == pytest.approx(105000.0)
    assert res["recommendations"][1].economics.profit_expected == pytest.approx(
        20 * 2296.75 - 25000, abs=1.0
    )


def test_real_profit_ranking_lists_all_without_yield_cost():
    """With real TODO_SOURCE economics CSV, profit ranking excludes crops lacking profit data."""
    with TestClient(app) as client:
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
                "rank_by": "profit",
            },
        )
    assert resp.status_code == 200
    data = resp.json()
    assert data["excluded_from_profit_ranking"] == ["rice", "watermelon", "pomegranate"]
    assert ECONOMICS_CSV.exists()
