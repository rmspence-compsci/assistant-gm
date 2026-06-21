import io
from unittest.mock import patch, MagicMock, call
import pandas as pd


def _mock_crosswalk_df():
    csv = (
        "sleeper_id,fantasypros_id,gsis_id,name,position,team,age\n"
        "4046,289,00-0033873,Patrick Mahomes,QB,KC,29.0\n"
    )
    return pd.read_csv(io.StringIO(csv), dtype=str)


_DEFAULT_MOCKS = {
    "valuation.pipeline.load_crosswalk": {"return_value": None},  # set per test
    "valuation.pipeline.build_fantasypros_index": {"return_value": {"289": "4046"}},
    "valuation.pipeline.build_gsis_index": {"return_value": {"00-0033873": "4046"}},
    "valuation.pipeline.fetch_player_values": {"return_value": {
        "289": {
            "value_1qb": 9200.0, "value_2qb": 9500.0,
            "player_name": "Patrick Mahomes", "pos": "QB", "age": 29.0, "team": "KC"
        }
    }},
    "valuation.pipeline.fetch_pick_values": {"return_value": []},
    "valuation.pipeline.fetch_adp": {"return_value": []},
    "valuation.pipeline.normalize_adp": {"return_value": {}},
    "valuation.pipeline.fetch_weekly_data": {"return_value": pd.DataFrame()},
    "valuation.pipeline.compute_momentum": {"return_value": {}},
    "valuation.pipeline.normalize_momentum": {"return_value": {}},
    "valuation.pipeline.fetch_trending": {"return_value": {}},
    "valuation.pipeline.normalize_trending": {"return_value": {}},
    "valuation.pipeline.upsert_player_values": {},
    "valuation.pipeline.upsert_pick_values": {},
}


def _run_with_mocks(extra_overrides=None):
    """Helper to run run_pipeline with all sources mocked."""
    mocks = dict(_DEFAULT_MOCKS)
    if extra_overrides:
        mocks.update(extra_overrides)

    df = _mock_crosswalk_df()

    patches = {}
    ctx_managers = {}

    import contextlib

    @contextlib.contextmanager
    def multi_patch():
        with (
            patch("valuation.pipeline.load_crosswalk", return_value=df),
            patch("valuation.pipeline.build_fantasypros_index", return_value={"289": "4046"}),
            patch("valuation.pipeline.build_gsis_index", return_value={"00-0033873": "4046"}),
            patch("valuation.pipeline.fetch_player_values", return_value=mocks.get(
                "valuation.pipeline.fetch_player_values", {}).get("return_value",
                {"289": {"value_1qb": 9200.0, "value_2qb": 9500.0, "player_name": "Patrick Mahomes", "pos": "QB", "age": 29.0, "team": "KC"}})),
            patch("valuation.pipeline.fetch_pick_values", return_value=[]),
            patch("valuation.pipeline.fetch_adp", return_value=[]),
            patch("valuation.pipeline.normalize_adp", return_value={}),
            patch("valuation.pipeline.fetch_weekly_data", return_value=pd.DataFrame()),
            patch("valuation.pipeline.compute_momentum", return_value={}),
            patch("valuation.pipeline.normalize_momentum", return_value={}),
            patch("valuation.pipeline.fetch_trending", return_value={}),
            patch("valuation.pipeline.normalize_trending", return_value={}),
            patch("valuation.pipeline.get_weights", return_value=MagicMock(
                dp_value=0.5, adp_normalized=0.25, age_factor=0.15, momentum=0.075, trending=0.025
            )),
            patch("valuation.pipeline.upsert_player_values") as mock_upsert_players,
            patch("valuation.pipeline.upsert_pick_values") as mock_upsert_picks,
        ):
            yield mock_upsert_players, mock_upsert_picks

    return multi_patch


def test_run_pipeline_calls_upsert_for_each_format():
    with _run_with_mocks()() as (mock_upsert_players, mock_upsert_picks):
        from valuation.pipeline import run_pipeline
        run_pipeline(formats=["1QB", "2QB"])
    # Called once per format
    assert mock_upsert_players.call_count == 2


def test_run_pipeline_produces_player_value_for_known_player():
    captured = []

    def capture(values):
        captured.extend(values)

    with _run_with_mocks()() as (mock_upsert_players, _):
        mock_upsert_players.side_effect = capture
        from valuation.pipeline import run_pipeline
        run_pipeline(formats=["1QB"])

    mahomes = next((v for v in captured if v.player_id == "4046" and v.format == "1QB"), None)
    assert mahomes is not None
    assert mahomes.value > 0


def test_run_pipeline_skips_format_when_weights_missing():
    with _run_with_mocks()() as (mock_upsert_players, _):
        # Override get_weights to return None (no weights configured)
        with patch("valuation.pipeline.get_weights", return_value=None):
            from valuation.pipeline import run_pipeline
            run_pipeline(formats=["1QB"])
    # Should not upsert anything if weights are missing
    mock_upsert_players.assert_not_called()
