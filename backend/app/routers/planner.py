"""Study planner."""
from __future__ import annotations
import uuid
from fastapi import APIRouter
from ..db import cursor, json_dump, json_load, rows_to_dicts
from ..agents.planner_agent import PlannerAgent
from ..models.schemas import PlannerIn

router = APIRouter(prefix="/planner", tags=["planner"])


@router.post("/generate")
def generate(body: PlannerIn):
    with cursor() as cur:
        tops = cur.execute(
            """SELECT t.name, COALESCE(i.score,0) score FROM topics t
               LEFT JOIN importance_scores i ON i.topic_id=t.id
               WHERE t.subject=? ORDER BY i.score DESC LIMIT 30""",
            (body.subject,),
        ).fetchall()
    topics = [{"name": t["name"], "score": t["score"]} for t in tops]
    out = PlannerAgent().execute(
        {
            "subject": body.subject,
            "exam_date": body.exam_date,
            "hours_per_day": body.hours_per_day,
            "topics": topics,
            "weak": [],
        }
    )
    plan_id = str(uuid.uuid4())
    with cursor() as cur:
        cur.execute(
            "INSERT INTO study_plans(id, subject, exam_date, hours_per_day, plan_json) VALUES (?,?,?,?,?)",
            (plan_id, body.subject, body.exam_date, body.hours_per_day, json_dump(out)),
        )
    return {"plan_id": plan_id, "plan": out}


@router.get("")
def list_plans(subject: str | None = None):
    with cursor() as cur:
        if subject:
            rows = cur.execute("SELECT * FROM study_plans WHERE subject=? ORDER BY created_at DESC", (subject,)).fetchall()
        else:
            rows = cur.execute("SELECT * FROM study_plans ORDER BY created_at DESC").fetchall()
    return [{**dict(r), "plan": json_load(r["plan_json"], {})} for r in rows]
