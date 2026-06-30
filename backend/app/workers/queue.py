"""In-process async job queue. No Redis. Tasks survive only while the
process is alive; for local single-user use that is the right tradeoff."""
from __future__ import annotations

import asyncio
import uuid
from dataclasses import dataclass, field
from typing import Any, Callable, Coroutine


@dataclass
class Job:
    id: str
    name: str
    status: str = "queued"  # queued | running | done | error
    progress: float = 0.0
    message: str = ""
    result: Any = None
    error: str | None = None


_jobs: dict[str, Job] = {}
_queue: asyncio.Queue | None = None
_started = False


def _ensure_queue() -> asyncio.Queue:
    global _queue
    if _queue is None:
        _queue = asyncio.Queue()
    return _queue


async def _worker():
    q = _ensure_queue()
    while True:
        job, fn, kwargs = await q.get()
        job.status = "running"
        try:
            job.result = await fn(job, **kwargs)
            job.status = "done"
            job.progress = 1.0
        except Exception as e:
            job.error = str(e)
            job.status = "error"
        finally:
            q.task_done()


def start_workers(n: int = 2):
    global _started
    if _started:
        return
    _started = True
    loop = asyncio.get_event_loop()
    for _ in range(n):
        loop.create_task(_worker())


def enqueue(name: str, fn: Callable[..., Coroutine], **kwargs) -> Job:
    job = Job(id=str(uuid.uuid4()), name=name)
    _jobs[job.id] = job
    _ensure_queue().put_nowait((job, fn, kwargs))
    return job


def get(job_id: str) -> Job | None:
    return _jobs.get(job_id)


def all_jobs() -> list[Job]:
    return list(_jobs.values())
