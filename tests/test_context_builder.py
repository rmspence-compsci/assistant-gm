from sleeper.models import League, Roster, Player
from rag.context_builder import build_context


def _make_league():
    return League(
        league_id="lg1", name="Russ League", season="2025",
        total_rosters=12, scoring_settings={"rec": 1}, settings={"leg": 10},
    )


def _make_roster():
    return Roster(
        roster_id=1, owner_id="u1", league_id="lg1",
        players=["p1", "p2"], starters=["p1"],
        wins=7, losses=3, ties=0, points_for=1200.0, points_against=1100.0,
    )


def _make_players():
    return {
        "p1": Player(player_id="p1", full_name="Justin Jefferson", position="WR", team="MIN", status="Active"),
        "p2": Player(player_id="p2", full_name="Nick Chubb", position="RB", team="CLE", status="Active"),
    }


def test_build_context_includes_league_name():
    data = {"league": _make_league()}
    result = build_context(data)
    assert "Russ League" in result
    assert "Week 10" in result


def test_build_context_includes_record():
    data = {"league": _make_league(), "user_roster": _make_roster(), "players": _make_players()}
    result = build_context(data)
    assert "7-3" in result


def test_build_context_includes_starters():
    data = {"league": _make_league(), "user_roster": _make_roster(), "players": _make_players()}
    result = build_context(data)
    assert "Justin Jefferson" in result


def test_build_context_empty_data():
    result = build_context({})
    assert "No league data" in result


def test_build_context_standings():
    rosters = [
        Roster(roster_id=1, owner_id="u1", league_id="lg1", players=[], starters=[],
               wins=8, losses=2, ties=0, points_for=1400.0, points_against=1100.0),
        Roster(roster_id=2, owner_id="u2", league_id="lg1", players=[], starters=[],
               wins=6, losses=4, ties=0, points_for=1200.0, points_against=1100.0),
    ]
    data = {"standings": rosters}
    result = build_context(data)
    assert "STANDINGS" in result
    assert "8-2" in result
