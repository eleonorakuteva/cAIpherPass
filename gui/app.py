"""Main GUI application for cAIpherPass — login screen and vault interface."""

import sys
from pathlib import Path

import customtkinter as ctk

# Add parent directory to path so we can import core and database
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.encryption import create_password_hash, verify_password
from database.database import init_db, has_verification_hash, save_verification_hash, get_verification_credentials


class LoginApp:
    """Login/setup screen for cAIpherPass.

    On first launch: asks user to set a master password (with confirmation).
    On subsequent launches: asks user to enter the master password.
    """

    def __init__(self):
        """Initialize the login app and set up the window."""
        self.root = ctk.CTk()
        self.root.title("cAIpherPass — Master Password")
        self.root.geometry("400x380")
        self.root.resizable(True, True)
        self.root.minsize(400, 350)  # Prevent window from being resized too small

        # Initialize database
        init_db()

        # Check if this is first-time setup
        self.is_setup = not has_verification_hash()

        # Set up the UI
        self._setup_ui()

    def _setup_ui(self):
        """Build the login/setup screen UI."""
        # Create a main container frame for all elements, centered in the window
        container = ctk.CTkFrame(self.root, fg_color="transparent")
        container.pack(expand=True, anchor="center", padx=40)

        # Title label
        title = ctk.CTkLabel(
            container,
            text="Set Master Password" if self.is_setup else "Master Password",
            font=("Helvetica", 20, "bold"),
            text_color="#ffffff"
        )
        title.pack(pady=(0, 10), anchor="center")

        # Subtitle
        subtitle_text = (
            "Create a strong password to encrypt your vault"
            if self.is_setup
            else "Enter your master password to login"
        )
        subtitle = ctk.CTkLabel(
            container,
            text=subtitle_text,
            font=("Helvetica", 12),
            text_color="#cccccc"
        )
        subtitle.pack(pady=(0, 30), anchor="center")

        # Password input (consistent styling for both setup and login)
        self.password_entry = ctk.CTkEntry(
            container,
            placeholder_text="Master Password",
            show="•",  # Mask the password
            font=("Helvetica", 14),
            height=40,
            width=300
        )
        self.password_entry.pack(pady=10, fill="x", expand=True)

        # Confirm password input (only on setup)
        if self.is_setup:
            self.confirm_entry = ctk.CTkEntry(
                container,
                placeholder_text="Confirm Password",
                show="•",
                font=("Helvetica", 14),
                height=40,
                width=300
            )
            self.confirm_entry.pack(pady=10, fill="x", expand=True)
        else:
            self.confirm_entry = None

        # Error message label (hidden by default)
        self.error_label = ctk.CTkLabel(
            container,
            text="",
            font=("Helvetica", 12),
            text_color="#ff6b6b"
        )
        self.error_label.pack(pady=2, anchor="center")

        # Login/Setup button
        button_text = "Set Password" if self.is_setup else "Login"
        self.login_button = ctk.CTkButton(
            container,
            text=button_text,
            command=self._handle_login,
            font=("Helvetica", 14, "bold"),
            height=40,
            fg_color="#4CAF50",
            hover_color="#45a049"
        )
        self.login_button.pack(pady=5, fill="x")

        # Bind Enter key to login
        self.password_entry.bind("<Return>", lambda e: self._handle_login())
        if self.confirm_entry:
            self.confirm_entry.bind("<Return>", lambda e: self._handle_login())

    def _handle_login(self):
        """Process login or setup based on the current mode."""
        password = self.password_entry.get()

        if self.is_setup:
            self._handle_setup(password)
        else:
            self._handle_verify(password)

    def _handle_setup(self, password):
        """Handle first-time setup: validate and store the master password."""
        confirm = self.confirm_entry.get()

        # Validate passwords match
        if password != confirm:
            self.error_label.configure(text="Passwords do not match")
            return

        # Validate password is not empty
        if not password.strip():
            self.error_label.configure(text="Password cannot be empty")
            return

        # Validate password is strong enough (at least 8 characters)
        if len(password) < 8:
            self.error_label.configure(text="Password must be at least 8 characters")
            return

        try:
            # Create and store the verification hash
            verification_salt, verification_hash = create_password_hash(password)
            save_verification_hash(verification_salt, verification_hash)

            # Success — proceed to main app
            self._login_success(password)
        except Exception as e:
            self.error_label.configure(text=f"Setup failed: {str(e)}")

    def _handle_verify(self, password):
        """Handle login: verify the entered password against the stored hash."""
        if not password.strip():
            self.error_label.configure(text="Password cannot be empty")
            return

        try:
            # Retrieve stored credentials
            verification_salt, verification_hash = get_verification_credentials()

            # Verify password
            if verify_password(password, verification_salt, verification_hash):
                self._login_success(password)
            else:
                self.error_label.configure(text="Incorrect password")
                self.password_entry.delete(0, "end")
        except Exception as e:
            self.error_label.configure(text=f"Login failed: {str(e)}")

    def _login_success(self, master_password):
        """Called after successful login/setup. Proceed to main app."""
        # Store the master password for use by the main app
        self.master_password = master_password

        # For now, just show a success message
        # In the next step, we'll show the main vault UI
        print(f"✅ Login successful! Master password: {master_password}")
        print("(This is a placeholder — main UI will be built next)")

        # Destroy the login window (placeholder for now)
        try:
            self.root.destroy()
        except Exception:
            # Window may already be destroyed in tests
            pass

    def run(self):
        """Start the GUI event loop."""
        self.root.mainloop()


def main():
    """Entry point for the cAIpherPass GUI."""
    app = LoginApp()
    app.run()


if __name__ == "__main__":
    main()
