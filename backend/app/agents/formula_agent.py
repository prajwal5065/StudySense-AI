"""FormulaAgent: extract + enrich formulas with variables, mistakes, related."""
from __future__ import annotations
from ..services import gemini
from .base import BaseAgent


class FormulaAgent(BaseAgent):
    name = "formula"
    role = "Find every formula and explain its variables, common mistakes, related laws."

    def execute(self, payload: dict):
        text = payload["text"][:12000]
        prompt = (
            "Find every formula. JSON array of "
            "{name, latex, description, variables:[{symbol,meaning,unit}], "
            "common_mistakes:[string], related:[string], topic:string}.\n\n"
            f"TEXT:\n{text}"
        )
        return gemini.generate_json(prompt, system="You are a physics+math tutor.")
