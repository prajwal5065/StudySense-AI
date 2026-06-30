import { createFileRoute } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import { AppShell } from "@/components/layout/AppShell";
import { api } from "@/lib/api";

export const Route = createFileRoute("/predict")({
  head: () => ({ meta: [{ title: "Predicted Paper — StudySmart" }] }),
  component: PredictPage,
});

function PredictPage() {
  const [subject, setSubject] = useState("Physics");
  const [busy, setBusy] = useState(false);
  const [paper, setPaper] = useState<any>(null);
  const [err, setErr] = useState<string | null>(null);
  const [papers, setPapers] = useState<any[]>([]);

  useEffect(() => { api<any[]>("/predict").then(setPapers).catch(() => {}); }, []);

  async function gen() {
    setBusy(true); setErr(null);
    try { setPaper(await api("/predict/generate", { method: "POST", json: { subject } })); }
    catch (e: any) { setErr(e?.detail || "error"); }
    setBusy(false);
  }

  return (
    <AppShell>
      <h1 className="text-2xl font-bold">Predicted Paper</h1>
      <div className="mt-4 flex gap-2 items-end">
        <label>
          <div className="text-xs text-slate-500">Subject</div>
          <input value={subject} onChange={(e) => setSubject(e.target.value)} className="border rounded px-3 py-2 text-sm" />
        </label>
        <button onClick={gen} disabled={busy} className="px-3 py-2 bg-slate-900 text-white rounded text-sm disabled:opacity-50">
          {busy ? "Predicting…" : "Generate prediction"}
        </button>
      </div>
      {err && <div className="mt-3 text-red-600 text-sm">{err}</div>}

      {paper && (
        <div className="mt-6 bg-white border rounded-lg p-5">
          <div className="font-semibold">Likely next paper ({paper.questions.length} questions)</div>
          <ol className="mt-3 space-y-3 list-decimal pl-5">
            {paper.questions.map((q: any, i: number) => (
              <li key={i}>
                <div>{q.text}</div>
                <div className="text-xs text-slate-500 mt-1">
                  topic: {q.topic} · marks: {q.marks ?? "?"} · probability: {((q.probability ?? 0) * 100).toFixed(0)}%
                </div>
                <div className="text-xs text-slate-500 italic">why: {q.reason}</div>
              </li>
            ))}
          </ol>
        </div>
      )}

      <div className="mt-8">
        <div className="text-sm font-semibold text-slate-700">Previous predictions</div>
        <ul className="mt-2 text-sm space-y-1">
          {papers.map((p: any) => (<li key={p.id} className="border-b py-1 flex justify-between"><span>{p.subject}</span><span className="text-xs text-slate-500">{p.created_at}</span></li>))}
        </ul>
      </div>
    </AppShell>
  );
}
