import io
from unittest.mock import patch, MagicMock
from valuation.sources.dynasty_process import fetch_player_values, fetch_pick_values

# Column names match the ACTUAL values-players.csv format
_SAMPLE_VALUES_CSV = """fp_id,player,pos,age,team,value_1qb,value_2qb,ecr_1qb,ecr_2qb,ecr_pos,draft_year,scrape_date
289,Patrick Mahomes,QB,29,KC,9200,9500,15.0,5.0,1.0,2017,2026-06-19
16,Travis Kelce,TE,35,KC,5500,5500,45.0,50.0,3.0,2013,2026-06-19
19788,Ja'Marr Chase,WR,26,CIN,10232,9076,1.1,6.2,1.0,2021,2026-06-19
"""

# Column names match the ACTUAL values-picks.csv format (no value_1qb/value_2qb)
_SAMPLE_PICKS_CSV = """player,pos,ecr_1qb,ecr_2qb,ecr_high_1qb,ecr_high_2qb,ecr_low_1qb,ecr_low_2qb,scrape_date,pick
2026 Pick 1.01,PICK,21.3075,10.76625,15.0,8.0,25.0,12.0,2026-06-19,1.0
2026 Pick 1.02,PICK,26.55,14.08,20.0,10.0,30.0,16.0,2026-06-19,2.0
2026 Pick 2.01,PICK,65.0,40.0,55.0,35.0,75.0,45.0,2026-06-19,25.0
"""


def _make_mock_get(csv_text):
    def _mock(url, **kwargs):
        resp = MagicMock()
        resp.text = csv_text
        resp.raise_for_status = MagicMock()
        return resp
    return _mock


def test_fetch_player_values_returns_dict_keyed_by_fp_id():
    with patch("valuation.sources.dynasty_process.requests.get",
               side_effect=_make_mock_get(_SAMPLE_VALUES_CSV)):
        result = fetch_player_values()
    assert "289" in result
    assert "16" in result
    assert result["289"]["player_name"] == "Patrick Mahomes"


def test_fetch_player_values_includes_both_format_values():
    with patch("valuation.sources.dynasty_process.requests.get",
               side_effect=_make_mock_get(_SAMPLE_VALUES_CSV)):
        result = fetch_player_values()
    assert result["289"]["value_1qb"] == 9200.0
    assert result["289"]["value_2qb"] == 9500.0


def test_fetch_player_values_raises_on_missing_columns():
    bad_csv = "player,pos\nPatrick Mahomes,QB\n"
    with patch("valuation.sources.dynasty_process.requests.get",
               side_effect=_make_mock_get(bad_csv)):
        try:
            fetch_player_values()
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "missing columns" in str(e).lower()


def test_fetch_pick_values_returns_list_of_dicts():
    with patch("valuation.sources.dynasty_process.requests.get",
               side_effect=_make_mock_get(_SAMPLE_PICKS_CSV)):
        result = fetch_pick_values()
    assert isinstance(result, list)
    assert len(result) == 3


def test_fetch_pick_values_derives_value_from_ecr():
    with patch("valuation.sources.dynasty_process.requests.get",
               side_effect=_make_mock_get(_SAMPLE_PICKS_CSV)):
        result = fetch_pick_values()
    # 1.01 has ecr_1qb ~21 → should derive ~10000
    first_pick = result[0]
    assert first_pick["value_1qb"] > 5000
    assert first_pick["value_1qb"] <= 10000
    # 2.01 has ecr_1qb 65 → should be lower value
    third_pick = result[2]
    assert third_pick["value_1qb"] < first_pick["value_1qb"]


def test_fetch_pick_values_raises_on_missing_columns():
    bad_csv = "player,pos\nPick 1,PICK\n"
    with patch("valuation.sources.dynasty_process.requests.get",
               side_effect=_make_mock_get(bad_csv)):
        try:
            fetch_pick_values()
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "missing columns" in str(e).lower()
