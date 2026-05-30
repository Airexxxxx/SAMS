# ===================================================================
# SAMS - User management page
# ===================================================================

import sqlite3
import pandas as pd
import streamlit as st

from sams.database import get_connection
from sams.auth import hash_password


def render_user_management():
    st.title("用户管理")

    if st.session_state.get("user_role") != "admin":
        st.error("仅管理员可访问此页面")
        return

    conn = get_connection()
    users = conn.execute("SELECT id, username, role, created_at FROM users ORDER BY id").fetchall()

    st.subheader("用户列表")
    user_data = [{"ID": u["id"], "用户名": u["username"],
                  "角色": u["role"], "创建时间": u["created_at"]} for u in users]
    st.dataframe(pd.DataFrame(user_data), use_container_width=True, hide_index=True)

    st.markdown("---")
    st.subheader("添加用户")
    with st.form("add_user_form"):
        col1, col2 = st.columns(2)
        with col1:
            new_user = st.text_input("用户名", key="new_username")
        with col2:
            new_password = st.text_input("密码", type="password", key="new_password")
        new_role = st.selectbox("角色", ["user", "admin"], key="new_role")

        if st.form_submit_button("添加用户"):
            if not new_user or not new_password:
                st.error("用户名和密码不能为空")
            else:
                try:
                    pw_hash = hash_password(new_password)
                    conn.execute(
                        "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                        (new_user, pw_hash, new_role),
                    )
                    conn.commit()
                    st.success(f"用户 {new_user} 创建成功")
                    st.rerun()
                except sqlite3.IntegrityError:
                    st.error("用户名已存在")
