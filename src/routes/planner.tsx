import { createFileRoute } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import { AppShell } from "@/components/layout/AppShell";
import { api } from "@/lib/api";

export const Route = createFileRoute("/planner")({
  head: () => ({ meta: [{ title: "Planner — StudySmart" }] }),
  component: PlannerPage,
});

function PlannerPage() {
  const [subject, setSubject] = useState("Physics");
  const [examDate, setExamDate] = useState("");
  const [hours, setHours] = useState(2);
  const [plan, setPlan] = useState<any>(null);
  const [list, setList] = useState<any[]>([]);
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState<string | null>(null);

  useEffect(() => { api<any[]>("/planner").then(setList).catch(() => {}); }, []);

  async function gen() {
    setBusy(true); setErr(null);
    try {
      const r = await api<any>("/planner/generate", { method: "POST", json: { subject, exam_date: examDate, hours_per_day: hours } });
      setPlan(r.plan);
    } catch (e: any) { setErr(e?.detail || "error"); }
    setBusy(false);
  }

  const days = plan?.days || [];

  return (
    <AppShell>
      <h1 className="text-2xl font-bold">Study Planner</h1>
      <div className="mt-4 flex gap-3 items-end flex-wrap">
        <label><div className="text-xs text-slate-500">Subject</div><input value={subject} onChange={(e) => setSubject(e.target.value)} className="border rounded px-3 py-2 text-sm" /></label>
        <label><div className="text-xs text-slate-500">Exam date</div><input type="date" value={examDate} onChange={(e) => setExamDate(e.target.value)} className="border rounded px-3 py-2 text-sm" /></label>
        <label><div className="text-xs text-slate-500">Hours/day</div><input type="number" step="0.5" value={hours} onChange={(e) => setHours(+e.target.value)} className="border rounded px-3 py-2 text-sm w-24" /></label>
        <button onClick={gen} disabled={busy || !examDate} className="px-3 py-2 bg-slate-900 text-white rounded text-sm disabled:opacity-50">{busy ? "Planning…" : "Generate plan"}</button>
      </div>
      {err && <div className="mt-3 text-red-600 text-sm">{err}</div>}

      {days.length > 0 && (
        <div className="mt-6 grid md:grid-cols-2 gap-3">
          {days.map((d: any, i: number) => (
            <div key={i} className="bg-white border rounded-lg p-4">
              <div className="flex justify-between"><div className="font-semibold">{d.date}</div><div className="text-xs text-slate-500">{d.focus_topic}</div></div>
              <ul className="mt-2 text-sm space-y-1">
                {(d.tasks || []).map((t: any, ti: number) => (
                  <li key={ti}>• <span className="font-medium">{t.kind}</span> ({t.minutes}m) — {t.detail}</li>
                ))}
              </ul>
              {d.target && <div className="mt-2 text-xs text-slate-500">Target: {d.target}</div>}
            </div>
          ))}
        </div>
      )}

      <div className="mt-8 text-sm font-semibold text-slate-700">Saved plans</div>
      <ul className="mt-2 text-sm">
        {list.map((p: any) => <li key={p.id} className="border-b py-1 flex justify-between"><span>{p.subject} — exam {p.exam_date}</span><span className="text-xs text-slate-500">{p.created_at}</span></li>)}
      </ul>
    </AppShell>
  );
}
