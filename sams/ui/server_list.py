# ===================================================================
# SAMS - Server list page & detail drawer
# ===================================================================

import pandas as pd
import streamlit as st

from sams.config import PAGE_SIZE, STATUS_LABELS, STATUS_OPTIONS
from sams.crud import get_servers, get_server_by_id, delete_server, get_distinct_values
from sams.stats import get_dashboard_stats
from sams.ui.common import render_status_badge


def render_server_list():
    st.title("资产列表")

    all_businesses = get_distinct_values("business")
    all_os = get_distinct_values("os_type")
    all_runtime = get_distinct_values("runtime_type")

    search = st.text_input("🔍 搜索", placeholder="主机名 / IP地址 / 负责人 / 业务线 ...",
                           key="list_search", label_visibility="collapsed")

    with st.expander("筛选条件", expanded=False):
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            status_f = st.multiselect("状态", STATUS_OPTIONS,
                                      format_func=lambda x: STATUS_LABELS.get(x, x),
                                      key="filter_status")
        with col2:
            os_f = st.multiselect("系统类型", all_os, key="filter_os")
        with col3:
            runtime_f = st.multiselect("运行方式", all_runtime, key="filter_runtime")
        with col4:
            biz_f = st.multiselect("业务线", all_businesses, key="filter_biz")

    page = st.session_state.get("list_page", 1)
    servers, total = get_servers(
        page=page, search=search,
        status_filter=status_f if status_f else None,
        os_filter=os_f if os_f else None,
        runtime_filter=runtime_f if runtime_f else None,
        business_filter=biz_f if biz_f else None,
    )
    total_pages = max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)

    col_left, col_right = st.columns([3, 1.5])

    with col_left:
        st.caption(f"共 {total} 条记录 | 第 {page}/{total_pages} 页")

        display_data = []
        for s in servers:
            display_data.append({
                "序号": s["id"],
                "主机名": s["hostname"],
                "IP地址": s["private_ip"],
                "操作系统": s["os_type"],
                "CPU": s["cpu_cores"],
                "内存(GB)": s["memory_gb"],
                "业务线": s["business"],
                "负责人": s["owner"],
                "状态": STATUS_LABELS.get(s["status"], s["status"]),
                "更新时间": s["updated_at"][:10] if s["updated_at"] else "",
            })

        if display_data:
            df = pd.DataFrame(display_data)

            event = st.dataframe(
                df,
                use_container_width=True,
                height=600,
                hide_index=True,
                on_select="rerun",
                selection_mode="multi-row",
                key="server_table",
            )

            selected_ids = []
            if event is not None and hasattr(event, 'selection') and event.selection.rows:
                for idx in event.selection.rows:
                    if idx < len(servers):
                        selected_ids.append(servers[idx]["id"])

            if len(selected_ids) == 1:
                st.session_state.selected_server_id = selected_ids[0]

            if len(selected_ids) >= 2:
                st.markdown(f"☑ 已勾选 **{len(selected_ids)}** 条资产")
                if st.button(f"🗑 批量删除 ({len(selected_ids)}条)", key="batch_del_btn", type="secondary"):
                    st.session_state.batch_delete_ids = selected_ids
                    st.rerun()

            batch_ids = st.session_state.get("batch_delete_ids", [])
            if batch_ids:
                st.error(f"⚠ 确认删除选中的 {len(batch_ids)} 条资产？此操作不可恢复。")
                cb1, cb2 = st.columns(2)
                with cb1:
                    if st.button("✅ 确认批量删除", key="confirm_batch_del", use_container_width=True):
                        for sid in batch_ids:
                            delete_server(sid)
                        st.session_state.batch_delete_ids = []
                        st.session_state.selected_server_id = None
                        get_dashboard_stats.clear()
                        st.success(f"已删除 {len(batch_ids)} 条资产")
                        st.rerun()
                with cb2:
                    if st.button("❌ 取消", key="cancel_batch_del", use_container_width=True):
                        st.session_state.batch_delete_ids = []
                        st.rerun()
        else:
            st.info("没有找到匹配的资产记录")

        # Pagination
        col_p1, col_p2, col_p3, col_p4, col_p5 = st.columns([1, 1, 2, 1, 1])
        with col_p1:
            if st.button("◀ 首页", disabled=(page == 1), key="first_page"):
                st.session_state.list_page = 1
                st.rerun()
        with col_p2:
            if st.button("◂ 上一页", disabled=(page == 1), key="prev_page"):
                st.session_state.list_page = max(1, page - 1)
                st.rerun()
        with col_p3:
            go_page = st.number_input(
                "页码", min_value=1, max_value=total_pages, value=page,
                label_visibility="collapsed", key="page_input"
            )
            if go_page != page:
                st.session_state.list_page = go_page
                st.rerun()
        with col_p4:
            if st.button("下一页 ▸", disabled=(page >= total_pages), key="next_page"):
                st.session_state.list_page = min(total_pages, page + 1)
                st.rerun()
        with col_p5:
            if st.button("末页 ▶", disabled=(page >= total_pages), key="last_page"):
                st.session_state.list_page = total_pages
                st.rerun()

    # Clear selection when page changes
    last_page = st.session_state.get("_last_list_page", 0)
    if page != last_page:
        st.session_state.selected_server_id = None
        st.session_state._last_list_page = page

    with col_right:
        server_id = st.session_state.get("selected_server_id")
        if server_id:
            render_detail_drawer(server_id)
        else:
            st.info("👈 勾选一条资产即可查看详情；勾选多条可批量删除")


