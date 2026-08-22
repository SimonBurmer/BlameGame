# Blame Game backend

FastAPI backend for the Blame Game game: rooms, players, photo upload, and a
backend-driven round timer. State is held **in memory** (no database) and live
updates are pushed over **WebSockets**.

## Run locally

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"     # installs runtime + test deps
pytest                       # 73 tests, no server needed
uvicorn app.main:app --reload
# → http://127.0.0.1:8000/docs
```

## Deploy to Railway

This directory is Railway-ready:

- `railway.json` — Nixpacks build + start command
  (`uvicorn app.main:app --host 0.0.0.0 --port $PORT`), pinned to **1 replica**,
  with a `/health` healthcheck that gates each deploy.
- `.python-version` — Python 3.12.

### One-time setup (manual, in the Railway dashboard)

1. Create a new project and add a service for this backend.
2. Leave **Settings → Root Directory** *empty*. The GitHub Actions deploy job
   runs `railway up` from within `backend/`, so it uploads this folder as the
   build root already. Setting Root Directory to `backend` on top of that makes
   Nixpacks look for `backend/backend/` and the build fails with
   `Failed to read app source directory`.
3. **Settings → Networking → Generate Domain** to get a public URL, e.g.
   `https://<app>.up.railway.app`.
4. **Variables**: `UPLOAD_DIR` is optional — it defaults to `uploads`, which
   works out of the box. Only set it if you attach a Volume (see below).
   `PORT` is injected by Railway; do not set it yourself.
5. Deploy. Railway installs `[project].dependencies` from `pyproject.toml`
   (the `dev` extras are skipped in production).
6. Verify: `curl https://<app>.up.railway.app/health` → `{"status":"ok"}`.

> If you ever switch to Railway's own GitHub integration instead of the Actions
> job, the opposite applies: that integration pulls the whole repo, so Root
> Directory **must** be set to `backend`.

### Automatic deploys (GitHub Actions)

`.github/workflows/backend.yml` runs the backend tests on every PR and, on
merge to `main`, deploys to Railway. It needs two things in the GitHub repo
(**Settings → Secrets and variables → Actions**):

| Kind | Name | Value |
|------|------|-------|
| Secret | `RAILWAY_TOKEN` | Railway → Account Settings → Tokens → create a token |
| Variable | `RAILWAY_SERVICE` | The service name shown in the Railway project |

If you'd rather not use GitHub Actions at all, Railway's own GitHub integration
can auto-deploy on push to `main` — in that case delete the `deploy` job from
the workflow so the two don't both deploy.

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
