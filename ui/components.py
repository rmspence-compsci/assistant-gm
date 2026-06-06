import streamlit as st
from sleeper.models import League


def render_username_input() -> str | None:
    username = st.text_input("Sleeper Username", placeholder="your_sleeper_username")
    return username.strip() if username else None


def render_league_selector(leagues: list) -> League | None:
    if not leagues:
        return None
    options = {league.name: league for league in leagues}
    selected_name = st.selectbox("Select League", list(options.keys()))
    return options.get(selected_name)


def render_team_summary(wins: int, losses: int, points_for: float) -> None:
    col1, col2 = st.columns(2)
    col1.metric("Record", f"{wins}-{losses}")
    col2.metric("Points For", f"{points_for:.1f}")


def render_chat_message(role: str, content: str) -> None:
    with st.chat_message(role):
        st.markdown(content)
