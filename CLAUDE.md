# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Common Commands

```bash
# Dev run
streamlit run sams.py

# Docker build & run
docker build -t sams:latest .
docker run -d --name sams -p 8501:8501 -v $(pwd)/data:/app/data sams:latest
docker compose up -d

# Syntax check (no test suite exists)
python3 -c "import py_compile; py_compile.compile('sams.py', doraise=True)"
```

## Architecture

Single-file Streamlit app (`sams.py`, ~1700 lines) with module sections delineated by `# ====` comment banners:

| Section | Lines | Purpose |
|---------|-------|---------|
| Config | ~40 | `DB_PATH`, `PAGE_SIZE`, status/OS/runtime constants, `TEMPLATE_COLUMNS`, `COLUMN_LABELS_CN` (Chinese→English column mapping) |
| Database | ~80 | `get_connection()` (WAL mode, cached), `init_db()` (CREATE TABLE IF NOT EXISTS), `create_indexes()` |
| Security/Auth | ~60 | SHA256 password hashing, `login()`/`logout()` via `st.session_state` |
| CRUD | ~130 | `add_server()`, `update_server()`, `delete_server()`, `get_servers()` (paginated, filtered, searched), `get_server_by_id()` |
| Statistics | ~40 | `get_dashboard_stats()` — `@st.cache_data(ttl=60)`, returns aggregations by status/os/runtime/business |
| Excel | ~200 | `generate_template()`, `validate_ip()`, `import_excel()` (Chinese & English header support, UPSERT by `private_ip`), `export_excel()` (excludes `credentials` column) |
| UI CSS | ~220 | Dark theme via `.streamlit/config.toml` (`base = "dark"`). Custom CSS for header, sidebar, badges, detail drawer, inputs, metrics, tabs |
| UI Pages | ~700 | `render_sidebar()`, `render_dashboard()`, `render_server_list()`, `render_add_server()`, `render_import()`, `render_export()`, `render_template()`, `render_analytics()`, `render_backup()`, `render_user_management()`, `render_profile()`, `render_change_password()` |
| Main | ~50 | Session state init, auth gate, page router via `st.session_state.current_page` |

## Key Patterns

- **DB connection**: `@st.cache_resource` on `get_connection()` — never close it manually. All queries use `?` parameterized placeholders.
- **Session state**: All UI state in `st.session_state` — `authenticated`, `current_page`, `selected_server_id`, `edit_server_id`, `confirm_delete_id`, `batch_delete_ids`, `list_page`, `analytics_tab`.
- **UPSERT key**: `private_ip` is the unique business key. Import uses `INSERT ... ON CONFLICT(private_ip) DO UPDATE`.
- **Credentials masking**: Both `credentials` (系统密码) and `credential_ref` (应用密码) display as `********` in the detail drawer. `credentials` is excluded from exports. `credential_ref` uses multi-line format `应用名:用户名:密码`.
- **Column name mapping**: `COLUMN_LABELS_CN` maps English internal names to Chinese display names. `COLUMN_LABELS_EN` is the reverse mapping (auto-generated). Import accepts both.
- **Pagination**: 20 rows per page, `LIMIT/OFFSET` in SQL. Page/filter changes clear `selected_server_id`.
- **Analytics navigation**: Sidebar buttons set `analytics_tab` in session state (0/1/2). Radio widget uses dynamic key `f"analytics_radio_{tab_idx}"` to force re-mount on tab change.
- **Batch delete**: Table uses `selection_mode="multi-row"`. Selected IDs tracked via `st.dataframe` return value's `.selection.rows`.

## Import CSV format

Column name `应用名:用户名:密码` means the import function normalizes headers: first checks `COLUMN_LABELS_EN` (Chinese→English), then lowercases and replaces spaces with underscores. So both Chinese headers and English headers work.
