"""Ingestion pipeline: extract -> chunk -> embed -> agents."""
from __future__ import annotations

import uuid
from pathlib import Path

from ..config import settings
from ..db import cursor, json_dump
from ..services import chunker, embeddings as emb, ocr
from ..agents.topic_agent import TopicAgent
from ..agents.question_agent import QuestionAgent
from ..agents.formula_agent import FormulaAgent
from ..agents.graph_agent import GraphAgent
from .queue import Job


async def ingest_document(job: Job, *, doc_id: str):
    with cursor() as cur:
        row = cur.execute("SELECT * FROM documents WHERE id=?", (doc_id,)).fetchone()
    if not row:
        raise RuntimeError("document missing")

    path = Path(settings.data_path) / "uploads" / doc_id / row["filename"]
    job.message = "extracting"
    with cursor() as cur:
        cur.execute("UPDATE documents SET status='parsing' WHERE id=?", (doc_id,))

    pages = ocr.extract(path, row["mime"] or "")
    with cursor() as cur:
        for pno, text in pages:
            cur.execute(
                "INSERT INTO pages(id, doc_id, page_no, text) VALUES (?,?,?,?)",
                (str(uuid.uuid4()), doc_id, pno, text),
            )
        cur.execute("UPDATE documents SET pages=? WHERE id=?", (len(pages), doc_id))

    job.message = "chunking"
    job.progress = 0.2
    chunks = chunker.chunk_pages(pages)

    job.message = "embedding"
    with cursor() as cur:
        cur.execute("UPDATE documents SET status='embedding' WHERE id=?", (doc_id,))
    for i, ch in enumerate(chunks):
        cid = str(uuid.uuid4())
        with cursor() as cur:
            cur.execute(
                "INSERT INTO chunks(id, doc_id, page_no, section, text, token_count) VALUES (?,?,?,?,?,?)",
                (cid, doc_id, ch["page_no"], ch["section"], ch["text"], ch["token_count"]),
            )
        if settings.has_key:
            try:
                blob, dim = emb.embed_text(ch["text"])
                with cursor() as cur:
                    cur.execute(
                        "INSERT OR REPLACE INTO embeddings(chunk_id, vector, dim) VALUES (?,?,?)",
                        (cid, blob, dim),
                    )
            except Exception as e:
                job.message = f"embed warn: {e}"
        if i % 5 == 0:
            job.progress = 0.2 + 0.4 * (i / max(1, len(chunks)))

    full_text = "\n\n".join(t for _, t in pages)
    subject = row["subject"] or "General"

    if settings.has_key and full_text.strip():
        job.message = "agents: topic"
        job.progress = 0.65
        topics_out = TopicAgent().run({"text": full_text, "subject": subject}, doc_id=doc_id).output or []
        topic_ids: dict[str, str] = {}
        with cursor() as cur:
            for t in topics_out if isinstance(topics_out, list) else []:
                tid = str(uuid.uuid4())
                topic_ids[t.get("name", "")] = tid
                cur.execute(
                    "INSERT INTO topics(id, subject, name, summary) VALUES (?,?,?,?)",
                    (tid, subject, t.get("name"), t.get("summary")),
                )

        if (row["kind"] or "") == "pyq":
            job.message = "agents: questions"
            job.progress = 0.75
            qs = QuestionAgent().run({"text": full_text, "year": None}, doc_id=doc_id).output or []
            with cursor() as cur:
                for q in qs if isinstance(qs, list) else []:
                    tid = topic_ids.get(q.get("topic", ""))
                    cur.execute(
                        "INSERT INTO questions(id, subject, doc_id, year, marks, text, topic_id) VALUES (?,?,?,?,?,?,?)",
                        (str(uuid.uuid4()), subject, doc_id, q.get("year"), q.get("marks"), q.get("text"), tid),
                    )

        job.message = "agents: formulas"
        job.progress = 0.85
        fs = FormulaAgent().run({"text": full_text}, doc_id=doc_id).output or []
        with cursor() as cur:
            for f in fs if isinstance(fs, list) else []:
                cur.execute(
                    "INSERT INTO formulas(id, subject, topic_id, latex, name, description, variables_json, mistakes_json, related_json) VALUES (?,?,?,?,?,?,?,?,?)",
                    (
                        str(uuid.uuid4()), subject, topic_ids.get(f.get("topic", "")),
                        f.get("latex"), f.get("name"), f.get("description"),
                        json_dump(f.get("variables", [])),
                        json_dump(f.get("common_mistakes", [])),
                        json_dump(f.get("related", [])),
                    ),
                )

        if topics_out:
            job.message = "agents: graph"
            job.progress = 0.92
            edges = GraphAgent().run({"topics": topics_out}, doc_id=doc_id).output or []
            with cursor() as cur:
                for e in edges if isinstance(edges, list) else []:
                    src = topic_ids.get(e.get("src", ""))
                    dst = topic_ids.get(e.get("dst", ""))
                    if src and dst and src != dst:
                        try:
                            cur.execute(
                                "INSERT OR REPLACE INTO topic_edges(src,dst,relation,weight) VALUES (?,?,?,?)",
                                (src, dst, e.get("relation", "related"), float(e.get("weight", 1.0))),
                            )
                        except Exception:
                            pass

    with cursor() as cur:
        cur.execute("UPDATE documents SET status='ready' WHERE id=?", (doc_id,))
    job.message = "done"
    return {"doc_id": doc_id, "chunks": len(chunks)}
