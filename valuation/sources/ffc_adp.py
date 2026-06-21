import requests
from config.settings import FFC_ADP_URL


def fetch_adp(teams: int = 12) -> list:
    """
    Fetch dynasty ADP from Fantasy Football Calculator. Raises on HTTP error.
    Note: Do NOT pass a year parameter — it causes empty results for the dynasty endpoint.
    """
    r = requests.get(FFC_ADP_URL, params={"teams": teams}, timeout=30)
    r.raise_for_status()
    return r.json().get("players", [])


def normalize_adp(players: list, max_adp: float = 300.0, scale: int = 10000) -> dict:
    """
    Converts ADP to 0–scale where lower ADP = higher value.
    Key: "{name}_{position}" for fuzzy crosswalk matching.
    Formula: value = scale * (1 - (adp - 1) / (max_adp - 1)), clamped to [0, scale].
    """
    result = {}
    for p in players:
        adp = float(p.get("adp", max_adp))
        value = max(0.0, scale * (1.0 - (adp - 1.0) / (max_adp - 1.0)))
        key = f"{p.get('name', '')}_{p.get('position', '')}"
        result[key] = round(value, 2)
    return result
