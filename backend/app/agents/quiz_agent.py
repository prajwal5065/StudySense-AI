"""QuizAgent: generate a mock test for a subject at a difficulty."""
from __future__ import annotations
from ..services import gemini
from .base import BaseAgent


class QuizAgent(BaseAgent):
    name = "quiz"
    role = "Generate mock-test questions grounded in the user's syllabus."

    def execute(self, payload: dict):
        topics = payload.get("topics", [])
        n = payload.get("n", 10)
        difficulty = payload.get("difficulty", "medium")
        subject = payload.get("subject", "General")
        prompt = (
            f"Create {n} {difficulty} {subject} questions. JSON array of "
            "{q, kind in [mcq,short,long], options (only for mcq), answer, marks, topic, explanation}.\n\n"
            "Cover these topics: " + ", ".join(topics[:25])
        )
        return gemini.generate_json(prompt, system="You are an exam paper setter.")
