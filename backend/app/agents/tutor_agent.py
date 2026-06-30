"""TutorAgent: answer grounded in retrieved chunks. GraderAgent: score free-text answers."""
from __future__ import annotations
from ..services import gemini
from .base import BaseAgent


class TutorAgent(BaseAgent):
    name = "tutor"
    role = "Tutor that answers ONLY from provided sources."

    def execute(self, payload: dict):
        question = payload["question"]
        hits = payload.get("hits", [])
        if hits:
            ctx = "\n\n".join(f"[{i+1}] (p.{h['page']} {h['filename']}) {h['text']}" for i, h in enumerate(hits))
            prompt = (
                "Answer the student strictly from the sources below. Cite as [1],[2] inline. "
                "If sources don't cover it, say so plainly.\n\n"
                f"SOURCES:\n{ctx}\n\nQUESTION: {question}"
            )
        else:
            prompt = f"Answer concisely: {question}"
        return gemini.generate_text(prompt, system="You are a precise study tutor.")


class GraderAgent(BaseAgent):
    name = "grader"
    role = "Grade a free-text answer against a model answer."

    def execute(self, payload: dict):
        prompt = (
            "Grade the student's answer. Return JSON "
            "{score 0..1, correct (bool), missing (list), feedback (string)}.\n\n"
            f"QUESTION: {payload['question']}\nMODEL ANSWER: {payload['answer']}\n"
            f"STUDENT ANSWER: {payload['student']}"
        )
        return gemini.generate_json(prompt, system="You are a strict but fair examiner.")
