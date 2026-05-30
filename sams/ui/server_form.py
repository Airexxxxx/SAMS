# ===================================================================
# SAMS - Add / Edit server form
# ===================================================================

import sqlite3
import streamlit as st

from sams.config import STATUS_OPTIONS, STATUS_LABELS, OS_OPTIONS, RUNTIME_OPTIONS
from sams.crud import get_server_by_id, add_server, update_server
from sams.excel_utils import validate_ip, validate_date
from sams.stats import get_dashboard_stats


def server_form_data(defaults: dict | None = None) -> dict:
    if defaults is None:
        defaults = {}
    col1, col2 = st.columns(2)
    data = {}
    with col1:
        data["hostname"] = st.text_input("主机名 *", value=defaults.get("hostname", ""), key="f_hostname")
        data["private_ip"] = st.text_input("内网IP *", value=defaults.get("private_ip", ""), key="f_private_ip")
        data["public_ip"] = st.text_input("公网IP", value=defaults.get("public_ip", ""), key="f_public_ip")
        data["system_user"] = st.text_input("系统用户", value=defaults.get("system_user", ""), key="f_system_user",
                                             help="服务器登录用户名，如 root / Administrator")
        data["credentials"] = st.text_input("系统密码", value=defaults.get("credentials", ""), key="f_credentials", type="password",
                                            help="服务器 root/Administrator 密码")
        data["system_key"] = st.text_area("系统密钥", value=defaults.get("system_key", ""), key="f_system_key", height=120,
                                            help="SSH 私钥或证书内容，多行文本；也可通过下方按钮导入密钥文件",
                                            placeholder="-----BEGIN OPENSSH PRIVATE KEY-----\n...\n-----END OPENSSH PRIVATE KEY-----")
        key_file = st.file_uploader("📎 导入密钥文件", type=["pem", "key", "txt", "pub", ""], key="f_key_upload",
                                    help="选择密钥文件，内容将自动填入上方文本框")
        if key_file is not None:
            try:
                key_content = key_file.getvalue().decode("utf-8")
                # Update the text_area by storing in session state for next rerun
                st.session_state.f_system_key = key_content
                st.rerun()
            except Exception:
                st.error("无法读取密钥文件，请检查编码")
        data["credential_ref"] = st.text_area("应用密码", value=defaults.get("credential_ref", ""), key="f_credential_ref", height=100,
                                              placeholder="应用名:用户名/密码（每行一条）\n例如:\nMySQL:root/MyPass123\nMySQL:app_user/AppPass456\nRedis:default/RedisPass789",
                                              help="格式: 应用名:用户名/密码，每行一条记录")
        data["os_type"] = st.selectbox("操作系统", [""] + OS_OPTIONS,
                                       index=([""] + OS_OPTIONS).index(defaults.get("os_type", "")) if defaults.get("os_type", "") in OS_OPTIONS else 0,
                                       key="f_os_type")
        data["os_version"] = st.text_input("系统版本", value=defaults.get("os_version", ""), key="f_os_version")
        data["kernel_version"] = st.text_input("内核版本", value=defaults.get("kernel_version", ""), key="f_kernel_version")
        data["cpu_cores"] = st.number_input("CPU(核)", min_value=0, step=1,
                                            value=int(defaults.get("cpu_cores", 0) or 0), key="f_cpu")
        data["memory_gb"] = st.number_input("内存(GB)", min_value=0, step=1,
                                            value=int(defaults.get("memory_gb", 0) or 0), key="f_memory")
        data["disk_info"] = st.text_input("磁盘", value=defaults.get("disk_info", ""), key="f_disk")
        data["location"] = st.text_input("位置", value=defaults.get("location", ""), key="f_location")
        data["business"] = st.text_input("业务线", value=defaults.get("business", ""), key="f_business")
        data["owner"] = st.text_input("负责人", value=defaults.get("owner", ""), key="f_owner")
    with col2:
        status_idx = STATUS_OPTIONS.index(defaults.get("status", "running")) if defaults.get("status", "") in STATUS_OPTIONS else 0
        data["status"] = st.selectbox("状态", STATUS_OPTIONS, index=status_idx,
                                      format_func=lambda x: STATUS_LABELS.get(x, x), key="f_status")
        rt_idx = ([""] + RUNTIME_OPTIONS).index(defaults.get("runtime_type", "")) if defaults.get("runtime_type", "") in RUNTIME_OPTIONS else 0
        data["runtime_type"] = st.selectbox("运行方式", [""] + RUNTIME_OPTIONS, index=rt_idx, key="f_runtime_type")
        data["runtime_detail"] = st.text_input("运行详情", value=defaults.get("runtime_detail", ""), key="f_runtime_detail")
        data["db_info"] = st.text_input("数据库", value=defaults.get("db_info", ""), key="f_db_info")
        data["port_info"] = st.text_input("端口信息", value=defaults.get("port_info", ""), key="f_port_info")
        data["purchase_date"] = st.text_input("采购日期", value=defaults.get("purchase_date", ""), key="f_purchase_date", placeholder="YYYY-MM-DD")
        data["warranty_expire"] = st.text_input("保修截止", value=defaults.get("warranty_expire", ""), key="f_warranty", placeholder="YYYY-MM-DD")
        data["business_service"] = st.text_input("业务服务", value=defaults.get("business_service", ""), key="f_biz_service")
        data["app_framework"] = st.text_input("应用框架", value=defaults.get("app_framework", ""), key="f_app_framework")
        data["remarks"] = st.text_area("备注", value=defaults.get("remarks", ""), key="f_remarks", height=80)
    return data


def render_add_server():
    edit_id = st.session_state.get("edit_server_id")
    existing = get_server_by_id(edit_id) if edit_id else None

    if edit_id:
        st.title("编辑资产")
        st.info(f"当前编辑: **{existing.get('hostname', 'N/A')}** ({existing.get('private_ip', 'N/A')})")
    else:
        st.title("新增资产")

    with st.form("server_form"):
        data = server_form_data(existing)

        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            submitted = st.form_submit_button("💾 保存", use_container_width=True)
        with col2:
            reset = st.form_submit_button("🔄 重置", use_container_width=True)
        with col3:
            back = st.form_submit_button("↩ 返回", use_container_width=True)

        if back:
            st.session_state.edit_server_id = None
            st.session_state.current_page = "server_list"
            st.rerun()

        if submitted:
            errors = []
            if not data["hostname"].strip():
                errors.append("主机名不能为空")
            if not validate_ip(data["private_ip"].strip()):
                errors.append("内网IP格式不正确")
            if data["purchase_date"] and not validate_date(data["purchase_date"].strip()):
                errors.append("采购日期格式不正确 (YYYY-MM-DD)")
            if data["warranty_expire"] and not validate_date(data["warranty_expire"].strip()):
                errors.append("保修截止格式不正确 (YYYY-MM-DD)")

            if errors:
                for e in errors:
                    st.error(e)
            else:
                try:
                    if edit_id:
                        update_server(edit_id, data)
                        st.success("资产更新成功")
                        st.session_state.edit_server_id = None
                    else:
                        add_server(data)
                        st.success("资产添加成功")
                    get_dashboard_stats.clear()
                    st.session_state.current_page = "server_list"
                    st.rerun()
                except sqlite3.IntegrityError:
                    st.error("内网IP已存在，请检查后重试")
                except Exception as e:
                    st.error(f"保存失败: {e}")
