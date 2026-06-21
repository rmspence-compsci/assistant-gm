import pandas as pd
from unittest.mock import patch
from valuation.sources.nfl_data import compute_momentum, normalize_momentum


def _make_weekly_df(rows):
    """Create a minimal weekly data DataFrame matching nfl_data_py output."""
    return pd.DataFrame(rows, columns=["player_id", "week", "target_share"])


def test_compute_momentum_returns_ratio_above_1_for_rising_player():
    df = _make_weekly_df([
        # Weeks 1-4: avg 0.10. Weeks 5-8: avg 0.20 (last 4 weeks)
        {"player_id": "ABC", "week": 1, "target_share": 0.10},
        {"player_id": "ABC", "week": 2, "target_share": 0.10},
        {"player_id": "ABC", "week": 3, "target_share": 0.10},
        {"player_id": "ABC", "week": 4, "target_share": 0.10},
        {"player_id": "ABC", "week": 5, "target_share": 0.20},
        {"player_id": "ABC", "week": 6, "target_share": 0.20},
        {"player_id": "ABC", "week": 7, "target_share": 0.20},
        {"player_id": "ABC", "week": 8, "target_share": 0.20},
    ])
    result = compute_momentum(df, last_n_weeks=4)
    assert result["ABC"] > 1.0


def test_compute_momentum_returns_1_for_flat_player():
    df = _make_weekly_df([
        {"player_id": "FLAT", "week": w, "target_share": 0.15}
        for w in range(1, 9)
    ])
    result = compute_momentum(df, last_n_weeks=4)
    assert abs(result["FLAT"] - 1.0) < 0.01


def test_compute_momentum_caps_at_3():
    df = _make_weekly_df([
        {"player_id": "HOT", "week": 1, "target_share": 0.01},
        {"player_id": "HOT", "week": 2, "target_share": 0.01},
        {"player_id": "HOT", "week": 3, "target_share": 0.01},
        {"player_id": "HOT", "week": 4, "target_share": 0.01},
        {"player_id": "HOT", "week": 5, "target_share": 0.50},
        {"player_id": "HOT", "week": 6, "target_share": 0.50},
        {"player_id": "HOT", "week": 7, "target_share": 0.50},
        {"player_id": "HOT", "week": 8, "target_share": 0.50},
    ])
    result = compute_momentum(df, last_n_weeks=4)
    assert result["HOT"] <= 3.0


def test_compute_momentum_handles_zero_season_targets():
    df = _make_weekly_df([
        {"player_id": "ZERO", "week": w, "target_share": 0.0}
        for w in range(1, 5)
    ])
    result = compute_momentum(df, last_n_weeks=4)
    assert result["ZERO"] == 0.0


def test_normalize_momentum_maps_ratio_to_0_10000():
    raw = {"ABC": 1.5, "DEF": 0.5, "GHI": 3.0}
    result = normalize_momentum(raw)
    assert result["GHI"] == 10000.0
    assert result["ABC"] == 5000.0
    assert result["DEF"] > 0.0
