# Deployment Guide

## Local Development

### Frontend
```bash
bun install
bun run dev
```

### Backend
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env  # add your GEMINI_API_KEY
uvicorn app.main:app --reload --port 8000
```

## Docker

```bash
docker compose up --build
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `GEMINI_API_KEY` | — | Required for AI features |
| `MAX_WORKERS` | `4` | Background worker count |
| `LOG_LEVEL` | `INFO` | Logging verbosity |
| `DATA_DIR` | `./data` | Data storage path |
