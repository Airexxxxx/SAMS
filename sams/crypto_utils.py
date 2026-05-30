# ===================================================================
# SAMS - Encryption utilities (Fernet symmetric encryption)
# ===================================================================

import os
from cryptography.fernet import Fernet

from sams.config import DB_PATH

KEY_FILE = os.path.join(os.path.dirname(DB_PATH), ".encryption_key")

_fernet = None


def _get_key_path() -> str:
    return KEY_FILE


def init_encryption_key():
    """Load or generate the Fernet encryption key."""
    global _fernet
    key_path = _get_key_path()
    if os.path.exists(key_path):
        with open(key_path, "rb") as f:
            key = f.read()
    else:
        key = Fernet.generate_key()
        os.makedirs(os.path.dirname(key_path), exist_ok=True)
        with open(key_path, "wb") as f:
            f.write(key)
    _fernet = Fernet(key)


def _get_fernet() -> Fernet:
    if _fernet is None:
        init_encryption_key()
    return _fernet


def encrypt_field(value: str) -> str:
    """Encrypt a field value. Returns the Fernet token string.
    Returns empty string as-is. Already-encrypted values are not re-encrypted.
    """
    if not value or str(value).strip() == "":
        return ""
    s = str(value)
    # Already a Fernet token
    if s.startswith("gAAAAA"):
        return s
    return _get_fernet().encrypt(s.encode()).decode()


def decrypt_field(value: str) -> str:
    """Decrypt a field value. Returns plaintext.
    Empty strings and non-encrypted values are returned as-is.
    """
    if not value or str(value).strip() == "":
        return ""
    s = str(value)
    if not s.startswith("gAAAAA"):
        return s
    try:
        return _get_fernet().decrypt(s.encode()).decode()
    except Exception:
        return s


def migrate_plaintext_to_encrypted():
    """One-time migration: encrypt existing plaintext credentials/system_key/credential_ref rows."""
    from sams.database import get_connection
    conn = get_connection()
    rows = conn.execute("SELECT id, credentials, system_key, credential_ref FROM servers").fetchall()
    updated = 0
    for row in rows:
        new_creds = encrypt_field(row["credentials"] or "")
        new_key = encrypt_field(row["system_key"] or "")
        new_ref = encrypt_field(row["credential_ref"] or "")
        if (new_creds != (row["credentials"] or "") or
            new_key != (row["system_key"] or "") or
            new_ref != (row["credential_ref"] or "")):
            conn.execute(
                "UPDATE servers SET credentials = ?, system_key = ?, credential_ref = ? WHERE id = ?",
                (new_creds, new_key, new_ref, row["id"]),
            )
            updated += 1
    if updated:
        conn.commit()
