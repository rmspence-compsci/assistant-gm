import json
import sqlite3
import time
from pathlib import Path

from config import settings
from sleeper.models import League, Roster, Player, Matchup, Transaction


def _conn() -> sqlite3.Connection:
    Path(settings.DB_PATH).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(settings.DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    schema_path = Path(__file__).parent / "schema.sql"
    schema = schema_path.read_text()
    with _conn() as conn:
        conn.executescript(schema)


def _is_stale(fetched_at: float, ttl: int) -> bool:
    return (time.time() - fetched_at) > ttl


def get_league(league_id: str) -> League | None:
    with _conn() as conn:
        row = conn.execute("SELECT data, fetched_at FROM leagues WHERE league_id = ?", (league_id,)).fetchone()
    if not row or _is_stale(row["fetched_at"], settings.CACHE_TTL_SECONDS):
        return None
    d = json.loads(row["data"])
    return League(**d)


def upsert_league(league: League) -> None:
    with _conn() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO leagues (league_id, data, fetched_at) VALUES (?, ?, ?)",
            (league.league_id, json.dumps(league.__dict__), time.time()),
        )


def get_rosters(league_id: str) -> list | None:
    with _conn() as conn:
        row = conn.execute("SELECT data, fetched_at FROM rosters WHERE league_id = ?", (league_id,)).fetchone()
    if not row or _is_stale(row["fetched_at"], settings.CACHE_TTL_SECONDS):
        return None
    return [Roster(**d) for d in json.loads(row["data"])]


def upsert_rosters(league_id: str, rosters: list) -> None:
    with _conn() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO rosters (league_id, data, fetched_at) VALUES (?, ?, ?)",
            (league_id, json.dumps([r.__dict__ for r in rosters]), time.time()),
        )


def get_matchups(league_id: str, week: int) -> list | None:
    with _conn() as conn:
        row = conn.execute(
            "SELECT data, fetched_at FROM matchups WHERE league_id = ? AND week = ?", (league_id, week)
        ).fetchone()
    if not row or _is_stale(row["fetched_at"], settings.CACHE_TTL_SECONDS):
        return None
    return [Matchup(**d) for d in json.loads(row["data"])]


def upsert_matchups(league_id: str, week: int, matchups: list) -> None:
    with _conn() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO matchups (league_id, week, data, fetched_at) VALUES (?, ?, ?, ?)",
            (league_id, week, json.dumps([m.__dict__ for m in matchups]), time.time()),
        )


def get_players() -> dict | None:
    with _conn() as conn:
        row = conn.execute("SELECT data, fetched_at FROM players").fetchone()
    if not row or _is_stale(row["fetched_at"], settings.PLAYER_CACHE_TTL_SECONDS):
        return None
    return {pid: Player(**p) for pid, p in json.loads(row["data"]).items()}


def upsert_players(players: dict) -> None:
    with _conn() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO players (id, data, fetched_at) VALUES (1, ?, ?)",
            (json.dumps({pid: p.__dict__ for pid, p in players.items()}), time.time()),
        )


def get_transactions(league_id: str, week: int) -> list | None:
    with _conn() as conn:
        row = conn.execute(
            "SELECT data, fetched_at FROM transactions WHERE league_id = ? AND week = ?", (league_id, week)
        ).fetchone()
    if not row or _is_stale(row["fetched_at"], settings.CACHE_TTL_SECONDS):
        return None
    return [Transaction(**d) for d in json.loads(row["data"])]


def upsert_transactions(league_id: str, week: int, transactions: list) -> None:
    with _conn() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO transactions (league_id, week, data, fetched_at) VALUES (?, ?, ?, ?)",
            (league_id, week, json.dumps([t.__dict__ for t in transactions]), time.time()),
        )


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


def _get_current_week(league_id: str) -> int:
    league = get_league(league_id)
    if league and league.settings.get("leg"):
        return int(league.settings["leg"])
    return 1
