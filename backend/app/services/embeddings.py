"""Embedding service with on-disk cache so we never recompute."""
from __future__ import annotations

import hashlib
import struct

import numpy as np

from ..config import settings
from ..db import cursor
from . import gemini


def _key(text: str) -> str:
    h = hashlib.sha256()
    h.update(settings.gemini_embed_model.encode())
    h.update(b"::")
    h.update(text.encode("utf-8", errors="ignore"))
    return h.hexdigest()


def _pack(vec: list[float]) -> bytes:
    return struct.pack(f"<{len(vec)}f", *vec)


def unpack(blob: bytes) -> np.ndarray:
    n = len(blob) // 4
    return np.array(struct.unpack(f"<{n}f", blob), dtype=np.float32)


def embed_text(text: str) -> tuple[bytes, int]:
    sha = _key(text)
    with cursor() as cur:
        row = cur.execute("SELECT vector, dim FROM embedding_cache WHERE sha=?", (sha,)).fetchone()
        if row:
            return row["vector"], row["dim"]
    vec = gemini.embed(text)
    blob = _pack(vec)
    with cursor() as cur:
        cur.execute(
            "INSERT OR REPLACE INTO embedding_cache(sha, vector, dim) VALUES (?,?,?)",
            (sha, blob, len(vec)),
        )
    return blob, len(vec)


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    na = float(np.linalg.norm(a))
    nb = float(np.linalg.norm(b))
    if na == 0 or nb == 0:
        return 0.0
    return float(np.dot(a, b) / (na * nb))