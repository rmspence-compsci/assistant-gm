import logging

import pandas as pd

logger = logging.getLogger(__name__)


def fetch_weekly_data(season: int) -> pd.DataFrame:
    """
    Download weekly player stats from nfl_data_py for the given season.
    Falls back to the prior season if the requested season's file isn't
    published upstream yet (common early in a new NFL season, before
    nflverse has released that year's data).
    """
    import nfl_data_py as nfl
    try:
        return nfl.import_weekly_data(years=[season])
    except Exception as e:
        logger.warning(f"No nfl_data_py data for season {season} ({e}); falling back to {season - 1}.")
        return nfl.import_weekly_data(years=[season - 1])


def compute_momentum(df: pd.DataFrame, last_n_weeks: int = 4) -> dict:
    """
    Returns {gsis_player_id: momentum_ratio}.
    momentum_ratio = recent_avg_target_share / season_avg_target_share.
    Capped at 3.0. Players with zero season targets get 0.
    """
    if df.empty or "target_share" not in df.columns:
        return {}

    df = df.dropna(subset=["player_id", "target_share"]).copy()
    season_avg = df.groupby("player_id")["target_share"].mean()

    max_week = int(df["week"].max())
    recent = df[df["week"] >= max_week - last_n_weeks + 1]
    recent_avg = recent.groupby("player_id")["target_share"].mean()

    momentum = (recent_avg / season_avg.replace(0.0, float("nan"))).fillna(0.0).clip(0.0, 3.0)
    return momentum.to_dict()


def normalize_momentum(raw: dict, scale: int = 10000) -> dict:
    """Maps [0, 3.0] momentum ratio to [0, scale]."""
    return {gsis_id: round(ratio / 3.0 * scale, 2) for gsis_id, ratio in raw.items()}
