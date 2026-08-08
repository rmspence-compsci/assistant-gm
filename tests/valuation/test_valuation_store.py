import importlib
from unittest.mock import MagicMock, patch
from valuation.models import PlayerValue, PickValue, ValuationWeights, FantasyCalcValue


def _make_client():
    return MagicMock()


def test_get_player_value_returns_none_when_no_row():
    mock_client = _make_client()
    mock_client.table.return_value.select.return_value.eq.return_value.eq.return_value \
        .order.return_value.limit.return_value.maybe_single.return_value.execute.return_value = None

    with patch("auth.client.get_client", return_value=mock_client):
        import storage.valuation_store as vs
        importlib.reload(vs)
        result = vs.get_player_value("4046", "1QB")
    assert result is None


def test_get_player_value_returns_player_value_object():
    mock_client = _make_client()
    mock_resp = MagicMock()
    mock_resp.data = {
        "player_id": "4046",
        "format": "1QB",
        "value": 8500,
        "breakdown_json": {"dp_value": 9000},
        "computed_at": "2025-10-01T00:00:00+00:00",
    }
    mock_client.table.return_value.select.return_value.eq.return_value.eq.return_value \
        .order.return_value.limit.return_value.maybe_single.return_value.execute.return_value = mock_resp

    with patch("auth.client.get_client", return_value=mock_client):
        import storage.valuation_store as vs
        importlib.reload(vs)
        result = vs.get_player_value("4046", "1QB")
    assert isinstance(result, PlayerValue)
    assert result.value == 8500
    assert result.breakdown["dp_value"] == 9000


def test_upsert_player_values_calls_upsert_with_correct_payload():
    mock_client = _make_client()
    with patch("auth.client.get_service_client", return_value=mock_client):
        import storage.valuation_store as vs
        importlib.reload(vs)
        pv = PlayerValue(
            player_id="4046", format="1QB", value=8500,
            breakdown={"dp_value": 9000}, computed_at="2025-10-01T00:00:00+00:00"
        )
        vs.upsert_player_values([pv])
    mock_client.table.return_value.upsert.assert_called_once()
    payload = mock_client.table.return_value.upsert.call_args[0][0]
    assert payload[0]["player_id"] == "4046"
    assert payload[0]["value"] == 8500


def test_get_weights_returns_valuation_weights():
    mock_client = _make_client()
    mock_resp = MagicMock()
    mock_resp.data = {
        "format": "1QB",
        "dp_value": 0.5,
        "adp_normalized": 0.25,
        "age_factor": 0.15,
        "momentum": 0.075,
        "trending": 0.025,
    }
    mock_client.table.return_value.select.return_value.eq.return_value \
        .maybe_single.return_value.execute.return_value = mock_resp

    with patch("auth.client.get_service_client", return_value=mock_client):
        import storage.valuation_store as vs
        importlib.reload(vs)
        result = vs.get_weights("1QB")
    assert isinstance(result, ValuationWeights)
    assert result.dp_value == 0.5


def test_get_player_values_for_ids_returns_dict_keyed_by_player_id():
    mock_client = _make_client()
    mock_resp = MagicMock()
    mock_resp.data = [
        {"player_id": "4046", "format": "1QB", "value": 8500,
         "breakdown_json": {}, "computed_at": "2025-10-01T00:00:00+00:00"},
        {"player_id": "2133", "format": "1QB", "value": 5500,
         "breakdown_json": {}, "computed_at": "2025-10-01T00:00:00+00:00"},
    ]
    mock_client.table.return_value.select.return_value.in_.return_value.eq.return_value \
        .order.return_value.execute.return_value = mock_resp

    with patch("auth.client.get_client", return_value=mock_client):
        import storage.valuation_store as vs
        importlib.reload(vs)
        result = vs.get_player_values_for_ids(["4046", "2133"], "1QB")
    assert "4046" in result
    assert result["4046"].value == 8500


def test_upsert_fantasycalc_values_calls_upsert_with_correct_payload():
    mock_client = _make_client()
    with patch("auth.client.get_service_client", return_value=mock_client):
        import storage.valuation_store as vs
        importlib.reload(vs)
        fv = FantasyCalcValue(
            player_id="9509", format="1QB", value=11174, redraft_value=10498,
            overall_rank=1, position_rank=1, trend_30day=565,
            computed_at="2025-10-01T00:00:00+00:00",
        )
        vs.upsert_fantasycalc_values([fv])
    mock_client.table.return_value.upsert.assert_called_once()
    payload = mock_client.table.return_value.upsert.call_args[0][0]
    assert payload[0]["player_id"] == "9509"
    assert payload[0]["value"] == 11174
    assert payload[0]["redraft_value"] == 10498


def test_get_fantasycalc_values_for_ids_returns_dict_keyed_by_player_id():
    mock_client = _make_client()
    mock_resp = MagicMock()
    mock_resp.data = [
        {"player_id": "9509", "format": "1QB", "value": 11174, "redraft_value": 10498,
         "overall_rank": 1, "position_rank": 1, "trend_30day": 565,
         "computed_at": "2025-10-01T00:00:00+00:00"},
    ]
    mock_client.table.return_value.select.return_value.in_.return_value.eq.return_value \
        .order.return_value.execute.return_value = mock_resp

    with patch("auth.client.get_client", return_value=mock_client):
        import storage.valuation_store as vs
        importlib.reload(vs)
        result = vs.get_fantasycalc_values_for_ids(["9509"], "1QB")
    assert "9509" in result
    assert result["9509"].value == 11174
    assert result["9509"].overall_rank == 1


def test_get_fantasycalc_values_for_ids_returns_empty_dict_for_empty_ids():
    mock_client = _make_client()
    with patch("auth.client.get_client", return_value=mock_client):
        import storage.valuation_store as vs
        importlib.reload(vs)
        result = vs.get_fantasycalc_values_for_ids([], "1QB")
    assert result == {}
