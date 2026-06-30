"""Tests for StudySense AI backend configuration."""
import pytest
from app.config import Settings


def test_default_max_workers():
    s = Settings(gemini_api_key="")
    assert s.max_workers == 4


def test_default_log_level():
    s = Settings(gemini_api_key="")
    assert s.log_level == "INFO"


def test_has_key_false_when_empty():
    s = Settings(gemini_api_key="")
    assert s.has_key is False


def test_has_key_true_when_set():
    s = Settings(gemini_api_key="test-key-123")
    assert s.has_key is True


def test_cors_list_split():
    s = Settings(gemini_api_key="", cors_origins="http://a.com,http://b.com")
    assert s.cors_list == ["http://a.com", "http://b.com"]
