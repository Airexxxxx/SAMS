# ===================================================================
# SAMS - Dashboard statistics
# ===================================================================

import os
import streamlit as st

from sams.database import get_connection
from sams.config import STATUS_OPTIONS, DB_PATH


@st.cache_data(ttl=60)
def get_dashboard_stats() -> dict:
    conn = get_connection()
    stats = {}

    stats["total"] = conn.execute("SELECT COUNT(*) FROM servers").fetchone()[0]

    for status in STATUS_OPTIONS:
        stats[status] = conn.execute(
            "SELECT COUNT(*) FROM servers WHERE status = ?", (status,)
        ).fetchone()[0]

    os_rows = conn.execute(
        "SELECT os_type, COUNT(*) as cnt FROM servers WHERE os_type != '' GROUP BY os_type ORDER BY cnt DESC"
    ).fetchall()
    stats["os_distribution"] = {r["os_type"]: r["cnt"] for r in os_rows}

    runtime_rows = conn.execute(
        "SELECT runtime_type, COUNT(*) as cnt FROM servers WHERE runtime_type != '' GROUP BY runtime_type ORDER BY cnt DESC"
    ).fetchall()
    stats["runtime_distribution"] = {r["runtime_type"]: r["cnt"] for r in runtime_rows}

    business_rows = conn.execute(
        "SELECT business, COUNT(*) as cnt FROM servers WHERE business != '' GROUP BY business ORDER BY cnt DESC"
    ).fetchall()
    stats["business_distribution"] = {r["business"]: r["cnt"] for r in business_rows}

    return stats


@st.cache_data(ttl=60)
def get_warranty_stats() -> list[dict]:
    """Return warranty expiry info: list of {business, hostname, warranty_expire, days_left} sorted by days_left."""
    from datetime import date
    conn = get_connection()
    rows = conn.execute(
        "SELECT hostname, business, warranty_expire FROM servers WHERE warranty_expire IS NOT NULL AND warranty_expire != ''"
    ).fetchall()
    results = []
    today = date.today()
    for r in rows:
        try:
            expiry = date.fromisoformat(r["warranty_expire"][:10])
            days = (expiry - today).days
        except (ValueError, TypeError):
            continue
        if days < 0:
            status = "expired"
        elif days <= 30:
            status = "warning"
        else:
            status = "ok"
        results.append({
            "business": r["business"] or "未分类",
            "hostname": r["hostname"],
            "warranty_expire": r["warranty_expire"][:10] if r["warranty_expire"] else "",
            "days_left": days,
            "status": status,
        })
    results.sort(key=lambda x: x["days_left"])
    return results


def get_db_size() -> str:
    if os.path.exists(DB_PATH):
        size_bytes = os.path.getsize(DB_PATH)
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        else:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
    return "N/A"
