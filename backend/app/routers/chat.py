"""RAG tutor chat with citations + grounding confidence."""
from __future__ import annotations
import uuid
from fastapi import APIRouter
from ..db import cursor, json_dump, rows_to_dicts
from ..services.retriever import retrieve
from ..services.citations import format_citations
from ..services.hallucination import grounding_score
from ..agents.tutor_agent import TutorAgent
from ..models.schemas import ChatIn

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("")
def ask(body: ChatIn):
    session_id = body.session_id or str(uuid.uuid4())
    with cursor() as cur:
        cur.execute("INSERT OR IGNORE INTO chat_sessions(id, subject) VALUES (?,?)", (session_id, body.subject))
        cur.execute(
            "INSERT INTO chat_messages(id, session_id, role, content) VALUES (?,?,?,?)",
            (str(uuid.uuid4()), session_id, "user", body.question),
        )
    hits = retrieve(body.question, subject=body.subject, k=6)
    answer = TutorAgent().execute({"question": body.question, "hits": hits})
    citations = format_citations(hits)
    confidence = grounding_score(answer, hits)
    with cursor() as cur:
        cur.execute(
            "INSERT INTO chat_messages(id, session_id, role, content, citations_json, confidence) VALUES (?,?,?,?,?,?)",
            (str(uuid.uuid4()), session_id, "assistant", answer, json_dump(citations), confidence),
        )
    return {
        "session_id": session_id, "answer": answer,
        "citations": citations, "confidence": confidence,
        "reasons": [f"retrieved {len(hits)} chunks", f"grounding={confidence}"],
    }


@router.get("/sessions")
def sessions():
    with cursor() as cur:
        rows = cur.execute("SELECT * FROM chat_sessions ORDER BY created_at DESC LIMIT 50").fetchall()
    return rows_to_dicts(rows)


@router.get("/sessions/{sid}")
def messages(sid: str):
    with cursor() as cur:
        rows = cur.execute(
            "SELECT * FROM chat_messages WHERE session_id=? ORDER BY created_at", (sid,)
        ).fetchall()
    return rows_to_dicts(rows)
