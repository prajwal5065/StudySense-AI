"""BaseAgent: each agent declares role/input/output/prompt/tools/memory.
run() records an agent_runs audit row with timing for the multi-agent trace UI."""
from __future__ import annotations

import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from ..db import cursor


@dataclass
class AgentResult:
    ok: bool
    output: Any
    error: str | None = None


class BaseAgent(ABC):
    name: str = "base"
    role: str = ""

    @abstractmethod
    def execute(self, payload: dict) -> Any: ...

    def run(self, payload: dict, *, doc_id: str | None = None) -> AgentResult:
        t0 = time.time()
        try:
            out = self.execute(payload)
            ms = int((time.time() - t0) * 1000)
            self._log(doc_id, payload, out, ms, ok=True, error=None)
            return AgentResult(True, out)
        except Exception as e:
            ms = int((time.time() - t0) * 1000)
            self._log(doc_id, payload, None, ms, ok=False, error=str(e))
            return AgentResult(False, None, str(e))

    def _log(self, doc_id, payload, out, ms, *, ok, error):
        with cursor() as cur:
            cur.execute(
                "INSERT INTO agent_runs(agent, doc_id, input_summary, output_summary, ms, ok, error) VALUES (?,?,?,?,?,?,?)",
                (
                    self.name, doc_id, str(payload)[:300],
                    str(out)[:300] if out is not None else None,
                    ms, 1 if ok else 0, error,
                ),
            )
