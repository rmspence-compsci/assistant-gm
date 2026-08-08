from unittest.mock import patch, MagicMock
from valuation.sources.fantasycalc import fetch_values, normalize_values

_SAMPLE_RESPONSE = [
    {
        "player": {
            "id": 9833, "name": "Bijan Robinson", "position": "RB", "maybeTeam": "ATL",
            "sleeperId": "9509", "espnId": "4430807",
        },
        "value": 11174, "overallRank": 1, "positionRank": 1,
        "trend30Day": 565, "redraftValue": 10498,
    },
    {
        "player": {
            "id": 100, "name": "Some Kicker", "position": "K", "maybeTeam": "KC",
            "sleeperId": None,
        },
        "value": 50, "overallRank": 400, "positionRank": 10,
        "trend30Day": 0, "redraftValue": 50,
    },
]


def _mock_get(url, **kwargs):
    resp = MagicMock()
    resp.json.return_value = _SAMPLE_RESPONSE
    resp.raise_for_status = MagicMock()
    return resp


def test_fetch_values_returns_list_and_passes_params():
    with patch("valuation.sources.fantasycalc.requests.get", side_effect=_mock_get) as mock_get:
        result = fetch_values(is_dynasty=True, num_qbs=2, num_teams=12, ppr=1)
    assert len(result) == 2
    _, kwargs = mock_get.call_args
    assert kwargs["params"] == {"isDynasty": "true", "numQbs": 2, "numTeams": 12, "ppr": 1}


def test_fetch_values_raises_on_http_error():
    def bad_get(url, **kwargs):
        resp = MagicMock()
        resp.raise_for_status.side_effect = Exception("HTTP 429")
        return resp

    with patch("valuation.sources.fantasycalc.requests.get", side_effect=bad_get):
        try:
            fetch_values()
            assert False, "Should have raised"
        except Exception:
            pass


def test_normalize_values_keys_by_sleeper_id():
    normalized = normalize_values(_SAMPLE_RESPONSE)
    assert "9509" in normalized
    assert normalized["9509"]["value"] == 11174
    assert normalized["9509"]["redraft_value"] == 10498
    assert normalized["9509"]["overall_rank"] == 1
    assert normalized["9509"]["position_rank"] == 1
    assert normalized["9509"]["trend_30day"] == 565


def test_normalize_values_skips_missing_sleeper_id():
    normalized = normalize_values(_SAMPLE_RESPONSE)
    assert len(normalized) == 1
    assert all(v.get("value") != 50 for v in normalized.values())
