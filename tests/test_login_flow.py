"""Test script to verify the login/setup flow works correctly."""

import sys
import shutil
from pathlib import Path
import io

# Add the repo root (parent of tests/) to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Set stdout to UTF-8 for proper Unicode support on Windows
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from core.encryption import create_password_hash, verify_password
from database.database import (
    init_db,
    has_verification_hash,
    save_verification_hash,
    get_verification_credentials,
    DB_PATH
)

def test_login_flow():
    """Test the complete login/setup flow."""

    # Clean up old database if it exists
    if DB_PATH.exists():
        DB_PATH.unlink()
        print(f"✓ Cleaned up old database: {DB_PATH}")

    # Step 1: Initialize database
    print("\n[STEP 1] Initialize database")
    init_db()
    print("✓ Database initialized")

    # Step 2: Check if this is first-time setup
    print("\n[STEP 2] Check if first-time setup")
    is_setup = not has_verification_hash()
    print(f"✓ Is first-time setup: {is_setup}")
    assert is_setup, "Should detect first-time setup"

    # Step 3: Simulate first-time setup - create password hash
    print("\n[STEP 3] First-time setup - create master password")
    master_password = "MySecurePassword123!"
    verification_salt, verification_hash = create_password_hash(master_password)
    print(f"✓ Created password hash")
    print(f"  - Salt length: {len(verification_salt)} bytes")
    print(f"  - Hash length: {len(verification_hash)} bytes")

    # Step 4: Save verification credentials
    print("\n[STEP 4] Save verification credentials to database")
    save_verification_hash(verification_salt, verification_hash)
    print("✓ Verification credentials saved")

    # Step 5: Verify we're no longer in setup mode
    print("\n[STEP 5] Verify we're no longer in setup mode")
    is_setup_after = not has_verification_hash()
    print(f"✓ Is first-time setup: {is_setup_after}")
    assert not is_setup_after, "Should detect that setup is complete"

    # Step 6: Retrieve credentials for login
    print("\n[STEP 6] Retrieve stored credentials")
    stored_salt, stored_hash = get_verification_credentials()
    print(f"✓ Retrieved credentials from database")
    print(f"  - Salt matches: {stored_salt == verification_salt}")
    print(f"  - Hash matches: {stored_hash == verification_hash}")
    assert stored_salt == verification_salt, "Salt should match"
    assert stored_hash == verification_hash, "Hash should match"

    # Step 7: Test login with correct password
    print("\n[STEP 7] Test login with CORRECT password")
    is_correct = verify_password(master_password, stored_salt, stored_hash)
    print(f"✓ Password verification result: {is_correct}")
    assert is_correct, "Correct password should verify successfully"

    # Step 8: Test login with wrong password
    print("\n[STEP 8] Test login with WRONG password")
    is_wrong = verify_password("WrongPassword123!", stored_salt, stored_hash)
    print(f"✓ Password verification result: {is_wrong}")
    assert not is_wrong, "Wrong password should not verify"

    # Step 9: Test edge cases
    print("\n[STEP 9] Test edge cases")

    # Empty password
    is_empty = verify_password("", stored_salt, stored_hash)
    print(f"✓ Empty password verification: {is_empty}")
    assert not is_empty, "Empty password should not verify"

    # Password with whitespace
    is_whitespace = verify_password("  MySecurePassword123!  ", stored_salt, stored_hash)
    print(f"✓ Password with whitespace verification: {is_whitespace}")
    assert not is_whitespace, "Password with extra whitespace should not verify"

    print("\n" + "="*60)
    print("✅ ALL TESTS PASSED!")
    print("="*60)
    print("\nSummary:")
    print("- Database initialization works")
    print("- First-time setup detection works")
    print("- Password hashing works")
    print("- Credential storage and retrieval works")
    print("- Correct password verification works")
    print("- Wrong password rejection works")
    print("- Edge cases handled correctly")


if __name__ == "__main__":
    try:
        test_login_flow()
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
