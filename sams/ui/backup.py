# ===================================================================
# SAMS - Backup & Restore page
# ===================================================================

import os
import shutil
from datetime import datetime
import streamlit as st

from sams.config import DB_PATH
from sams.stats import get_db_size, get_dashboard_stats


def render_backup():
    st.title("数据库备份与恢复")
    st.markdown(f"**数据库路径**: `{DB_PATH}`  |  **数据库大小**: {get_db_size()}")

    st.subheader("📤 数据备份")
    if st.button("💾 立即备份", use_container_width=True):
        if os.path.exists(DB_PATH):
            backup_path = DB_PATH + f".backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            shutil.copy2(DB_PATH, backup_path)
            st.success(f"备份成功: `{backup_path}`")
            st.info(f"备份大小: {os.path.getsize(backup_path) / 1024:.1f} KB")
        else:
            st.warning("数据库文件不存在")

    st.markdown("---")
    st.subheader("📥 数据恢复")
    uploaded_db = st.file_uploader(
        "选择备份文件 (.db)", type=["db"],
        help="上传之前备份的 sams.db 文件恢复数据",
        key="restore_upload"
    )
    if uploaded_db:
        st.warning("⚠ 恢复将覆盖当前所有数据，不可撤销！")
        if st.button("确认恢复数据库", type="primary", use_container_width=True):
            if os.path.exists(DB_PATH):
                safety_path = DB_PATH + f".before_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                shutil.copy2(DB_PATH, safety_path)
                st.info(f"当前数据已备份到: `{safety_path}`")
            with open(DB_PATH, "wb") as f:
                f.write(uploaded_db.getvalue())
            get_dashboard_stats.clear()
            st.success("数据库恢复成功")
            st.rerun()
