import re
import streamlit as st
from werkzeug.security import generate_password_hash, check_password_hash
from database import create_user, find_user

def auth_page():
    st.markdown("""<style>
    [data-testid="stAppViewContainer"] {background:linear-gradient(135deg,#eef2ff 0%,#f8fafc 55%,#ecfeff 100%);}
    .auth-title {text-align:center;font-size:2.5rem;font-weight:800;color:#312e81;margin-bottom:0;}
    .auth-sub {text-align:center;color:#64748b;margin-top:4px;margin-bottom:24px;}
    </style>""", unsafe_allow_html=True)
    st.markdown('<div class="auth-title">CareerForge AI</div><div class="auth-sub">Build your next career move with AI</div>', unsafe_allow_html=True)
    left, center, right = st.columns([1,1.35,1])
    with center:
        with st.container(border=True):
            mode = st.radio("Welcome", ["Login", "Create account"], horizontal=True, label_visibility="collapsed")
            username = st.text_input("Username", max_chars=40)
            password = st.text_input("Password", type="password")
            if mode == "Create account":
                confirm = st.text_input("Confirm password", type="password")
                if st.button("Create account", type="primary", use_container_width=True):
                    username = username.strip()
                    if not re.fullmatch(r"[A-Za-z0-9_.-]{3,40}", username):
                        st.error("Username must be 3–40 characters: letters, numbers, dot, underscore or hyphen.")
                    elif len(password) < 8:
                        st.error("Use a password with at least 8 characters.")
                    elif password != confirm:
                        st.error("Passwords do not match.")
                    elif create_user(username, generate_password_hash(password)):
                        st.success("Account created. Please login.")
                    else:
                        st.error("That username already exists.")
            else:
                if st.button("Login", type="primary", use_container_width=True):
                    user = find_user(username.strip())
                    if user and check_password_hash(user["password_hash"], password):
                        st.session_state["user_id"] = user["id"]
                        st.session_state["username"] = user["username"]
                        st.rerun()
                    else:
                        st.error("Incorrect username or password.")

def logout():
    for key in list(st.session_state.keys()):
        if key not in ("_" ,):
            del st.session_state[key]
    st.rerun()
