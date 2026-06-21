from valuation.models import PlayerValue, PickValue, ValuationWeights


def test_player_value_is_instantiatable():
    pv = PlayerValue(
        player_id="4046",
        format="1QB",
        value=8500,
        breakdown={"dp_value": 9000, "adp_normalized": 7500},
        computed_at="2025-10-01T00:00:00+00:00",
    )
    assert pv.player_id == "4046"
    assert pv.value == 8500
    assert pv.breakdown["dp_value"] == 9000


def test_pick_value_is_instantiatable():
    pv = PickValue(
        pick_key="2026_1_early",
        format="2QB",
        value=7200,
        computed_at="2025-10-01T00:00:00+00:00",
    )
    assert pv.pick_key == "2026_1_early"
    assert pv.value == 7200


def test_valuation_weights_fields_sum_to_one():
    w = ValuationWeights(
        format="1QB",
        dp_value=0.50,
        adp_normalized=0.25,
        age_factor=0.15,
        momentum=0.075,
        trending=0.025,
    )
    total = w.dp_value + w.adp_normalized + w.age_factor + w.momentum + w.trending
    assert abs(total - 1.0) < 1e-9
