import json
import time
import importlib
from unittest.mock import MagicMock
from sleeper.models import League, Roster, Matchup, Transaction, Player


def _make_cache(mock_client):
    import storage.cache as cache
    importlib.reload(cache)
    cache.get_client = lambda: mock_client
    return cache


def _single_eq_mock(row_data):
    """Mock for queries with one .eq() call (leagues, rosters, players, league_users)."""
    mock = MagicMock()
    target = (
        mock.table.return_value
        .select.return_value
        .eq.return_value
        .maybe_single.return_value
        .execute
    )
    if row_data is None:
        target.return_value = None
    else:
        target.return_value.data = row_data
    return mock


def _double_eq_mock(row_data):
    """Mock for queries with two .eq() calls (matchups, transactions)."""
    mock = MagicMock()
    target = (
        mock.table.return_value
        .select.return_value
        .eq.return_value
        .eq.return_value
        .maybe_single.return_value
        .execute
    )
    if row_data is None:
        target.return_value = None
    else:
        target.return_value.data = row_data
    return mock


# --- League ---

def test_get_league_returns_none_when_no_cache():
    cache = _make_cache(_single_eq_mock(None))
    assert cache.get_league("lg1") is None


def test_get_league_returns_none_when_stale():
    league_dict = {"league_id": "lg1", "name": "Stale", "season": "2025",
                   "total_rosters": 10, "scoring_settings": {}, "settings": {}}
    row = {"data": json.dumps(league_dict), "fetched_at": time.time() - 7200}
    cache = _make_cache(_single_eq_mock(row))
    assert cache.get_league("lg1") is None


def test_get_league_returns_league_when_fresh():
    league_dict = {"league_id": "lg1", "name": "Test", "season": "2025",
                   "total_rosters": 12, "scoring_settings": {"rec": 1}, "settings": {"leg": 10}}
    row = {"data": json.dumps(league_dict), "fetched_at": time.time()}
    mock_client = _single_eq_mock(row)
    cache = _make_cache(mock_client)

    result = cache.get_league("lg1")

    assert result is not None
    assert result.name == "Test"
    assert result.settings["leg"] == 10
    mock_client.table.assert_called_with("cache_leagues")


def test_upsert_league_calls_supabase_upsert():
    mock_client = MagicMock()
    cache = _make_cache(mock_client)
    league = League(league_id="lg1", name="Test", season="2025",
                    total_rosters=12, scoring_settings={}, settings={})

    cache.upsert_league(league)

    mock_client.table.assert_called_with("cache_leagues")
    upsert_args = mock_client.table.return_value.upsert.call_args[0][0]
    assert upsert_args["league_id"] == "lg1"
    assert "data" in upsert_args
    assert "fetched_at" in upsert_args


# --- Rosters ---

def test_get_rosters_returns_none_when_no_cache():
    cache = _make_cache(_single_eq_mock(None))
    assert cache.get_rosters("lg1") is None


def test_get_rosters_returns_list_when_fresh():
    roster_list = [{"roster_id": 1, "owner_id": "u1", "league_id": "lg1",
                    "players": ["p1"], "starters": ["p1"],
                    "wins": 5, "losses": 3, "ties": 0,
                    "points_for": 950.5, "points_against": 870.0}]
    row = {"data": json.dumps(roster_list), "fetched_at": time.time()}
    cache = _make_cache(_single_eq_mock(row))

    result = cache.get_rosters("lg1")

    assert result is not None
    assert len(result) == 1
    assert result[0].wins == 5
    assert isinstance(result[0], Roster)


# --- Players ---

def test_get_players_returns_none_when_no_cache():
    cache = _make_cache(_single_eq_mock(None))
    assert cache.get_players() is None


def test_get_players_returns_dict_when_fresh():
    players_dict = {"p1": {"player_id": "p1", "full_name": "Justin Jefferson",
                            "position": "WR", "team": "MIN", "status": "Active"}}
    row = {"data": json.dumps(players_dict), "fetched_at": time.time()}
    cache = _make_cache(_single_eq_mock(row))

    result = cache.get_players()

    assert result is not None
    assert result["p1"].full_name == "Justin Jefferson"
    assert isinstance(result["p1"], Player)


# --- Matchups ---

def test_get_matchups_returns_none_when_no_cache():
    cache = _make_cache(_double_eq_mock(None))
    assert cache.get_matchups("lg1", 10) is None


def test_get_matchups_returns_list_when_fresh():
    matchup_list = [{"matchup_id": 1, "roster_id": 1, "points": 115.5,
                     "starters": ["p1"], "week": 10}]
    row = {"data": json.dumps(matchup_list), "fetched_at": time.time()}
    cache = _make_cache(_double_eq_mock(row))

    result = cache.get_matchups("lg1", 10)

    assert result is not None
    assert result[0].points == 115.5
    assert isinstance(result[0], Matchup)


# --- Transactions ---

def test_get_transactions_returns_none_when_no_cache():
    cache = _make_cache(_double_eq_mock(None))
    assert cache.get_transactions("lg1", 10) is None


def test_get_transactions_returns_list_when_fresh():
    tx_list = [{"transaction_id": "t1", "type": "waiver", "roster_ids": [1],
                "adds": {"p1": 1}, "drops": None, "week": 10, "created": 1700000000}]
    row = {"data": json.dumps(tx_list), "fetched_at": time.time()}
    cache = _make_cache(_double_eq_mock(row))

    result = cache.get_transactions("lg1", 10)

    assert result is not None
    assert result[0].type == "waiver"
    assert isinstance(result[0], Transaction)


# --- League Users ---

def test_get_league_users_returns_none_when_no_cache():
    cache = _make_cache(_single_eq_mock(None))
    assert cache.get_league_users("lg1") is None


def test_get_league_users_returns_list_when_fresh():
    users_list = [{"user_id": "u1", "display_name": "testuser"}]
    row = {"data": json.dumps(users_list), "fetched_at": time.time()}
    cache = _make_cache(_single_eq_mock(row))

    result = cache.get_league_users("lg1")

    assert result is not None
    assert result[0]["display_name"] == "testuser"


# --- init_db is a no-op ---

def test_init_db_does_nothing():
    cache = _make_cache(MagicMock())
    cache.init_db()  # Should not raise
