import { createFileRoute } from "@tanstack/react-router";
import { useState } from "react";
import { AppShell } from "@/components/layout/AppShell";
import { api } from "@/lib/api";

export const Route = createFileRoute("/chat")({
  head: () => ({ meta: [{ title: "Tutor Chat — StudySmart" }] }),
  component: ChatPage,
});

type Msg = { role: "user" | "assistant"; content: string; citations?: any[]; confidence?: number; reasons?: string[] };

function ChatPage() {
  const [msgs, setMsgs] = useState<Msg[]>([]);
  const [input, setInput] = useState("");
  const [session, setSession] = useState<string | undefined>(undefined);
  const [busy, setBusy] = useState(false);
  const [subject, setSubject] = useState("");

  async function send() {
    if (!input.trim()) return;
    const q = input; setInput("");
    setMsgs((m) => [...m, { role: "user", content: q }]); setBusy(true);
    try {
      const r = await api<{ session_id: string; answer: string; citations: any[]; confidence: number; reasons: string[] }>(
        "/chat", { method: "POST", json: { question: q, subject: subject || undefined, session_id: session } }
      );
      setSession(r.session_id);
      setMsgs((m) => [...m, { role: "assistant", content: r.answer, citations: r.citations, confidence: r.confidence, reasons: r.reasons }]);
    } catch (e: any) {
      setMsgs((m) => [...m, { role: "assistant", content: `Error: ${e?.detail || "unknown"}` }]);
    }
    setBusy(false);
  }

  return (
    <AppShell>
      <h1 className="text-2xl font-bold">Tutor Chat</h1>
      <div className="mt-2 text-sm text-slate-600">Answers are grounded in your uploaded material. Citations + confidence shown for every reply.</div>
      <div className="mt-3"><input value={subject} onChange={(e) => setSubject(e.target.value)} placeholder="Restrict to subject (optional)" className="border rounded px-3 py-2 text-sm w-64" /></div>

      <div className="mt-4 bg-white border rounded-lg p-4 space-y-3 min-h-[300px]">
        {msgs.length === 0 && <div className="text-slate-500 text-sm">Ask anything about your uploaded material.</div>}
        {msgs.map((m, i) => (
          <div key={i} className={`p-3 rounded ${m.role === "user" ? "bg-slate-100" : "bg-emerald-50"}`}>
            <div className="text-xs text-slate-500 mb-1">{m.role}{m.confidence !== undefined && ` · grounding ${(m.confidence * 100).toFixed(0)}%`}</div>
            <div className="text-sm whitespace-pre-wrap">{m.content}</div>
            {m.citations && m.citations.length > 0 && (
              <details className="mt-2 text-xs">
                <summary className="cursor-pointer text-slate-500">{m.citations.length} citations</summary>
                <ul className="mt-1 space-y-1">
                  {m.citations.map((c, ci) => (<li key={ci} className="border-l-2 border-slate-300 pl-2">[{ci + 1}] {c.filename} p.{c.page} — <span className="text-slate-500">{c.snippet}</span></li>))}
                </ul>
              </details>
            )}
          </div>
        ))}
      </div>
      <div className="mt-3 flex gap-2">
        <input value={input} onChange={(e) => setInput(e.target.value)} onKeyDown={(e) => e.key === "Enter" && send()}
          placeholder="Ask…" className="flex-1 border rounded px-3 py-2 text-sm" />
        <button onClick={send} disabled={busy} className="px-4 py-2 bg-slate-900 text-white rounded disabled:opacity-50">{busy ? "…" : "Send"}</button>
      </div>
    </AppShell>
  );
}
