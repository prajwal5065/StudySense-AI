# StudySmart AI Intelligence Platform — Plan

## Ground rules from your message
- **No Supabase / no Lovable Cloud.** Use a local database.
- **No login / signup.** Single-user local app.
- **No API key from me.** I leave `GEMINI_API_KEY` blank in `.env` — you fill it in.
- **Backend:** Python + FastAPI (as you asked).
- **Frontend:** Keep the existing TanStack Start + Tailwind UI, extend it.
- Do **not** remove existing features; add on top.

## Architecture

```text
┌────────────────────────────┐        ┌──────────────────────────────┐
│  Frontend (TanStack Start) │ HTTP   │  Backend (FastAPI, Python)   │
│  - existing UI             │ ─────▶ │  - REST + SSE streaming      │
│  - new dashboards/graphs   │        │  - Multi-agent orchestrator  │
└────────────────────────────┘        │  - Gemini client (your key)  │
                                      │  - SQLite + sqlite-vec       │
                                      │  - Local file storage        │
                                      │  - Background jobs (RQ-lite) │
                                      └──────────────────────────────┘
```

- **DB:** SQLite (file at `backend/data/studysmart.db`) + `sqlite-vec` extension for embeddings. Zero-install, fully local.
- **Vector search:** `sqlite-vec` (cosine).
- **File storage:** `backend/data/uploads/<doc_id>/...` on disk.
- **Jobs:** in-process task queue (asyncio) — no Redis required for local.
- **AI key:** read from `GEMINI_API_KEY` env var; `.env.example` ships blank.

## Repo layout (added, nothing removed)

```text
/backend
  app/
    main.py                  # FastAPI app + CORS
    config.py                # reads .env, GEMINI_API_KEY (blank by default)
    db.py                    # SQLite + sqlite-vec setup, migrations runner
    migrations/              # numbered .sql files
    models/                  # pydantic schemas
    routers/
      documents.py           # upload, list, delete
      ingest.py              # trigger pipeline, status
      graph.py               # knowledge graph nodes/edges
      topics.py              # importance, trends, hot/cold
      questions.py           # clusters, variations
      formulas.py            # formula intelligence
      predict.py             # predicted paper
      quiz.py                # mock test gen + submit + score
      planner.py             # study planner
      progress.py            # weakness tracking
      chat.py                # RAG tutor (SSE stream)
      revision.py            # 1/5/15-min revision
      analytics.py           # dashboard aggregates
    agents/
      base.py                # Agent ABC (role/input/output/prompt/tools/memory)
      orchestrator.py        # DAG runner with retries + caching
      parser_agent.py
      ocr_agent.py
      topic_agent.py
      question_agent.py
      formula_agent.py
      graph_agent.py
      trend_agent.py
      importance_agent.py
      prediction_agent.py
      planner_agent.py
      quiz_agent.py
      tutor_agent.py
      report_agent.py
    services/
      gemini.py              # thin client; raises clear error if key blank
      embeddings.py          # Gemini embeddings + cache table
      ocr.py                 # Gemini vision OCR
      chunker.py
      retriever.py           # hybrid: vector + BM25
      citations.py           # page/section provenance
      hallucination.py       # grounding check
      clustering.py          # HDBSCAN over question embeddings
      importance.py          # weighted scoring formula
      trends.py
    workers/
      queue.py               # asyncio job queue
      jobs.py                # ingestion pipeline job
  .env.example               # GEMINI_API_KEY=  (blank)
  requirements.txt
  README.md                  # how to run

/src (existing TanStack app — extended)
  lib/api.ts                 # fetch wrapper -> VITE_API_URL (default http://localhost:8000)
  routes/
    dashboard.tsx            # analytics dashboard (new)
    graph.tsx                # interactive knowledge graph
    trends.tsx               # topic trend charts
    predict.tsx              # predicted paper view
    quiz.tsx, quiz.$id.tsx   # mock tests
    planner.tsx              # study planner
    revision.tsx             # 1/5/15-min modes
    progress.tsx             # weakness/strength tracking
    (existing routes untouched)
  components/
    graph/KnowledgeGraph.tsx # React Flow
    charts/* (Recharts)
    citations/CitationBadge.tsx
    ai/ConfidenceBadge.tsx
    ai/ReasonList.tsx        # explainability block
```

## Database schema (SQLite migrations)

