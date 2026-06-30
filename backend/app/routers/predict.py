"""Predicted paper generator."""
from __future__ import annotations
import uuid
from fastapi import APIRouter, HTTPException
from ..db import cursor, json_dump, json_load, rows_to_dicts
from ..agents.prediction_agent import PredictionAgent
from ..models.schemas import PredictIn

router = APIRouter(prefix="/predict", tags=["predict"])


@router.post("/generate")
def generate(body: PredictIn):
    with cursor() as cur:
        rows = cur.execute(
            """SELECT t.id, t.name, COALESCE(i.score,0) score, COALESCE(i.frequency,0) frequency,
                      i.last_year
               FROM topics t LEFT JOIN importance_scores i ON i.topic_id=t.id
               WHERE t.subject=? ORDER BY i.score DESC""",
            (body.subject,),
        ).fetchall()
    if not rows:
        raise HTTPException(400, "No topics yet. Upload syllabus + PYQs first.")
    signals = [dict(r) for r in rows]
    out = PredictionAgent().execute({"signals": signals, "subject": body.subject})
    paper_id = str(uuid.uuid4())
    qs = out.get("questions", []) if isinstance(out, dict) else []
    name_to_id = {r["name"]: r["id"] for r in rows}
    with cursor() as cur:
        cur.execute(
            "INSERT INTO predicted_papers(id, subject, meta_json) VALUES (?,?,?)",
            (paper_id, body.subject, json_dump({"count": len(qs)})),
        )
        for q in qs:
            cur.execute(
                "INSERT INTO predicted_questions(id, paper_id, topic_id, text, marks, probability, reason) VALUES (?,?,?,?,?,?,?)",
                (str(uuid.uuid4()), paper_id, name_to_id.get(q.get("topic", "")),
                 q.get("text"), q.get("marks"), q.get("probability"), q.get("reason")),
            )
    return {"paper_id": paper_id, "questions": qs}


@router.get("")
def list_papers(subject: str | None = None):
    with cursor() as cur:
        if subject:
            rows = cur.execute("SELECT * FROM predicted_papers WHERE subject=? ORDER BY created_at DESC", (subject,)).fetchall()
        else:
            rows = cur.execute("SELECT * FROM predicted_papers ORDER BY created_at DESC").fetchall()
    return [{**dict(r), "meta": json_load(r["meta_json"], {})} for r in rows]


@router.get("/{paper_id}")
def get_paper(paper_id: str):
    with cursor() as cur:
        paper = cur.execute("SELECT * FROM predicted_papers WHERE id=?", (paper_id,)).fetchone()
        if not paper:
            raise HTTPException(404)
        qs = cur.execute("SELECT * FROM predicted_questions WHERE paper_id=?", (paper_id,)).fetchall()
    return {"paper": dict(paper), "questions": rows_to_dicts(qs)}
