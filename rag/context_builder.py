def build_context(data: dict) -> str:
    parts = []
    players = data.get("players", {})
    roster_owner_map: dict[int, str] = data.get("roster_owner_map", {})

    if league := data.get("league"):
        scoring = "PPR" if league.scoring_settings.get("rec", 0) == 1 else "Standard"
        week = league.settings.get("leg", "?")
        parts.append(f"LEAGUE: {league.name} ({league.total_rosters}-team {scoring}, Week {week})")
        try:
            if int(week) >= 15:
                parts.append("OFFSEASON: The season has concluded. Data below reflects the final week. Treat matchup scores and rosters as historical, not live.")
        except (ValueError, TypeError):
            pass

    if user_roster := data.get("user_roster"):
        record = f"{user_roster.wins}-{user_roster.losses}-{user_roster.ties}"
        team_label = roster_owner_map.get(user_roster.roster_id, f"Roster {user_roster.roster_id}")
        parts.append(f"YOUR TEAM: {team_label} | Record {record} | PF: {user_roster.points_for:.1f}")
        starters = [players[pid].full_name for pid in user_roster.starters if pid in players]
        bench = [players[pid].full_name for pid in user_roster.players
                 if pid not in user_roster.starters and pid in players]
        parts.append(f"YOUR STARTERS: {', '.join(starters) or 'none'}")
        parts.append(f"YOUR BENCH: {', '.join(bench) or 'none'}")

    if matchups := data.get("all_matchups"):
        user_roster_id = data.get("user_roster", None)
        user_roster_id = user_roster_id.roster_id if user_roster_id else None
        paired: dict[int, list] = {}
        for m in matchups:
            if m.matchup_id is not None:
                paired.setdefault(m.matchup_id, []).append(m)
        lines = ["THIS WEEK'S MATCHUPS:"]
        for _, pair in sorted(paired.items()):
            if len(pair) == 2:
                a, b = pair
                a_name = roster_owner_map.get(a.roster_id, f"Roster {a.roster_id}")
                b_name = roster_owner_map.get(b.roster_id, f"Roster {b.roster_id}")
                lines.append(f"  {a_name} ({a.points:.1f} pts) vs {b_name} ({b.points:.1f} pts)")
            elif len(pair) == 1:
                m = pair[0]
                m_name = roster_owner_map.get(m.roster_id, f"Roster {m.roster_id}")
                lines.append(f"  {m_name} ({m.points:.1f} pts) — bye")
        parts.append("\n".join(lines))

    if all_rosters := data.get("all_rosters"):
        user_roster_id = data.get("user_roster", None)
        user_roster_id = user_roster_id.roster_id if user_roster_id else None
        sorted_rosters = sorted(all_rosters, key=lambda r: (-r.wins, -r.points_for))
        lines = ["LEAGUE STANDINGS:"]
        for i, r in enumerate(sorted_rosters, 1):
            record = f"{r.wins}-{r.losses}-{r.ties}"
            team_label = roster_owner_map.get(r.roster_id, f"Roster {r.roster_id}")
            marker = " (YOU)" if r.roster_id == user_roster_id else ""
            lines.append(f"  {i}. {team_label}{marker} | {record} | PF: {r.points_for:.1f}")
        parts.append("\n".join(lines))

        other_rosters = [r for r in all_rosters if r.roster_id != user_roster_id]
        if other_rosters:
            lines = ["ALL TEAM ROSTERS:"]
            for r in other_rosters:
                team_label = roster_owner_map.get(r.roster_id, f"Roster {r.roster_id}")
                starters = [players[pid].full_name for pid in r.starters if pid in players]
                bench = [players[pid].full_name for pid in r.players
                         if pid not in r.starters and pid in players]
                lines.append(f"  {team_label}:")
                lines.append(f"    Starters: {', '.join(starters) or 'none'}")
                lines.append(f"    Bench: {', '.join(bench) or 'none'}")
            parts.append("\n".join(lines))

    if available := data.get("available_players"):
        players_list = list(available.values())[:20]
        names = [f"{p.full_name} ({p.position})" for p in players_list]
        parts.append(f"AVAILABLE PLAYERS (top 20): {', '.join(names)}")

    if txns := data.get("recent_transactions"):
        lines = ["RECENT LEAGUE TRANSACTIONS:"]
        for t in txns[:10]:
            roster_labels = [roster_owner_map.get(rid, f"Roster {rid}") for rid in t.roster_ids]
            team_str = " / ".join(roster_labels)
            adds = ", ".join(
                f"added {players[pid].full_name if pid in players else pid}"
                for pid in (t.adds or {}).keys()
            )
            drops = ", ".join(
                f"dropped {players[pid].full_name if pid in players else pid}"
                for pid in (t.drops or {}).keys()
            )
            detail = " | ".join(filter(None, [adds, drops])) or "details unavailable"
            lines.append(f"  [{t.type}] {team_str}: {detail}")
        parts.append("\n".join(lines))

    return "\n".join(parts) if parts else "No league data available."
