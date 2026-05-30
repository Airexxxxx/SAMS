# ===================================================================
# SAMS - Import / Export / Template pages
# ===================================================================

import streamlit as st

from sams.config import TEMPLATE_COLUMNS, COLUMN_LABELS_CN, STATUS_LABELS, STATUS_OPTIONS
from sams.database import get_connection
from sams.crud import get_distinct_values
from sams.excel_utils import import_excel, export_excel, generate_template
from sams.stats import get_dashboard_stats


def render_import():
    st.title("批量导入")
    st.markdown("支持 `.xlsx` 和 `.csv` 格式，自动根据内网IP进行新增或更新。")

    uploaded_file = st.file_uploader(
        "选择文件", type=["xlsx", "csv"],
        help="模板可通过 系统管理 → 模板下载 获取"
    )

    if uploaded_file:
        with st.spinner("正在导入..."):
            success, updated, errors = import_excel(uploaded_file)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("新增", success)
        with col2:
            st.metric("更新", updated)
        with col3:
            st.metric("失败", len(errors))

        if errors:
            st.error("失败详情")
            for e in errors[:50]:
                st.write(f"- {e}")
            if len(errors) > 50:
                st.write(f"... 还有 {len(errors) - 50} 条错误")

        if success > 0 or updated > 0:
            get_dashboard_stats.clear()
            st.success("导入完成")


def render_export():
    from datetime import datetime
    st.title("导出资产")

    all_businesses = get_distinct_values("business")

    export_biz = st.multiselect("按业务线筛选（留空导出全部）", all_businesses, key="exp_biz")
    export_status = st.multiselect("按状态筛选（留空导出全部）", STATUS_OPTIONS,
                                   format_func=lambda x: STATUS_LABELS.get(x, x),
                                   key="exp_status")

    if st.button("📥 导出 Excel", use_container_width=True):
        conn = get_connection()
        conditions = []
        params = []
        if export_biz:
            conditions.append(f"business IN ({','.join(['?']*len(export_biz))})")
            params += export_biz
        if export_status:
            conditions.append(f"status IN ({','.join(['?']*len(export_status))})")
            params += export_status
        where = ("WHERE " + " AND ".join(conditions)) if conditions else ""
        rows = conn.execute(f"SELECT * FROM servers {where} ORDER BY updated_at DESC", params).fetchall()

        # Decrypt sensitive fields before export
        from sams.crypto_utils import decrypt_field
        servers = []
        for r in rows:
            d = dict(r)
            d["credentials"] = decrypt_field(d["credentials"] or "")
            d["system_key"] = decrypt_field(d["system_key"] or "")
            d["credential_ref"] = decrypt_field(d["credential_ref"] or "")
            servers.append(d)

        if servers:
            excel_data = export_excel(servers)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            st.download_button(
                "💾 下载文件",
                data=excel_data,
                file_name=f"servers_{timestamp}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )
            st.success(f"共导出 {len(servers)} 条记录")
        else:
            st.warning("没有符合条件的数据")


def render_template():
    st.title("模板下载")
    st.markdown("下载标准导入模板，用于批量导入资产数据。")

    st.markdown("### 模板字段说明")
    cn_labels = [COLUMN_LABELS_CN[c] for c in TEMPLATE_COLUMNS]
    cols_str = " | ".join(cn_labels)
    st.markdown(f"`{cols_str}`")

    st.markdown("""
    - **主机名** / **内网IP**: 必填
    - **状态**: `running` `stopped` `maintenance` `decommissioned`
    - **系统用户**: 服务器登录用户名
    - **系统密码**: 服务器密码（存储时加密）
    - **系统密钥**: SSH 密钥或证书（存储时加密，选填）
    - **应用密码**: 格式 `应用名:用户名/密码`，每行一条
    - **采购日期** / **保修截止**: YYYY-MM-DD 格式
    """)

    col1, col2 = st.columns(2)
    with col1:
        template_data = generate_template(with_data=False)
        st.download_button(
            "📥 下载空白模板",
            data=template_data,
            file_name="sams_import_template.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )
    with col2:
        test_data = generate_template(with_data=True)
        st.download_button(
            "📋 下载测试数据（含12条示例）",
            data=test_data,
            file_name="sams_test_data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )
