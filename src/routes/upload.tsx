import { createFileRoute } from "@tanstack/react-router";
import { useState } from "react";
import { AppShell } from "@/components/layout/AppShell";
import { api, uploadFile } from "@/lib/api";

export const Route = createFileRoute("/upload")({
  head: () => ({ meta: [{ title: "Upload — StudySmart" }] }),
  component: UploadPage,
});

type Job = { id: string; status: string; progress: number; message: string; error?: string | null };

function UploadPage() {
  const [subject, setSubject] = useState("Physics");
  const [kind, setKind] = useState("notes");
  const [file, setFile] = useState<File | null>(null);
  const [job, setJob] = useState<Job | null>(null);
  const [err, setErr] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function go(e: React.FormEvent) {
    e.preventDefault();
    if (!file) return;
    setErr(null); setBusy(true); setJob(null);
    try {
      const r = await uploadFile(file, subject, kind);
      // poll
      const tick = async () => {
        try {
          const j = await api<Job>(`/documents/jobs/${r.job_id}`);
          setJob(j);
          if (j.status !== "done" && j.status !== "error") setTimeout(tick, 1500);
          else setBusy(false);
        } catch (e: any) { setErr(e?.detail || "error"); setBusy(false); }
      };
      tick();
    } catch (e: any) { setErr(e?.detail || "error"); setBusy(false); }
  }

  return (
    <AppShell>
      <h1 className="text-2xl font-bold">Upload</h1>
      <p className="text-slate-600 mt-1">Drop a PDF, image, DOCX, or TXT. The ingestion pipeline runs automatically.</p>
      <form onSubmit={go} className="mt-6 max-w-xl space-y-4 bg-white border rounded-lg p-5">
        <label className="block">
          <div className="text-sm font-medium">Subject</div>
          <input value={subject} onChange={(e) => setSubject(e.target.value)} className="mt-1 w-full border rounded px-3 py-2" />
        </label>
        <label className="block">
          <div className="text-sm font-medium">Kind</div>
          <select value={kind} onChange={(e) => setKind(e.target.value)} className="mt-1 w-full border rounded px-3 py-2">
            <option value="syllabus">Syllabus</option>
            <option value="pyq">Previous Year Questions</option>
            <option value="notes">Notes</option>
            <option value="other">Other</option>
          </select>
        </label>
        <label className="block">
          <div className="text-sm font-medium">File</div>
          <input type="file" onChange={(e) => setFile(e.target.files?.[0] || null)} className="mt-1 w-full" />
        </label>
        <button disabled={!file || busy} className="px-4 py-2 rounded bg-slate-900 text-white disabled:opacity-50">
          {busy ? "Working…" : "Upload & ingest"}
        </button>
      </form>

      {err && <div className="mt-4 max-w-xl p-3 rounded bg-red-50 border border-red-200 text-red-700">{err}</div>}
      {job && (
        <div className="mt-4 max-w-xl bg-white border rounded-lg p-5">
          <div className="text-sm font-medium">Job {job.id.slice(0, 8)} — {job.status}</div>
          <div className="mt-2 h-2 bg-slate-100 rounded overflow-hidden">
            <div className="h-full bg-slate-900 transition-all" style={{ width: `${Math.round((job.progress || 0) * 100)}%` }} />
          </div>
          <div className="mt-2 text-xs text-slate-600">{job.message}</div>
          {job.error && <div className="mt-2 text-xs text-red-600">{job.error}</div>}
        </div>
      )}
    </AppShell>
  );
}
