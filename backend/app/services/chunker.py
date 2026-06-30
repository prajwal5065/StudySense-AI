"""Simple recursive chunker. ~800 chars with 120 overlap; keeps page numbers."""
from __future__ import annotations


def chunk_pages(pages: list[tuple[int, str]], size: int = 800, overlap: int = 120) -> list[dict]:
    out: list[dict] = []
    for page_no, text in pages:
        text = (text or "").strip()
        if not text:
            continue
        i = 0
        while i < len(text):
            piece = text[i : i + size]
            out.append({"page_no": page_no, "section": None, "text": piece, "token_count": len(piece) // 4})
            if i + size >= len(text):
                break
            i += size - overlap
    return out


def count_tokens_approx(text: str) -> int:
    """Approximate token count: ~4 chars per token for English text."""
    return max(1, len(text) // 4)
