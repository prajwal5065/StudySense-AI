import { createFileRoute } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import { AppShell } from "@/components/layout/AppShell";
import { api } from "@/lib/api";

export const Route = createFileRoute("/agents")({
  head: () => ({ meta: [{ title: "Agent Trace — StudySmart" }] }),
  component: AgentsPage,
});

function AgentsPage() {
  const [rows, setRows] = useState<any[]>([]);
  useEffect(() => {
    const t = setInterval(() => api<any[]>("/analytics/agent-runs?limit=50").then(setRows).catch(() => {}), 2000);
    api<any[]>("/analytics/agent-runs?limit=50").then(setRows).catch(() => {});
    return () => clearInterval(t);
  }, []);
  return (
    <AppShell>
      <h1 className="text-2xl font-bold">Multi-Agent Activity</h1>
      <p className="text-slate-600 mt-1">Live trace of every agent run (auto-refresh every 2s).</p>
      <div className="mt-4 bg-white border rounded-lg overflow-x-auto">
        <table className="w-full text-sm">
          <thead className="bg-slate-50 text-left">
            <tr><th className="p-2">When</th><th>Agent</th><th>Doc</th><th>ms</th><th>OK</th><th>In</th><th>Out</th></tr>
          </thead>
          <tbody>
            {rows.map((r) => (
              <tr key={r.id} className="border-t align-top">
                <td className="p-2 text-xs">{r.created_at}</td>
                <td className="font-medium">{r.agent}</td>
                <td className="font-mono text-xs">{r.doc_id?.slice(0, 8)}</td>
                <td>{r.ms}</td>
                <td>{r.ok ? "✓" : <span className="text-red-600">✗ {r.error}</span>}</td>
                <td className="text-xs text-slate-500 max-w-xs truncate">{r.input_summary}</td>
                <td className="text-xs text-slate-500 max-w-xs truncate">{r.output_summary}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </AppShell>
  );
}
