import io
import requests
import pandas as pd

from config.settings import DP_BASE_URL

_VALUES_URL = f"{DP_BASE_URL}/values-players.csv"
_PICKS_URL = f"{DP_BASE_URL}/values-picks.csv"

# Verified against actual CSV downloads — update if upstream changes column names
_REQUIRED_VALUE_COLS = {"fp_id", "player", "pos", "age", "team", "value_1qb", "value_2qb"}
_REQUIRED_PICK_COLS = {"pick", "ecr_1qb", "ecr_2qb"}

# Smallest ECR observed for dynasty picks (~21 = top overall pick slot)
_PICK_ECR_FLOOR = 21.0


def fetch_player_values() -> dict:
    """
    Returns {fp_id: {value_1qb, value_2qb, player_name, pos, age, team}}.
    Raises ValueError if expected columns are absent.
    """
    r = requests.get(_VALUES_URL, timeout=30)
    r.raise_for_status()
    df = pd.read_csv(io.StringIO(r.text))

    missing = _REQUIRED_VALUE_COLS - set(df.columns)
    if missing:
        raise ValueError(f"DynastyProcess values-players.csv missing columns: {missing}")

    df = df.dropna(subset=["fp_id", "value_1qb"])
    df["fp_id"] = df["fp_id"].astype(str).str.strip()

    return {
        row["fp_id"]: {
            "value_1qb": float(row["value_1qb"]),
            "value_2qb": float(row["value_2qb"]) if pd.notna(row.get("value_2qb")) else float(row["value_1qb"]),
            "player_name": str(row.get("player", "")),
            "pos": str(row.get("pos", "")),
            "age": float(row["age"]) if pd.notna(row.get("age")) else None,
            "team": str(row.get("team", "")),
        }
        for _, row in df.iterrows()
    }


def _ecr_to_value(ecr: float, ecr_floor: float = _PICK_ECR_FLOOR) -> int:
    """Convert an ECR rank to a 0-10000 dynasty value. Lower ECR = higher value."""
    if ecr <= 0:
        return 10000
    return max(0, min(10000, round(10000 * ecr_floor / ecr)))


def fetch_pick_values() -> list:
    """
    Returns list of pick dicts with derived value_1qb and value_2qb from ECR ranks.
    Raises ValueError if expected columns are absent.
    """
    r = requests.get(_PICKS_URL, timeout=30)
    r.raise_for_status()
    df = pd.read_csv(io.StringIO(r.text))

    missing = _REQUIRED_PICK_COLS - set(df.columns)
    if missing:
        raise ValueError(f"DynastyProcess values-picks.csv missing columns: {missing}")

    df = df.dropna(subset=["pick", "ecr_1qb"])
    return [
        {
            "pick": str(row["pick"]),
            "player_name": str(row.get("player", "")),
            "value_1qb": _ecr_to_value(float(row["ecr_1qb"])),
            "value_2qb": _ecr_to_value(float(row["ecr_2qb"])) if pd.notna(row.get("ecr_2qb")) else _ecr_to_value(float(row["ecr_1qb"])),
        }
        for _, row in df.iterrows()
    ]
