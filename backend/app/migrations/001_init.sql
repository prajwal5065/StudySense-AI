-- Core ingestion
CREATE TABLE IF NOT EXISTS documents (
    id TEXT PRIMARY KEY,
    subject TEXT,
    kind TEXT,                  -- syllabus | pyq | notes | other
    filename TEXT,
    mime TEXT,
    sha256 TEXT,
    pages INTEGER DEFAULT 0,
    status TEXT DEFAULT 'uploaded', -- uploaded | parsing | embedding | ready | error
    error TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS pages (
    id TEXT PRIMARY KEY,
    doc_id TEXT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    page_no INTEGER,
    text TEXT
);

CREATE TABLE IF NOT EXISTS chunks (
    id TEXT PRIMARY KEY,
    doc_id TEXT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    page_no INTEGER,
    section TEXT,
    text TEXT,
    token_count INTEGER
);

CREATE TABLE IF NOT EXISTS embeddings (
    chunk_id TEXT PRIMARY KEY REFERENCES chunks(id) ON DELETE CASCADE,
    vector BLOB,                -- float32 little-endian
    dim INTEGER
);

CREATE TABLE IF NOT EXISTS embedding_cache (
    sha TEXT PRIMARY KEY,       -- sha256 of text+model
    vector BLOB,
    dim INTEGER
);

-- Knowledge layer
CREATE TABLE IF NOT EXISTS topics (
    id TEXT PRIMARY KEY,
    subject TEXT,
    name TEXT,
    summary TEXT,
    parent_id TEXT REFERENCES topics(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS topic_edges (
    src TEXT NOT NULL REFERENCES topics(id) ON DELETE CASCADE,
    dst TEXT NOT NULL REFERENCES topics(id) ON DELETE CASCADE,
    relation TEXT,              -- prerequisite | related | part_of
    weight REAL DEFAULT 1.0,
    PRIMARY KEY (src, dst, relation)
);

CREATE TABLE IF NOT EXISTS questions (
    id TEXT PRIMARY KEY,
    subject TEXT,
    doc_id TEXT REFERENCES documents(id) ON DELETE SET NULL,
    year INTEGER,
    marks INTEGER,
    text TEXT,
    topic_id TEXT REFERENCES topics(id) ON DELETE SET NULL,
    cluster_id INTEGER
);

CREATE TABLE IF NOT EXISTS question_clusters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject TEXT,
    label TEXT,
    size INTEGER
);

CREATE TABLE IF NOT EXISTS formulas (
    id TEXT PRIMARY KEY,
    subject TEXT,
    topic_id TEXT REFERENCES topics(id) ON DELETE SET NULL,
    latex TEXT,
    name TEXT,
    description TEXT,
    variables_json TEXT,
    mistakes_json TEXT,
    related_json TEXT
);

-- Analytics / scoring
CREATE TABLE IF NOT EXISTS importance_scores (
    topic_id TEXT PRIMARY KEY REFERENCES topics(id) ON DELETE CASCADE,
    score REAL,
    frequency INTEGER,
    avg_marks REAL,
    last_year INTEGER,
    reason_json TEXT
);

CREATE TABLE IF NOT EXISTS trend_points (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    topic_id TEXT REFERENCES topics(id) ON DELETE CASCADE,
    year INTEGER,
    count INTEGER,
    marks INTEGER
);

CREATE TABLE IF NOT EXISTS predicted_papers (
    id TEXT PRIMARY KEY,
    subject TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    meta_json TEXT
);

CREATE TABLE IF NOT EXISTS predicted_questions (
    id TEXT PRIMARY KEY,
    paper_id TEXT NOT NULL REFERENCES predicted_papers(id) ON DELETE CASCADE,
    topic_id TEXT,
    text TEXT,
    marks INTEGER,
    probability REAL,
    reason TEXT
);

-- Quizzes / mock tests
CREATE TABLE IF NOT EXISTS mock_tests (
    id TEXT PRIMARY KEY,
    subject TEXT,
    title TEXT,
    difficulty TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    questions_json TEXT          -- [{q, options?, answer, marks, topic_id}]
);

CREATE TABLE IF NOT EXISTS mock_attempts (
    id TEXT PRIMARY KEY,
    test_id TEXT REFERENCES mock_tests(id) ON DELETE CASCADE,
    started_at TEXT DEFAULT CURRENT_TIMESTAMP,
    submitted_at TEXT,
    score REAL,
    answers_json TEXT,
    feedback_json TEXT
);

-- Planner / progress
CREATE TABLE IF NOT EXISTS study_plans (
    id TEXT PRIMARY KEY,
    subject TEXT,
    exam_date TEXT,
    hours_per_day REAL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    plan_json TEXT
);

CREATE TABLE IF NOT EXISTS progress_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    topic_id TEXT,
    kind TEXT,                  -- quiz_correct | quiz_wrong | studied | revised
    delta REAL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Chat
CREATE TABLE IF NOT EXISTS chat_sessions (
    id TEXT PRIMARY KEY,
    subject TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS chat_messages (
    id TEXT PRIMARY KEY,
    session_id TEXT REFERENCES chat_sessions(id) ON DELETE CASCADE,
    role TEXT,                  -- user | assistant
    content TEXT,
    citations_json TEXT,
    confidence REAL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Multi-agent audit log
CREATE TABLE IF NOT EXISTS agent_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    agent TEXT,
    doc_id TEXT,
    input_summary TEXT,
    output_summary TEXT,
    ms INTEGER,
    ok INTEGER,
    error TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_chunks_doc ON chunks(doc_id);
CREATE INDEX IF NOT EXISTS idx_questions_subject ON questions(subject);
CREATE INDEX IF NOT EXISTS idx_questions_topic ON questions(topic_id);
CREATE INDEX IF NOT EXISTS idx_trend_topic ON trend_points(topic_id);