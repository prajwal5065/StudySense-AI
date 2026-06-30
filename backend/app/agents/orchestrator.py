"""Minimal DAG runner. Records every step; failures don't abort downstream."""
from __future__ import annotations
from typing import Callable
from .base import AgentResult, BaseAgent


class Orchestrator:
    def __init__(self):
        self.results: dict[str, AgentResult] = {}

    def run(self, agent: BaseAgent, payload_fn: Callable[[dict[str, AgentResult]], dict], *, doc_id=None) -> AgentResult:
        payload = payload_fn(self.results)
        res = agent.run(payload, doc_id=doc_id)
        self.results[agent.name] = res
        return res
