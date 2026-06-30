"""Formula intelligence list."""
from __future__ import annotations
from fastapi import APIRouter
from ..db import cursor, json_load

router = APIRouter(prefix="/formulas", tags=["formulas"])


@router.get("")
def list_formulas(subject: str | None = None):
    with cursor() as cur:
        if subject:
            rows = cur.execute("SELECT * FROM formulas WHERE subject=?", (subject,)).fetchall()
        else:
            rows = cur.execute("SELECT * FROM formulas").fetchall()
    return [
        {
            "id": r["id"], "subject": r["subject"], "topic_id": r["topic_id"],
            "name": r["name"], "latex": r["latex"], "description": r["description"],
            "variables": json_load(r["variables_json"], []),
            "mistakes": json_load(r["mistakes_json"], []),
            "related": json_load(r["related_json"], []),
        }
        for r in rows
    ]
