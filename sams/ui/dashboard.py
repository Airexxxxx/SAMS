# ===================================================================
# SAMS - Dashboard page
# ===================================================================

import pandas as pd
import streamlit as st

from sams.stats import get_dashboard_stats, get_warranty_stats


def render_dashboard():
    st.title("仪表盘")
    stats = get_dashboard_stats()

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("总资产数", stats["total"])
    with col2:
        st.metric("运行中", stats["running"])
    with col3:
        st.metric("已停止", stats["stopped"])
    with col4:
        st.metric("维护中", stats["maintenance"])
    with col5:
        st.metric("已下线", stats["decommissioned"])

    st.markdown("---")
    st.subheader("资产状态分布")
    status_df = pd.DataFrame({
        "运行中": [stats["running"]],
        "已停止": [stats["stopped"]],
        "维护中": [stats["maintenance"]],
        "已下线": [stats["decommissioned"]],
    })
    st.bar_chart(status_df, color=["#10b981", "#f59e0b", "#3b82f6", "#ef4444"])

    st.markdown("---")
    st.subheader("保修到期提醒")
    warranty_list = get_warranty_stats()
    if warranty_list:
        expired = [w for w in warranty_list if w["status"] == "expired"]
        warning = [w for w in warranty_list if w["status"] == "warning"]
        col_w1, col_w2, col_w3 = st.columns(3)
        with col_w1:
            st.metric("已过期", len(expired))
        with col_w2:
            st.metric("30天内到期", len(warning))
        with col_w3:
            st.metric("正常", len(warranty_list) - len(expired) - len(warning))

        # Build display table grouped by business
        display_rows = []
        for w in warranty_list:
            if w["days_left"] < 0:
                day_str = f"已过期 {abs(w['days_left'])} 天"
                icon = "🔴"
            elif w["days_left"] <= 30:
                day_str = f"剩余 {w['days_left']} 天"
                icon = "🟡"
            else:
                day_str = f"剩余 {w['days_left']} 天"
                icon = "🟢"
            display_rows.append({
                "业务线": w["business"],
                "主机名": w["hostname"],
                "保修截止": w["warranty_expire"],
                "到期状态": f"{icon} {day_str}",
            })
        df_warranty = pd.DataFrame(display_rows)
        st.dataframe(df_warranty, use_container_width=True, hide_index=True,
                     column_config={
                         "到期状态": st.column_config.TextColumn(width="medium"),
                     })
    else:
        st.info("暂无保修数据")

    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("系统类型分布")
        if stats["os_distribution"]:
            os_df = pd.DataFrame(
                list(stats["os_distribution"].items()),
                columns=["系统类型", "数量"]
            ).set_index("系统类型")
            st.bar_chart(os_df, horizontal=True)
        else:
            st.info("暂无数据")

    with col2:
        st.subheader("运行方式分布")
        if stats["runtime_distribution"]:
            rt_df = pd.DataFrame(
                list(stats["runtime_distribution"].items()),
                columns=["运行方式", "数量"]
            ).set_index("运行方式")
            st.bar_chart(rt_df, horizontal=True)
        else:
            st.info("暂无数据")

    st.markdown("---")
    st.subheader("业务线分布")
    if stats["business_distribution"]:
        biz_df = pd.DataFrame(
            list(stats["business_distribution"].items()),
            columns=["业务线", "数量"]
        ).set_index("业务线")
        st.bar_chart(biz_df, horizontal=True)
    else:
        st.info("暂无数据")
