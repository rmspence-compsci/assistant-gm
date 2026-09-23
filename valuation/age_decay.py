_DECAY_CURVES = {
    "RB": {"prime_end": 26.0, "cliff_age": 32.0, "floor": 0.3},
    "WR": {"prime_end": 28.0, "cliff_age": 34.0, "floor": 0.3},
    "TE": {"prime_end": 28.0, "cliff_age": 34.0, "floor": 0.3},
    "QB": {"prime_end": 32.0, "cliff_age": 38.0, "floor": 0.3},
}


def compute_decay(position: str, age: float) -> float:
    """Return a 0.0–1.0 dynasty age multiplier for the given position and age."""
    curve = _DECAY_CURVES.get(position)
    if curve is None:
        return 1.0
    if age <= curve["prime_end"]:
        return 1.0
    if age >= curve["cliff_age"]:
        return curve["floor"]
    slope = (curve["floor"] - 1.0) / (curve["cliff_age"] - curve["prime_end"])
    return max(curve["floor"], 1.0 + slope * (age - curve["prime_end"]))
