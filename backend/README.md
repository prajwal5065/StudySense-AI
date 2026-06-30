# StudySmart Backend (FastAPI)

Local, single-user AI study platform backend. No login, no cloud, no API key
is shipped — paste your own Gemini key into `.env` to enable AI features.

## Quick start

```bash
cd backend
python -m venv .venv
source .venv/bin/activate           # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                 # then edit and paste your GEMINI_API_KEY
uvicorn app.main:app --reload --port 8000
```

Then run the frontend (`bun run dev`) and it will talk to `http://localhost:8000`.

## What it does

- SQLite database at `./data/studysmart.db` (auto-created, with migrations)
- Local file storage at `./data/uploads/<doc_id>/`
- Multi-agent ingestion pipeline (parse → OCR → chunk → embed → topic/question/formula/graph)
- REST APIs for all 18 platform features (graph, importance, trends, prediction,
  quiz, planner, chat with RAG, revision, analytics, etc.)
- Embedding + LLM-response cache to avoid recomputation
- Citations on every retrieved chunk; confidence + reasoning on every AI output

## When `GEMINI_API_KEY` is blank

The server still starts and all CRUD endpoints work. AI endpoints return
`503 {"detail": "GEMINI_API_KEY not set"}` so the UI can show a friendly banner
— nothing crashes.

## Architecture

See the inline module docstrings:
- `app/agents/` — one file per agent, all inherit `BaseAgent`.
- `app/services/` — pure functions (Gemini client, chunker, retriever, etc.).
- `app/routers/` — thin HTTP layer.
- `app/workers/` — async background queue (in-process, no Redis).
- `app/migrations/` — numbered SQL files run on startup.