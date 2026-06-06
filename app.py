import streamlit as st
from config import settings
from sleeper import client as sleeper_client
from storage import cache
from rag.retriever import retrieve_context
from rag.context_builder import build_context
from llm.client import ask_stream
from storage.finetune_log import log_qa
from ui.components import (
    render_username_input,
    render_league_selector,
    render_team_summary,
    render_chat_message,
)

st.set_page_config(page_title="Assistant GM", page_icon="🏈", layout="wide")
cache.init_db()

for key, default in {
    "username": None,
    "user_id": None,
    "leagues": [],
    "selected_league": None,
    "roster_id": None,
    "messages": [],
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

with st.sidebar:
    st.title("🏈 Assistant GM")
    st.caption("Powered by Claude + Sleeper")
    st.divider()

    username = render_username_input()

    if st.button("Load Leagues", disabled=not username):
        with st.spinner("Loading leagues..."):
            try:
                user = sleeper_client.get_user(username)
                leagues = sleeper_client.get_user_leagues(user.user_id, settings.NFL_SEASON)
                st.session_state.user_id = user.user_id
                st.session_state.username = username
                st.session_state.leagues = leagues
                st.session_state.selected_league = None
                st.session_state.roster_id = None
                st.session_state.messages = []
            except Exception as e:
                st.error(f"Could not load user '{username}': {e}")

    if st.session_state.leagues:
        selected = render_league_selector(st.session_state.leagues)

        if selected and (not st.session_state.selected_league or selected.league_id != st.session_state.selected_league.league_id):
            with st.spinner("Loading league data..."):
                st.session_state.selected_league = selected
                st.session_state.messages = []
                cache.upsert_league(selected)
                cache.refresh_league(selected.league_id)
                rosters = cache.get_rosters(selected.league_id)
                if rosters:
                    user_roster = next(
                        (r for r in rosters if r.owner_id == st.session_state.user_id), None
                    )
                    st.session_state.roster_id = user_roster.roster_id if user_roster else None

        if st.session_state.selected_league and st.session_state.roster_id:
            rosters = cache.get_rosters(st.session_state.selected_league.league_id)
            if rosters:
                user_roster = next((r for r in rosters if r.roster_id == st.session_state.roster_id), None)
                if user_roster:
                    st.divider()
                    render_team_summary(user_roster.wins, user_roster.losses, user_roster.points_for)

        if st.session_state.selected_league:
            st.divider()
            if st.button("🔄 Refresh League Data"):
                with st.spinner("Refreshing..."):
                    cache.refresh_league(st.session_state.selected_league.league_id, force=True)
                st.success("Data refreshed!")

st.title("Ask Your Assistant GM")
st.caption("⚠️ AI-generated advice. Always use your own judgment before making lineup or trade decisions.")

for msg in st.session_state.messages:
    render_chat_message(msg["role"], msg["content"])

if prompt := st.chat_input("Ask anything about your league..."):
    if not st.session_state.selected_league:
        st.warning("Select a league in the sidebar first.")
    else:
        render_chat_message("user", prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        retrieved = retrieve_context(
            prompt,
            st.session_state.selected_league.league_id,
            st.session_state.roster_id,
        )
        context_str = build_context(retrieved)

        with st.chat_message("assistant"):
            response_text = st.write_stream(ask_stream(prompt, context_str))

        st.session_state.messages.append({"role": "assistant", "content": response_text})
        log_qa(prompt, context_str, response_text)
