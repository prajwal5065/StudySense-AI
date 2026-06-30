import { createFileRoute } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import { AppShell } from "@/components/layout/AppShell";
import { api } from "@/lib/api";

export const Route = createFileRoute("/graph")({
  head: () => ({ meta: [{ title: "Knowledge Graph — StudySmart" }] }),
  component: GraphPage,
});

type Node = { id: string; label: string; summary: string; importance: number };
type Edge = { src: string; dst: string; relation: string; weight: number };

/**
 * Lightweight SVG force-ish layout: radial placement by importance bucket.
 * Click a node to see details (questions + formulas).
 */
function GraphPage() {
  const [data, setData] = useState<{ nodes: Node[]; edges: Edge[] }>({ nodes: [], edges: [] });
  const [sel, setSel] = useState<any>(null);

  useEffect(() => { api<typeof data>("/graph").then(setData); }, []);

  const W = 800, H = 560, cx = W / 2, cy = H / 2;
  const ringR = (i: number, n: number) => 80 + (i % 3) * 110;
  const positions = new Map<string, { x: number; y: number }>();
  const sorted = [...data.nodes].sort((a, b) => (b.importance ?? 0) - (a.importance ?? 0));
  sorted.forEach((n, i) => {
    const r = ringR(i, sorted.length);
    const a = (2 * Math.PI * i) / Math.max(sorted.length, 1);
    positions.set(n.id, { x: cx + Math.cos(a) * r, y: cy + Math.sin(a) * r });
  });

  async function openTopic(id: string) {
    const d = await api(`/graph/topic/${id}`);
    setSel(d);
  }

  return (
    <AppShell>
      <h1 className="text-2xl font-bold">Knowledge Graph</h1>
      <p className="text-slate-600 mt-1">Edges from the graph agent (prerequisite / related / part_of). Node size ∝ importance.</p>
      <div className="mt-4 grid grid-cols-3 gap-4">
        <div className="col-span-2 bg-white border rounded-lg p-2 overflow-auto">
          <svg width={W} height={H}>
            {data.edges.map((e, i) => {
              const a = positions.get(e.src), b = positions.get(e.dst);
              if (!a || !b) return null;
              const color = e.relation === "prerequisite" ? "#0ea5e9" : e.relation === "part_of" ? "#a855f7" : "#94a3b8";
              return <line key={i} x1={a.x} y1={a.y} x2={b.x} y2={b.y} stroke={color} strokeOpacity={0.45} strokeWidth={Math.max(1, e.weight * 2)} />;
            })}
            {data.nodes.map((n) => {
              const p = positions.get(n.id)!;
              const r = 8 + (n.importance ?? 0) * 22;
              return (
                <g key={n.id} onClick={() => openTopic(n.id)} style={{ cursor: "pointer" }}>
                  <circle cx={p.x} cy={p.y} r={r} fill="#0f172a" />
                  <text x={p.x} y={p.y + r + 12} textAnchor="middle" fontSize={11} fill="#334155">{n.label}</text>
                </g>
              );
            })}
          </svg>
          {data.nodes.length === 0 && <div className="p-6 text-center text-slate-500">No graph yet. Upload material, then Recompute on the Topics page.</div>}
        </div>
        <div className="bg-white border rounded-lg p-4 min-h-[320px]">
          {!sel ? <div className="text-slate-500 text-sm">Click a node to inspect.</div> : (
            <div>
              <div className="font-semibold">{sel.topic.name}</div>
              <div className="text-sm text-slate-600 mt-1">{sel.topic.summary}</div>
              <div className="mt-3 text-xs uppercase text-slate-500">Past questions ({sel.questions.length})</div>
              <ul className="mt-1 text-sm space-y-1 max-h-40 overflow-auto">
                {sel.questions.slice(0, 8).map((q: any) => <li key={q.id} className="border-b py-1">{q.text} <span className="text-xs text-slate-400">[{q.marks ?? "?"}m]</span></li>)}
              </ul>
              <div className="mt-3 text-xs uppercase text-slate-500">Formulas ({sel.formulas.length})</div>
              <ul className="mt-1 text-sm space-y-1 max-h-40 overflow-auto">
                {sel.formulas.slice(0, 6).map((f: any) => <li key={f.id}><span className="font-mono text-xs">{f.latex}</span> — {f.name}</li>)}
              </ul>
            </div>
          )}
        </div>
      </div>
    </AppShell>
  );
}
