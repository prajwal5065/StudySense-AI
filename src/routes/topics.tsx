import { createFileRoute } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import { AppShell } from "@/components/layout/AppShell";
import { api } from "@/lib/api";

export const Route = createFileRoute("/topics")({
  head: () => ({ meta: [{ title: "Topics — StudySmart" }] }),
  component: TopicsPage,
});

type Imp = { id: string; name: string; subject: string | null; score: number | null; frequency: number | null; avg_marks: number | null; last_year: number | null; reason: Record<string, number> };

function TopicsPage() {
  const [rows, setRows] = useState<Imp[]>([]);
  const [busy, setBusy] = useState(false);
  const [msg, setMsg] = useState<string | null>(null);

  async function load() { setRows(await api<Imp[]>("/topics/importance")); }
  useEffect(() => { load(); }, []);

  async function recompute() {
    setBusy(true); setMsg(null);
    try {
      const r = await api<{ topics: number; trend_points: number }>("/topics/recompute", { method: "POST" });
      setMsg(`Recomputed ${r.topics} topics, ${r.trend_points} trend points.`);
      load();
    } catch (e: any) { setMsg(e?.detail || "error"); }
    setBusy(false);
  }

  return (
    <AppShell>
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Topics & Importance</h1>
        <button onClick={recompute} disabled={busy} className="px-3 py-2 bg-slate-900 text-white rounded text-sm disabled:opacity-50">
          {busy ? "Computing…" : "Recompute importance + trends"}
        </button>
      </div>
      {msg && <div className="mt-3 text-sm text-slate-600">{msg}</div>}
      <div className="mt-4 bg-white border rounded-lg overflow-x-auto">
        <table className="w-full text-sm">
          <thead className="bg-slate-50 text-left">
            <tr><th className="p-2">Topic</th><th>Subject</th><th>Score</th><th>Freq</th><th>Avg marks</th><th>Last year</th><th>Why</th></tr>
          </thead>
          <tbody>
            {rows.map((r) => (
              <tr key={r.id} className="border-t">
                <td className="p-2 font-medium">{r.name}</td>
                <td>{r.subject}</td>
                <td><span className="font-mono">{(r.score ?? 0).toFixed(3)}</span></td>
                <td>{r.frequency ?? 0}</td>
                <td>{r.avg_marks ? r.avg_marks.toFixed(1) : "—"}</td>
                <td>{r.last_year ?? "—"}</td>
                <td className="text-xs text-slate-500">{Object.entries(r.reason || {}).map(([k, v]) => `${k}:${(v as number).toFixed(2)}`).join("  ")}</td>
              </tr>
            ))}
            {rows.length === 0 && <tr><td colSpan={7} className="p-6 text-center text-slate-500">No topics. Upload material, then click Recompute.</td></tr>}
          </tbody>
        </table>
      </div>
    </AppShell>
  );
}
