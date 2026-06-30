# API Reference

Base URL: `http://localhost:8000`

## Core Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Root status |
| GET | `/health` | Health check |
| GET | `/version` | API version |

## Documents

| Method | Path | Description |
|--------|------|-------------|
| POST | `/documents/upload` | Upload a document |
| GET | `/documents` | List all documents |
| DELETE | `/documents/{id}` | Delete a document |

## Topics & Knowledge

| Method | Path | Description |
|--------|------|-------------|
| GET | `/topics` | List topics |
| POST | `/topics/recompute` | Recompute importance |
| GET | `/graph` | Knowledge graph |

## Study Tools

| Method | Path | Description |
|--------|------|-------------|
| POST | `/chat` | Tutor chat |
| POST | `/quiz/generate` | Generate quiz |
| GET | `/predict` | Exam prediction |
| GET | `/planner` | Study planner |
| GET | `/analytics/overview` | Dashboard stats |
