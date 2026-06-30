"""Previous-year questions + clusters."""
from __future__ import annotations
from fastapi import APIRouter
from ..db import cursor, rows_to_dicts

router = APIRouter(prefix="/questions", tags=["questions"])


@router.get("")
def list_questions(subject: str | None = None, topic_id: str | None = None):
    with cursor() as cur:
        sql = "SELECT * FROM questions WHERE 1=1"
        args: list = []
        if subject:
            sql += " AND subject=?"; args.append(subject)
        if topic_id:
            sql += " AND topic_id=?"; args.append(topic_id)
        rows = cur.execute(sql + " ORDER BY year DESC NULLS LAST", args).fetchall()
    return rows_to_dicts(rows)


@router.get("/clusters")
def clusters(subject: str | None = None):
    with cursor() as cur:
        if subject:
            rows = cur.execute("SELECT * FROM question_clusters WHERE subject=? ORDER BY size DESC", (subject,)).fetchall()
        else:
            rows = cur.execute("SELECT * FROM question_clusters ORDER BY size DESC").fetchall()
    return rows_to_dicts(rows)
