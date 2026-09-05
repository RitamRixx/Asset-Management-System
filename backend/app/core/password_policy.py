"""
Password strength policy (IAM Phase 9).

Kept as pure functions with no DB/request dependency so both the reset
flow (Phase 4) and account creation/change-password can call the same
check and never drift apart. Deliberately rule-based rather than an
entropy score — easier for users to understand *why* a password was
rejected, and easier for us to unit test exhaustively.
"""
import re

MIN_LENGTH = 10

_UPPER = re.compile(r"[A-Z]")
_LOWER = re.compile(r"[a-z]")
_DIGIT = re.compile(r"\d")
_SPECIAL = re.compile(r"[^\w\s]")

# Deliberately small and boring — the point isn't to catch every leaked
# password on earth (that's what a breach-list API is for, out of scope
# here), just to block the handful of things people type first.
_COMMON_PASSWORDS = {
    "password", "password1", "password123", "12345678", "123456789",
    "qwerty123", "letmein", "welcome1", "changeme", "changeme123",
    "admin123", "iloveyou", "monkey123",
}


def validate_password_strength(password: str) -> list[str]:
    """Returns a list of human-readable violations. Empty list = valid.
    Returns *all* violations at once rather than the first one, so the
    user isn't stuck fixing one problem per submit."""
    errors: list[str] = []

    if len(password) < MIN_LENGTH:
        errors.append(f"Password must be at least {MIN_LENGTH} characters long.")
    if not _UPPER.search(password):
        errors.append("Password must contain at least one uppercase letter.")
    if not _LOWER.search(password):
        errors.append("Password must contain at least one lowercase letter.")
    if not _DIGIT.search(password):
        errors.append("Password must contain at least one digit.")
    if not _SPECIAL.search(password):
        errors.append("Password must contain at least one special character.")
    if password.lower() in _COMMON_PASSWORDS:
        errors.append("This password is too common. Choose something less predictable.")

    return errors