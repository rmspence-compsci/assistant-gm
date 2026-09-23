import io
from unittest.mock import patch, MagicMock
import pandas as pd
from valuation.crosswalk import (
    load_crosswalk,
    build_fantasypros_index,
    build_gsis_index,
    fuzzy_lookup,
)

_SAMPLE_CSV = """sleeper_id,fantasypros_id,gsis_id,espn_id,name,position,team,age
4046,289,00-0033873,3054211,Patrick Mahomes,QB,KC,29.0
2133,16,00-0027973,2576980,Travis Kelce,TE,KC,35.0
6786,,00-0036355,,DeAndre Hopkins,WR,TEN,32.0
"""


def _mock_get(url, **kwargs):
    mock_resp = MagicMock()
    mock_resp.text = _SAMPLE_CSV
    mock_resp.raise_for_status = MagicMock()
    return mock_resp


def test_load_crosswalk_returns_dataframe():
    with patch("valuation.crosswalk.requests.get", side_effect=_mock_get):
        df = load_crosswalk()
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 3
    assert "sleeper_id" in df.columns


def test_build_fantasypros_index_maps_fp_to_sleeper():
    df = pd.read_csv(io.StringIO(_SAMPLE_CSV))
    index = build_fantasypros_index(df)
    assert index["289"] == "4046"
    assert index["16"] == "2133"


def test_build_gsis_index_maps_gsis_to_sleeper():
    df = pd.read_csv(io.StringIO(_SAMPLE_CSV))
    index = build_gsis_index(df)
    assert index["00-0033873"] == "4046"
    assert index["00-0027973"] == "2133"


def test_build_gsis_index_excludes_rows_with_missing_gsis():
    df = pd.read_csv(io.StringIO(_SAMPLE_CSV))
    index = build_gsis_index(df)
    assert "4046" in index.values()
    assert "2133" in index.values()


def test_fuzzy_lookup_finds_close_name_match():
    df = pd.read_csv(io.StringIO(_SAMPLE_CSV))
    result = fuzzy_lookup("Patrick Mahomes II", "QB", df)
    assert result == "4046"


def test_fuzzy_lookup_returns_none_below_threshold():
    df = pd.read_csv(io.StringIO(_SAMPLE_CSV))
    result = fuzzy_lookup("Totally Unknown Player", "QB", df)
    assert result is None


def test_fuzzy_lookup_restricts_to_position():
    df = pd.read_csv(io.StringIO(_SAMPLE_CSV))
    # "Travis Kelce" is TE; searching as WR should not match
    result = fuzzy_lookup("Travis Kelce", "WR", df)
    assert result is None
