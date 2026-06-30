"""Extract text from PDF / image / docx / txt. Uses Gemini Vision OCR for images
(only if a key is configured)."""
from __future__ import annotations

from pathlib import Path

from ..config import settings
from . import gemini


def extract(path: Path, mime: str) -> list[tuple[int, str]]:
    suffix = path.suffix.lower()
    if suffix == ".txt" or mime.startswith("text/"):
        return [(1, path.read_text(encoding="utf-8", errors="ignore"))]
    if suffix == ".docx":
        from docx import Document

        d = Document(str(path))
        return [(1, "\n".join(p.text for p in d.paragraphs))]
    if suffix == ".pdf" or mime == "application/pdf":
        from pypdf import PdfReader

        reader = PdfReader(str(path))
        pages: list[tuple[int, str]] = []
        for i, page in enumerate(reader.pages, start=1):
            try:
                pages.append((i, page.extract_text() or ""))
            except Exception:
                pages.append((i, ""))
        return pages
    if mime.startswith("image/"):
        if settings.has_key:
            data = path.read_bytes()
            return [(1, gemini.vision_ocr(data, mime))]
        return [(1, "")]
    return [(1, "")]