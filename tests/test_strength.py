"""Quick test script for the rule-based password-strength scorer."""

import sys
from pathlib import Path

# Add the repo root (parent of tests/) to path so we can import the ai package.
sys.path.insert(0, str(Path(__file__).parent.parent))

from ai.strength import score_password, calculate_entropy

print("=" * 70)
print("Testing cAIpherPass Password-Strength Scorer (Phase 1, rule-based)")
print("=" * 70)

# Running tally so we can print a summary at the end.
passed = 0
failed = 0


def check_label(password, expected, note=""):
    """Assert score_password(password) returns the expected label."""
    global passed, failed
    result = score_password(password)
    actual = result["label"]
    ok = actual == expected
    mark = "[OK]" if ok else "[FAIL]"
    if ok:
        passed += 1
    else:
        failed += 1
    print(f"{mark} {password!r:24} expected {expected:7} got {actual:7} "
          f"({result['entropy']:.1f} bits)  {note}")


print("\n[1] Edge cases")
check_label("", "Weak", "empty password")

print("\n[2] Too-short penalty (caps at Weak)")
check_label("abc", "Weak", "3 chars")
check_label("Ab1!", "Weak", "varied but only 4 chars")

print("\n[3] Single-type penalty (caps at Medium, never raises)")
# Regression: 'password' is 8 lowercase chars (37.6 bits). The single-type cap
# must NOT raise it from Weak to Medium — this is the bug we fixed.
check_label("password", "Weak", "low entropy + single type stays Weak")
# 13 lowercase chars = 61 bits (Strong on entropy alone); cap pulls it to Medium.
check_label("aaaaaaaaaaaaa", "Medium", "long but single type -> capped")

print("\n[4] Normal entropy-based grading")
check_label("Sunshine22", "Medium", "mixed, ~59 bits")
check_label("K9#mQ2$vL7@pX4!w", "Strong", "16 chars, all types")

print("\n[5] calculate_entropy sanity checks")
# Empty -> 0 bits, and a known value: 8 lowercase chars = 8 * log2(26) ~= 37.6.
for pw, low, high in [("", -0.1, 0.1), ("password", 37.0, 38.0)]:
    e = calculate_entropy(pw)
    ok = low <= e <= high
    mark = "[OK]" if ok else "[FAIL]"
    if ok:
        passed += 1
    else:
        failed += 1
    print(f"{mark} entropy({pw!r}) = {e:.1f} (expected {low}..{high})")

print("\n" + "=" * 70)
print(f"Summary: {passed} passed, {failed} failed")
print("=" * 70)

# Non-zero exit code on failure so CI / the shell can detect it.
sys.exit(1 if failed else 0)
