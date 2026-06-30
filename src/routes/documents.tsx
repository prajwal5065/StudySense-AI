import { createFileRoute } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import { AppShell } from "@/components/layout/AppShell";
import { api } from "@/lib/api";

export const Route = createFileRoute("/documents")({
  head: () => ({ meta: [{ title: "Documents — StudySmart" }] }),
  component: DocsPage,
});

type Doc = { id: string; subject: string | null; kind: string | null; filename: string; pages: number; status: string; created_at?: string };

function DocsPage() {
  const [docs, setDocs] = useState<Doc[]>([]);
  const [err, setErr] = useState<string | null>(null);

  async function load() {
    try { setDocs(await api<Doc[]>("/documents")); } catch (e: any) { setErr(e?.detail || "error"); }
  }
  useEffect(() => { load(); }, []);

  async function del(id: string) {
    if (!confirm("Delete this document and all its data?")) return;
    await api(`/documents/${id}`, { method: "DELETE" });
    load();
  }

  return (
    <AppShell>
      <h1 className="text-2xl font-bold">Documents</h1>
      {err && <div className="mt-4 p-3 rounded bg-red-50 border border-red-200 text-red-700">{err}</div>}
      <div className="mt-4 overflow-x-auto bg-white border rounded-lg">
        <table className="w-full text-sm">
          <thead className="bg-slate-50 text-left">
            <tr>
              <th className="p-2">Filename</th><th>Subject</th><th>Kind</th><th>Pages</th><th>Status</th><th></th>
            </tr>
          </thead>
          <tbody>
            {docs.map((d) => (
              <tr key={d.id} className="border-t">
                <td className="p-2 font-mono text-xs">{d.filename}</td>
                <td>{d.subject}</td>
                <td>{d.kind}</td>
                <td>{d.pages}</td>
                <td><span className={`px-2 py-0.5 rounded text-xs ${d.status === "ready" ? "bg-emerald-100 text-emerald-700" : "bg-slate-100"}`}>{d.status}</span></td>
                <td><button onClick={() => del(d.id)} className="text-red-600 text-xs hover:underline">delete</button></td>
              </tr>
            ))}
            {docs.length === 0 && <tr><td colSpan={6} className="p-6 text-center text-slate-500">No documents yet. <a href="/upload" className="underline">Upload one</a>.</td></tr>}
          </tbody>
        </table>
      </div>
    </AppShell>
  );
}
