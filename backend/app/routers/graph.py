"""Knowledge graph nodes + edges + per-topic detail."""
from __future__ import annotations
from fastapi import APIRouter, HTTPException
from ..db import cursor, rows_to_dicts, json_load

router = APIRouter(prefix="/graph", tags=["graph"])


@router.get("")
def get_graph(subject: str | None = None):
    with cursor() as cur:
        if subject:
            topics = cur.execute("SELECT * FROM topics WHERE subject=?", (subject,)).fetchall()
        else:
            topics = cur.execute("SELECT * FROM topics").fetchall()
        topic_ids = {t["id"] for t in topics}
        edges = cur.execute("SELECT * FROM topic_edges").fetchall()
        scores = {r["topic_id"]: r["score"] for r in cur.execute("SELECT * FROM importance_scores").fetchall()}
    nodes = [
        {"id": t["id"], "label": t["name"], "summary": t["summary"], "importance": scores.get(t["id"], 0.0)}
        for t in topics
    ]
    edges_out = [
        {"src": e["src"], "dst": e["dst"], "relation": e["relation"], "weight": e["weight"]}
        for e in edges if e["src"] in topic_ids and e["dst"] in topic_ids
    ]
    return {"nodes": nodes, "edges": edges_out}


@router.get("/topic/{topic_id}")
def topic_detail(topic_id: str):
    with cursor() as cur:
        t = cur.execute("SELECT * FROM topics WHERE id=?", (topic_id,)).fetchone()
        if not t:
            raise HTTPException(404)
        qs = cur.execute("SELECT id, text, marks, year FROM questions WHERE topic_id=?", (topic_id,)).fetchall()
        fs = cur.execute("SELECT * FROM formulas WHERE topic_id=?", (topic_id,)).fetchall()
        s = cur.execute("SELECT * FROM importance_scores WHERE topic_id=?", (topic_id,)).fetchone()
    return {
        "topic": dict(t),
        "questions": rows_to_dicts(qs),
        "formulas": [{**dict(f), "variables": json_load(f["variables_json"], [])} for f in fs],
        "importance": dict(s) if s else None,
    }
