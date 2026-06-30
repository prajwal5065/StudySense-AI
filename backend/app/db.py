"""SQLite connection + lightweight migrations runner.

We use the stdlib sqlite3 module synchronously (the dataset is small and
single-user; async + sqlite-vec would add deploy complexity). Vector search
is done in Python with numpy cosine over a small embeddings table — fine for
thousands of chunks.
"""
from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from .config import settings

MIGRATIONS_DIR = Path(__file__).parent / "migrations"


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(settings.db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA journal_mode = WAL;")
    return conn


_conn: sqlite3.Connection | None = None


def get_conn() -> sqlite3.Connection:
    global _conn
    if _conn is None:
        _conn = _connect()
        _run_migrations(_conn)
    return _conn


@contextmanager
def cursor() -> Iterator[sqlite3.Cursor]:
    conn = get_conn()
    cur = conn.cursor()
    try:
        yield cur
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()


def _run_migrations(conn: sqlite3.Connection) -> None:
    conn.execute(
        "CREATE TABLE IF NOT EXISTS _migrations (name TEXT PRIMARY KEY, applied_at TEXT DEFAULT CURRENT_TIMESTAMP)"
    )
    applied = {r[0] for r in conn.execute("SELECT name FROM _migrations").fetchall()}
    for path in sorted(MIGRATIONS_DIR.glob("*.sql")):
        if path.name in applied:
            continue
        sql = path.read_text(encoding="utf-8")
        conn.executescript(sql)
        conn.execute("INSERT INTO _migrations(name) VALUES (?)", (path.name,))
        conn.commit()


def rows_to_dicts(rows) -> list[dict]:
    return [dict(r) for r in rows]


def json_dump(obj) -> str:
    return json.dumps(obj, ensure_ascii=False)


def json_load(s: str | None, default=None):
    if not s:
        return default
    try:
        return json.loads(s)
    except Exception:
        return default