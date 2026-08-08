import importlib
from unittest.mock import MagicMock, patch
from valuation.models import PlayerValue, FantasyCalcValue
from sleeper.models import League, Roster


def _make_league(has_superflex=True):
    positions = ["QB", "RB", "WR", "TE", "BN"]
    if has_superflex:
        positions = ["QB", "RB", "WR", "TE", "SF", "BN"]
    return League(
        league_id="123",
        name="Test League",
        season="2025",
        total_rosters=12,
        scoring_settings={"rec": 1.0},
        settings={"leg": 10, "roster_positions": positions},
    )


def _make_roster(roster_id, players):
    return Roster(
        roster_id=roster_id,
        owner_id="user1",
        league_id="123",
        players=players,
        starters=[],
        wins=5,
        losses=5,
        ties=0,
        points_for=1000.0,
        points_against=1000.0,
    )


def test_retrieve_context_includes_player_values_for_trade_question():
    mock_pv = PlayerValue(
        player_id="4046", format="2QB", value=9500,
        breakdown={}, computed_at="2025-10-01T00:00:00+00:00"
    )

    with (
        patch("storage.cache.get_league", return_value=_make_league(has_superflex=True)),
        patch("storage.cache.get_rosters", return_value=[_make_roster(1, ["4046"])]),
        patch("storage.cache.get_players", return_value={}),
        patch("storage.cache.get_matchups", return_value=[]),
        patch("storage.cache.get_transactions", return_value=[]),
        patch("storage.cache.get_league_users", return_value=[]),
        patch("storage.valuation_store.get_player_values_for_ids", return_value={"4046": mock_pv}),
        patch("storage.valuation_store.get_fantasycalc_values_for_ids", return_value={}),
    ):
        import rag.retriever as r
        importlib.reload(r)
        result = r.retrieve_context("should I trade Mahomes?", "123", 1)

    assert "player_values" in result
    assert result["player_values"]["4046"].value == 9500


def test_retrieve_context_includes_fantasycalc_values_for_trade_question():
    mock_fv = FantasyCalcValue(
        player_id="4046", format="2QB", value=9800, redraft_value=9200,
        overall_rank=2, position_rank=1, trend_30day=120,
        computed_at="2025-10-01T00:00:00+00:00",
    )

    with (
        patch("storage.cache.get_league", return_value=_make_league(has_superflex=True)),
        patch("storage.cache.get_rosters", return_value=[_make_roster(1, ["4046"])]),
        patch("storage.cache.get_players", return_value={}),
        patch("storage.cache.get_matchups", return_value=[]),
        patch("storage.cache.get_transactions", return_value=[]),
        patch("storage.cache.get_league_users", return_value=[]),
        patch("storage.valuation_store.get_player_values_for_ids", return_value={}),
        patch("storage.valuation_store.get_fantasycalc_values_for_ids", return_value={"4046": mock_fv}),
    ):
        import rag.retriever as r
        importlib.reload(r)
        result = r.retrieve_context("should I trade Mahomes?", "123", 1)

    assert "fantasycalc_values" in result
    assert result["fantasycalc_values"]["4046"].value == 9800


def test_retrieve_context_excludes_fantasycalc_values_for_lineup_question():
    with (
        patch("storage.cache.get_league", return_value=_make_league()),
        patch("storage.cache.get_rosters", return_value=[_make_roster(1, ["4046"])]),
        patch("storage.cache.get_players", return_value={}),
        patch("storage.cache.get_matchups", return_value=[]),
        patch("storage.cache.get_transactions", return_value=[]),
        patch("storage.cache.get_league_users", return_value=[]),
    ):
        import rag.retriever as r
        importlib.reload(r)
        result = r.retrieve_context("who should I start at RB?", "123", 1)

    assert "fantasycalc_values" not in result


def test_retrieve_context_excludes_player_values_for_lineup_question():
    with (
        patch("storage.cache.get_league", return_value=_make_league()),
        patch("storage.cache.get_rosters", return_value=[_make_roster(1, ["4046"])]),
        patch("storage.cache.get_players", return_value={}),
        patch("storage.cache.get_matchups", return_value=[]),
        patch("storage.cache.get_transactions", return_value=[]),
        patch("storage.cache.get_league_users", return_value=[]),
    ):
        import rag.retriever as r
        importlib.reload(r)
        result = r.retrieve_context("who should I start at RB?", "123", 1)

    assert "player_values" not in result


def test_infer_format_returns_2qb_for_superflex_league():
    import rag.retriever as r
    importlib.reload(r)
    league = _make_league(has_superflex=True)
    assert r._infer_format(league) == "2QB"


def test_infer_format_returns_1qb_for_standard_league():
    import rag.retriever as r
    importlib.reload(r)
    league = _make_league(has_superflex=False)
    assert r._infer_format(league) == "1QB"
