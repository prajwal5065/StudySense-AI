"""Cheap grounding check: lexical overlap of answer sentences vs retrieved chunks."""
from __future__ import annotations

import re


def _sentences(s: str) -> list[str]:
    return [x.strip() for x in re.split(r"(?<=[.!?])\s+", s or "") if x.strip()]


def grounding_score(answer: str, hits: list[dict]) -> float:
    sents = _sentences(answer)
    if not sents or not hits:
        return 0.0
    corpus = " ".join((h.get("text") or "").lower() for h in hits)
    grounded = 0
    for s in sents:
        words = [w for w in re.findall(r"\w+", s.lower()) if len(w) > 4]
        if not words:
            continue
        hit = sum(1 for w in words if w in corpus)
        if hit / max(len(words), 1) >= 0.4:
            grounded += 1
    return round(grounded / len(sents), 3)