# Architecture Overview

StudySense AI is a full-stack, locally-runnable AI study assistant.

## Components

- **Frontend**: React + TanStack Router (Vite/Bun)
- **Backend**: FastAPI + SQLite + Google Gemini
- **AI Pipeline**: Document ingestion → chunking → embedding → RAG

## Data Flow

1. User uploads PDF/DOCX/image/TXT
2. Backend parses, chunks, and embeds the content
3. Topic, question, and formula agents extract structured knowledge
4. RAG retrieval powers chat, quiz, prediction, and planning features

## Database

SQLite is used for persistence. Schema migrations run on startup.
