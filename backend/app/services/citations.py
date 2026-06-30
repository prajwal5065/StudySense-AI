"""Format retrieved chunks into citation objects the UI can render."""
from __future__ import annotations


def format_citations(hits: list[dict]) -> list[dict]:
    return [
        {
            "doc_id": h["doc_id"],
            "filename": h.get("filename"),
            "page": h.get("page"),
            "snippet": (h.get("text") or "")[:240],
            "score": h.get("score"),
        }
        for h in hits
    ]