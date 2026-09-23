from valuation.age_decay import compute_decay


def test_rb_prime_age_returns_full_value():
    assert compute_decay("RB", 24.0) == 1.0


def test_rb_at_prime_end_returns_full_value():
    assert compute_decay("RB", 26.0) == 1.0


def test_rb_past_cliff_returns_floor():
    assert compute_decay("RB", 33.0) == 0.3


def test_rb_in_decay_range_is_between_floor_and_one():
    value = compute_decay("RB", 29.0)
    assert 0.3 < value < 1.0


def test_wr_prime_end_is_later_than_rb():
    # WR prime ends at 28, so age 27 still full value
    assert compute_decay("WR", 27.0) == 1.0
    # RB decays at 27
    assert compute_decay("RB", 27.0) < 1.0


def test_qb_still_prime_at_30():
    assert compute_decay("QB", 30.0) == 1.0


def test_qb_decays_past_32():
    assert compute_decay("QB", 35.0) < 1.0


def test_te_prime_at_26():
    assert compute_decay("TE", 26.0) == 1.0


def test_unknown_position_returns_full_value():
    assert compute_decay("DEF", 28.0) == 1.0
    assert compute_decay("K", 30.0) == 1.0


def test_decay_is_clamped_to_floor():
    assert compute_decay("RB", 50.0) == 0.3
