"""Phase 1 password-strength scorer — rule-based, no machine learning.

We estimate how hard a password is to guess using *entropy* (bits), then apply
a couple of common-sense penalties and map the result to a Weak / Medium / Strong
label. All the "intelligence" here is hand-written rules based on established
security guidance — no model, no training, no network. This becomes the baseline
(and the feature extractor) for the Phase 2 scikit-learn classifier.
"""

import math
import string

# Size each character category contributes to the guessing pool.
# These are just the counts of each Python string constant:
#   lowercase a-z = 26, uppercase A-Z = 26, digits 0-9 = 10, punctuation ≈ 32.
LOWERCASE_POOL = len(string.ascii_lowercase)   # 26
UPPERCASE_POOL = len(string.ascii_uppercase)   # 26
DIGITS_POOL = len(string.digits)               # 10
SYMBOLS_POOL = len(string.punctuation)         # 32

# Minimum length below which a password is always Weak, no matter how varied.
MIN_LENGTH = 8

# Entropy (in bits) cut-offs that separate the three labels.
# Drawn from common security guidance: <40 weak, 40-60 medium, 60+ strong.
MEDIUM_THRESHOLD = 40
STRONG_THRESHOLD = 60

# Labels ordered weakest → strongest. The index gives each label a rank, which
# lets a penalty "cap" a score: we take the weaker of two labels, so a penalty
# can only ever lower a result — never raise it.
LABELS = ("Weak", "Medium", "Strong")


def _character_pool(password):
    """Return the size of the character pool the password draws from.

    We add a category's size only if the password actually uses a character
    from it. A bigger pool means each character could be one of more options,
    which makes the password exponentially harder to brute-force.
    """
    pool = 0
    if any(c in string.ascii_lowercase for c in password):
        pool += LOWERCASE_POOL
    if any(c in string.ascii_uppercase for c in password):
        pool += UPPERCASE_POOL
    if any(c in string.digits for c in password):
        pool += DIGITS_POOL
    if any(c in string.punctuation for c in password):
        pool += SYMBOLS_POOL
    return pool


def _count_character_types(password):
    """Count how many of the four categories the password uses (0-4).

    Used by the single-type penalty: a password drawing from only one category
    (e.g. all lowercase) is weak even if it's long.
    """
    types = 0
    if any(c in string.ascii_lowercase for c in password):
        types += 1
    if any(c in string.ascii_uppercase for c in password):
        types += 1
    if any(c in string.digits for c in password):
        types += 1
    if any(c in string.punctuation for c in password):
        types += 1
    return types


def calculate_entropy(password):
    """Estimate password entropy in bits: length × log2(pool_size).

    Entropy is the number of bits an attacker must guess. Each extra bit
    doubles the work. log2(pool) is the bits contributed by ONE character;
    multiplying by length gives the total for the whole password.
    """
    pool = _character_pool(password)
    if pool == 0:          # empty password — no characters, no entropy.
        return 0.0
    return len(password) * math.log2(pool)


def _weaker(label_a, label_b):
    """Return whichever of two labels is weaker (lower rank in LABELS).

    This is how a penalty "caps" a score: weaker(current, cap) can only keep
    the label the same or lower it — it can never raise it.
    """
    return LABELS[min(LABELS.index(label_a), LABELS.index(label_b))]


def _entropy_label(entropy):
    """Map raw entropy (bits) to a label using the threshold constants."""
    if entropy < MEDIUM_THRESHOLD:
        return "Weak"
    if entropy < STRONG_THRESHOLD:
        return "Medium"
    return "Strong"


def score_password(password):
    """Score a password and return {label, entropy, reason}.

    label   — "Weak" / "Medium" / "Strong" (drives the GUI badge colour)
    entropy — the estimated bits (handy for debugging and as a Phase-2 feature)
    reason  — a short human hint about the verdict
    """
    # Edge case: nothing typed yet.
    if not password:
        return {"label": "Weak", "entropy": 0.0, "reason": "Empty password"}

    entropy = calculate_entropy(password)

    # 1. Start from what the entropy alone suggests.
    label = _entropy_label(entropy)
    if label == "Strong":
        reason = "Strong password"
    elif label == "Medium":
        reason = "Decent — add length or symbols to reach Strong"
    else:
        reason = "Low entropy — make it longer or more varied"

    # 2. Apply penalties as CAPS — they can only lower the label, never raise it.
    # Penalty 1 — too short: brute-forceable no matter how varied, so cap at Weak.
    if len(password) < MIN_LENGTH:
        label = _weaker(label, "Weak")
        reason = f"Too short — use at least {MIN_LENGTH} characters"
    # Penalty 2 — only one character type (all lowercase, all digits, ...): cap
    # at Medium. We only overwrite the hint if this cap actually lowered the label.
    elif _count_character_types(password) == 1:
        capped = _weaker(label, "Medium")
        if capped != label:
            reason = "Mix in uppercase, digits, or symbols to strengthen"
        label = capped

    return {"label": label, "entropy": entropy, "reason": reason}
