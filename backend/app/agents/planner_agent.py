"""PlannerAgent: produce a day-by-day plan from now to exam_date."""
from __future__ import annotations
from ..services import gemini
from .base import BaseAgent


class PlannerAgent(BaseAgent):
    name = "planner"
    role = "Build a study plan personalized to topic importance and weakness."

    def execute(self, payload: dict):
        prompt = (
            "Build a study plan as JSON {days:[{date, focus_topic, tasks:[{kind,minutes,detail}], target}]}. "
            f"Exam date: {payload['exam_date']}. Hours/day: {payload['hours_per_day']}. "
            f"Subject: {payload['subject']}.\n"
            f"Important topics (score desc): {payload['topics'][:20]}\n"
            f"Weak topics: {payload.get('weak', [])}"
        )
        return gemini.generate_json(prompt, system="You are a personal study coach.")
