"""RevisionAgent: 1-min / 5-min / 15-min / deep summaries of a topic."""
from __future__ import annotations
from ..services import gemini
from .base import BaseAgent

MODES = {
    "1min": "30-second flashcard: 3 bullet points, ultra terse.",
    "5min": "5-minute revision: key ideas + 1 worked example.",
    "15min": "15-minute deep review: all subtopics, formulas, common pitfalls.",
    "deep": "Full reference notes with examples and gotchas.",
}


class RevisionAgent(BaseAgent):
    name = "revision"
    role = "Produce revision at the requested compression."

    def execute(self, payload: dict):
        mode = payload.get("mode", "5min")
        spec = MODES.get(mode, MODES["5min"])
        prompt = (
            f"Topic: {payload['topic']}\nMode: {mode} -- {spec}\n"
            f"Source notes:\n{payload.get('context','')[:8000]}"
        )
        return gemini.generate_text(prompt, system="You are a master revision coach.")