Tables: `documents`, `pages`, `chunks`, `embeddings` (vec0 virtual table), `topics`, `subtopics`, `topic_edges`, `questions`, `question_clusters`, `formulas`, `papers` (year/subject), `paper_questions`, `importance_scores`, `trend_points`, `predicted_papers`, `predicted_questions`, `mock_tests`, `mock_attempts`, `mock_answers`, `study_plans`, `plan_tasks`, `progress_events`, `weak_topics`, `chat_sessions`, `chat_messages`, `citations`, `agent_runs` (audit log), `embedding_cache` (hash→vector to avoid recompute).

Every AI output row stores: `confidence`, `reason_json`, `source_doc_id`, `source_page`, `source_section` for the explainability + hallucination layers.

## Feature → module map (all 18)

1. Knowledge Graph → `graph_agent` + `routers/graph.py` + `KnowledgeGraph.tsx` (React Flow).
2. Semantic Q clustering → `clustering.py` (HDBSCAN on embeddings) + `question_clusters` table.
3. Importance score → `importance.py` weighted formula (freq, marks, coverage, similarity, recency, edges).
4. Trend analysis → `trends.py` + Recharts line/area.
5. Prediction engine → `prediction_agent` using trends + clusters + marks distribution.
6. Mock test gen → `quiz_agent` with difficulty knob; auto-grade via tutor_agent with rubric.
7. Weakness tracking → `progress_events` rollups → recommendations.
8. Study planner → `planner_agent` produces day-by-day tasks until exam date.
9. Formula intelligence → `formula_agent` enriches every formula (vars, mistakes, related).
10. Explainability → every response wraps `{answer, confidence, reasons[], citations[]}`.
11. Hallucination detection → `hallucination.py` re-checks claims vs retrieved chunks.
12. Multi-agent workflow → `orchestrator.py` DAG; each agent declares role/input/output/prompt/tools/memory.
13. Analytics dashboard → `routers/analytics.py` aggregates + dashboard route.
14. Citation system → `citations.py` attaches `{doc, page, paragraph}` to every chunk used.
15. Revision modes → `revision.py` summarizer at 4 compression levels.
16. Modular architecture → enforced by the `services/` + `agents/` split above.
17. Performance → embedding cache table, file-hash dedupe, async pipeline, SSE streaming, incremental re-ingest.
18. UI improvements → Recharts, React Flow, progress rings, heatmap, calendar, dark mode toggle.

## Data flow (ingest → intelligence)

```text
upload → parser → ocr → chunker → embeddings(+cache)
       → topic_agent ─┐
       → question_agent ─┐
       → formula_agent ─┐
                         ├─▶ graph_agent ─▶ importance_agent ─▶ trend_agent
                         │                                    └─▶ prediction_agent
                         └─▶ clustering ─▶ question_clusters
chat / quiz / revision / planner agents read from this consolidated store.
```

## Frontend integration

- New `src/lib/api.ts` reads `VITE_API_URL` (default `http://localhost:8000`).
- Existing pages keep working; new pages added as separate routes so nothing existing breaks.
- Chat uses SSE (`EventSource`) from `/chat/stream`.
- Knowledge graph uses React Flow (`reactflow` package).
- Charts use Recharts (already common in shadcn stack).

## How you run it locally

```bash
# backend
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # then paste your Gemini key into .env
uvicorn app.main:app --reload --port 8000

# frontend (existing)
bun install
bun run dev
```

If `GEMINI_API_KEY` is blank, AI endpoints return `503 {error: "GEMINI_API_KEY not set"}` so the UI can show a friendly banner — nothing crashes.

## Delivery in small PR-sized steps

I'll ship in this order so each step is reviewable and the app stays working:

1. **Backend skeleton** — FastAPI app, SQLite + sqlite-vec, migrations, `.env.example`, health check, CORS, Gemini client stub.
2. **Ingestion pipeline** — upload, parser, OCR, chunker, embeddings + cache, citations.
3. **Agents framework + orchestrator** — base class, DAG runner, agent_runs audit, first 4 agents (topic, question, formula, graph).
4. **Knowledge graph API + UI** (React Flow page).
5. **Clustering + importance + trends** (APIs + charts page).
6. **Prediction engine + predicted paper UI.**
7. **Mock test generator + grading + UI.**
8. **Planner + weakness tracking + recommendations UI.**
9. **RAG chat (SSE) + citations + hallucination + confidence badges.**
10. **Revision modes + analytics dashboard + dark mode polish.**

Each step lands as one focused change set with its own migrations and types. Existing features stay untouched.

## Open assumption I'm making (flag now if wrong)
- Local SQLite + sqlite-vec is fine for you (single user, no server). If you'd rather use local Postgres + pgvector via Docker, say the word and I'll swap step 1 only — the rest of the plan is unchanged.

Approve and I'll start with **Step 1: backend skeleton**.