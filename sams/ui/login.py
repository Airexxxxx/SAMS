# ===================================================================
# SAMS - Login page
# ===================================================================

import streamlit as st

from sams.auth import login


def render_login():
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style="text-align: center; margin-bottom: 30px;">
            <h1 style="color: #93c5fd;">🖥 SAMS</h1>
            <p style="color: #94a3b8;">服务器资产管理系统</p>
        </div>
        """, unsafe_allow_html=True)

        with st.form("login_form"):
            username = st.text_input("用户名", placeholder="admin")
            password = st.text_input("密码", type="password", placeholder="admin123")
            submitted = st.form_submit_button("登 录", use_container_width=True)

            if submitted:
                if login(username, password):
                    st.session_state.current_page = "dashboard"
                    st.rerun()
                else:
                    st.error("用户名或密码错误")
