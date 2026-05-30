# ===================================================================
# SAMS - Main entry point & page router
# ===================================================================

import streamlit as st

from sams.database import init_db
from sams.auth import check_auth
from sams.ui.common import inject_css
from sams.ui.sidebar import render_header, render_sidebar
from sams.ui.login import render_login
from sams.ui.dashboard import render_dashboard
from sams.ui.server_list import render_server_list
from sams.ui.server_form import render_add_server
from sams.ui.import_export import render_import, render_export, render_template
from sams.ui.analytics import render_analytics
from sams.ui.backup import render_backup
from sams.ui.user_mgmt import render_user_management
from sams.ui.profile import render_profile, render_change_password


def _run_startup():
    """Run DB init, encryption setup, and data migration once per startup.
    Wrapped in try/except so any startup error won't kill the session."""
    try:
        init_db()
        from sams.crypto_utils import init_encryption_key, migrate_plaintext_to_encrypted
        init_encryption_key()
        migrate_plaintext_to_encrypted()
        # Ensure sessions table exists for token-based auth persistence
        from sams.auth import _ensure_sessions_table
        _ensure_sessions_table()
    except Exception:
        pass  # DB already initialized, continue with existing session


def init_session_state():
    """Initialize UI state keys. `authenticated` is handled by check_auth() token fallback."""
    defaults = {
        "current_page": "dashboard",
        "selected_server_id": None,
        "edit_server_id": None,
        "confirm_delete_id": None,
        "list_page": 1,
        "analytics_tab": 0,
        "batch_delete_ids": [],
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


def main():
    st.set_page_config(
        page_title="SAMS - 资产管理系统",
        page_icon="🖥",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    inject_css()
    _run_startup()
    init_session_state()

    if not check_auth():
        render_login()
        return

    render_header()
    render_sidebar()

    page = st.session_state.current_page

    page_map = {
        "dashboard": render_dashboard,
        "server_list": render_server_list,
        "add_server": render_add_server,
        "import": render_import,
        "export": render_export,
        "template": render_template,
        "analytics": render_analytics,
        "backup": render_backup,
        "user_mgmt": render_user_management,
        "profile": render_profile,
        "change_pwd": render_change_password,
    }

    render_func = page_map.get(page, render_dashboard)
    render_func()

    st.markdown('<div class="sams-footer">SAMS v1.0 — 服务器资产管理系统</div>',
                unsafe_allow_html=True)
