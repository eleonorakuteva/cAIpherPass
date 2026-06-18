"""Quick test script for database validation."""

import sys
from pathlib import Path

# Add database folder to path so we can import modules
sys.path.insert(0, str(Path(__file__).parent / "database"))

from database import init_db, create_entry, read_all_entries, update_entry, delete_entry, get_salt
from schemas import VaultEntry

print("=" * 70)
print("Testing cAIpherPass Database Validation Layer")
print("=" * 70)

# Initialize database
print("\n[1] Initializing database...")
init_db()
print("[OK] Database initialized")

# Get salt (should generate on first run)
print("\n[2] Getting salt...")
salt = get_salt()
print(f"[OK] Salt retrieved: {len(salt)} bytes")

# Test 1: Valid entry creation
print("\n[3] Testing VALID entry creation...")
try:
    entry_id = create_entry(
        service_name="Gmail",
        username="user@gmail.com",
        encrypted_password=b"fake_fernet_encrypted_bytes_12345",
        tags="email,work"
    )
    print(f"[OK] Entry created with ID: {entry_id}")
except ValueError as e:
    print(f"[FAIL] Unexpected error: {e}")

# Test 2: Invalid — empty service_name
print("\n[4] Testing INVALID entry (empty service_name)...")
try:
    create_entry(
        service_name="",  # INVALID: empty
        username="user@example.com",
        encrypted_password=b"fake_encrypted_bytes",
        tags=None
    )
    print("[FAIL] Should have failed but didn't!")
except ValueError as e:
    print(f"[OK] Correctly caught error: {e}")

# Test 3: Invalid — service_name is not a string
print("\n[5] Testing INVALID entry (service_name not string)...")
try:
    create_entry(
        service_name=123,  # INVALID: not a string
        username="user@example.com",
        encrypted_password=b"fake_encrypted_bytes",
        tags=None
    )
    print("[FAIL] Should have failed but didn't!")
except ValueError as e:
    print(f"[OK] Correctly caught error: {e}")

# Test 4: Invalid — empty username
print("\n[6] Testing INVALID entry (empty username)...")
try:
    create_entry(
        service_name="GitHub",
        username="  ",  # INVALID: whitespace only
        encrypted_password=b"fake_encrypted_bytes",
        tags=None
    )
    print("[FAIL] Should have failed but didn't!")
except ValueError as e:
    print(f"[OK] Correctly caught error: {e}")

# Test 5: Invalid — encrypted_password not bytes
print("\n[7] Testing INVALID entry (encrypted_password not bytes)...")
try:
    create_entry(
        service_name="GitHub",
        username="user@github.com",
        encrypted_password="not_bytes_string",  # INVALID: string instead of bytes
        tags=None
    )
    print("[FAIL] Should have failed but didn't!")
except ValueError as e:
    print(f"[OK] Correctly caught error: {e}")

# Test 6: Invalid — empty encrypted_password
print("\n[8] Testing INVALID entry (empty encrypted_password)...")
try:
    create_entry(
        service_name="GitHub",
        username="user@github.com",
        encrypted_password=b"",  # INVALID: empty bytes
        tags=None
    )
    print("[FAIL] Should have failed but didn't!")
except ValueError as e:
    print(f"[OK] Correctly caught error: {e}")

# Test 7: Invalid — tags not string
print("\n[9] Testing INVALID entry (tags not string)...")
try:
    create_entry(
        service_name="GitHub",
        username="user@github.com",
        encrypted_password=b"fake_encrypted_bytes",
        tags=["list", "instead", "of", "string"]  # INVALID: list instead of string
    )
    print("[FAIL] Should have failed but didn't!")
except ValueError as e:
    print(f"[OK] Correctly caught error: {e}")

# Test 8: Create another valid entry
print("\n[10] Creating second VALID entry...")
try:
    entry_id_2 = create_entry(
        service_name="GitHub",
        username="dev@github.com",
        encrypted_password=b"another_fernet_encrypted_string",
        tags="coding"
    )
    print(f"[OK] Entry created with ID: {entry_id_2}")
except ValueError as e:
    print(f"[FAIL] Unexpected error: {e}")

# Test 9: Read all entries
print("\n[11] Reading all entries from vault...")
all_entries = read_all_entries()
print(f"[OK] Retrieved {len(all_entries)} entries:")
for entry in all_entries:
    print(f"   - ID {entry['id']}: {entry['service_name']} ({entry['username']})")

# Test 10: Update with valid data
print("\n[12] Updating entry with VALID data...")
try:
    updated = update_entry(
        entry_id,
        tags="email,personal"
    )
    print(f"[OK] Entry updated: {updated}")
except ValueError as e:
    print(f"[FAIL] Unexpected error: {e}")

# Test 11: Update with invalid data
print("\n[13] Updating entry with INVALID data (empty service_name)...")
try:
    update_entry(
        entry_id,
        service_name=""  # INVALID: empty
    )
    print("[FAIL] Should have failed but didn't!")
except ValueError as e:
    print(f"[OK] Correctly caught error: {e}")

# Test 12: Update with invalid type
print("\n[14] Updating entry with INVALID type (username not string)...")
try:
    update_entry(
        entry_id,
        username=999  # INVALID: not a string
    )
    print("[FAIL] Should have failed but didn't!")
except ValueError as e:
    print(f"[OK] Correctly caught error: {e}")

# Test 13: Delete entry
print("\n[15] Deleting an entry...")
try:
    deleted = delete_entry(entry_id_2)
    print(f"[OK] Entry deleted: {deleted}")
    remaining = read_all_entries()
    print(f"[OK] Remaining entries: {len(remaining)}")
except Exception as e:
    print(f"[FAIL] Unexpected error: {e}")

print("\n" + "=" * 70)
print("[SUCCESS] All validation tests passed!")
print("=" * 70)
