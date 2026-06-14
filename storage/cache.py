import json
import time

from auth.client import get_client
from config import settings
from sleeper.models import League, Roster, Player, Matchup, Transaction


def init_db() -> None:
    pass  # Tables are managed in Supabase; no local initialization needed.


def _is_stale(fetched_at: float, ttl: int) -> bool:
    return (time.time() - fetched_at) > ttl


# --- League ---

def get_league(league_id: str) -> League | None:
    res = (
        get_client()
        .table("cache_leagues")
        .select("data, fetched_at")
        .eq("league_id", league_id)
        .maybe_single()
        .execute()
    )
    if res is None or _is_stale(res.data["fetched_at"], settings.CACHE_TTL_SECONDS):
        return None
    return League(**json.loads(res.data["data"]))


def upsert_league(league: League) -> None:
    get_client().table("cache_leagues").upsert({
        "league_id": league.league_id,
        "data": json.dumps(league.__dict__),
        "fetched_at": time.time(),
    }).execute()


# --- Rosters ---

def get_rosters(league_id: str) -> list | None:
    res = (
        get_client()
        .table("cache_rosters")
        .select("data, fetched_at")
        .eq("league_id", league_id)
        .maybe_single()
        .execute()
    )
    if res is None or _is_stale(res.data["fetched_at"], settings.CACHE_TTL_SECONDS):
        return None
    return [Roster(**d) for d in json.loads(res.data["data"])]


def upsert_rosters(league_id: str, rosters: list) -> None:
    get_client().table("cache_rosters").upsert({
        "league_id": league_id,
        "data": json.dumps([r.__dict__ for r in rosters]),
        "fetched_at": time.time(),
    }).execute()


# --- Matchups ---

def get_matchups(league_id: str, week: int) -> list | None:
    res = (
        get_client()
        .table("cache_matchups")
        .select("data, fetched_at")
        .eq("league_id", league_id)
        .eq("week", week)
        .maybe_single()
        .execute()
    )
    if res is None or _is_stale(res.data["fetched_at"], settings.CACHE_TTL_SECONDS):
        return None
    return [Matchup(**d) for d in json.loads(res.data["data"])]


def upsert_matchups(league_id: str, week: int, matchups: list) -> None:
    get_client().table("cache_matchups").upsert({
        "league_id": league_id,
        "week": week,
        "data": json.dumps([m.__dict__ for m in matchups]),
        "fetched_at": time.time(),
    }).execute()


# --- Players ---

def get_players() -> dict | None:
    res = (
        get_client()
        .table("cache_players")
        .select("data, fetched_at")
        .eq("id", 1)
        .maybe_single()
        .execute()
    )
    if res is None or _is_stale(res.data["fetched_at"], settings.PLAYER_CACHE_TTL_SECONDS):
        return None
    return {pid: Player(**p) for pid, p in json.loads(res.data["data"]).items()}


def upsert_players(players: dict) -> None:
    get_client().table("cache_players").upsert({
        "id": 1,
        "data": json.dumps({pid: p.__dict__ for pid, p in players.items()}),
        "fetched_at": time.time(),
    }).execute()


# --- League Users ---

def get_league_users(league_id: str) -> list[dict] | None:
    res = (
        get_client()
        .table("cache_league_users")
        .select("data, fetched_at")
        .eq("league_id", league_id)
        .maybe_single()
        .execute()
    )
    if res is None or _is_stale(res.data["fetched_at"], settings.CACHE_TTL_SECONDS):
        return None
    return json.loads(res.data["data"])


def upsert_league_users(league_id: str, users: list[dict]) -> None:
    get_client().table("cache_league_users").upsert({
        "league_id": league_id,
        "data": json.dumps(users),
        "fetched_at": time.time(),
    }).execute()


# --- Transactions ---

def get_transactions(league_id: str, week: int) -> list | None:
    res = (
        get_client()
        .table("cache_transactions")
        .select("data, fetched_at")
        .eq("league_id", league_id)
        .eq("week", week)
        .maybe_single()
        .execute()
    )
    if res is None or _is_stale(res.data["fetched_at"], settings.CACHE_TTL_SECONDS):
        return None
    return [Transaction(**d) for d in json.loads(res.data["data"])]


def upsert_transactions(league_id: str, week: int, transactions: list) -> None:
    get_client().table("cache_transactions").upsert({
        "league_id": league_id,
        "week": week,
        "data": json.dumps([t.__dict__ for t in transactions]),
        "fetched_at": time.time(),
    }).execute()


# --- Refresh ---

def refresh_league(league_id: str, force: bool = False) -> None:
    from sleeper import client as sleeper_client
    current_week = _get_current_week(league_id)

    if force or get_rosters(league_id) is None:
        upsert_rosters(league_id, sleeper_client.get_rosters(league_id))

    if force or get_matchups(league_id, current_week) is None:
        upsert_matchups(league_id, current_week, sleeper_client.get_matchups(league_id, current_week))

    if force or get_transactions(league_id, current_week) is None:
        upsert_transactions(league_id, current_week, sleeper_client.get_transactions(league_id, current_week))

    if force or get_players() is None:
        upsert_players(sleeper_client.get_all_players())

    if force or get_league_users(league_id) is None:
        upsert_league_users(league_id, sleeper_client.get_league_users(league_id))


def _get_current_week(league_id: str) -> int:
    league = get_league(league_id)
    if league and league.settings.get("leg"):
        return int(league.settings["leg"])
    return 1
