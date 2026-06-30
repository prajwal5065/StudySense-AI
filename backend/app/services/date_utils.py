"""Date and time utility helpers for StudySense AI."""
from __future__ import annotations

from datetime import datetime, timezone


def utcnow() -> datetime:
    """Return current UTC datetime (timezone-aware)."""
    return datetime.now(tz=timezone.utc)


def utcnow_iso() -> str:
    """Return current UTC time as ISO 8601 string."""
    return utcnow().isoformat()


def days_until(target: datetime) -> int:
    """Return number of days from now until the target datetime."""
    delta = target - utcnow()
    return max(0, delta.days)


def format_duration_seconds(seconds: float) -> str:
    """Format a duration in seconds as a human-readable string."""
    if seconds < 60:
        return f"{seconds:.0f}s"
    if seconds < 3600:
        return f"{seconds / 60:.0f}m {seconds % 60:.0f}s"
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    return f"{hours}h {minutes}m"
