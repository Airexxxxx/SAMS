# CLAUDE.md

本文件为 Claude Code 在此仓库中工作时提供指引。

## 常用命令

```bash
# 开发运行（使用项目虚拟环境）
/home/air/Desktop/py_venv/streamlit_dev/bin/streamlit run sams.py

# Docker 构建与运行
docker build -t sams:latest .
docker run -d --name sams -p 8501:8501 -v $(pwd)/data:/app/data sams:latest
docker compose up -d

# 语法检查（无测试套件）
python3 -c "import py_compile; py_compile.compile('sams.py', doraise=True)"
```

## 项目结构

```
sams/
├── __init__.py
├── main.py              # st.set_page_config、session state 初始化、页面路由、页脚
├── config.py            # DB_PATH、PAGE_SIZE、状态/OS/运行时常量、TEMPLATE_COLUMNS、COLUMN_LABELS_CN
├── database.py          # get_connection()（WAL 模式，缓存）、init_db()、create_indexes()、schema 迁移
├── auth.py              # SHA256 密码哈希、login()/logout()
├── crud.py              # add/update/delete/get_servers、get_server_by_id、get_distinct_values，内置加解密
├── stats.py             # get_dashboard_stats() — @st.cache_data(ttl=60)
├── crypto_utils.py      # Fernet 对称加密/解密/密钥管理/明文迁移
├── excel_utils.py       # generate_template、validate_ip、import_excel（中英文表头、按 private_ip UPSERT）、export_excel
└── ui/
    ├── __init__.py
    ├── common.py         # inject_css()（暗色主题）、render_status_badge()
    ├── sidebar.py        # render_header()、render_sidebar()
    ├── login.py          # render_login()
    ├── dashboard.py      # render_dashboard()
    ├── server_list.py    # render_server_list()、render_detail_drawer()
    ├── server_form.py    # render_add_server()、server_form_data()
    ├── import_export.py  # render_import()、render_export()、render_template()
    ├── analytics.py      # render_analytics()
    ├── backup.py         # render_backup()
    ├── user_mgmt.py      # render_user_management()
    └── profile.py        # render_profile()、render_change_password()
```

入口文件 `sam.py`：
```python
from sams.main import main
if __name__ == "__main__":
    main()
```

## 数据库

- SQLite，WAL 模式，连接通过 `@st.cache_resource` 缓存，不可手动关闭。
- `servers` 表 27 列（id + 24 业务列 + created_at + updated_at），含 `system_user`、`credentials`、`system_key`、`credential_ref` 四个敏感字段。
- `users` 表存储 SHA256 哈希密码。
- `private_ip` 为唯一业务键，导入时按 `INSERT ... ON CONFLICT(private_ip) DO UPDATE` 实现 UPSERT。

## 敏感字段加密

- `credentials`（系统密码）、`system_key`（系统密钥）、`credential_ref`（应用密码）在数据库中使用 Fernet 对称加密存储。
- 首次运行时自动生成加密密钥，存储在 `data/.encryption_key` 文件中。
- `encrypt_field()` 自动跳过空值和已加密值（以 `gAAAAA` 开头）。
- `decrypt_field()` 自动跳过空值和非加密值。
- 已有明文数据在首次启动时自动迁移加密。
- 导出时排除 `credentials` 和 `system_key` 两列，`credential_ref` 导出为明文。

## 关键模式

- **DB 连接**: `get_connection()` 由 `@st.cache_resource` 缓存。所有查询使用 `?` 参数化占位符。
- **Session state**: 所有 UI 状态统一在 `main.py` 的 `init_session_state()` 中初始化：`authenticated`、`current_page`、`selected_server_id`、`edit_server_id`、`confirm_delete_id`、`batch_delete_ids`、`list_page`、`analytics_tab`、`batch_mode`。
- **UPSERT 键**: `private_ip` 为唯一业务键。
- **凭证显示**: `credentials`、`system_key`、`credential_ref` 在详情抽屉中均显示为 `********`。`credentials` 和 `system_key` 不导出。
- **列名映射**: `COLUMN_LABELS_CN` 英文内部名→中文显示名，`COLUMN_LABELS_EN` 为反向映射（自动生成）。导入时两种表头均可识别。
- **分页**: 每页 20 条，SQL 使用 `LIMIT/OFFSET`。翻页或筛选条件变化时清除 `selected_server_id`。
- **统计分析导航**: 侧边栏按钮设置 `analytics_tab`（0/1/2），radio 组件使用动态 key 强制重新挂载。
- **批量删除**: 表格使用 `selection_mode="multi-row"`。多选时显示批量删除按钮，单选时显示详情面板。

## 导入 CSV 格式

列名首先检查 `COLUMN_LABELS_EN`（中文→英文映射），然后转小写并将空格替换为下划线，因此中英文表头均可正确处理。
应用密码字段格式为 `应用名:用户名/密码`，每行一条记录。
