"""SQLite database layer for cAIpherPass vault storage."""

import os
import sqlite3
from datetime import datetime
from pathlib import Path

from schemas import VaultEntry


# Database file location
DB_PATH = Path(__file__).parent.parent / "data" / "vault.db"


def init_db():
    """Initialize the database and create tables if they don't exist."""
    # Ensure data directory exists
    DB_PATH.parent.mkdir(exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Metadata table: stores global config (like salt)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS metadata (
            key TEXT PRIMARY KEY,
            value BLOB
        )
    """)

    # Vault table: stores encrypted passwords
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vault (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            service_name TEXT NOT NULL,
            username TEXT NOT NULL,
            encrypted_password BLOB NOT NULL,
            created_at TEXT NOT NULL,
            tags TEXT,
            UNIQUE(service_name, username)
        )
    """)

    conn.commit()
    conn.close()


def get_salt():
    """Retrieve the salt from metadata. If not found, generate and store it."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Try to fetch existing salt
    cursor.execute("SELECT value FROM metadata WHERE key = 'salt'")
    result = cursor.fetchone()

    if result:
        salt = result[0]
    else:
        # Generate a new salt and store it
        salt = os.urandom(16)  # 16 bytes of cryptographically random data
        cursor.execute(
            "INSERT INTO metadata (key, value) VALUES (?, ?)",
            ("salt", salt)
        )
        conn.commit()

    conn.close()
    return salt


def create_entry(service_name, username, encrypted_password, tags=None):
    """Insert a new encrypted password entry into the vault.

    Args:
        service_name: Name of the service (e.g., "Gmail")
        username: Username or email for this service
        encrypted_password: Already-encrypted password (bytes from Fernet)
        tags: Optional tags for searching (comma-separated string)

    Returns:
        The id of the newly created entry

    Raises:
        ValueError: If data does not match the VaultEntry schema
    """
    created_at = datetime.now().isoformat()

    # Validate against schema BEFORE any database operation
    VaultEntry.validate(service_name, username, encrypted_password, created_at, tags)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO vault (service_name, username, encrypted_password, created_at, tags)
        VALUES (?, ?, ?, ?, ?)
    """, (service_name, username, encrypted_password, created_at, tags))

    entry_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return entry_id


def read_entry(entry_id):
    """Fetch a single entry by id.

    Args:
        entry_id: The id of the vault entry

    Returns:
        A dict with keys: id, service_name, username, encrypted_password, created_at, tags
        Or None if not found
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Return rows as dicts
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM vault WHERE id = ?", (entry_id,))
    row = cursor.fetchone()
    conn.close()

    return dict(row) if row else None


def read_all_entries():
    """Fetch all entries from the vault.

    Returns:
        A list of dicts, each with keys: id, service_name, username, encrypted_password, created_at, tags
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM vault")
    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


def search_entries(query):
    """Search entries by service_name, username, or tags.

    Args:
        query: A search string (case-insensitive)

    Returns:
        A list of matching entries
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Search in service_name, username, and tags (case-insensitive)
    cursor.execute("""
        SELECT * FROM vault
        WHERE LOWER(service_name) LIKE ?
           OR LOWER(username) LIKE ?
           OR LOWER(tags) LIKE ?
    """, (f"%{query.lower()}%", f"%{query.lower()}%", f"%{query.lower()}%"))

    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


def update_entry(entry_id, service_name=None, username=None, encrypted_password=None, tags=None):
    """Update an existing vault entry.

    Only provided arguments are updated; None values are skipped.

    Args:
        entry_id: The id of the entry to update
        service_name: New service name (optional)
        username: New username (optional)
        encrypted_password: New encrypted password (optional)
        tags: New tags (optional)

    Returns:
        True if the entry was updated, False if entry not found

    Raises:
        ValueError: If any provided field does not match the VaultEntry schema
    """
    # Validate each field if provided — raise early before DB operation
    if service_name is not None:
        if not isinstance(service_name, str):
            raise ValueError("service_name must be a string")
        if not service_name.strip():
            raise ValueError("service_name cannot be empty")

    if username is not None:
        if not isinstance(username, str):
            raise ValueError("username must be a string")
        if not username.strip():
            raise ValueError("username cannot be empty")

    if encrypted_password is not None:
        if not isinstance(encrypted_password, bytes):
            raise ValueError("encrypted_password must be bytes")
        if len(encrypted_password) == 0:
            raise ValueError("encrypted_password cannot be empty")

    if tags is not None:
        if not isinstance(tags, str):
            raise ValueError("tags must be a string or None")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Build the UPDATE query dynamically based on what's provided
    updates = []
    values = []

    if service_name is not None:
        updates.append("service_name = ?")
        values.append(service_name)
    if username is not None:
        updates.append("username = ?")
        values.append(username)
    if encrypted_password is not None:
        updates.append("encrypted_password = ?")
        values.append(encrypted_password)
    if tags is not None:
        updates.append("tags = ?")
        values.append(tags)

    if not updates:
        # Nothing to update
        conn.close()
        return False

    values.append(entry_id)
    query = f"UPDATE vault SET {', '.join(updates)} WHERE id = ?"

    cursor.execute(query, values)
    conn.commit()

    # Check if any row was affected
    affected = cursor.rowcount > 0
    conn.close()

    return affected


def delete_entry(entry_id):
    """Delete an entry from the vault.

    Args:
        entry_id: The id of the entry to delete

    Returns:
        True if the entry was deleted, False if entry not found
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM vault WHERE id = ?", (entry_id,))
    conn.commit()

    affected = cursor.rowcount > 0
    conn.close()

    return affected
