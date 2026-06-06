import pytest
from unittest.mock import patch, MagicMock
from sleeper.client import get_user, get_user_leagues, get_rosters, get_matchups, get_transactions, get_all_players, get_league_users
from sleeper.models import SleeperUser, League, Roster, Matchup, Transaction


def _mock_response(data):
    mock = MagicMock()
    mock.json.return_value = data
    mock.raise_for_status = MagicMock()
    return mock


@patch("sleeper.client.requests.get")
def test_get_user(mock_get):
    mock_get.return_value = _mock_response(
        {"user_id": "u1", "username": "russ", "display_name": "Russ M"}
    )
    user = get_user("russ")
    assert isinstance(user, SleeperUser)
    assert user.user_id == "u1"
    mock_get.assert_called_once_with("https://api.sleeper.app/v1/user/russ", timeout=10)


@patch("sleeper.client.requests.get")
def test_get_user_leagues(mock_get):
    mock_get.return_value = _mock_response([
        {
            "league_id": "lg1", "name": "Test League", "season": "2025",
            "total_rosters": 12, "scoring_settings": {"rec": 1}, "settings": {"leg": 10},
        }
    ])
    leagues = get_user_leagues("u1", "2025")
    assert len(leagues) == 1
    assert isinstance(leagues[0], League)
    assert leagues[0].name == "Test League"


@patch("sleeper.client.requests.get")
def test_get_rosters(mock_get):
    mock_get.return_value = _mock_response([
        {
            "roster_id": 1, "owner_id": "u1", "players": ["p1"], "starters": ["p1"],
            "settings": {"wins": 5, "losses": 3, "ties": 0, "fpts": 950, "fpts_decimal": 50,
                         "fpts_against": 870, "fpts_against_decimal": 0},
        }
    ])
    rosters = get_rosters("lg1")
    assert len(rosters) == 1
    assert isinstance(rosters[0], Roster)
    assert rosters[0].wins == 5
    assert rosters[0].points_for == pytest.approx(950.5)


@patch("sleeper.client.requests.get")
def test_get_matchups(mock_get):
    mock_get.return_value = _mock_response([
        {"matchup_id": 1, "roster_id": 1, "points": 120.5, "starters": ["p1"]}
    ])
    matchups = get_matchups("lg1", 10)
    assert len(matchups) == 1
    assert isinstance(matchups[0], Matchup)
    assert matchups[0].week == 10


@patch("sleeper.client.requests.get")
def test_get_transactions(mock_get):
    mock_get.return_value = _mock_response([
        {
            "transaction_id": "t1", "type": "waiver", "roster_ids": [1],
            "adds": {"p99": 1}, "drops": None, "created": 1700000000,
        }
    ])
    transactions = get_transactions("lg1", 10)
    assert len(transactions) == 1
    assert isinstance(transactions[0], Transaction)
    assert transactions[0].type == "waiver"


@patch("sleeper.client.requests.get")
def test_get_all_players(mock_get):
    mock_get.return_value = _mock_response({
        "p1": {"full_name": "Justin Jefferson", "position": "WR", "team": "MIN", "status": "Active"},
        "p2": {"first_name": "Josh", "last_name": "Allen", "position": "QB", "team": "BUF", "status": "Active"},
        "p3": {"full_name": "Some Coach", "position": "COACH", "team": None, "status": None},
    })
    players = get_all_players()
    assert "p1" in players
    assert "p2" in players
    assert "p3" not in players  # COACH filtered out
    assert players["p1"].full_name == "Justin Jefferson"
    assert players["p2"].full_name == "Josh Allen"  # assembled from first/last


@patch("sleeper.client.requests.get")
def test_get_league_users(mock_get):
    mock_get.return_value = _mock_response([
        {"user_id": "u1", "display_name": "Russ", "metadata": {}}
    ])
    users = get_league_users("lg1")
    assert len(users) == 1
    assert users[0]["user_id"] == "u1"
