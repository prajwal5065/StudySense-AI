"""Document upload / list / delete + ingestion trigger."""
from __future__ import annotations
import hashlib, re, shutil, uuid
from pathlib import Path
from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from ..config import settings
from ..db import cursor, rows_to_dicts
from ..workers import queue as q
from ..workers.jobs import ingest_document

router = APIRouter(prefix="/documents", tags=["documents"])


def _safe_filename(name: str | None, fallback: str = "upload.bin") -> str:
    """Strip path components and disallowed characters from a client-supplied filename.

    Prevents path traversal (e.g. "../../etc/passwd") or absolute paths from
    escaping the per-document upload directory. Only the basename survives,
    and it's limited to a safe character set. The original filename is still
    stored as-is in the `documents.filename` DB column for display purposes.
    """
    if not name:
        return fallback
    name = Path(name).name  # drop any directory components (../, /, \)
    name = re.sub(r"[^A-Za-z0-9._-]", "_", name).strip("._")
    return name or fallback


@router.get("")
def list_documents(subject: str | None = None):
    with cursor() as cur:
        if subject:
            rows = cur.execute("SELECT * FROM documents WHERE subject=? ORDER BY created_at DESC", (subject,)).fetchall()
        else:
            rows = cur.execute("SELECT * FROM documents ORDER BY created_at DESC").fetchall()
    return rows_to_dicts(rows)


@router.post("/upload")
async def upload(
    file: UploadFile = File(...),
    subject: str = Form("General"),
    kind: str = Form("notes"),
):
    doc_id = str(uuid.uuid4())
    dest_dir = Path(settings.data_path) / "uploads" / doc_id
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / _safe_filename(file.filename)
    sha = hashlib.sha256()
    with dest.open("wb") as f:
        while True:
            chunk = await file.read(65536)
            if not chunk:
                break
            sha.update(chunk)
            f.write(chunk)

    with cursor() as cur:
        cur.execute(
            "INSERT INTO documents(id, subject, kind, filename, mime, sha256, status) VALUES (?,?,?,?,?,?,?)",
            (doc_id, subject, kind, file.filename, file.content_type, sha.hexdigest(), "uploaded"),
        )

    job = q.enqueue("ingest", ingest_document, doc_id=doc_id)
    return {"document_id": doc_id, "job_id": job.id}


@router.delete("/{doc_id}")
def delete_document(doc_id: str):
    folder = Path(settings.data_path) / "uploads" / doc_id
    if folder.exists():
        shutil.rmtree(folder, ignore_errors=True)
    with cursor() as cur:
        cur.execute("DELETE FROM documents WHERE id=?", (doc_id,))
    return {"ok": True}


@router.get("/jobs/{job_id}")
def job_status(job_id: str):
    j = q.get(job_id)
    if not j:
        raise HTTPException(404)
    return {"id": j.id, "name": j.name, "status": j.status, "progress": j.progress,
            "message": j.message, "error": j.error, "result": j.result}


@router.get("/jobs")
def list_jobs():
    return [
        {"id": j.id, "name": j.name, "status": j.status, "progress": j.progress, "message": j.message}
        for j in q.all_jobs()
    ][-30:]
