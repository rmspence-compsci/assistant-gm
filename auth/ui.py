import streamlit as st
from auth import session as auth_session


def render() -> None:
    st.title("🏈 Assistant GM")
    st.caption("Sign in to access your fantasy leagues.")
    st.divider()

    login_tab, signup_tab = st.tabs(["Log In", "Sign Up"])

    with login_tab:
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")
        if st.button("Log In", use_container_width=True):
            try:
                auth_session.sign_in(email, password)
                st.rerun()
            except Exception as e:
                if "not confirmed" in str(e).lower():
                    st.warning("Please confirm your email before logging in. Check your inbox for a confirmation link.")
                else:
                    st.error("Invalid email or password.")

    with signup_tab:
        email = st.text_input("Email", key="signup_email")
        password = st.text_input("Password", type="password", key="signup_password")
        if st.button("Sign Up", use_container_width=True):
            try:
                auth_session.sign_up(email, password)
                st.success("Account created! Check your email for a confirmation link, then log in.")
            except Exception:
                st.error("Could not create account. Try a different email.")
