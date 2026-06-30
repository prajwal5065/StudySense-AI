"""Text cleaning utilities for StudySense AI document processing."""
from __future__ import annotations

import re
import unicodedata


def normalize_whitespace(text: str) -> str:
    """Collapse multiple spaces/newlines into a single space."""
    text = unicodedata.normalize("NFKC", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def remove_control_chars(text: str) -> str:
    """Remove non-printable control characters, keeping newlines and tabs."""
    return "".join(
        c for c in text if unicodedata.category(c) != "Cc" or c in "\n\t"
    )


def clean_document_text(text: str) -> str:
    """Full cleaning pipeline: remove control chars then normalize whitespace."""
    text = remove_control_chars(text)
    return normalize_whitespace(text)
