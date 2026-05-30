# ===================================================================
# SAMS - Authentication (with URL token fallback for refresh persistence)
# ===================================================================

import hashlib
import uuid
import streamlit as st

from sams.database import get_connection


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password: str, password_hash: str) -> bool:
    return hash_password(password) == password_hash


def _ensure_sessions_table():
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            token TEXT PRIMARY KEY,
            username TEXT NOT NULL,
            user_role TEXT DEFAULT 'user',
            created_at TEXT DEFAULT (datetime('now', 'localtime'))
        )
    """)
    conn.commit()


def check_auth() -> bool:
    """Return True if user is authenticated. Checks session state first,
    then falls back to URL query param token for refresh persistence."""
    if st.session_state.get("authenticated", False):
        return True

    # Fallback: check URL token (survives browser refresh)
    token = st.query_params.get("token")
    if token:
        conn = get_connection()
        row = conn.execute(
            "SELECT username, user_role FROM sessions WHERE token = ?", (token,)
        ).fetchone()
        if row:
            st.session_state.authenticated = True
            st.session_state.username = row["username"]
            st.session_state.user_role = row["user_role"]
            return True
        else:
            # Stale token — remove from URL
            del st.query_params["token"]

    return False


def login(username: str, password: str) -> bool:
    conn = get_connection()
    user = conn.execute(
        "SELECT * FROM users WHERE username = ?", (username,)
    ).fetchone()
    if user and verify_password(password, user["password_hash"]):
        _ensure_sessions_table()
        # Generate token and persist in DB + URL
        token = uuid.uuid4().hex
        conn.execute(
            "INSERT OR REPLACE INTO sessions (token, username, user_role) VALUES (?, ?, ?)",
            (token, user["username"], user["role"]),
        )
        conn.commit()
        st.session_state.authenticated = True
        st.session_state.username = user["username"]
        st.session_state.user_role = user["role"]
        st.query_params["token"] = token
        return True
    return False


def logout():
    token = st.query_params.get("token")
    if token:
        conn = get_connection()
        conn.execute("DELETE FROM sessions WHERE token = ?", (token,))
        conn.commit()
    st.query_params.clear()
    for key in list(st.session_state.keys()):
        del st.session_state[key]
