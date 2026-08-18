# PhotoRoulette2 — Project Knowledge

A clone of the "Photo Roulette" party game: players join a room, contribute random
photos from their camera roll, then guess *whose* photo each round shows. Points are
awarded for correct + fast guesses; rounds tally into a final leaderboard.

## Stack

- **Frontend:** Flutter (Dart SDK `^3.11.5`), Material 3. Code in `lib/`.
- **Backend:** FastAPI (Python 3.12), in-memory state + WebSockets. Code in `backend/app/`.
- **Deploy:** backend targets Railway (`backend/railway.json`, `Procfile`). Single replica.

## Architecture

### Flutter (`lib/`)
Layered: `config → models → services → state → screens`.
- `config.dart` — `apiBase` from `String.fromEnvironment('API_BASE', default 'http://localhost:8000')`; `wsBase` derived by swapping `http`→`ws`. Production URL is passed via `--dart-define=API_BASE=<url>`.
- `models/game_models.dart` — `GamePlayer`, `PhotoInfo`, and a sealed `GameEvent` hierarchy (deserialize-only).
- `services/api_client.dart` — thin `http` REST wrapper; injectable `http.Client` for tests.
- `services/game_socket.dart` — `web_socket_channel`, exposes `Stream<GameEvent>`.
- `state/game_controller.dart` — `ChangeNotifier` (no Provider/Riverpod/Bloc). One instance is created in `HomeScreen` and passed by constructor down through Lobby → Game → Results. Owns the ApiClient + GameSocket and all live game state.
- `screens/` — `home`, `lobby`, `game`, `results`.

### Backend (`backend/app/`)
Pure logic under thin I/O layers:
- `game.py`, `scoring.py` — pure game rules + scoring (well unit-tested).
- `main.py` — FastAPI routes (REST + one WS route `/ws/{code}/{player_id}`).
- `store.py` — process-wide in-memory `GameStore` singleton (`dict[code→Room]`). **State is lost on restart and can't be shared across replicas.**
- `connection.py` — `ConnectionManager`, broadcasts events to a room's sockets.
- `timer.py` — `RoundDriver` drives round timing (sleep injectable for tests).
- Photos are written to local disk under `uploads/{code}/` (ephemeral on Railway).

## Commands

### Flutter
```sh
flutter pub get
flutter analyze
flutter test
flutter run                      # needs a simulator/device
```

### Backend
```sh
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest                           # currently 39 tests
ruff check .                     # pyflakes (F) rules only — see backend/pyproject.toml
```

## Tickets / Backlog

Work is tracked with **Backlog.md** in `backlog/`. Tasks are grouped under milestones
(Core Gameplay, Accounts & Social, Infrastructure & Persistence, Gameplay Polish,
Testing & Quality) with dependency links.

```sh
backlog task list --plain
backlog board
backlog browser                  # web UI
```

## Working conventions (IMPORTANT)

- **One ticket = one PR.** Each Backlog task is implemented on its own branch
  (`feature/task-<id>-<slug>`) and opened as a separate pull request. Never bundle
  multiple tickets into one branch/PR.
- **Spawn a subagent per ticket when it fits.** For tickets that are self-contained
  units of work (most of them), dispatch a subagent to implement it — use an isolated
  **worktree** so parallel tickets don't collide. Keep small/trivial changes inline.
- Mark the ticket `In Progress` when starting and check off acceptance criteria as they
  land (`backlog task edit <id> -s "In Progress" --check-ac <n>`).
- **Never push to git without being asked** (also a global rule). Commit on the feature
  branch; open the PR only when the user requests it.
- Branch feature work off `main`, not off another in-flight feature branch.

## Style

Prefer the simplest solution that actually works: reuse what's already in the codebase,
stdlib/native before new dependencies, no abstractions or config that aren't needed yet.
Don't simplify away input validation at trust boundaries, error handling, or security.
