from unittest.mock import patch, MagicMock
from valuation.sources.sleeper_trending import fetch_trending, normalize_trending


def _mock_get(url, **kwargs):
    resp = MagicMock()
    resp.json.return_value = [
        {"player_id": "4046", "count": 500},
        {"player_id": "2133", "count": 200},
        {"player_id": "6786", "count": 50},
    ]
    resp.raise_for_status = MagicMock()
    return resp


def test_fetch_trending_returns_dict_of_player_id_to_count():
    with patch("valuation.sources.sleeper_trending.requests.get", side_effect=_mock_get):
        result = fetch_trending()
    assert result["4046"] == 500
    assert result["2133"] == 200


def test_normalize_trending_gives_highest_score_to_top_count():
    raw = {"4046": 500, "2133": 200, "6786": 50}
    result = normalize_trending(raw)
    assert result["4046"] == 10000.0
    assert result["2133"] < result["4046"]


def test_normalize_trending_player_with_zero_count_gets_zero():
    raw = {"4046": 500, "9999": 0}
    result = normalize_trending(raw)
    assert result["9999"] == 0.0


def test_normalize_trending_empty_input_returns_empty():
    result = normalize_trending({})
    assert result == {}
