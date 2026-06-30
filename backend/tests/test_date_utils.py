"""Tests for StudySense AI date utilities."""
from datetime import datetime, timezone, timedelta
from app.services.date_utils import utcnow, utcnow_iso, days_until, format_duration_seconds


def test_utcnow_is_aware():
    dt = utcnow()
    assert dt.tzinfo is not None


def test_utcnow_iso_is_string():
    s = utcnow_iso()
    assert isinstance(s, str)
    assert "T" in s


def test_days_until_future():
    future = utcnow() + timedelta(days=5)
    assert days_until(future) == 5


def test_days_until_past():
    past = utcnow() - timedelta(days=3)
    assert days_until(past) == 0


def test_format_duration_seconds():
    assert format_duration_seconds(30) == "30s"
    assert format_duration_seconds(90) == "1m 30s"
    assert format_duration_seconds(3661) == "1h 1m"
