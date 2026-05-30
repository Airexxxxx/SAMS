# ===================================================================
# SAMS - Analytics page
# ===================================================================

import pandas as pd
import streamlit as st

from sams.stats import get_dashboard_stats


def render_analytics():
    st.title("统计分析")
    stats = get_dashboard_stats()

    tab_idx = st.session_state.get("analytics_tab", 0)
    tab_labels = ["业务统计", "系统类型统计", "运行方式统计"]
    selected = st.radio("选择统计维度", tab_labels, index=tab_idx, horizontal=True,
                        key=f"analytics_radio_{tab_idx}", label_visibility="collapsed")
    current_tab = tab_labels.index(selected)
    st.session_state.analytics_tab = current_tab

    if current_tab == 0:
        st.subheader("按业务线统计")
        if stats["business_distribution"]:
            biz_df = pd.DataFrame(
                list(stats["business_distribution"].items()),
                columns=["业务线", "数量"]
            ).set_index("业务线")
            st.bar_chart(biz_df, horizontal=True)
            st.dataframe(biz_df, use_container_width=True)
        else:
            st.info("暂无数据")

    elif current_tab == 1:
        st.subheader("按系统类型统计")
        if stats["os_distribution"]:
            os_df = pd.DataFrame(
                list(stats["os_distribution"].items()),
                columns=["系统类型", "数量"]
            ).set_index("系统类型")
            col1, col2 = st.columns([2, 1])
            with col1:
                st.bar_chart(os_df, horizontal=True)
            with col2:
                st.dataframe(os_df, use_container_width=True)
        else:
            st.info("暂无数据")

    elif current_tab == 2:
        st.subheader("按运行方式统计")
        if stats["runtime_distribution"]:
            rt_df = pd.DataFrame(
                list(stats["runtime_distribution"].items()),
                columns=["运行方式", "数量"]
            ).set_index("运行方式")
            col1, col2 = st.columns([2, 1])
            with col1:
                st.bar_chart(rt_df, horizontal=True)
            with col2:
                st.dataframe(rt_df, use_container_width=True)
        else:
            st.info("暂无数据")
