import logging
from datetime import datetime, timezone

from valuation.crosswalk import load_crosswalk, build_fantasypros_index, build_gsis_index, fuzzy_lookup
from valuation.age_decay import compute_decay
from valuation.blend import blend_player, blend_pick
from valuation.sources.dynasty_process import fetch_player_values, fetch_pick_values
from valuation.sources.ffc_adp import fetch_adp, normalize_adp
from valuation.sources.nfl_data import fetch_weekly_data, compute_momentum, normalize_momentum
from valuation.sources.sleeper_trending import fetch_trending, normalize_trending
from storage.valuation_store import get_weights, upsert_player_values, upsert_pick_values
from config.settings import NFL_SEASON, PIPELINE_FORMATS

logger = logging.getLogger(__name__)


def run_pipeline(formats: list = None) -> None:
    """Run the full valuation pipeline for all specified formats."""
    if formats is None:
        formats = PIPELINE_FORMATS

    computed_at = datetime.now(timezone.utc).isoformat()

    logger.info("Loading ID crosswalk...")
    crosswalk_df = load_crosswalk()
    fp_index = build_fantasypros_index(crosswalk_df)     # {fp_id: sleeper_id}
    gsis_index = build_gsis_index(crosswalk_df)          # {gsis_id: sleeper_id}

    logger.info("Fetching DynastyProcess values...")
    dp_players = fetch_player_values()
    dp_picks = fetch_pick_values()

    logger.info("Fetching FFC ADP...")
    ffc_raw = fetch_adp()
    ffc_norm = normalize_adp(ffc_raw)                    # {"Name_POS": 0-10000}

    logger.info("Fetching nfl_data_py momentum...")
    weekly_df = fetch_weekly_data(int(NFL_SEASON))
    momentum_raw = compute_momentum(weekly_df)
    momentum_norm = normalize_momentum(momentum_raw)     # {gsis_id: 0-10000}

    logger.info("Fetching Sleeper trending...")
    trending_raw = fetch_trending()
    trending_norm = normalize_trending(trending_raw)     # {sleeper_id: 0-10000}

    for fmt in formats:
        logger.info(f"Blending values for format: {fmt}")
        weights = get_weights(fmt)
        if weights is None:
            logger.warning(f"No weights found for format {fmt}; skipping.")
            continue

        player_values = []

        for fp_id, dp_data in dp_players.items():
            # Resolve fp_id → sleeper_id via crosswalk
            sleeper_id = fp_index.get(str(fp_id))
            if sleeper_id is None:
                # Fuzzy fallback using player name + position
                sleeper_id = fuzzy_lookup(
                    dp_data.get("player_name", ""),
                    dp_data.get("pos", ""),
                    crosswalk_df,
                )
            if sleeper_id is None:
                continue

            dp_val = dp_data["value_1qb"] if fmt == "1QB" else dp_data["value_2qb"]
            pos = dp_data.get("pos", "")
            age = dp_data.get("age") or 0.0
            decay = compute_decay(pos, float(age))

            # ADP: lookup by "Name_POS" key
            ffc_key = f"{dp_data.get('player_name', '')}_{pos}"
            adp_val = ffc_norm.get(ffc_key, 0.0)

            # Momentum: GSIS ID lookup via crosswalk row
            row = crosswalk_df[crosswalk_df["sleeper_id"] == str(sleeper_id)]
            gsis_id = row.iloc[0]["gsis_id"] if not row.empty else None
            mom_val = momentum_norm.get(str(gsis_id), 0.0) if gsis_id and str(gsis_id) != "nan" else 0.0

            trend_val = trending_norm.get(str(sleeper_id), 0.0)

            pv = blend_player(
                player_id=str(sleeper_id),
                format=fmt,
                dp_value=dp_val,
                adp_norm=adp_val,
                age_decay=decay,
                momentum_norm=mom_val,
                trending_norm=trend_val,
                weights=weights,
                computed_at=computed_at,
            )
            player_values.append(pv)

        upsert_player_values(player_values)
        logger.info(f"Upserted {len(player_values)} player values for {fmt}.")

        # Process pick values
        pick_values = []
        for pick_row in dp_picks:
            pv = blend_pick(
                pick_key=str(pick_row["pick"]),
                format=fmt,
                dp_value=pick_row["value_1qb"] if fmt == "1QB" else pick_row["value_2qb"],
                computed_at=computed_at,
            )
            pick_values.append(pv)
        upsert_pick_values(pick_values)
        logger.info(f"Upserted {len(pick_values)} pick values for {fmt}.")
