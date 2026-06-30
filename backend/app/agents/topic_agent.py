"""TopicAgent: extract canonical topics + summaries from study material."""
from __future__ import annotations
from ..services import gemini
from .base import BaseAgent


class TopicAgent(BaseAgent):
    name = "topic"
    role = "Extract canonical topics and one-line summaries from study material."

    def execute(self, payload: dict):
        text = payload["text"][:12000]
        subject = payload.get("subject", "General")
        prompt = (
            f"You analyze {subject} study material. From the text below, output a JSON array of "
            "topics. Each item: {name, summary, parent}. Use 6-15 items. parent may be null.\n\n"
            f"TEXT:\n{text}"
        )
        return gemini.generate_json(prompt, system="You are a careful curriculum architect.")
