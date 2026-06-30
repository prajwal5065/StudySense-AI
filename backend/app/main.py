"""FastAPI entrypoint. Mounts every router; starts the worker pool on boot."""
from __future__ import annotations

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .db import get_conn
from .workers import queue as q
from .routers import (
    documents, graph, topics, questions, formulas,
    predict, quiz, planner, progress, chat, revision, analytics,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    get_conn()  # run migrations
    q.start_workers(2)
    yield


app = FastAPI(title="StudySense AI API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_list,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "name": "StudySense AI API",
        "ok": True,
        "ai_enabled": settings.has_key,
        "note": None if settings.has_key else "Paste GEMINI_API_KEY into backend/.env to enable AI features.",
    }


for r in (documents.router, graph.router, topics.router, questions.router, formulas.router,
          predict.router, quiz.router, planner.router, progress.router,
          chat.router, revision.router, analytics.router):
    app.include_router(r)
