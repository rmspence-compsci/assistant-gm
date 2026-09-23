from unittest.mock import patch, MagicMock
from valuation.sources.ffc_adp import fetch_adp, normalize_adp

_SAMPLE_RESPONSE = {
    "players": [
        {"player_id": 4864, "name": "Jonathan Taylor", "position": "RB", "team": "IND",
         "adp": 1.4, "adp_formatted": "1.01", "times_drafted": 46, "high": 1, "low": 3, "stdev": 0.6, "bye": 13},
        {"player_id": 289,  "name": "Patrick Mahomes", "position": "QB", "team": "KC",
         "adp": 15.0, "adp_formatted": "2.03", "times_drafted": 200, "high": 10, "low": 20, "stdev": 2.5, "bye": 10},
        {"player_id": 99,   "name": "Deep Sleeper",   "position": "WR", "team": "HOU",
         "adp": 250.0, "adp_formatted": "21.02", "times_drafted": 5, "high": 240, "low": 260, "stdev": 10.0, "bye": 7},
    ]
}


def _mock_get(url, **kwargs):
    resp = MagicMock()
    resp.json.return_value = _SAMPLE_RESPONSE
    resp.raise_for_status = MagicMock()
    return resp


def test_fetch_adp_returns_list_of_player_dicts():
    with patch("valuation.sources.ffc_adp.requests.get", side_effect=_mock_get):
        result = fetch_adp()
    assert len(result) == 3
    assert result[0]["name"] == "Jonathan Taylor"
    assert result[0]["adp"] == 1.4


def test_fetch_adp_raises_on_http_error():
    def bad_get(url, **kwargs):
        resp = MagicMock()
        resp.raise_for_status.side_effect = Exception("HTTP 429")
        return resp

    with patch("valuation.sources.ffc_adp.requests.get", side_effect=bad_get):
        try:
            fetch_adp()
            assert False, "Should have raised"
        except Exception:
            pass


def test_normalize_adp_gives_highest_score_to_lowest_adp():
    players = _SAMPLE_RESPONSE["players"]
    normalized = normalize_adp(players, max_adp=300.0)
    jt_key = "Jonathan Taylor_RB"
    mahomes_key = "Patrick Mahomes_QB"
    deep_key = "Deep Sleeper_WR"
    assert normalized[jt_key] > normalized[mahomes_key]
    assert normalized[mahomes_key] > normalized[deep_key]


def test_normalize_adp_scales_top_pick_near_10000():
    players = [{"name": "Top Pick", "position": "QB", "adp": 1.0, "times_drafted": 100}]
    result = normalize_adp(players, max_adp=300.0)
    assert result["Top Pick_QB"] == 10000.0


def test_normalize_adp_floor_at_zero_for_beyond_max():
    players = [{"name": "Deep Pick", "position": "RB", "adp": 350.0, "times_drafted": 5}]
    result = normalize_adp(players, max_adp=300.0)
    assert result["Deep Pick_RB"] == 0.0
