from valuation.blend import blend_player, blend_pick
from valuation.models import PlayerValue, PickValue, ValuationWeights


_WEIGHTS_1QB = ValuationWeights(
    format="1QB",
    dp_value=0.50,
    adp_normalized=0.25,
    age_factor=0.15,
    momentum=0.075,
    trending=0.025,
)


def test_blend_player_produces_value_in_0_to_10000():
    result = blend_player(
        player_id="4046",
        format="1QB",
        dp_value=9200.0,
        adp_norm=9500.0,
        age_decay=1.0,
        momentum_norm=6000.0,
        trending_norm=3000.0,
        weights=_WEIGHTS_1QB,
        computed_at="2025-10-01T00:00:00+00:00",
    )
    assert isinstance(result, PlayerValue)
    assert 0 <= result.value <= 10000


def test_blend_player_stores_all_breakdown_components():
    result = blend_player(
        player_id="4046",
        format="1QB",
        dp_value=9200.0,
        adp_norm=9500.0,
        age_decay=1.0,
        momentum_norm=6000.0,
        trending_norm=3000.0,
        weights=_WEIGHTS_1QB,
        computed_at="2025-10-01T00:00:00+00:00",
    )
    assert "dp_value" in result.breakdown
    assert "adp_norm" in result.breakdown
    assert "age_factor" in result.breakdown
    assert "momentum_norm" in result.breakdown
    assert "trending_norm" in result.breakdown


def test_blend_player_only_dp_value_gives_half_scale():
    # All sources zero except DP at 10000 → 10000 * 0.50 = 5000
    result = blend_player(
        player_id="X",
        format="1QB",
        dp_value=10000.0,
        adp_norm=0.0,
        age_decay=0.0,
        momentum_norm=0.0,
        trending_norm=0.0,
        weights=_WEIGHTS_1QB,
        computed_at="2025-10-01T00:00:00+00:00",
    )
    assert result.value == 5000


def test_blend_player_full_all_sources_gives_10000():
    # All sources at 10000 and age_decay=1.0 → weighted sum = 10000
    result = blend_player(
        player_id="X",
        format="1QB",
        dp_value=10000.0,
        adp_norm=10000.0,
        age_decay=1.0,
        momentum_norm=10000.0,
        trending_norm=10000.0,
        weights=_WEIGHTS_1QB,
        computed_at="2025-10-01T00:00:00+00:00",
    )
    assert result.value == 10000


def test_blend_pick_returns_pick_value_object():
    result = blend_pick(
        pick_key="2026_1_early",
        format="1QB",
        dp_value=7500.0,
        computed_at="2025-10-01T00:00:00+00:00",
    )
    assert isinstance(result, PickValue)
    assert result.value == 7500
    assert result.pick_key == "2026_1_early"
