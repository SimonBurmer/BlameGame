# PhotoRoulette Backend

FastAPI backend for the PhotoRoulette game: rooms, players, photo upload, and a
backend-driven round timer. State is held **in memory** (no database) and live
updates are pushed over **WebSockets**.

## Run locally

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"     # installs runtime + test deps
pytest                       # 39 tests, no server needed
uvicorn app.main:app --reload
# → http://127.0.0.1:8000/docs
```

## Deploy to Railway

This directory is Railway-ready:

- `railway.json` — Nixpacks build + start command
  (`uvicorn app.main:app --host 0.0.0.0 --port $PORT`), pinned to **1 replica**.
- `Procfile` — same start command as a fallback.
- `.python-version` — Python 3.12.

Steps:

1. In Railway, create a project from this GitHub repo.
2. Set the **root directory** to `backend/` (so Railway builds this folder, not
   the Flutter app at the repo root).
3. Deploy. Railway installs the `[project].dependencies` from `pyproject.toml`
   (the `dev` extras are skipped in production).
4. Note the generated public URL, e.g. `https://<app>.up.railway.app`.

### Important constraints (by design)

- **Single instance only.** Game state lives in RAM, so it cannot be shared
  across replicas — keep `numReplicas: 1`. Do not enable horizontal scaling.
- **Ephemeral storage.** Railway's filesystem resets on each redeploy, so
  uploaded photos and in-progress games are lost on deploy. Acceptable for
  short-lived party games. (For persistence later: attach a Railway Volume and
  point `UPLOAD_DIR` at it, plus a real store for game state.)
- **CORS is open** (`allow_origins=["*"]`) so the Flutter web/mobile client can
  call it from any origin.

## Pointing the Flutter app at this backend

The Flutter app reads its base URL from a compile-time define:

```bash
# Local backend
flutter run -d chrome --dart-define=API_BASE=http://localhost:8000

# Deployed Railway backend
flutter run -d chrome --dart-define=API_BASE=https://<app>.up.railway.app
```

The app derives the WebSocket URL automatically (`http`→`ws`, `https`→`wss`).
