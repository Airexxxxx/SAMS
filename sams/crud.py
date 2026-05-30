# ===================================================================
# SAMS - CRUD operations for servers
# ===================================================================

from datetime import datetime

from sams.database import get_connection
from sams.config import PAGE_SIZE, TEMPLATE_COLUMNS, ENCRYPTED_FIELDS
from sams.crypto_utils import encrypt_field, decrypt_field


def _prepare_write_data(data: dict) -> dict:
    """Encrypt sensitive fields before writing to DB."""
    result = dict(data)
    for field in ENCRYPTED_FIELDS:
        if field in result:
            result[field] = encrypt_field(result[field])
    return result


def _decrypt_row(row: dict) -> dict:
    """Decrypt sensitive fields after reading from DB."""
    for field in ENCRYPTED_FIELDS:
        if field in row:
            row[field] = decrypt_field(row[field] or "")
    return row


def add_server(data: dict) -> int:
    conn = get_connection()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    write_data = _prepare_write_data(data)
    columns = list(TEMPLATE_COLUMNS)
    placeholders = ", ".join(["?"] * len(columns))
    cols_str = ", ".join(columns)
    values = [write_data.get(c, "") for c in columns]
    cursor = conn.execute(
        f"INSERT INTO servers ({cols_str}, created_at, updated_at) VALUES ({placeholders}, ?, ?)",
        values + [now, now],
    )
    conn.commit()
    return cursor.lastrowid


def update_server(server_id: int, data: dict) -> bool:
    conn = get_connection()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    write_data = _prepare_write_data(data)
    columns = list(TEMPLATE_COLUMNS)
    set_clause = ", ".join([f"{c} = ?" for c in columns])
    values = [write_data.get(c, "") for c in columns] + [now, server_id]
    conn.execute(
        f"UPDATE servers SET {set_clause}, updated_at = ? WHERE id = ?", values
    )
    conn.commit()
    return True


def delete_server(server_id: int):
    conn = get_connection()
    conn.execute("DELETE FROM servers WHERE id = ?", (server_id,))
    conn.commit()


def get_server_by_id(server_id: int) -> dict | None:
    conn = get_connection()
    row = conn.execute("SELECT * FROM servers WHERE id = ?", (server_id,)).fetchone()
    if row:
        return _decrypt_row(dict(row))
    return None


def get_servers(
    page: int = 1,
    search: str = "",
    status_filter: list | None = None,
    os_filter: list | None = None,
    runtime_filter: list | None = None,
    business_filter: list | None = None,
    sort_by: str = "updated_at",
    sort_order: str = "DESC",
) -> tuple[list, int]:
    conn = get_connection()
    conditions = []
    params = []

    if search:
        search_cols = ["hostname", "private_ip", "owner", "business"]
        search_clauses = " OR ".join([f"{c} LIKE ?" for c in search_cols])
        conditions.append(f"({search_clauses})")
        params += [f"%{search}%"] * len(search_cols)

    if status_filter:
        conditions.append(f"status IN ({','.join(['?']*len(status_filter))})")
        params += status_filter

    if os_filter:
        conditions.append(f"os_type IN ({','.join(['?']*len(os_filter))})")
        params += os_filter

    if runtime_filter:
        conditions.append(f"runtime_type IN ({','.join(['?']*len(runtime_filter))})")
        params += runtime_filter

    if business_filter:
        conditions.append(f"business IN ({','.join(['?']*len(business_filter))})")
        params += business_filter

    where = ("WHERE " + " AND ".join(conditions)) if conditions else ""

    valid_sort_cols = ["hostname", "private_ip", "os_type", "cpu_cores", "memory_gb",
                       "business", "owner", "status", "updated_at", "created_at"]
    if sort_by not in valid_sort_cols:
        sort_by = "updated_at"
    if sort_order.upper() not in ("ASC", "DESC"):
        sort_order = "DESC"

    count_row = conn.execute(
        f"SELECT COUNT(*) FROM servers {where}", params
    ).fetchone()
    total = count_row[0]

    offset = (page - 1) * PAGE_SIZE
    rows = conn.execute(
        f"SELECT * FROM servers {where} ORDER BY {sort_by} {sort_order} LIMIT ? OFFSET ?",
        params + [PAGE_SIZE, offset],
    ).fetchall()

    return [_decrypt_row(dict(r)) for r in rows], total


def get_distinct_values(column: str) -> list:
    conn = get_connection()
    rows = conn.execute(
        f"SELECT DISTINCT {column} FROM servers WHERE {column} IS NOT NULL AND {column} != '' ORDER BY {column}"
    ).fetchall()
    return [r[column] for r in rows]
