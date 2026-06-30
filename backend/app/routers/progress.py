"""Weakness tracking + study recommendations."""
from __future__ import annotations
from fastapi import APIRouter
from ..db import cursor, rows_to_dicts

router = APIRouter(prefix="/progress", tags=["progress"])


@router.get("/summary")
def summary():
    with cursor() as cur:
        rows = cur.execute(
            "SELECT kind, COUNT(*) c, AVG(delta) avg_delta FROM progress_events GROUP BY kind"
        ).fetchall()
        weak = cur.execute(
            """SELECT topic_id, AVG(delta) avg_score, COUNT(*) attempts
               FROM progress_events WHERE topic_id IS NOT NULL GROUP BY topic_id
               HAVING avg_score < 0.6 ORDER BY avg_score ASC LIMIT 10"""
        ).fetchall()
    return {"by_kind": rows_to_dicts(rows), "weak_topics": rows_to_dicts(weak)}


@router.get("/events")
def list_events():
    with cursor() as cur:
        rows = cur.execute("SELECT * FROM progress_events ORDER BY id DESC LIMIT 200").fetchall()
    return rows_to_dicts(rows)
