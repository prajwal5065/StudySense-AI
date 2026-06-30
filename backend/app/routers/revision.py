"""1-min / 5-min / 15-min / deep revision summaries."""
from __future__ import annotations
from fastapi import APIRouter
from ..services.retriever import retrieve
from ..agents.revision_agent import RevisionAgent
from ..models.schemas import RevisionIn

router = APIRouter(prefix="/revision", tags=["revision"])


@router.post("")
def revise(body: RevisionIn):
    hits = retrieve(body.topic, k=6)
    ctx = "\n\n".join(h["text"] for h in hits)
    out = RevisionAgent().execute({"topic": body.topic, "mode": body.mode, "context": ctx})
    return {"mode": body.mode, "topic": body.topic, "summary": out, "sources": len(hits)}
