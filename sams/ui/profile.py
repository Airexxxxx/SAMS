# ===================================================================
# SAMS - Profile & Change Password pages
# ===================================================================

import streamlit as st

from sams.config import DB_PATH
from sams.database import get_connection
from sams.auth import hash_password, verify_password


def render_profile():
    st.title("当前用户信息")
    username = st.session_state.get("username", "N/A")
    role = st.session_state.get("user_role", "N/A")

    col1, col2 = st.columns(2)
    with col1:
        st.metric("用户名", username)
    with col2:
        st.metric("角色", role)

    st.info(f"数据库路径: {DB_PATH}")


def render_change_password():
    st.title("修改密码")

    with st.form("change_pwd_form"):
        old_pw = st.text_input("旧密码", type="password")
        new_pw = st.text_input("新密码", type="password")
        confirm_pw = st.text_input("确认新密码", type="password")

        if st.form_submit_button("确认修改"):
            if not old_pw or not new_pw:
                st.error("请填写所有字段")
            elif new_pw != confirm_pw:
                st.error("两次密码不一致")
            elif len(new_pw) < 6:
                st.error("密码长度至少6位")
            else:
                conn = get_connection()
                user = conn.execute(
                    "SELECT * FROM users WHERE username = ?",
                    (st.session_state.username,)
                ).fetchone()
                if user and verify_password(old_pw, user["password_hash"]):
                    new_hash = hash_password(new_pw)
                    conn.execute(
                        "UPDATE users SET password_hash = ? WHERE username = ?",
                        (new_hash, st.session_state.username),
                    )
                    conn.commit()
                    st.success("密码修改成功")
                else:
                    st.error("旧密码错误")
