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
    data = {"all_rosters": rosters}
    result = build_context(data)
    assert "STANDINGS" in result
    assert "8-2" in result


def test_build_context_renders_dynasty_trade_values_for_trade_question():
    from valuation.models import PlayerValue

    pv = PlayerValue(
        player_id="4046", format="1QB", value=8500,
        breakdown={}, computed_at="2025-10-01T00:00:00+00:00"
    )
    data = {
        "player_values": {"4046": pv},
        "valuation_format": "1QB",
        "players": {},  # no player name lookup, falls back to player_id
    }
    result = build_context(data)
    assert "DYNASTY TRADE VALUES (1QB" in result
    assert "8500" in result


def test_build_context_caps_valuation_at_30_players():
    from valuation.models import PlayerValue

    player_values = {
        str(i): PlayerValue(
            player_id=str(i), format="1QB", value=i * 100,
            breakdown={}, computed_at="2025-10-01T00:00:00+00:00"
        )
        for i in range(1, 51)  # 50 players
    }
    data = {"player_values": player_values, "valuation_format": "1QB", "players": {}}
    result = build_context(data)
    # Count how many player lines appear (lines starting with "  ")
    value_lines = [line for line in result.split("\n") if line.startswith("  ") and ":" in line]
    assert len(value_lines) <= 30


def test_build_context_omits_valuation_section_when_no_player_values():
    data = {}  # no player_values key
    result = build_context(data)
    assert "DYNASTY TRADE VALUES" not in result


def test_build_context_renders_fantasycalc_market_consensus_for_trade_question():
    from valuation.models import FantasyCalcValue

    fv = FantasyCalcValue(
        player_id="4046", format="1QB", value=9500, redraft_value=9000,
        overall_rank=3, position_rank=1, trend_30day=250,
        computed_at="2025-10-01T00:00:00+00:00",
    )
    data = {
        "fantasycalc_values": {"4046": fv},
        "valuation_format": "1QB",
        "players": {},  # no player name lookup, falls back to player_id
    }
    result = build_context(data)
    assert "MARKET CONSENSUS (FantasyCalc, 1QB" in result
    assert "9500" in result
    assert "rank #3" in result
    assert "trend +250/30d" in result


def test_build_context_caps_fantasycalc_at_30_players():
    from valuation.models import FantasyCalcValue

    fantasycalc_values = {
        str(i): FantasyCalcValue(
            player_id=str(i), format="1QB", value=i * 100, redraft_value=i * 90,
            overall_rank=i, position_rank=i, trend_30day=0,
            computed_at="2025-10-01T00:00:00+00:00",
        )
        for i in range(1, 51)  # 50 players
    }
    data = {"fantasycalc_values": fantasycalc_values, "valuation_format": "1QB", "players": {}}
    result = build_context(data)
    value_lines = [line for line in result.split("\n") if line.startswith("  ") and ":" in line]
    assert len(value_lines) <= 30


def test_build_context_omits_fantasycalc_section_when_absent():
    data = {}  # no fantasycalc_values key
    result = build_context(data)
    assert "MARKET CONSENSUS" not in result
