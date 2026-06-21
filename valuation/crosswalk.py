import io
import requests
import pandas as pd
from rapidfuzz import process

from config.settings import DP_BASE_URL

_CROSSWALK_URL = f"{DP_BASE_URL}/db_playerids.csv"


def load_crosswalk() -> pd.DataFrame:
    """Download db_playerids.csv and return as DataFrame."""
    r = requests.get(_CROSSWALK_URL, timeout=30)
    r.raise_for_status()
    df = pd.read_csv(io.StringIO(r.text), dtype=str)
    for col in df.columns:
        df[col] = df[col].str.strip()
    return df


def build_fantasypros_index(df: pd.DataFrame) -> dict:
    """Returns {fantasypros_id: sleeper_id} (both as strings)."""
    mask = df["sleeper_id"].notna() & df["fantasypros_id"].notna()
    sub = df[mask].copy()
    return {
        str(int(float(fp))): str(int(float(sl)))
        for fp, sl in zip(sub["fantasypros_id"], sub["sleeper_id"])
    }


def build_gsis_index(df: pd.DataFrame) -> dict:
    """Returns {gsis_id: sleeper_id} (both as strings)."""
    mask = df["sleeper_id"].notna() & df["gsis_id"].notna()
    sub = df[mask].copy()
    return {
        str(gsis): str(int(float(sl)))
        for gsis, sl in zip(sub["gsis_id"], sub["sleeper_id"])
    }


def fuzzy_lookup(name: str, pos: str, df: pd.DataFrame, threshold: int = 85) -> str | None:
    """Name + position fuzzy match fallback. Returns sleeper_id or None."""
    pos_col = "position" if "position" in df.columns else "pos"
    pos_df = df[df[pos_col] == pos] if pos_col in df.columns else df
    candidates = pos_df["name"].dropna().tolist()
    if not candidates:
        return None
    match = process.extractOne(name, candidates)
    if match is None or match[1] < threshold:
        return None
    matched_name = match[0]
    row = pos_df[pos_df["name"] == matched_name]
    if row.empty:
        return None
    sleeper_id = row.iloc[0]["sleeper_id"]
    return str(sleeper_id) if pd.notna(sleeper_id) else None
