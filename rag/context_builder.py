def build_context(data: dict) -> str:
    parts = []

    if league := data.get("league"):
        scoring = "PPR" if league.scoring_settings.get("rec", 0) == 1 else "Standard"
        week = league.settings.get("leg", "?")
        parts.append(f"LEAGUE: {league.name} ({league.total_rosters}-team {scoring}, Week {week})")

    if user_roster := data.get("user_roster"):
        record = f"{user_roster.wins}-{user_roster.losses}-{user_roster.ties}"
        parts.append(f"YOUR TEAM: Record {record} | PF: {user_roster.points_for:.1f}")
        players = data.get("players", {})
        starters = [players[pid].full_name for pid in user_roster.starters if pid in players]
        bench = [players[pid].full_name for pid in user_roster.players
                 if pid not in user_roster.starters and pid in players]
        parts.append(f"YOUR STARTERS: {', '.join(starters) or 'none'}")
        parts.append(f"YOUR BENCH: {', '.join(bench) or 'none'}")

    if opponent := data.get("opponent_roster"):
        players = data.get("players", {})
        opp_names = [players[pid].full_name for pid in opponent.players if pid in players]
        parts.append(f"OPPONENT ROSTER: {', '.join(opp_names) or 'unknown'}")

    if standings := data.get("standings"):
        lines = ["LEAGUE STANDINGS:"]
        for i, r in enumerate(standings, 1):
            record = f"{r.wins}-{r.losses}-{r.ties}"
            lines.append(f"  {i}. Roster {r.roster_id} | {record} | PF: {r.points_for:.1f}")
        parts.append("\n".join(lines))

    if available := data.get("available_players"):
        players_list = list(available.values())[:20]
        names = [f"{p.full_name} ({p.position})" for p in players_list]
        parts.append(f"AVAILABLE PLAYERS (top 20): {', '.join(names)}")

    if txns := data.get("recent_transactions"):
        players = data.get("players", {})
        lines = ["RECENT TRANSACTIONS:"]
        for t in txns[:5]:
            adds = ", ".join(
                f"added {players[pid].full_name if pid in players else pid}"
                for pid in (t.adds or {}).keys()
            )
            drops = ", ".join(
                f"dropped {players[pid].full_name if pid in players else pid}"
                for pid in (t.drops or {}).keys()
            )
            detail = " | ".join(filter(None, [adds, drops])) or "details unavailable"
            lines.append(f"  [{t.type}] {detail}")
        parts.append("\n".join(lines))

    return "\n".join(parts) if parts else "No league data available."
