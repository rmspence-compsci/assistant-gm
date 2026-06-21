import requests
from config.settings import SLEEPER_TRENDING_URL


def fetch_trending(lookback_hours: int = 24, limit: int = 200) -> dict:
    """Returns {sleeper_player_id: add_count} for the trending window."""
    r = requests.get(
        SLEEPER_TRENDING_URL,
        params={"lookback_hours": lookback_hours, "limit": limit},
        timeout=30,
    )
    r.raise_for_status()
    return {item["player_id"]: item["count"] for item in r.json()}


def normalize_trending(raw: dict, scale: int = 10000) -> dict:
    """Maps [0, max_count] to [0, scale]."""
    if not raw:
        return {}
    max_count = max(raw.values())
    if max_count == 0:
        return {pid: 0.0 for pid in raw}
    return {pid: round(count / max_count * scale, 2) for pid, count in raw.items()}
