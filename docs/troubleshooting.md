# Troubleshooting

## AI features not working

Ensure `GEMINI_API_KEY` is set in `backend/.env`.

## Upload fails

- Check that the `data/uploads` directory exists and is writable.
- Verify the file size is under 50 MB.

## Database errors

Delete `data/studysmart.db` and restart the backend to re-run migrations.

## CORS errors

Add your frontend origin to `CORS_ORIGINS` in `backend/.env`, e.g.:
```
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

## Port conflicts

Change the port via the `PORT` env variable or CLI flag:
```bash
uvicorn app.main:app --port 8001
```
