"""Input validation helpers for StudySense AI."""
from __future__ import annotations

import re

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt", ".png", ".jpg", ".jpeg", ".webp"}
MAX_FILE_SIZE_BYTES = 50 * 1024 * 1024  # 50 MB


def validate_filename(filename: str) -> str:
    """Return cleaned filename or raise ValueError for invalid names."""
    if not filename or len(filename.strip()) == 0:
        raise ValueError("Filename must not be empty.")
    ext = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError(
            f"File type '{ext}' is not supported. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
        )
    # Strip path separators to prevent directory traversal
    safe_name = re.sub(r"[/\\]", "_", filename)
    return safe_name


def validate_file_size(size_bytes: int) -> None:
    """Raise ValueError if file size exceeds the limit."""
    if size_bytes > MAX_FILE_SIZE_BYTES:
        limit_mb = MAX_FILE_SIZE_BYTES // (1024 * 1024)
        actual_mb = size_bytes / (1024 * 1024)
        raise ValueError(f"File too large ({actual_mb:.1f} MB). Max allowed: {limit_mb} MB.")
