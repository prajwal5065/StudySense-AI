"""QuestionAgent: extract previous-year questions from a PYQ document."""
from __future__ import annotations
from ..services import gemini
from .base import BaseAgent


class QuestionAgent(BaseAgent):
    name = "question"
    role = "Extract past-exam questions with marks and topic guess."

    def execute(self, payload: dict):
        text = payload["text"][:14000]
        year = payload.get("year")
        prompt = (
            "Extract every distinct exam question. JSON array of "
            "{text, marks (int or null), topic (short string)}.\n"
            f"Assume year = {year}.\n\nTEXT:\n{text}"
        )
        return gemini.generate_json(prompt, system="You are an exam analyst.")
