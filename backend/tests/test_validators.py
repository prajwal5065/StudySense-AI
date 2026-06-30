"""Tests for StudySense AI input validators."""
import pytest
from app.services.validators import validate_filename, validate_file_size


def test_valid_pdf():
    result = validate_filename("lecture.pdf")
    assert result == "lecture.pdf"


def test_valid_docx():
    result = validate_filename("notes.docx")
    assert result == "notes.docx"


def test_invalid_extension_raises():
    with pytest.raises(ValueError, match="not supported"):
        validate_filename("script.exe")


def test_empty_filename_raises():
    with pytest.raises(ValueError, match="empty"):
        validate_filename("")


def test_path_traversal_sanitized():
    result = validate_filename("../../../etc/passwd.txt")
    assert "/" not in result and "\\" not in result


def test_file_size_ok():
    validate_file_size(1024 * 1024)  # 1 MB — should not raise


def test_file_size_too_large():
    with pytest.raises(ValueError, match="too large"):
        validate_file_size(100 * 1024 * 1024)  # 100 MB
