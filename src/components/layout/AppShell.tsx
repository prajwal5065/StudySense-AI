import { Link, useRouterState } from "@tanstack/react-router";
import type { ReactNode } from "react";
import { useEffect, useState } from "react";
import { api, API_URL } from "@/lib/api";

const NAV = [
  { to: "/", label: "Dashboard" },
  { to: "/upload", label: "Upload" },
  { to: "/documents", label: "Documents" },
  { to: "/topics", label: "Topics" },
  { to: "/graph", label: "Knowledge Graph" },
  { to: "/predict", label: "Predicted Paper" },
  { to: "/quiz", label: "Mock Tests" },
  { to: "/planner", label: "Planner" },
  { to: "/revision", label: "Revision" },
  { to: "/chat", label: "Tutor Chat" },
  { to: "/agents", label: "Agent Trace" },
  { to: "/settings", label: "Settings" },
];

export function AppShell({ children }: { children: ReactNode }) {
  const path = useRouterState({ select: (s) => s.location.pathname });
  const [status, setStatus] = useState<{ ok: boolean; ai_enabled: boolean; note: string | null } | null>(null);
  const [err, setErr] = useState<string | null>(null);

  useEffect(() => {
    api<{ ok: boolean; ai_enabled: boolean; note: string | null }>("/")
      .then(setStatus)
      .catch((e) => setErr(e?.detail || "Backend unreachable"));
  }, []);

  return (
    <div className="min-h-screen flex bg-slate-50 text-slate-900">
      <aside className="w-60 shrink-0 border-r bg-white p-4 flex flex-col gap-1">
        <div className="font-bold text-lg mb-4">StudySmart</div>
        {NAV.map((n) => {
          const active = n.to === "/" ? path === "/" : path.startsWith(n.to);
          return (
            <Link
              key={n.to}
              to={n.to}
              className={`px-3 py-2 rounded text-sm ${active ? "bg-slate-900 text-white" : "hover:bg-slate-100"}`}
            >
              {n.label}
            </Link>
          );
        })}
        <div className="mt-auto pt-4 text-xs text-slate-500">
          Backend: <span className="font-mono">{API_URL}</span>
          <div className="mt-2">
            {err ? (
              <span className="text-red-600">offline</span>
            ) : status ? (
              <>
                <span className="text-emerald-600">online</span>
                {!status.ai_enabled && (
                  <div className="mt-1 text-amber-700">No GEMINI_API_KEY — AI disabled</div>
                )}
              </>
            ) : (
              "checking…"
            )}
          </div>
        </div>
      </aside>
      <main className="flex-1 p-6 overflow-x-auto">{children}</main>
    </div>
  );
}
