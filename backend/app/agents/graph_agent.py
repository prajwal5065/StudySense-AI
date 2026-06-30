"""GraphAgent: from a topic list, propose edges (prerequisite / related / part_of)."""
from __future__ import annotations
from ..services import gemini
from .base import BaseAgent


class GraphAgent(BaseAgent):
    name = "graph"
    role = "Build the topic knowledge graph."

    def execute(self, payload: dict):
        topics = payload["topics"]
        names = [t["name"] for t in topics]
        prompt = (
            "Given this topic list, output a JSON array of edges "
            "{src, dst, relation in [prerequisite, related, part_of], weight 0..1}. "
            "Only use names from the list.\n\nTOPICS:\n" + "\n".join(f"- {n}" for n in names)
        )
        return gemini.generate_json(prompt, system="You are a curriculum graph designer.")
