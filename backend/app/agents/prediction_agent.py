"""PredictionAgent: synthesize a likely next exam paper from importance + trends."""
from __future__ import annotations
from ..services import gemini
from .base import BaseAgent


class PredictionAgent(BaseAgent):
    name = "prediction"
    role = "Generate the most likely next-exam paper."

    def execute(self, payload: dict):
        signals = payload["signals"][:60]
        subject = payload.get("subject", "General")
        prompt = (
            f"You are predicting the next {subject} exam. Use these topic signals "
            "(importance, frequency, trend slope, last_year):\n"
            + "\n".join(
                f"- {s['name']} | score={s['score']} freq={s['frequency']} "
                f"last_year={s['last_year']} slope={s.get('slope',0)}"
                for s in signals
            )
            + "\n\nProduce JSON {questions:[{text, topic, marks, probability 0..1, reason}]}. "
            "10-15 questions across difficulty."
        )
        return gemini.generate_json(prompt, system="You are an exam predictor.")
