from enum import Enum
from storage import cache
from storage.valuation_store import get_player_values_for_ids, get_fantasycalc_values_for_ids


class QuestionType(Enum):
    LINEUP = "lineup"
    TRADE = "trade"
    WAIVER = "waiver"
    STANDINGS = "standings"
    GENERAL = "general"


_KEYWORDS = {
    QuestionType.LINEUP: ["start", "sit", "lineup", "flex", "bench", "play", "starter"],
    QuestionType.TRADE: ["trade", "offer", "deal", "worth", "value", "give up", "receive"],
    QuestionType.WAIVER: ["waiver", "pickup", "pick up", "add", "free agent", "available"],
    QuestionType.STANDINGS: ["standing", "rank", "place", "lead", "behind", "ahead", "record", "playoff"],
}


def _infer_format(league) -> str:
    """Returns '2QB' if league has a SuperFlex slot, else '1QB'."""
    positions = league.settings.get("roster_positions", []) if league else []
    return "2QB" if "SF" in positions else "1QB"


def classify_question(question: str) -> QuestionType:
    lowered = question.lower()
    for qtype, keywords in _KEYWORDS.items():
        if any(kw in lowered for kw in keywords):
            return qtype
    return QuestionType.GENERAL


def _build_roster_owner_map(league_id: str, rosters: list) -> dict[int, str]:
    league_users = cache.get_league_users(league_id) or []
    user_map = {u["user_id"]: u for u in league_users}

    result = {}
    for roster in rosters:
        owner = user_map.get(roster.owner_id or "")
        if owner:
            team_name = owner.get("team_name")
            username = owner.get("username", "")
            label = f"{team_name} ({username})" if team_name else username
        else:
            label = f"Roster {roster.roster_id}"
        result[roster.roster_id] = label
    return result


def retrieve_context(question: str, league_id: str, user_roster_id: int) -> dict:
    qtype = classify_question(question)
    data: dict = {}

    league = cache.get_league(league_id)
    if league:
        data["league"] = league

    rosters = cache.get_rosters(league_id)
    players = cache.get_players()
    if players:
        data["players"] = players

    if rosters:
        data["all_rosters"] = rosters
        data["roster_owner_map"] = _build_roster_owner_map(league_id, rosters)

        user_roster = next((r for r in rosters if r.roster_id == user_roster_id), None)
        if user_roster:
            data["user_roster"] = user_roster

        current_week = int(league.settings.get("leg", 1)) if league else 1
        matchups = cache.get_matchups(league_id, current_week)
        if matchups:
            data["all_matchups"] = matchups

        if qtype == QuestionType.WAIVER and players:
            owned_ids = {pid for r in rosters for pid in r.players}
            data["available_players"] = {
                pid: p for pid, p in players.items()
                if pid not in owned_ids and p.position in ("QB", "RB", "WR", "TE")
            }

        if qtype == QuestionType.TRADE:
            all_player_ids = list({pid for r in rosters for pid in (r.players or [])})
            fmt = _infer_format(league)
            player_values = get_player_values_for_ids(all_player_ids, fmt)
            if player_values:
                data["player_values"] = player_values
                data["valuation_format"] = fmt

            fantasycalc_values = get_fantasycalc_values_for_ids(all_player_ids, fmt)
            if fantasycalc_values:
                data["fantasycalc_values"] = fantasycalc_values

    current_week = int(league.settings.get("leg", 1)) if league else 1
    transactions = cache.get_transactions(league_id, current_week)
    if transactions:
        data["recent_transactions"] = transactions[:10]

    return data
