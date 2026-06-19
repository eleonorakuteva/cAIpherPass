"""Test the GUI login screen by simulating user interaction."""

import sys
from pathlib import Path
import io

# Set UTF-8 encoding for Windows
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

sys.path.insert(0, str(Path(__file__).parent.parent))

# Clean up old database for fresh test
from database.database import DB_PATH
if DB_PATH.exists():
    DB_PATH.unlink()

import customtkinter as ctk
from gui.app import LoginApp

def test_first_time_setup():
    """Test the first-time setup flow."""
    print("[TEST] First-Time Setup Flow")
    print("-" * 60)

    # Create the app (should detect first-time setup)
    app = LoginApp()

    # Verify it's in setup mode
    assert app.is_setup, "Should detect first-time setup"
    print("✓ App correctly detected first-time setup mode")

    # Verify setup UI elements exist
    assert hasattr(app, 'password_entry'), "Should have password_entry"
    assert hasattr(app, 'confirm_entry'), "Should have confirm_entry (setup mode)"
    assert app.confirm_entry is not None, "confirm_entry should not be None in setup mode"
    print("✓ Setup UI elements created correctly")

    # Simulate user input - fill in password fields
    password = "TestPassword123!"
    app.password_entry.insert(0, password)
    app.confirm_entry.insert(0, password)
    print(f"✓ Simulated user entering password: {len(password)} characters")

    # Verify input was captured
    assert app.password_entry.get() == password, "Password entry should contain the input"
    assert app.confirm_entry.get() == password, "Confirm entry should contain the input"
    print("✓ Password entries captured correctly")

    # Simulate clicking "Set Password" button
    print("✓ Simulating 'Set Password' button click...")
    app._handle_login()

    # Check that no error message appeared
    error_msg = app.error_label.cget("text")
    if error_msg:
        print(f"✗ Unexpected error: {error_msg}")
        raise AssertionError(f"Setup failed with error: {error_msg}")
    print("✓ Setup completed without errors")

    # Clean up
    try:
        app.root.destroy()
    except Exception:
        pass
    print("\n✅ First-Time Setup Test PASSED\n")


def test_login_flow():
    """Test the login flow on second launch."""
    print("[TEST] Login Flow")
    print("-" * 60)

    # Create new app (should detect existing verification hash)
    app = LoginApp()

    # Verify it's NOT in setup mode
    assert not app.is_setup, "Should NOT be in setup mode on second launch"
    print("✓ App correctly detected existing verification hash (login mode)")

    # Verify login UI elements exist
    assert hasattr(app, 'password_entry'), "Should have password_entry"
    assert app.confirm_entry is None, "confirm_entry should be None in login mode"
    print("✓ Login UI elements created correctly")

    # Simulate user input - enter correct password
    correct_password = "TestPassword123!"
    app.password_entry.insert(0, correct_password)
    print(f"✓ Simulated user entering password")

    # Simulate clicking "Login" button
    print("✓ Simulating 'Login' button click with correct password...")
    app._handle_login()

    # Check that no error message appeared
    error_msg = app.error_label.cget("text")
    if error_msg:
        print(f"✗ Unexpected error: {error_msg}")
        raise AssertionError(f"Login failed with error: {error_msg}")
    print("✓ Login succeeded with correct password")

    # Clean up
    try:
        app.root.destroy()
    except Exception:
        pass
    print("\n✅ Login Test PASSED\n")


def test_wrong_password():
    """Test rejection of wrong password."""
    print("[TEST] Wrong Password Rejection")
    print("-" * 60)

    # Create new app
    app = LoginApp()

    # Simulate user input - enter wrong password
    wrong_password = "WrongPassword123!"
    app.password_entry.insert(0, wrong_password)
    print(f"✓ Simulated user entering wrong password")

    # Simulate clicking "Login" button
    print("✓ Simulating 'Login' button click with wrong password...")
    app._handle_login()

    # Check that error message appeared
    error_msg = app.error_label.cget("text")
    assert error_msg, "Should show error message for wrong password"
    assert "Incorrect password" in error_msg, f"Error message should mention incorrect password, got: {error_msg}"
    print(f"✓ Correctly rejected wrong password with message: '{error_msg}'")

    # Password entry should be cleared
    assert app.password_entry.get() == "", "Password entry should be cleared after wrong password"
    print("✓ Password entry cleared after rejection")

    # Clean up
    app.root.destroy()
    print("\n✅ Wrong Password Test PASSED\n")


if __name__ == "__main__":
    try:
        print("\n" + "="*60)
        print("CAIPHERPASS GUI TEST SUITE")
        print("="*60 + "\n")

        test_first_time_setup()
        test_login_flow()
        test_wrong_password()

        print("="*60)
        print("✅ ALL GUI TESTS PASSED!")
        print("="*60)

    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
