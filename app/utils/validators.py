"""
Reusable, framework-agnostic validation helpers.

These are plain functions with no Pydantic/FastAPI imports, so they can be
unit-tested in isolation and reused anywhere in the codebase -- not just
inside Pydantic schemas. `app/schemas.py` wires these into `field_validator`s;
this module is where the actual rules live.
"""

import re

USERNAME_REGEX = re.compile(r"^[a-zA-Z0-9_]+$")
USERNAME_MIN_LENGTH = 3
USERNAME_MAX_LENGTH = 50
PASSWORD_MIN_LENGTH = 8


def is_valid_username(username: str) -> bool:
    """True if `username` contains only letters, numbers, and underscores."""
    return bool(USERNAME_REGEX.match(username))


def validate_username(username: str) -> str:
    """Return `username` unchanged if valid, else raise ValueError."""
    if not is_valid_username(username):
        raise ValueError("Username may only contain letters, numbers, and underscores")
    return username


def is_strong_password(password: str) -> bool:
    """True if `password` contains at least one letter and one digit."""
    return bool(re.search(r"[A-Za-z]", password) and re.search(r"\d", password))


def validate_password_strength(password: str) -> str:
    """Return `password` unchanged if it meets the strength rules, else raise ValueError."""
    if not re.search(r"[A-Za-z]", password):
        raise ValueError("Password must contain at least one letter")
    if not re.search(r"\d", password):
        raise ValueError("Password must contain at least one digit")
    return password
