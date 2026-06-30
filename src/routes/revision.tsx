import { createFileRoute } from "@tanstack/react-router";
import { useState } from "react";
import { AppShell } from "@/components/layout/AppShell";
import { api } from "@/lib/api";

export const Route = createFileRoute("/revision")({
  head: () => ({ meta: [{ title: "Revision — StudySmart" }] }),
  component: RevisionPage,
});

const MODES = ["1min", "5min", "15min", "deep"] as const;

function RevisionPage() {
  const [topic, setTopic] = useState("");
  const [mode, setMode] = useState<(typeof MODES)[number]>("5min");
  const [out, setOut] = useState<string>("");
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState<string | null>(null);

  async function go() {
    setBusy(true); setErr(null); setOut("");
    try {
      const r = await api<{ summary: string }>("/revision", { method: "POST", json: { topic, mode } });
      setOut(r.summary);
    } catch (e: any) { setErr(e?.detail || "error"); }
    setBusy(false);
  }

  return (
    <AppShell>
      <h1 className="text-2xl font-bold">Revision Modes</h1>
      <div className="mt-4 flex gap-2 items-end flex-wrap">
        <label className="flex-1"><div className="text-xs text-slate-500">Topic</div>
          <input value={topic} onChange={(e) => setTopic(e.target.value)} className="border rounded px-3 py-2 text-sm w-full" placeholder="e.g. Newton's Laws" /></label>
        <div className="flex gap-1">
          {MODES.map((m) => (
            <button key={m} onClick={() => setMode(m)} className={`px-3 py-2 rounded text-sm ${mode === m ? "bg-slate-900 text-white" : "bg-white border"}`}>{m}</button>
          ))}
        </div>
        <button onClick={go} disabled={busy || !topic} className="px-3 py-2 bg-emerald-600 text-white rounded text-sm disabled:opacity-50">{busy ? "…" : "Revise"}</button>
      </div>
      {err && <div className="mt-3 text-red-600 text-sm">{err}</div>}
      {out && (<pre className="mt-5 bg-white border rounded-lg p-5 whitespace-pre-wrap text-sm">{out}</pre>)}
    </AppShell>
  );
}
