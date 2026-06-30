"""Pydantic request/response shapes shared by routers."""
from __future__ import annotations
from pydantic import BaseModel
from typing import Any


class Ok(BaseModel):
    ok: bool = True


class DocumentOut(BaseModel):
    id: str
    subject: str | None
    kind: str | None
    filename: str | None
    mime: str | None
    pages: int
    status: str
    created_at: str | None = None
    error: str | None = None


class ChatIn(BaseModel):
    question: str
    subject: str | None = None
    session_id: str | None = None


class QuizGenIn(BaseModel):
    subject: str
    difficulty: str = "medium"
    n: int = 10
    topics: list[str] | None = None


class QuizSubmitIn(BaseModel):
    answers: dict[str, Any]


class PlannerIn(BaseModel):
    subject: str
    exam_date: str
    hours_per_day: float = 2.0


class PredictIn(BaseModel):
    subject: str


class RevisionIn(BaseModel):
    topic: str
    mode: str = "5min"
