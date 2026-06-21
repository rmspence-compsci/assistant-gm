from valuation.models import PlayerValue, PickValue, ValuationWeights


def blend_player(
    player_id: str,
    format: str,
    dp_value: float,
    adp_norm: float,
    age_decay: float,      # 0.0–1.0 from age_decay.compute_decay
    momentum_norm: float,
    trending_norm: float,
    weights: ValuationWeights,
    computed_at: str,
) -> PlayerValue:
    """
    Blends 5 component scores into a single 0–10000 dynasty trade value.
    age_decay (0–1) is scaled to 0–10000 internally.
    """
    age_component = age_decay * 10000.0

    raw = (
        dp_value      * weights.dp_value +
        adp_norm      * weights.adp_normalized +
        age_component * weights.age_factor +
        momentum_norm * weights.momentum +
        trending_norm * weights.trending
    )
    value = round(max(0, min(10000, raw)))

    breakdown = {
        "dp_value": dp_value,
        "adp_norm": adp_norm,
        "age_factor": age_component,
        "momentum_norm": momentum_norm,
        "trending_norm": trending_norm,
        "weights": {
            "dp_value": weights.dp_value,
            "adp_normalized": weights.adp_normalized,
            "age_factor": weights.age_factor,
            "momentum": weights.momentum,
            "trending": weights.trending,
        },
    }

    return PlayerValue(
        player_id=player_id,
        format=format,
        value=value,
        breakdown=breakdown,
        computed_at=computed_at,
    )


def blend_pick(
    pick_key: str,
    format: str,
    dp_value: float,
    computed_at: str,
) -> PickValue:
    """Pick values come from DynastyProcess ECR conversion — no multi-source blending."""
    return PickValue(
        pick_key=pick_key,
        format=format,
        value=round(max(0, min(10000, dp_value))),
        computed_at=computed_at,
    )
