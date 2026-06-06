from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class SleeperUser:
    user_id: str
    username: str
    display_name: str


@dataclass
class League:
    league_id: str
    name: str
    season: str
    total_rosters: int
    scoring_settings: dict[str, Any]
    settings: dict[str, Any]


@dataclass
class Roster:
    roster_id: int
    owner_id: Optional[str]
    league_id: str
    players: list[str]
    starters: list[str]
    wins: int
    losses: int
    ties: int
    points_for: float
    points_against: float


@dataclass
class Player:
    player_id: str
    full_name: str
    position: str
    team: Optional[str]
    status: Optional[str]


@dataclass
class Matchup:
    matchup_id: int
    roster_id: int
    points: float
    starters: list[str]
    week: int


@dataclass
class Transaction:
    transaction_id: str
    type: str
    roster_ids: list[int]
    adds: Optional[dict[str, int]]
    drops: Optional[dict[str, int]]
    week: int
    created: int
