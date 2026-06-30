import { createFileRoute, Link } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import { AppShell } from "@/components/layout/AppShell";
import { api } from "@/lib/api";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "Dashboard — StudySense AI" },
      { name: "description", content: "Local AI study platform: ingest syllabus + PYQs, get predicted papers, quizzes, planners, and tutor chat." },
    ],
  }),
  component: Dashboard,
});

type Overview = {
  documents: number; chunks: number; topics: number; questions: number;
  formulas: number; mock_attempts: number; chat_messages: number;
};

function Dashboard() {
  const [stats, setStats] = useState<Overview | null>(null);
  const [err, setErr] = useState<string | null>(null);

  useEffect(() => {
    api<Overview>("/analytics/overview").then(setStats).catch((e) => setErr(e?.detail || "error"));
  }, []);

  const cards = [
    { label: "Documents", k: "documents" as const, to: "/documents" },
    { label: "Chunks indexed", k: "chunks" as const, to: "/documents" },
    { label: "Topics", k: "topics" as const, to: "/topics" },
    { label: "Past questions", k: "questions" as const, to: "/topics" },
    { label: "Formulas", k: "formulas" as const, to: "/topics" },
    { label: "Mock attempts", k: "mock_attempts" as const, to: "/quiz" },
    { label: "Chat messages", k: "chat_messages" as const, to: "/chat" },
  ];

  return (
    <AppShell>
      <h1 className="text-2xl font-bold">Dashboard</h1>
      <p className="text-slate-600 mt-1">
        Welcome to StudySense AI! Upload your syllabus and previous-year papers to unlock predictions, quizzes, and a personalized planner.
      </p>
      {err && <div className="mt-4 p-3 rounded bg-red-50 border border-red-200 text-red-700">{err}</div>}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mt-6">
        {cards.map((c) => (
          <Link key={c.k} to={c.to} aria-label={c.label} className="rounded-lg border bg-white p-4 hover:shadow-sm">
            <div className="text-xs uppercase text-slate-500">{c.label}</div>
            <div className="text-3xl font-bold mt-1" aria-live="polite">{stats?.[c.k] ?? "—"}</div>
          </Link>
        ))}
      </div>
      <div className="mt-8 grid md:grid-cols-2 gap-4">
        <Link to="/upload" className="rounded-lg border bg-white p-5 hover:shadow-sm">
          <div className="text-lg font-semibold">1. Upload material</div>
          <div className="text-sm text-slate-600 mt-1">PDF, image, DOCX, or TXT. The pipeline parses, chunks, embeds, and runs topic/question/formula/graph agents.</div>
        </Link>
        <Link to="/topics" className="rounded-lg border bg-white p-5 hover:shadow-sm">
          <div className="text-lg font-semibold">2. Recompute importance</div>
          <div className="text-sm text-slate-600 mt-1">Once you have a few PYQs, run the importance + trend job to unlock predictions and the planner.</div>
        </Link>
      </div>
    </AppShell>
  );
}
