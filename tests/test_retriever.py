from unittest.mock import patch
from sleeper.models import League, Roster
from rag.retriever import classify_question, QuestionType, retrieve_context


def test_classify_lineup():
    assert classify_question("Should I start Davante Adams or Tyreek Hill?") == QuestionType.LINEUP


def test_classify_trade():
    assert classify_question("Is this trade fair?") == QuestionType.TRADE


def test_classify_waiver():
    assert classify_question("Who should I pick up off waivers?") == QuestionType.WAIVER


def test_classify_standings():
    assert classify_question("How does my team rank in the league?") == QuestionType.STANDINGS


def test_classify_general():
    assert classify_question("Tell me about my team") == QuestionType.GENERAL


@patch("storage.cache.get_league_users", return_value=None)
@patch("storage.cache.get_matchups", return_value=None)
@patch("storage.cache.get_transactions", return_value=None)
@patch("storage.cache.get_players", return_value=None)
@patch("storage.cache.get_rosters")
@patch("storage.cache.get_league")
def test_retrieve_context_standings(mock_get_league, mock_get_rosters, mock_get_players, mock_get_transactions, mock_get_matchups, mock_get_league_users):
    mock_get_league.return_value = League(
        league_id="lg1", name="Test", season="2025",
        total_rosters=12, scoring_settings={}, settings={"leg": 10},
    )
    mock_get_rosters.return_value = [
        Roster(roster_id=1, owner_id="u1", league_id="lg1", players=[], starters=[],
               wins=8, losses=2, ties=0, points_for=1400.0, points_against=1100.0),
        Roster(roster_id=2, owner_id="u2", league_id="lg1", players=[], starters=[],
               wins=5, losses=5, ties=0, points_for=1100.0, points_against=1100.0),
    ]

    result = retrieve_context("How does my team rank?", "lg1", 1)

    assert "league" in result
    assert "user_roster" in result
    all_rosters = result.get("all_rosters")
    assert all_rosters is not None
    assert all_rosters[0].wins == 8
