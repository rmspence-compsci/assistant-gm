from sleeper.models import SleeperUser, League, Roster, Player, Matchup, Transaction


def test_sleeper_user_fields():
    u = SleeperUser(user_id="123", username="russ", display_name="Russ")
    assert u.user_id == "123"
    assert u.username == "russ"


def test_roster_record():
    r = Roster(
        roster_id=1, owner_id="abc", league_id="lg1",
        players=["p1", "p2"], starters=["p1"],
        wins=5, losses=3, ties=0,
        points_for=950.5, points_against=870.0,
    )
    assert r.wins == 5
    assert r.points_for == 950.5


def test_transaction_optional_fields():
    t = Transaction(
        transaction_id="t1", type="waiver",
        roster_ids=[1], adds={"p1": 1}, drops=None, week=5, created=1700000000,
    )
    assert t.drops is None
    assert t.adds == {"p1": 1}
