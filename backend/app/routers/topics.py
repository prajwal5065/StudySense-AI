"""Importance scoring + trend + hot/cold."""
from __future__ import annotations
from datetime import datetime
from fastapi import APIRouter
from ..db import cursor, rows_to_dicts, json_dump
from ..services import importance, trends, embeddings as emb, clustering
from ..config import settings

router = APIRouter(prefix="/topics", tags=["topics"])


@router.get("")
def list_topics(subject: str | None = None):
    with cursor() as cur:
        if subject:
            rows = cur.execute("SELECT * FROM topics WHERE subject=?", (subject,)).fetchall()
        else:
            rows = cur.execute("SELECT * FROM topics").fetchall()
    return rows_to_dicts(rows)


@router.post("/recompute")
def recompute():
    """Recompute clusters, importance scores, and trends."""
    current_year = datetime.now().year

    # 1) Cluster questions by embedding (subject-scoped)
    cluster_count = 0
    if settings.has_key:
        with cursor() as cur:
            subjects = [r["subject"] for r in cur.execute("SELECT DISTINCT subject FROM questions").fetchall() if r["subject"]]
        for subject in subjects:
            with cursor() as cur:
                qs = cur.execute("SELECT id, text FROM questions WHERE subject=?", (subject,)).fetchall()
            if len(qs) < 2:
                continue
            vecs = []
            for q in qs:
                blob, _ = emb.embed_text(q["text"] or "")
                vecs.append(emb.unpack(blob))
            labels = clustering.cluster_vectors(vecs)
            with cursor() as cur:
                cur.execute("DELETE FROM question_clusters WHERE subject=?", (subject,))
                # Map per-subject local label to a stored cluster row
                seen: dict[int, int] = {}
                for q, lab in zip(qs, labels):
                    if lab not in seen:
                        cur.execute(
                            "INSERT INTO question_clusters(subject, label, size) VALUES (?,?,?)",
                            (subject, f"cluster-{lab}", labels.count(lab)),
                        )
                        seen[lab] = cur.lastrowid
                    cur.execute("UPDATE questions SET cluster_id=? WHERE id=?", (seen[lab], q["id"]))
                    cluster_count += 1

    # 2) Trend points
    tp = trends.rebuild_trends()

    # 3) Importance per topic
    with cursor() as cur:
        topics = cur.execute("SELECT * FROM topics").fetchall()
        if not topics:
            return {"topics": 0, "trend_points": tp}
        stats = {}
        for t in topics:
            qrows = cur.execute(
                "SELECT COUNT(*) c, COALESCE(AVG(marks),0) avg_m, MAX(year) last_year FROM questions WHERE topic_id=?",
                (t["id"],),
            ).fetchone()
            edges = cur.execute("SELECT COUNT(*) c FROM topic_edges WHERE src=? OR dst=?", (t["id"], t["id"])).fetchone()
            cluster_size = cur.execute(
                "SELECT COUNT(DISTINCT cluster_id) c FROM questions WHERE topic_id=? AND cluster_id IS NOT NULL",
                (t["id"],),
            ).fetchone()["c"]
            stats[t["id"]] = dict(freq=qrows["c"], avg_m=qrows["avg_m"], last_year=qrows["last_year"],
                                  edges=edges["c"], cluster=cluster_size)
        max_freq = max((s["freq"] for s in stats.values()), default=1) or 1
        max_marks = max((s["avg_m"] for s in stats.values()), default=1) or 1
        max_edges = max((s["edges"] for s in stats.values()), default=1) or 1
        max_cluster = max((s["cluster"] for s in stats.values()), default=1) or 1
        cur.execute("DELETE FROM importance_scores")
        for tid, s in stats.items():
            score, parts = importance.importance(
                frequency=s["freq"], max_frequency=max_freq,
                avg_marks=s["avg_m"], max_marks=max_marks,
                last_year=s["last_year"], current_year=current_year,
                cluster_size=s["cluster"], max_cluster=max_cluster,
                edges=s["edges"], max_edges=max_edges,
            )
            cur.execute(
                "INSERT INTO importance_scores(topic_id, score, frequency, avg_marks, last_year, reason_json) VALUES (?,?,?,?,?,?)",
                (tid, score, s["freq"], s["avg_m"], s["last_year"], json_dump(parts)),
            )
    return {"topics": len(topics), "trend_points": tp, "clusters_assigned": cluster_count}


@router.get("/importance")
def importance_list(subject: str | None = None):
    with cursor() as cur:
        q = """SELECT t.id, t.name, t.subject, i.score, i.frequency, i.avg_marks, i.last_year, i.reason_json
               FROM topics t LEFT JOIN importance_scores i ON i.topic_id=t.id"""
        if subject:
            q += " WHERE t.subject=?"
            rows = cur.execute(q + " ORDER BY i.score DESC NULLS LAST", (subject,)).fetchall()
        else:
            rows = cur.execute(q + " ORDER BY i.score DESC").fetchall()
    out = []
    from ..db import json_load
    for r in rows:
        d = dict(r)
        d["reason"] = json_load(r["reason_json"], {})
        out.append(d)
    return out


@router.get("/trends")
def trend_points(topic_id: str | None = None):
    with cursor() as cur:
        if topic_id:
            rows = cur.execute(
                "SELECT * FROM trend_points WHERE topic_id=? ORDER BY year", (topic_id,)
            ).fetchall()
        else:
            rows = cur.execute(
                """SELECT tp.*, t.name FROM trend_points tp
                   JOIN topics t ON t.id=tp.topic_id ORDER BY tp.year"""
            ).fetchall()
    return rows_to_dicts(rows)
