"""Encryption layer: derive a Fernet key from a master password using PBKDF2."""

import base64

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

# How many times PBKDF2 grinds the password. Higher = slower for everyone,
# but that slowness is the point: it cripples brute-force guessing.
ITERATIONS = 600_000


def derive_key(master_password, salt):
    """Turn a master password + salt into a Fernet-ready encryption key.

    This is one-way: you cannot get the password back from the key.
    """
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),  # the underlying hash PBKDF2 uses
        length=32,                  # produce a 32-byte (256-bit) key
        salt=salt,                  # the unique, public random value
        iterations=ITERATIONS,      # the deliberate "speed bump"
    )
    # The password is text; PBKDF2 works on raw bytes, so we encode it first.
    raw_key = kdf.derive(master_password.encode())

    # Fernet expects its key as url-safe base64 text, so wrap the raw bytes.
    return base64.urlsafe_b64encode(raw_key)


def encrypt_password(plaintext, key):
    """Encrypt a plaintext password with the derived key. Returns bytes."""
    fernet = Fernet(key)
    return fernet.encrypt(plaintext.encode())


def decrypt_password(token, key):
    """Decrypt an encrypted password (token) with the derived key. Returns text."""
    fernet = Fernet(key)
    return fernet.decrypt(token).decode()
