import requests
from config.settings import FANTASYCALC_URL


def fetch_values(is_dynasty: bool = True, num_qbs: int = 1, num_teams: int = 12, ppr: float = 1) -> list:
    """Fetch current trade values from FantasyCalc. Raises on HTTP error."""
    params = {
        "isDynasty": str(is_dynasty).lower(),
        "numQbs": num_qbs,
        "numTeams": num_teams,
        "ppr": ppr,
    }
    r = requests.get(FANTASYCALC_URL, params=params, timeout=30)
    r.raise_for_status()
    return r.json()


def normalize_values(raw_players: list) -> dict:
    """
    Converts raw FantasyCalc entries into a dict keyed by sleeper_id.
    Entries missing a sleeperId (e.g. some DEF/rookie records) are skipped.
    """
    result = {}
    for entry in raw_players:
        player = entry.get("player", {})
        sleeper_id = player.get("sleeperId")
        if not sleeper_id:
            continue
        result[str(sleeper_id)] = {
            "value": entry.get("value"),
            "redraft_value": entry.get("redraftValue"),
            "overall_rank": entry.get("overallRank"),
            "position_rank": entry.get("positionRank"),
            "trend_30day": entry.get("trend30Day"),
        }
    return result
