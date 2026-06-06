import requests
from .models import SleeperUser, League, Roster, Player, Matchup, Transaction

BASE_URL = "https://api.sleeper.app/v1"


def _get(path: str):
    response = requests.get(f"{BASE_URL}{path}", timeout=10)
    response.raise_for_status()
    return response.json()


def get_user(username: str) -> SleeperUser:
    data = _get(f"/user/{username}")
    return SleeperUser(
        user_id=data["user_id"],
        username=data["username"],
        display_name=data.get("display_name", data["username"]),
    )


def get_user_leagues(user_id: str, season: str) -> list:
    data = _get(f"/user/{user_id}/leagues/nfl/{season}")
    data = data or []
    return [
        League(
            league_id=d["league_id"],
            name=d["name"],
            season=d["season"],
            total_rosters=d["total_rosters"],
            scoring_settings=d.get("scoring_settings", {}),
            settings=d.get("settings", {}),
        )
        for d in data
    ]


def get_rosters(league_id: str) -> list:
    data = _get(f"/league/{league_id}/rosters") or []
    return [_roster_from_dict(d, league_id) for d in data]


def _roster_from_dict(d: dict, league_id: str) -> Roster:
    s = d.get("settings", {})
    return Roster(
        roster_id=d["roster_id"],
        owner_id=d.get("owner_id"),
        league_id=league_id,
        players=d.get("players") or [],
        starters=d.get("starters") or [],
        wins=s.get("wins", 0),
        losses=s.get("losses", 0),
        ties=s.get("ties", 0),
        points_for=s.get("fpts", 0) + s.get("fpts_decimal", 0) / 100,
        points_against=s.get("fpts_against", 0) + s.get("fpts_against_decimal", 0) / 100,
    )


def get_matchups(league_id: str, week: int) -> list:
    data = _get(f"/league/{league_id}/matchups/{week}") or []
    return [
        Matchup(
            matchup_id=d["matchup_id"],
            roster_id=d["roster_id"],
            points=d.get("points", 0.0),
            starters=d.get("starters") or [],
            week=week,
        )
        for d in data
    ]


def get_transactions(league_id: str, week: int) -> list:
    data = _get(f"/league/{league_id}/transactions/{week}")
    data = data or []
    return [
        Transaction(
            transaction_id=d["transaction_id"],
            type=d["type"],
            roster_ids=d.get("roster_ids") or [],
            adds=d.get("adds"),
            drops=d.get("drops"),
            week=week,
            created=d.get("created", 0),
        )
        for d in data
    ]


def get_league_users(league_id: str) -> list:
    return _get(f"/league/{league_id}/users")


def get_all_players() -> dict:
    data = _get("/players/nfl")
    if not isinstance(data, dict):
        raise ValueError("Unexpected response from /players/nfl")
    return {
        pid: Player(
            player_id=pid,
            full_name=p.get("full_name", f"{p.get('first_name', '')} {p.get('last_name', '')}".strip()),
            position=p.get("position", ""),
            team=p.get("team"),
            status=p.get("status"),
        )
        for pid, p in data.items()
        if p.get("position") in ("QB", "RB", "WR", "TE", "K", "DEF")
    }
