"""Password generation using the cryptographically secure `secrets` module."""

import secrets
import string

# The "ingredient" pools the generator can draw characters from.
# `string` gives us these ready-made so we don't type out every letter.
LOWERCASE = string.ascii_lowercase   # "abcdefghijklmnopqrstuvwxyz"
UPPERCASE = string.ascii_uppercase   # "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
DIGITS = string.digits               # "0123456789"
SYMBOLS = "!@#$%^&*"                 # our chosen set of special characters


def generate_password(length=16, use_uppercase=True, use_digits=True, use_symbols=True):
    """Generate a secure password from the selected character types.

    Lowercase letters are always included as the base alphabet.
    """
    # Start with the bags the user actually wants.
    # `pools` is a list of strings; each string is one selected character group.
    pools = [LOWERCASE]
    if use_uppercase:
        pools.append(UPPERCASE)
    if use_digits:
        pools.append(DIGITS)
    if use_symbols:
        pools.append(SYMBOLS)

    # Validate the request before doing any work — fail loudly, not silently.
    if length < len(pools):
        raise ValueError(
            f"length must be at least {len(pools)} to fit one of each selected "
            f"character type (got {length})."
        )

    # Glue the selected bags into one big string to pick from.
    all_characters = "".join(pools)

    # Part 1 — guarantee: take one character from EACH selected bag,
    # so a requested type can never be missing by bad luck.
    password_chars = [secrets.choice(pool) for pool in pools]

    # Part 2 — fill the remaining slots from the full combined pool.
    while len(password_chars) < length:
        password_chars.append(secrets.choice(all_characters))

    # Part 3 — shuffle so the guaranteed characters aren't always at the front.
    # Secure Fisher-Yates shuffle using secrets (never random.shuffle).
    for i in range(len(password_chars) - 1, 0, -1):
        j = secrets.randbelow(i + 1)
        password_chars[i], password_chars[j] = password_chars[j], password_chars[i]

    # Join the list of characters into the final password string.
    return "".join(password_chars)


def _secure_shuffle(items):
    """Shuffle a list in place using `secrets` (secure Fisher-Yates)."""
    for i in range(len(items) - 1, 0, -1):
        j = secrets.randbelow(i + 1)
        items[i], items[j] = items[j], items[i]


def generate_password_with_counts(lowercase=0, uppercase=0, digits=0, symbols=0):
    """Generate a password with an exact count of each character type.

    Unlike `generate_password` (total length + on/off types), this builds the
    password from explicit per-type counts. The final length is the sum of all
    counts. Each count says how many characters of that type to include.
    """
    # Pair each character pool with how many characters we want from it.
    pool_counts = [
        (LOWERCASE, lowercase),
        (UPPERCASE, uppercase),
        (DIGITS, digits),
        (SYMBOLS, symbols),
    ]

    # Validate: counts can't be negative, and we need at least one character.
    if any(count < 0 for _, count in pool_counts):
        raise ValueError("character counts cannot be negative.")
    if sum(count for _, count in pool_counts) == 0:
        raise ValueError("select at least one character.")

    # Take exactly `count` characters from each requested pool.
    password_chars = []
    for pool, count in pool_counts:
        for _ in range(count):
            password_chars.append(secrets.choice(pool))

    # Shuffle so the types aren't grouped together (all lowercase first, etc.).
    _secure_shuffle(password_chars)

    return "".join(password_chars)
