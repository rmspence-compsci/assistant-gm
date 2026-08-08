from dataclasses import dataclass


@dataclass
class PlayerValue:
    player_id: str
    format: str
    value: int
    breakdown: dict
    computed_at: str


@dataclass
class PickValue:
    pick_key: str
    format: str
    value: int
    computed_at: str


@dataclass
class ValuationWeights:
    format: str
    dp_value: float
    adp_normalized: float
    age_factor: float
    momentum: float
    trending: float


@dataclass
class FantasyCalcValue:
    player_id: str
    format: str
    value: int
    redraft_value: int
    overall_rank: int
    position_rank: int
    trend_30day: int
    computed_at: str
