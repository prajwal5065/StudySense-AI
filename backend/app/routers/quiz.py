"""Mock test generation + grading."""
from __future__ import annotations
import uuid
from fastapi import APIRouter, HTTPException
from ..db import cursor, json_dump, json_load
from ..agents.quiz_agent import QuizAgent
from ..agents.tutor_agent import GraderAgent
from ..models.schemas import QuizGenIn, QuizSubmitIn

router = APIRouter(prefix="/quiz", tags=["quiz"])


@router.post("/generate")
def generate(body: QuizGenIn):
    topics = body.topics
    if not topics:
        with cursor() as cur:
            rows = cur.execute(
                """SELECT t.name FROM topics t LEFT JOIN importance_scores i ON i.topic_id=t.id
                   WHERE t.subject=? ORDER BY i.score DESC LIMIT 20""",
                (body.subject,),
            ).fetchall()
        topics = [r["name"] for r in rows]
    out = QuizAgent().execute(
        {"topics": topics, "n": body.n, "difficulty": body.difficulty, "subject": body.subject}
    )
    qs = out if isinstance(out, list) else out.get("questions", [])
    test_id = str(uuid.uuid4())
    with cursor() as cur:
        cur.execute(
            "INSERT INTO mock_tests(id, subject, title, difficulty, questions_json) VALUES (?,?,?,?,?)",
            (test_id, body.subject, f"{body.subject} {body.difficulty} mock", body.difficulty, json_dump(qs)),
        )
    return {"test_id": test_id, "questions": qs}


@router.get("/{test_id}")
def get_test(test_id: str):
    with cursor() as cur:
        r = cur.execute("SELECT * FROM mock_tests WHERE id=?", (test_id,)).fetchone()
        if not r:
            raise HTTPException(404)
    return {**dict(r), "questions": json_load(r["questions_json"], [])}


@router.post("/{test_id}/submit")
def submit(test_id: str, body: QuizSubmitIn):
    with cursor() as cur:
        r = cur.execute("SELECT * FROM mock_tests WHERE id=?", (test_id,)).fetchone()
        if not r:
            raise HTTPException(404)
    qs = json_load(r["questions_json"], [])
    feedback = []
    total = 0.0
    earned = 0.0
    grader = GraderAgent()
    for i, q in enumerate(qs):
        key = str(i)
        student = body.answers.get(key, "")
        marks = float(q.get("marks") or 1)
        total += marks
        if q.get("kind") == "mcq":
            correct = str(student).strip().lower() == str(q.get("answer")).strip().lower()
            score = 1.0 if correct else 0.0
            feedback.append({"i": i, "correct": correct, "score": score, "feedback": q.get("explanation", "")})
            earned += score * marks
        else:
            try:
                g = grader.execute({"question": q.get("q"), "answer": q.get("answer"), "student": student})
                sc = float(g.get("score", 0))
                feedback.append({"i": i, "correct": bool(g.get("correct")), "score": sc, "feedback": g.get("feedback", "")})
                earned += sc * marks
            except Exception as e:
                feedback.append({"i": i, "correct": False, "score": 0, "feedback": f"grader-error: {e}"})

    pct = (earned / total * 100) if total else 0.0
    attempt_id = str(uuid.uuid4())
    with cursor() as cur:
        cur.execute(
            "INSERT INTO mock_attempts(id, test_id, score, answers_json, feedback_json, submitted_at) VALUES (?,?,?,?,?, CURRENT_TIMESTAMP)",
            (attempt_id, test_id, pct, json_dump(body.answers), json_dump(feedback)),
        )
        # progress events for weakness tracking
        for q, fb in zip(qs, feedback):
            cur.execute(
                "INSERT INTO progress_events(topic_id, kind, delta) VALUES (?,?,?)",
                (None, "quiz_correct" if fb["correct"] else "quiz_wrong", fb["score"]),
            )
    return {"attempt_id": attempt_id, "score_pct": pct, "feedback": feedback}
