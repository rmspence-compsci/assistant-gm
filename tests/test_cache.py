import time
import pytest
from sleeper.models import League, Roster, Matchup, Transaction, Player


def test_upsert_and_get_league(tmp_db):
    league = League(
        league_id="lg1", name="Test", season="2025",
        total_rosters=12, scoring_settings={"rec": 1}, settings={"leg": 10},
    )
    tmp_db.upsert_league(league)
    result = tmp_db.get_league("lg1")
    assert result is not None
    assert result.name == "Test"
    assert result.settings["leg"] == 10


def test_get_league_returns_none_when_stale(tmp_db, monkeypatch):
    import config.settings as s
    monkeypatch.setattr(s, "CACHE_TTL_SECONDS", 0)
    league = League(
        league_id="lg2", name="Stale", season="2025",
        total_rosters=10, scoring_settings={}, settings={},
    )
    tmp_db.upsert_league(league)
    time.sleep(0.01)
    result = tmp_db.get_league("lg2")
    assert result is None


def test_upsert_and_get_rosters(tmp_db):
    rosters = [
        Roster(roster_id=1, owner_id="u1", league_id="lg1",
               players=["p1"], starters=["p1"],
               wins=5, losses=3, ties=0, points_for=950.5, points_against=870.0),
    ]
    tmp_db.upsert_rosters("lg1", rosters)
    result = tmp_db.get_rosters("lg1")
    assert result is not None
    assert len(result) == 1
    assert result[0].wins == 5


def test_upsert_and_get_matchups(tmp_db):
    matchups = [Matchup(matchup_id=1, roster_id=1, points=115.5, starters=["p1"], week=10)]
    tmp_db.upsert_matchups("lg1", 10, matchups)
    result = tmp_db.get_matchups("lg1", 10)
    assert result is not None
    assert result[0].points == 115.5


def test_upsert_and_get_players(tmp_db):
    players = {"p1": Player(player_id="p1", full_name="Justin Jefferson", position="WR", team="MIN", status="Active")}
    tmp_db.upsert_players(players)
    result = tmp_db.get_players()
    assert result is not None
    assert result["p1"].full_name == "Justin Jefferson"


def test_upsert_and_get_transactions(tmp_db):
    transactions = [Transaction(transaction_id="t1", type="waiver", roster_ids=[1],
                                adds={"p1": 1}, drops=None, week=10, created=1700000000)]
    tmp_db.upsert_transactions("lg1", 10, transactions)
    result = tmp_db.get_transactions("lg1", 10)
    assert result is not None
    assert result[0].type == "waiver"
