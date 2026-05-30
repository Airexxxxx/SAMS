# ===================================================================
# SAMS - UI Sidebar & Header
# ===================================================================

import os
from datetime import datetime
import streamlit as st

from sams.config import DB_PATH
from sams.auth import logout


def render_header():
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    db_status = "🟢" if os.path.exists(DB_PATH) else "🔴"

    st.markdown(f"""
    <div class="sams-header">
        <div class="left">
            <span class="logo">🖥</span>
            <span>服务器资产管理系统</span>
        </div>
        <div class="right">
            <span>👤 {st.session_state.get('username', 'N/A')}</span>
            <span>🕐 {current_time}</span>
            <span>DB {db_status}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_sidebar():
    with st.sidebar:
        st.markdown("### SAMS")
        st.markdown("---")

        menu_sections = {
            "仪表盘": {
                "📊 资产总览": "dashboard",
            },
            "资产管理": {
                "📋 资产列表": "server_list",
                "➕ 新增资产": "add_server",
                "📥 批量导入": "import",
                "📤 导出资产": "export",
            },
            "统计分析": {
                "📊 资产统计分析": "analytics",
            },
            "系统管理": {
                "📝 模板下载": "template",
                "💾 数据库备份": "backup",
                "👥 用户管理": "user_mgmt",
            },
            "用户中心": {
                "👤 当前信息": "profile",
                "🔑 修改密码": "change_pwd",
                "🚪 退出登录": "logout",
            },
        }

        for section, items in menu_sections.items():
            expanded = (section == "仪表盘")
            with st.expander(section, expanded=expanded):
                for label, page in items.items():
                    if st.button(label, key=f"menu_{page}_{label}", use_container_width=True):
                        if page == "logout":
                            logout()
                            st.rerun()
                        if page == "analytics":
                            tab_map = {"业务统计": 0, "系统类型统计": 1, "运行方式统计": 2}
                            st.session_state.analytics_tab = tab_map.get(label, 0)
                        st.session_state.current_page = page
                        st.rerun()
