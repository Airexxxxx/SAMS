# ===================================================================
# SAMS - Database connection, initialization, migration
# ===================================================================

import sqlite3
import hashlib

from sams.config import DB_PATH

_connection = None


def get_connection():
    """Return a shared SQLite connection (WAL mode, row factory). Created once per process."""
    global _connection
    if _connection is None:
        _connection = sqlite3.connect(DB_PATH, check_same_thread=False)
        _connection.execute("PRAGMA journal_mode=WAL")
        _connection.execute("PRAGMA foreign_keys=ON")
        _connection.row_factory = sqlite3.Row
    return _connection


def init_db():
    """Initialize database schema, indexes, and default admin. Must be idempotent."""
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS servers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            hostname TEXT NOT NULL,
            private_ip TEXT NOT NULL UNIQUE,
            public_ip TEXT DEFAULT '',
            os_type TEXT DEFAULT '',
            os_version TEXT DEFAULT '',
            kernel_version TEXT DEFAULT '',
            cpu_cores INTEGER DEFAULT 0,
            memory_gb INTEGER DEFAULT 0,
            disk_info TEXT DEFAULT '',
            location TEXT DEFAULT '',
            business TEXT DEFAULT '',
            owner TEXT DEFAULT '',
            status TEXT DEFAULT 'running',
            purchase_date TEXT DEFAULT '',
            warranty_expire TEXT DEFAULT '',
            business_service TEXT DEFAULT '',
            app_framework TEXT DEFAULT '',
            db_info TEXT DEFAULT '',
            runtime_type TEXT DEFAULT '',
            runtime_detail TEXT DEFAULT '',
            port_info TEXT DEFAULT '',
            system_user TEXT DEFAULT '',
            credentials TEXT DEFAULT '',
            system_key TEXT DEFAULT '',
            credential_ref TEXT DEFAULT '',
            remarks TEXT DEFAULT '',
            created_at TEXT DEFAULT (datetime('now', 'localtime')),
            updated_at TEXT DEFAULT (datetime('now', 'localtime'))
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'user',
            created_at TEXT DEFAULT (datetime('now', 'localtime'))
        )
    """)
    conn.commit()

    _migrate_schema(conn)
    create_indexes()
    _create_default_admin(conn)


def _migrate_schema(conn):
    """Add system_user and system_key columns if missing (pre-migration from old schema)."""
    existing = {r[1] for r in conn.execute("PRAGMA table_info('servers')").fetchall()}
    for col in ["system_user", "system_key"]:
        if col not in existing:
            conn.execute(f"ALTER TABLE servers ADD COLUMN {col} TEXT DEFAULT ''")
    conn.commit()


def create_indexes():
    conn = get_connection()
    indexes = [
        "CREATE UNIQUE INDEX IF NOT EXISTS idx_private_ip ON servers(private_ip)",
        "CREATE INDEX IF NOT EXISTS idx_hostname ON servers(hostname)",
        "CREATE INDEX IF NOT EXISTS idx_owner ON servers(owner)",
        "CREATE INDEX IF NOT EXISTS idx_business ON servers(business)",
        "CREATE INDEX IF NOT EXISTS idx_status ON servers(status)",
        "CREATE INDEX IF NOT EXISTS idx_os_type ON servers(os_type)",
        "CREATE INDEX IF NOT EXISTS idx_updated_at ON servers(updated_at)",
    ]
    for idx_sql in indexes:
        conn.execute(idx_sql)
    conn.commit()


def _create_default_admin(conn):
    existing = conn.execute("SELECT id FROM users WHERE username = ?", ("admin",)).fetchone()
    if not existing:
        pw_hash = hashlib.sha256("admin123".encode()).hexdigest()
        conn.execute(
            "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
            ("admin", pw_hash, "admin"),
        )
        conn.commit()
