import re

import streamlit as st
from werkzeug.security import check_password_hash, generate_password_hash

from database import create_user, find_user


def auth_page():
    st.markdown(
        """
        <style>
        [data-testid="stAppViewContainer"] {
            background:
                radial-gradient(ellipse at 12% 18%, #e0e7ff 0, transparent 38%),
                radial-gradient(ellipse at 88% 82%, #cffafe 0, transparent 34%),
                #f8fafc;
        }
        [data-testid="stHeader"] { background: transparent; }
        [data-testid="stMain"] .block-container {
            max-width: 1180px;
            padding-top: 4rem;
            padding-bottom: 3rem;
        }
        .auth-brand {
            color: #4338ca;
            font-size: .78rem;
            font-weight: 800;
            letter-spacing: .14em;
            text-transform: uppercase;
            margin-bottom: 1.2rem;
        }
        .auth-hero h1 {
            color: #172554;
            font-size: clamp(2.5rem, 5vw, 4.1rem);
            font-weight: 850;
            letter-spacing: -.055em;
            line-height: 1.05;
            margin: 0 0 1rem;
        }
        .auth-hero .auth-description {
            color: #475569;
            font-size: 1.12rem;
            line-height: 1.75;
            max-width: 590px;
            margin-bottom: 1.7rem;
        }
        .auth-benefits {
            display: grid;
            gap: .75rem;
            max-width: 570px;
        }
        .auth-benefit {
            display: flex;
            gap: .85rem;
            align-items: flex-start;
            padding: .9rem 1rem;
            border: 1px solid #e2e8f0;
            border-radius: 14px;
            background: rgba(255,255,255,.82);
            color: #334155;
            line-height: 1.5;
        }
        .auth-benefit strong {
            display: block;
            color: #1e293b;
            margin-bottom: .12rem;
        }
        .auth-benefit-icon {
            display: grid;
            place-items: center;
            flex: 0 0 2.2rem;
            height: 2.2rem;
            border-radius: 10px;
            background: #eef2ff;
            color: #4338ca;
            font-weight: 800;
        }
        .auth-footnote {
            color: #64748b;
            font-size: .86rem;
            margin-top: 1.1rem;
        }
        [data-testid="stVerticalBlockBorderWrapper"] {
            background: #fff;
            border: 1px solid #e2e8f0;
            border-radius: 22px;
            box-shadow: 0 22px 65px rgba(30, 41, 59, .10);
        }
        [data-testid="stWidgetLabel"],
        [data-testid="stRadio"] label,
        [data-testid="stMarkdownContainer"] p {
            color: #334155;
        }
        [data-testid="stTextInput"] input {
            background: #fff;
            color: #0f172a;
            border: 1px solid #cbd5e1;
            border-radius: 10px;
        }
        [data-testid="stTextInput"] input::placeholder { color: #64748b; }
        @media (max-width: 760px) {
            [data-testid="stMain"] .block-container {
                padding-top: 1.5rem;
                padding-left: 1rem;
                padding-right: 1rem;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    intro, form_column = st.columns([1.2, 0.88], gap="large")
    with intro:
        st.markdown(
            """
            <div class="auth-hero">
                <div class="auth-brand">Career development, with a plan</div>
                <h1>Make your next career move with confidence.</h1>
                <p class="auth-description">
                    CareerForge AI helps you turn your goals into a practical path forward.
                    Explore the skills your target role needs, see where to focus, and build
                    a personalized learning roadmap you can follow.
                </p>
                <div class="auth-benefits">
                    <div class="auth-benefit">
                        <span class="auth-benefit-icon">01</span>
                        <span><strong>Know what to learn</strong>Compare your current skills with the requirements of your target role.</span>
                    </div>
                    <div class="auth-benefit">
                        <span class="auth-benefit-icon">02</span>
                        <span><strong>Follow a clear roadmap</strong>Get focused weekly steps, learning resources, and interview practice.</span>
                    </div>
                    <div class="auth-benefit">
                        <span class="auth-benefit-icon">03</span>
                        <span><strong>Keep your progress together</strong>Save career plans to your account and revisit them from your dashboard.</span>
                    </div>
                </div>
                <div class="auth-footnote">Your career goals, organized into your next steps.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with form_column:
        with st.container(border=True):
            st.markdown("### Welcome to CareerForge")
            st.caption("Sign in to continue, or create an account to get started.")
            mode = st.radio(
                "Welcome",
                ["Login", "Create account"],
                horizontal=True,
                label_visibility="collapsed",
            )
            st.markdown(
                "#### Sign in" if mode == "Login" else "#### Create your account"
            )
            username = st.text_input("Username", max_chars=40)
            password = st.text_input("Password", type="password")
            if mode == "Create account":
                confirm = st.text_input("Confirm password", type="password")
                if st.button("Create account", type="primary", width="stretch"):
                    username = username.strip()
                    if not re.fullmatch(r"[A-Za-z0-9_.-]{3,40}", username):
                        st.error(
                            "Username must be 3–40 characters: letters, numbers, dot, underscore or hyphen."
                        )
                    elif len(password) < 8:
                        st.error("Use a password with at least 8 characters.")
                    elif password != confirm:
                        st.error("Passwords do not match.")
                    elif create_user(username, generate_password_hash(password)):
                        st.success("Account created. Please login.")
                    else:
                        st.error("That username already exists.")
            elif st.button("Login", type="primary", width="stretch"):
                user = find_user(username.strip())
                if user and check_password_hash(user["password_hash"], password):
                    st.session_state["user_id"] = user["id"]
                    st.session_state["username"] = user["username"]
                    st.rerun()
                else:
                    st.error("Incorrect username or password.")


def logout():
    for key in list(st.session_state.keys()):
        if key not in ("_",):
            del st.session_state[key]
    st.rerun()
