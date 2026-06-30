"""Thin Gemini client.

If GEMINI_API_KEY is blank, every call raises HTTPException(503)
so the UI can render a friendly error banner — nothing crashes.

Callers should implement exponential back-off for 429 rate-limit responses.
"""
from __future__ import annotations

import json
import re
from typing import Any

from fastapi import HTTPException

from ..config import settings


def _require_key() -> None:
    if not settings.has_key:
        raise HTTPException(
            status_code=503,
            detail="GEMINI_API_KEY not set. Paste your key into backend/.env and restart.",
        )


def _client():
    _require_key()
    import google.generativeai as genai

    genai.configure(api_key=settings.gemini_api_key)
    return genai


def generate_text(prompt: str, *, system: str | None = None, temperature: float = 0.3) -> str:
    genai = _client()
    model = genai.GenerativeModel(
        settings.gemini_text_model,
        system_instruction=system,
        generation_config={"temperature": temperature},
    )
    resp = model.generate_content(prompt)
    return (resp.text or "").strip()


def generate_json(prompt: str, *, system: str | None = None, temperature: float = 0.2) -> Any:
    """Ask for JSON and parse it; tolerates ```json fences."""
    raw = generate_text(
        prompt + "\n\nRespond ONLY with valid JSON. No prose, no markdown fences.",
        system=system,
        temperature=temperature,
    )
    raw = raw.strip()
    m = re.search(r"```(?:json)?\s*(.*?)```", raw, re.DOTALL)
    if m:
        raw = m.group(1).strip()
    try:
        return json.loads(raw)
    except Exception:
        # last-chance: find first {...} or [...]
        m = re.search(r"(\{.*\}|\[.*\])", raw, re.DOTALL)
        if m:
            return json.loads(m.group(1))
        raise HTTPException(status_code=502, detail=f"Model did not return JSON: {raw[:200]}")


def vision_ocr(image_bytes: bytes, mime: str = "image/png") -> str:
    genai = _client()
    model = genai.GenerativeModel(settings.gemini_vision_model)
    resp = model.generate_content(
        [
            "Extract ALL text from this page. Preserve order, equations and structure. "
            "Output plain text only.",
            {"mime_type": mime, "data": image_bytes},
        ]
    )
    return (resp.text or "").strip()


def embed(text: str) -> list[float]:
    genai = _client()
    resp = genai.embed_content(
        model=f"models/{settings.gemini_embed_model}",
        content=text[:8000],
        task_type="retrieval_document",
    )
    return list(resp["embedding"])