def render_detail_drawer(server_id: int):
    server = get_server_by_id(server_id)
    if not server:
        st.warning("资产不存在")
        return

    st.markdown("### 资产详情")

    fields = [
        ("主机名", "hostname"),
        ("内网IP", "private_ip"),
        ("公网IP", "public_ip"),
        ("系统用户", "system_user"),
        ("系统密码", "credentials"),
        ("系统密钥", "system_key"),
        ("应用密码", "credential_ref"),
        ("操作系统", "os_type"),
        ("系统版本", "os_version"),
        ("内核版本", "kernel_version"),
        ("CPU(核)", "cpu_cores"),
        ("内存(GB)", "memory_gb"),
        ("磁盘", "disk_info"),
        ("位置", "location"),
        ("业务线", "business"),
        ("负责人", "owner"),
        ("状态", "status"),
        ("运行方式", "runtime_type"),
        ("运行详情", "runtime_detail"),
        ("数据库", "db_info"),
        ("端口信息", "port_info"),
        ("业务服务", "business_service"),
        ("应用框架", "app_framework"),
        ("采购日期", "purchase_date"),
        ("保修截止", "warranty_expire"),
        ("备注", "remarks"),
        ("创建时间", "created_at"),
        ("更新时间", "updated_at"),
    ]

    MASKED_FIELDS = {"credentials", "system_key", "credential_ref"}

    html_parts = ['<div class="detail-section">']
    for label, key in fields:
        val = server.get(key, "")
        if str(val) == "" or val is None:
            val = "-"
        elif key in MASKED_FIELDS:
            val = "********"
        if key == "status":
            val = render_status_badge(str(val))
        html_parts.append(
            f'<div class="detail-row">'
            f'<span class="detail-label">{label}</span>'
            f'<span class="detail-value">{val}</span>'
            f'</div>'
        )
    html_parts.append('</div>')
    st.markdown("".join(html_parts), unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("✏ 编辑", key="detail_edit", use_container_width=True):
            st.session_state.edit_server_id = server_id
            st.session_state.current_page = "add_server"
            st.rerun()
    with col2:
        if st.button("🗑 删除", key="detail_delete", use_container_width=True, type="secondary"):
            st.session_state.confirm_delete_id = server_id
            st.rerun()
    with col3:
        if st.button("✖ 关闭", key="detail_close", use_container_width=True):
            st.session_state.selected_server_id = None
            st.rerun()

    # Key export button
    key_content = server.get("system_key", "")
    if key_content and str(key_content).strip():
        st.download_button(
            "🔑 导出密钥文件",
            data=str(key_content),
            file_name=f"{server.get('hostname', 'server')}_id_ed25519",
            mime="application/x-pem-file",
            key="export_key_btn",
            use_container_width=True,
        )

    if st.session_state.get("confirm_delete_id") == server_id:
        st.error("⚠ 确认删除该资产？此操作不可恢复。")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("✅ 确认删除", key="confirm_del_btn", use_container_width=True):
                delete_server(server_id)
                st.session_state.confirm_delete_id = None
                st.session_state.selected_server_id = None
                get_dashboard_stats.clear()
                st.success("已删除")
                st.rerun()
        with c2:
            if st.button("❌ 取消", key="cancel_del_btn", use_container_width=True):
                st.session_state.confirm_delete_id = None
                st.rerun()
