from auth.client import get_client, get_service_client
from valuation.models import PlayerValue, PickValue, ValuationWeights, FantasyCalcValue


def get_player_value(player_id: str, format: str) -> PlayerValue | None:
    res = (
        get_client()
        .table("player_values")
        .select("player_id, format, value, breakdown_json, computed_at")
        .eq("player_id", player_id)
        .eq("format", format)
        .order("computed_at", desc=True)
        .limit(1)
        .maybe_single()
        .execute()
    )
    if res is None or res.data is None:
        return None
    d = res.data
    return PlayerValue(
        player_id=d["player_id"],
        format=d["format"],
        value=d["value"],
        breakdown=d.get("breakdown_json") or {},
        computed_at=d["computed_at"],
    )


def get_player_values_for_ids(player_ids: list, format: str) -> dict:
    if not player_ids:
        return {}
    res = (
        get_client()
        .table("player_values")
        .select("player_id, format, value, breakdown_json, computed_at")
        .in_("player_id", player_ids)
        .eq("format", format)
        .order("computed_at", desc=True)
        .execute()
    )
    if res is None or not res.data:
        return {}
    seen: set = set()
    result: dict = {}
    for row in res.data:
        pid = row["player_id"]
        if pid not in seen:
            seen.add(pid)
            result[pid] = PlayerValue(
                player_id=pid,
                format=row["format"],
                value=row["value"],
                breakdown=row.get("breakdown_json") or {},
                computed_at=row["computed_at"],
            )
    return result


def upsert_player_values(values: list) -> None:
    rows = [
        {
            "player_id": v.player_id,
            "format": v.format,
            "value": v.value,
            "breakdown_json": v.breakdown,
            "computed_at": v.computed_at,
        }
        for v in values
    ]
    get_service_client().table("player_values").upsert(rows).execute()


def get_pick_value(pick_key: str, format: str) -> PickValue | None:
    res = (
        get_client()
        .table("pick_values")
        .select("pick_key, format, value, computed_at")
        .eq("pick_key", pick_key)
        .eq("format", format)
        .order("computed_at", desc=True)
        .limit(1)
        .maybe_single()
        .execute()
    )
    if res is None or res.data is None:
        return None
    d = res.data
    return PickValue(
        pick_key=d["pick_key"], format=d["format"],
        value=d["value"], computed_at=d["computed_at"]
    )


def upsert_pick_values(values: list) -> None:
    rows = [
        {"pick_key": v.pick_key, "format": v.format, "value": v.value, "computed_at": v.computed_at}
        for v in values
    ]
    get_service_client().table("pick_values").upsert(rows).execute()


def get_fantasycalc_values_for_ids(player_ids: list, format: str) -> dict:
    if not player_ids:
        return {}
    res = (
        get_client()
        .table("fantasycalc_values")
        .select("player_id, format, value, redraft_value, overall_rank, position_rank, trend_30day, computed_at")
        .in_("player_id", player_ids)
        .eq("format", format)
        .order("computed_at", desc=True)
        .execute()
    )
    if res is None or not res.data:
        return {}
    seen: set = set()
    result: dict = {}
    for row in res.data:
        pid = row["player_id"]
        if pid not in seen:
            seen.add(pid)
            result[pid] = FantasyCalcValue(
                player_id=pid,
                format=row["format"],
                value=row["value"],
                redraft_value=row["redraft_value"],
                overall_rank=row["overall_rank"],
                position_rank=row["position_rank"],
                trend_30day=row["trend_30day"],
                computed_at=row["computed_at"],
            )
    return result


def upsert_fantasycalc_values(values: list) -> None:
    rows = [
        {
            "player_id": v.player_id,
            "format": v.format,
            "value": v.value,
            "redraft_value": v.redraft_value,
            "overall_rank": v.overall_rank,
            "position_rank": v.position_rank,
            "trend_30day": v.trend_30day,
            "computed_at": v.computed_at,
        }
        for v in values
    ]
    get_service_client().table("fantasycalc_values").upsert(rows).execute()


def get_weights(format: str) -> ValuationWeights | None:
    res = (
        get_service_client()
        .table("valuation_weights")
        .select("*")
        .eq("format", format)
        .maybe_single()
        .execute()
    )
    if res is None or res.data is None:
        return None
    d = res.data
    return ValuationWeights(
        format=d["format"],
        dp_value=d["dp_value"],
        adp_normalized=d["adp_normalized"],
        age_factor=d["age_factor"],
        momentum=d["momentum"],
        trending=d["trending"],
    )
