"""
Small, general-purpose helper functions used across the app.
"""

import uuid
from datetime import datetime, timezone


def generate_request_id() -> str:
    """Return a short, unique id used to correlate log lines for a single request."""
    return uuid.uuid4().hex


def utcnow() -> datetime:
    """Timezone-aware 'now', in UTC -- prefer this over `datetime.utcnow()`."""
    return datetime.now(timezone.utc)


def mask_email(email: str) -> str:
    """
    Partially obscure an email address, for safely logging identifying
    information without writing full PII to log files, e.g.:

        mask_email("johndoe@example.com") -> "jo*****@example.com"
    """
    try:
        local, domain = email.split("@", 1)
    except ValueError:
        return "***"
    visible = local[:2]
    return f"{visible}{'*' * max(len(local) - 2, 3)}@{domain}"
