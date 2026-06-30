import { createFileRoute } from "@tanstack/react-router";
import { useState } from "react";
import { AppShell } from "@/components/layout/AppShell";
import { api } from "@/lib/api";

export const Route = createFileRoute("/quiz")({
  head: () => ({ meta: [{ title: "Mock Tests — StudySmart" }] }),
  component: QuizPage,
});

function QuizPage() {
  const [subject, setSubject] = useState("Physics");
  const [difficulty, setDifficulty] = useState("medium");
  const [n, setN] = useState(8);
  const [test, setTest] = useState<any>(null);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [result, setResult] = useState<any>(null);
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState<string | null>(null);

  async function gen() {
    setBusy(true); setErr(null); setResult(null);
    try { setTest(await api("/quiz/generate", { method: "POST", json: { subject, difficulty, n } })); }
    catch (e: any) { setErr(e?.detail || "error"); }
    setBusy(false);
  }
  async function submit() {
    if (!test) return;
    setBusy(true);
    try { setResult(await api(`/quiz/${test.test_id}/submit`, { method: "POST", json: { answers } })); }
    catch (e: any) { setErr(e?.detail || "error"); }
    setBusy(false);
  }

  return (
    <AppShell>
      <h1 className="text-2xl font-bold">Mock Tests</h1>
      <div className="mt-4 flex gap-3 items-end flex-wrap">
        <label><div className="text-xs text-slate-500">Subject</div><input value={subject} onChange={(e) => setSubject(e.target.value)} className="border rounded px-3 py-2 text-sm" /></label>
        <label><div className="text-xs text-slate-500">Difficulty</div>
          <select value={difficulty} onChange={(e) => setDifficulty(e.target.value)} className="border rounded px-3 py-2 text-sm">
            <option value="easy">Easy</option><option value="medium">Medium</option><option value="hard">Hard</option>
          </select></label>
        <label><div className="text-xs text-slate-500"># Questions</div><input type="number" value={n} onChange={(e) => setN(+e.target.value)} className="border rounded px-3 py-2 text-sm w-24" /></label>
        <button onClick={gen} disabled={busy} className="px-3 py-2 bg-slate-900 text-white rounded text-sm disabled:opacity-50">{busy ? "…" : "Generate"}</button>
      </div>
      {err && <div className="mt-3 text-red-600 text-sm">{err}</div>}

      {test && (
        <div className="mt-6 space-y-4">
          {test.questions.map((q: any, i: number) => (
            <div key={i} className="bg-white border rounded-lg p-4">
              <div className="font-medium">{i + 1}. {q.q} <span className="text-xs text-slate-500">[{q.marks ?? 1}m · {q.kind}]</span></div>
              {q.kind === "mcq" && Array.isArray(q.options) ? (
                <div className="mt-2 space-y-1">
                  {q.options.map((o: string, oi: number) => (
                    <label key={oi} className="flex items-center gap-2 text-sm">
                      <input type="radio" name={`q${i}`} value={o} onChange={(e) => setAnswers({ ...answers, [i]: e.target.value })} /> {o}
                    </label>
                  ))}
                </div>
              ) : (
                <textarea className="mt-2 w-full border rounded p-2 text-sm" rows={3}
                  onChange={(e) => setAnswers({ ...answers, [i]: e.target.value })} />
              )}
              {result && result.feedback?.[i] && (
                <div className={`mt-2 text-xs p-2 rounded ${result.feedback[i].correct ? "bg-emerald-50 text-emerald-700" : "bg-red-50 text-red-700"}`}>
                  score {(result.feedback[i].score * 100).toFixed(0)}% — {result.feedback[i].feedback}
                </div>
              )}
            </div>
          ))}
          {!result && (<button onClick={submit} disabled={busy} className="px-4 py-2 bg-emerald-600 text-white rounded">{busy ? "Grading…" : "Submit"}</button>)}
          {result && <div className="text-lg font-semibold">Score: {result.score_pct.toFixed(1)}%</div>}
        </div>
      )}
    </AppShell>
  );
}
