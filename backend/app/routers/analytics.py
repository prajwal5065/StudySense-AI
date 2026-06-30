"""Aggregate counts for the dashboard."""
from __future__ import annotations
from fastapi import APIRouter
from ..db import cursor, rows_to_dicts

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/overview")
def overview():
    with cursor() as cur:
        def one(sql):
            return cur.execute(sql).fetchone()[0]
        return {
            "documents": one("SELECT COUNT(*) FROM documents"),
            "chunks": one("SELECT COUNT(*) FROM chunks"),
            "topics": one("SELECT COUNT(*) FROM topics"),
            "questions": one("SELECT COUNT(*) FROM questions"),
            "formulas": one("SELECT COUNT(*) FROM formulas"),
            "mock_attempts": one("SELECT COUNT(*) FROM mock_attempts"),
            "chat_messages": one("SELECT COUNT(*) FROM chat_messages"),
        }


@router.get("/agent-runs")
def agent_runs(limit: int = 50):
    with cursor() as cur:
        rows = cur.execute(
            "SELECT * FROM agent_runs ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
    return rows_to_dicts(rows)
