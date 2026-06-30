"""Topic-year aggregates → trend lines."""
from __future__ import annotations

from ..db import cursor


def rebuild_trends() -> int:
    with cursor() as cur:
        cur.execute("DELETE FROM trend_points")
        cur.execute(
            """INSERT INTO trend_points(topic_id, year, count, marks)
               SELECT topic_id, year, COUNT(*), COALESCE(SUM(marks),0)
               FROM questions
               WHERE topic_id IS NOT NULL AND year IS NOT NULL
               GROUP BY topic_id, year"""
        )
        return cur.execute("SELECT COUNT(*) c FROM trend_points").fetchone()["c"]