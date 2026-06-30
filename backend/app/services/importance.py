"""Weighted importance score for a topic."""
from __future__ import annotations


def importance(
    *,
    frequency: int,
    max_frequency: int,
    avg_marks: float,
    max_marks: float,
    last_year: int | None,
    current_year: int,
    cluster_size: int,
    max_cluster: int,
    edges: int,
    max_edges: int,
) -> tuple[float, dict]:
    def n(x, mx):
        return (x / mx) if mx else 0.0

    recency = 0.0
    if last_year:
        gap = max(0, current_year - last_year)
        recency = max(0.0, 1.0 - gap / 8.0)

    parts = {
        "frequency": round(n(frequency, max_frequency), 3),
        "avg_marks": round(n(avg_marks, max_marks), 3),
        "recency": round(recency, 3),
        "cluster_size": round(n(cluster_size, max_cluster), 3),
        "edges": round(n(edges, max_edges), 3),
    }
    score = (
        0.32 * parts["frequency"]
        + 0.22 * parts["avg_marks"]
        + 0.18 * parts["recency"]
        + 0.16 * parts["cluster_size"]
        + 0.12 * parts["edges"]
    )
    return round(score, 3), parts