"""Main GUI application for cAIpherPass — login screen and vault interface."""

import sqlite3
import sys
from pathlib import Path

import customtkinter as ctk

# Add parent directory to path so we can import core and database
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.encryption import (
    create_password_hash, verify_password, derive_key, encrypt_password
)
from core.generator import generate_password, generate_password_with_counts
from database.database import (
    init_db, has_verification_hash, save_verification_hash,
    get_verification_credentials, get_salt, create_entry
)


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
        print(f"✅ Login successful!")

        # Destroy the login window
        try:
            self.root.destroy()
        except Exception:
            pass

        # Launch the main app with the master password
        main_app = MainApp(master_password)
        main_app.run()

    def run(self):
        """Start the GUI event loop."""
        self.root.mainloop()


class MainApp:
    """Main vault interface with tabs for Generate, View, and Search."""

    def __init__(self, master_password):
        """Initialize the main app with the master password."""
        self.master_password = master_password
        self.root = ctk.CTk()
        self.root.title("cAIpherPass — Vault")
        self.root.geometry("800x630")
        self.root.resizable(True, True)
        # Minimum size keeps all content (incl. the Generate button) visible —
        # the window can't be shrunk small enough to clip it.
        self.root.minsize(800, 650)

        # Set up the UI
        self._setup_ui()

    def _setup_ui(self):
        """Build the main app UI with tabs."""
        # Create tabview for the three tabs
        tabview = ctk.CTkTabview(self.root, fg_color="transparent")
        tabview.pack(fill="both", expand=True, padx=20, pady=20)

        # Add three tabs
        tabview.add("Generate Password")
        tabview.add("View Saved Entries")
        tabview.add("Search")

        # Set up the Generate Password tab
        self._setup_generate_tab(tabview.tab("Generate Password"))

        # Set up placeholder tabs
        self._setup_view_tab(tabview.tab("View Saved Entries"))
        self._setup_search_tab(tabview.tab("Search"))

    def _setup_generate_tab(self, tab):
        """Build the Generate Password tab.

        Layout is two columns:
          - LEFT: the generated password (normal single-line field) + copy button.
          - RIGHT: one slider per character type (each picks HOW MANY of that type),
            a derived total-length readout, and the Generate button beneath them.
        """
        # Create container for better layout
        container = ctk.CTkFrame(tab, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=20)

        # Title
        title = ctk.CTkLabel(
            container,
            text="Generate Password",
            font=("Helvetica", 18, "bold"),
            text_color="#ffffff"
        )
        title.pack(pady=(0, 20), anchor="center")

        # Two-column grid layout
        grid_frame = ctk.CTkFrame(container, fg_color="transparent")
        grid_frame.pack(fill="both", expand=True, pady=10)

        # LEFT COLUMN: new-entry form (service, username, password, tags) + save
        left_frame = ctk.CTkFrame(grid_frame, fg_color="transparent")
        left_frame.pack(side="left", fill="x", expand=True, padx=(0, 15), anchor="n")

        # Service name
        service_label = ctk.CTkLabel(
            left_frame, text="Service", font=("Helvetica", 12), text_color="#cccccc"
        )
        service_label.pack(anchor="w", pady=(0, 2))
        self.service_entry = ctk.CTkEntry(
            left_frame,
            placeholder_text="e.g. Facebook",
            font=("Helvetica", 14),
            height=40,
        )
        self.service_entry.pack(fill="x", pady=(0, 10))

        # Username / email
        username_label = ctk.CTkLabel(
            left_frame, text="Username / Email", font=("Helvetica", 12), text_color="#cccccc"
        )
        username_label.pack(anchor="w", pady=(0, 2))
        self.username_entry = ctk.CTkEntry(
            left_frame,
            placeholder_text="e.g. me@gmail.com",
            font=("Helvetica", 14),
            height=40,
        )
        self.username_entry.pack(fill="x", pady=(0, 10))

        # Password — editable: generated here, or paste an existing one.
        password_label = ctk.CTkLabel(
            left_frame, text="Password", font=("Helvetica", 12), text_color="#cccccc"
        )
        password_label.pack(anchor="w", pady=(0, 2))

        password_row = ctk.CTkFrame(left_frame, fg_color="transparent")
        password_row.pack(fill="x", pady=(0, 10))

        self.password_display = ctk.CTkEntry(
            password_row,
            placeholder_text="Generate or type a password",
            font=("Helvetica", 14),
            height=45,
        )
        self.password_display.pack(side="left", fill="x", expand=True)

        self.copy_button = ctk.CTkButton(
            password_row,
            text="Copy",
            command=self._copy_password,
            font=("Helvetica", 12),
            width=70,
            height=45,
            fg_color="#2196F3",
            hover_color="#0b7dda"
        )
        self.copy_button.pack(side="left", padx=(8, 0))

        # Tags (optional)
        tags_label = ctk.CTkLabel(
            left_frame, text="Tags (optional)", font=("Helvetica", 12), text_color="#cccccc"
        )
        tags_label.pack(anchor="w", pady=(0, 2))
        self.tags_entry = ctk.CTkEntry(
            left_frame,
            placeholder_text="e.g. work, social",
            font=("Helvetica", 14),
            height=40,
        )
        self.tags_entry.pack(fill="x", pady=(0, 10))

        # Save button — encrypts the password and stores the entry in the vault.
        self.save_button = ctk.CTkButton(
            left_frame,
            text="Save to Vault",
            command=self._save_entry,
            font=("Helvetica", 14, "bold"),
            height=40,
            fg_color="#4CAF50",
            hover_color="#45a049"
        )
        self.save_button.pack(fill="x", pady=(5, 5))

        # Inline status message (success or error), hidden until we save.
        self.save_status = ctk.CTkLabel(
            left_frame, text="", font=("Helvetica", 12)
        )
        self.save_status.pack(anchor="w")

        # RIGHT COLUMN: per-type length sliders + total + generate button
        right_frame = ctk.CTkFrame(grid_frame, fg_color="transparent")
        right_frame.pack(side="left", fill="both", expand=True, padx=(15, 0))

        options_label = ctk.CTkLabel(
            right_frame,
            text="Characters per type:",
            font=("Helvetica", 12),
            text_color="#cccccc"
        )
        options_label.pack(anchor="w", pady=(0, 10))

        # Build one count slider per character type. Each returns its slider so
        # we can read the value later. Defaults sum to 16 (8+4+2+2).
        # Lowercase has a minimum of 1 so the total length is never zero.
        self.lowercase_slider = self._make_count_slider(right_frame, "Lowercase (a-z)", 8, minimum=1)
        self.uppercase_slider = self._make_count_slider(right_frame, "Uppercase (A-Z)", 4)
        self.digits_slider = self._make_count_slider(right_frame, "Digits (0-9)", 2)
        self.symbols_slider = self._make_count_slider(right_frame, "Symbols (!@#$%^&*)", 2)

        # Derived total length (sum of the four sliders), updated live.
        self.total_label = ctk.CTkLabel(
            right_frame,
            text="Total length: 16",
            font=("Helvetica", 12, "bold"),
            text_color="#4CAF50"
        )
        self.total_label.pack(anchor="w", pady=(10, 10))

        # Generate button — lives in the right column, below the sliders.
        self.generate_button = ctk.CTkButton(
            right_frame,
            text="Generate Password",
            command=self._generate_password,
            font=("Helvetica", 14, "bold"),
            height=40,
            fg_color="#4CAF50",
            hover_color="#45a049"
        )
        self.generate_button.pack(fill="x", pady=(5, 0))

        # Show the initial total now that all sliders exist.
        self._update_total_label()

    def _make_count_slider(self, parent, text, default, minimum=0):
        """Create a labelled count slider (minimum..20) and return the widget.

        Each row shows the type name on the left and its current count on the
        right, with the slider beneath. The count label updates as you drag.
        `minimum` sets the lowest selectable count (e.g. 1 to force lowercase).
        """
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", pady=8)

        header = ctk.CTkFrame(frame, fg_color="transparent")
        header.pack(fill="x")

        name_label = ctk.CTkLabel(
            header,
            text=text,
            font=("Helvetica", 11),
            text_color="#cccccc"
        )
        name_label.pack(side="left")

        value_label = ctk.CTkLabel(
            header,
            text=str(default),
            font=("Helvetica", 11, "bold"),
            text_color="#4CAF50",
            width=30
        )
        value_label.pack(side="right")

        slider = ctk.CTkSlider(
            frame,
            from_=minimum,
            to=20,
            number_of_steps=20 - minimum,
        )
        slider.set(default)
        # Update this row's number and the running total whenever it moves.
        slider.configure(command=lambda v, lbl=value_label: self._on_count_change(v, lbl))
        slider.pack(fill="x", pady=(5, 0))

        return slider

    def _setup_view_tab(self, tab):
        """Placeholder for View Saved Entries tab."""
        label = ctk.CTkLabel(
            tab,
            text="View Saved Entries\n\n(Coming soon)",
            font=("Helvetica", 16),
            text_color="#cccccc"
        )
        label.pack(expand=True, anchor="center")

    def _setup_search_tab(self, tab):
        """Placeholder for Search tab."""
        label = ctk.CTkLabel(
            tab,
            text="Search\n\n(Coming soon)",
            font=("Helvetica", 16),
            text_color="#cccccc"
        )
        label.pack(expand=True, anchor="center")

    def _on_count_change(self, value, value_label):
        """Update one slider's count label, then refresh the running total."""
        value_label.configure(text=str(int(float(value))))
        self._update_total_label()

    def _update_total_label(self):
        """Recompute and show the total length (sum of all four sliders)."""
        total = (
            int(self.lowercase_slider.get())
            + int(self.uppercase_slider.get())
            + int(self.digits_slider.get())
            + int(self.symbols_slider.get())
        )
        self.total_label.configure(text=f"Total length: {total}")

    def _set_password_text(self, text):
        """Replace the contents of the (editable) password field."""
        self.password_display.delete(0, "end")
        self.password_display.insert(0, text)

    def _show_save_status(self, text, error=False):
        """Show an inline save message — red for errors, green for success."""
        self.save_status.configure(
            text=text, text_color="#ff6b6b" if error else "#4CAF50"
        )

    def _save_entry(self):
        """Encrypt the password and save the entry (service, username, tags) to the vault."""
        service = self.service_entry.get().strip()
        username = self.username_entry.get().strip()
        password = self.password_display.get()
        tags = self.tags_entry.get().strip()

        # Validate required fields before doing any crypto/DB work.
        if not service:
            self._show_save_status("Service is required", error=True)
            return
        if not username:
            self._show_save_status("Username is required", error=True)
            return
        if not password or password.startswith("Error"):
            self._show_save_status("Generate or enter a password first", error=True)
            return

        try:
            # Encrypt with a key derived from the master password — only the
            # ciphertext is ever stored. Tags are optional (None when blank).
            key = derive_key(self.master_password, get_salt())
            encrypted = encrypt_password(password, key)
            create_entry(service, username, encrypted, tags or None)

            self._show_save_status(f"Saved '{service}' ✓", error=False)

            # Clear the form so the next entry starts fresh.
            self.service_entry.delete(0, "end")
            self.username_entry.delete(0, "end")
            self.tags_entry.delete(0, "end")
            self._set_password_text("")
        except sqlite3.IntegrityError:
            # UNIQUE(service_name, username) was violated.
            self._show_save_status(
                "An entry for that service & username already exists", error=True
            )
        except Exception as e:
            self._show_save_status(f"Save failed: {str(e)}", error=True)

    def _generate_password(self):
        """Generate a password from the per-type count sliders."""
        try:
            password = generate_password_with_counts(
                lowercase=int(self.lowercase_slider.get()),
                uppercase=int(self.uppercase_slider.get()),
                digits=int(self.digits_slider.get()),
                symbols=int(self.symbols_slider.get()),
            )
            self._set_password_text(password)
        except Exception as e:
            self._set_password_text(f"Error: {str(e)}")

    def _copy_password(self):
        """Copy the generated password to clipboard."""
        password = self.password_display.get()
        if password and not password.startswith("Error"):
            self.root.clipboard_clear()
            self.root.clipboard_append(password)
            # Provide visual feedback
            original_text = self.copy_button.cget("text")
            self.copy_button.configure(text="Copied! ✓")
            self.root.after(2000, lambda: self.copy_button.configure(text=original_text))

    def run(self):
        """Start the GUI event loop."""
        self.root.mainloop()


def main():
    """Entry point for the cAIpherPass GUI."""
    app = LoginApp()
    app.run()


if __name__ == "__main__":
    main()
