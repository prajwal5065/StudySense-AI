"""Hybrid retriever: vector cosine + BM25 lexical. Returns top-k chunks with citations."""
from __future__ import annotations

import numpy as np
from rank_bm25 import BM25Okapi

from ..db import cursor
from . import embeddings as emb


def _tokenize(s: str) -> list[str]:
    return [t for t in s.lower().split() if t]


def retrieve(query: str, *, k: int = 6, subject: str | None = None) -> list[dict]:
    with cursor() as cur:
        if subject:
            rows = cur.execute(
                """SELECT c.id, c.doc_id, c.page_no, c.text, d.filename, d.subject
                   FROM chunks c JOIN documents d ON d.id=c.doc_id
                   WHERE d.subject=?""",
                (subject,),
            ).fetchall()
        else:
            rows = cur.execute(
                """SELECT c.id, c.doc_id, c.page_no, c.text, d.filename, d.subject
                   FROM chunks c JOIN documents d ON d.id=c.doc_id"""
            ).fetchall()
    if not rows:
        return []

    corpus = [_tokenize(r["text"]) for r in rows]
    bm25 = BM25Okapi(corpus)
    lex = bm25.get_scores(_tokenize(query))
    if lex.max() > lex.min():
        lex = (lex - lex.min()) / (lex.max() - lex.min())

    qvec_blob, _ = emb.embed_text(query)
    qv = emb.unpack(qvec_blob)
    with cursor() as cur:
        emb_rows = {
            r["chunk_id"]: emb.unpack(r["vector"])
            for r in cur.execute("SELECT chunk_id, vector FROM embeddings").fetchall()
        }
    vec_scores = np.array(
        [emb.cosine(qv, emb_rows[r["id"]]) if r["id"] in emb_rows else 0.0 for r in rows]
    )
    if vec_scores.max() > vec_scores.min():
        vec_scores = (vec_scores - vec_scores.min()) / (vec_scores.max() - vec_scores.min())

    final = 0.55 * vec_scores + 0.45 * lex
    order = np.argsort(-final)[:k]
    out = []
    for i in order:
        r = rows[int(i)]
        out.append(
            {
                "chunk_id": r["id"],
                "doc_id": r["doc_id"],
                "filename": r["filename"],
                "page": r["page_no"],
                "text": r["text"],
                "score": float(final[int(i)]),
            }
        )
    return out