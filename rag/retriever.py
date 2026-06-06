from enum import Enum
from storage import cache


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


def classify_question(question: str) -> QuestionType:
    lowered = question.lower()
    for qtype, keywords in _KEYWORDS.items():
        if any(kw in lowered for kw in keywords):
            return qtype
    return QuestionType.GENERAL


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
        user_roster = next((r for r in rosters if r.roster_id == user_roster_id), None)
        if user_roster:
            data["user_roster"] = user_roster

        if qtype == QuestionType.LINEUP:
            current_week = int(league.settings.get("leg", 1)) if league else 1
            matchups = cache.get_matchups(league_id, current_week)
            if matchups and user_roster:
                user_matchup = next((m for m in matchups if m.roster_id == user_roster_id), None)
                if user_matchup:
                    opponent_matchup = next(
                        (m for m in matchups
                         if m.matchup_id == user_matchup.matchup_id and m.roster_id != user_roster_id),
                        None,
                    )
                    if opponent_matchup:
                        opp_roster = next((r for r in rosters if r.roster_id == opponent_matchup.roster_id), None)
                        if opp_roster:
                            data["opponent_roster"] = opp_roster

        elif qtype == QuestionType.STANDINGS:
            data["standings"] = sorted(rosters, key=lambda r: (-r.wins, -r.points_for))

        elif qtype == QuestionType.WAIVER and players:
            owned_ids = {pid for r in rosters for pid in r.players}
            data["available_players"] = {
                pid: p for pid, p in players.items()
                if pid not in owned_ids and p.position in ("QB", "RB", "WR", "TE")
            }

    current_week = int(league.settings.get("leg", 1)) if league else 1
    transactions = cache.get_transactions(league_id, current_week)
    if transactions:
        user_txns = [t for t in transactions if user_roster_id in t.roster_ids]
        data["recent_transactions"] = user_txns[:10]

    return data
