import { createFileRoute } from "@tanstack/react-router";
import { AppShell } from "@/components/layout/AppShell";
import { API_URL } from "@/lib/api";

export const Route = createFileRoute("/settings")({
  head: () => ({ meta: [{ title: "Settings — StudySmart" }] }),
  component: SettingsPage,
});

function SettingsPage() {
  return (
    <AppShell>
      <h1 className="text-2xl font-bold">Settings</h1>
      <div className="mt-4 bg-white border rounded-lg p-5 max-w-2xl text-sm space-y-3">
        <div><div className="font-semibold">Backend URL</div><div className="font-mono">{API_URL}</div><div className="text-xs text-slate-500">Override with <code>VITE_API_URL</code> in frontend <code>.env</code>.</div></div>
        <hr />
        <div>
          <div className="font-semibold">Gemini API key</div>
          <p className="text-slate-600">The backend reads <code>GEMINI_API_KEY</code> from <code>backend/.env</code>. The shipped value is blank — paste your own key and restart <code>uvicorn</code>:</p>
          <pre className="mt-2 bg-slate-100 p-3 rounded text-xs">{`# backend/.env
GEMINI_API_KEY=YOUR_KEY_HERE`}</pre>
          <p className="text-xs text-slate-500 mt-2">Get a free key at <a className="underline" href="https://aistudio.google.com/apikey" target="_blank">aistudio.google.com/apikey</a>.</p>
        </div>
        <hr />
        <div>
          <div className="font-semibold">Storage</div>
          <p className="text-slate-600">All data is stored locally in <code>backend/data/</code> — SQLite DB + uploaded files. Nothing leaves your machine except calls to the Gemini API (only when AI features are used).</p>
        </div>
      </div>
    </AppShell>
  );
}
