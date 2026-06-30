/**
 * Tiny fetch wrapper to the local FastAPI backend.
 * Reads VITE_API_URL; defaults to http://localhost:8000.
 *
 * No auth is sent — the backend is a single-user local service.
 */
export const API_URL =
  (import.meta as any).env?.VITE_API_URL?.replace(/\/$/, "") || "http://localhost:8000";

export type ApiError = { status: number; detail: string };

export async function api<T = any>(
  path: string,
  init: RequestInit & { json?: any } = {}
): Promise<T> {
  const { json, headers, ...rest } = init;
  const res = await fetch(`${API_URL}${path}`, {
    ...rest,
    headers: {
      ...(json !== undefined ? { "Content-Type": "application/json" } : {}),
      ...(headers || {}),
    },
    body: json !== undefined ? JSON.stringify(json) : rest.body,
  });
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const j = await res.json();
      detail = j.detail || JSON.stringify(j);
    } catch {}
    const err: ApiError = { status: res.status, detail };
    throw err;
  }
  if (res.status === 204) return undefined as T;
  const ct = res.headers.get("content-type") || "";
  return ct.includes("application/json") ? ((await res.json()) as T) : ((await res.text()) as any);
}

export async function uploadFile(file: File, subject: string, kind: string) {
  const fd = new FormData();
  fd.append("file", file);
  fd.append("subject", subject);
  fd.append("kind", kind);
  const res = await fetch(`${API_URL}/documents/upload`, { method: "POST", body: fd });
  if (!res.ok) throw { status: res.status, detail: await res.text() } as ApiError;
  return res.json() as Promise<{ document_id: string; job_id: string }>;
}
