#!/usr/bin/env bash
# Rebuild and reinstall everything after merging changes into main.
#
# run-local-multiplayer.sh is for *starting from nothing*; it deliberately
# reuses a backend that is already up and installs over whatever app is on the
# simulator. After a merge that is exactly wrong: the old uvicorn keeps serving
# pre-merge Python (it rejects fields the new client sends) and the simulator
# keeps running a stale binary. Symptom is "my merged feature isn't there".
#
# This script force-restarts the backend, rebuilds the app, and does a clean
# uninstall/install on every booted simulator.
#
# Usage:
#   scripts/refresh-local.sh            # refresh both
#   scripts/refresh-local.sh backend    # backend only
#   scripts/refresh-local.sh app        # app only
set -euo pipefail

cd "$(dirname "$0")/.."

PORT="${PORT:-8010}"
API_BASE="${API_BASE:-http://localhost:$PORT}"
BUNDLE_ID="${BUNDLE_ID:-com.blamegame.app}"
APP_PATH="$PWD/build/ios/iphonesimulator/Runner.app"
LOG="${LOG:-/tmp/blamegame-backend.log}"

what="${1:-all}"

# --- backend -------------------------------------------------------------
if [ "$what" = all ] || [ "$what" = backend ]; then
  echo "==> Restarting backend on port $PORT"
  # Kill by the exact uvicorn invocation, not by port: something else may own
  # the port (an abandoned kubectl-oidc_login callback server squats :8000 and
  # answers 404 on /health, which reads exactly like a broken backend).
  pkill -f "uvicorn app.main:app" 2>/dev/null || true
  sleep 1

  # backend/.venv has been Python 3.9 on this machine while the project targets
  # 3.12, so prefer an explicit 3.12 venv if one is present.
  if [ -x backend/.venv312/bin/python ]; then
    PY="$PWD/backend/.venv312/bin/python"
  elif [ -x backend/.venv/bin/python ]; then
    PY="$PWD/backend/.venv/bin/python"
  else
    echo "No backend venv found. Create one:" >&2
    echo "  cd backend && /opt/homebrew/opt/python@3.12/bin/python3.12 -m venv .venv && .venv/bin/pip install -e '.[dev]'" >&2
    exit 1
  fi
  echo "    python: $("$PY" --version 2>&1) ($PY)"

  # Redirect stdin too: without it the child inherits the terminal and the
  # script blocks waiting on it instead of returning.
  (cd backend && PYTHONPATH=. nohup "$PY" -m uvicorn app.main:app \
     --host 0.0.0.0 --port "$PORT" < /dev/null > "$LOG" 2>&1 &)
  disown 2>/dev/null || true

  for _ in $(seq 1 30); do
    curl -sf "$API_BASE/health" > /dev/null 2>&1 && break
    sleep 1
  done
  if ! curl -sf "$API_BASE/health" > /dev/null 2>&1; then
    echo "Backend failed to start. Last 20 lines of $LOG:" >&2
    tail -20 "$LOG" >&2
    exit 1
  fi
  echo "    up at $API_BASE"
fi

# --- app -----------------------------------------------------------------
if [ "$what" = all ] || [ "$what" = app ]; then
  # A live `flutter run` holds build/ios; a rebuild underneath it races.
  if pgrep -f "flutter run" > /dev/null 2>&1; then
    echo "A 'flutter run' session is live. Quit it (q) first, then re-run." >&2
    exit 1
  fi

  BOOTED=$(xcrun simctl list devices booted | sed -nE 's/.*\(([-A-F0-9]{36})\) \(Booted\).*/\1/p')
  if [ -z "$BOOTED" ]; then
    echo "No booted simulators. Boot one, or use scripts/run-local-multiplayer.sh." >&2
    exit 1
  fi

  echo "==> Building app (API_BASE=$API_BASE)"
  flutter build ios --simulator --debug --dart-define=API_BASE="$API_BASE"

  # Uninstall before install: installing over the top can leave a stale app
  # that looks like "my change didn't work" (see .claude/CLAUDE.md).
  for udid in $BOOTED; do
    name=$(xcrun simctl list devices booted | grep -F "$udid" | sed -E 's/^ *(.*) \(.*\) \(Booted\).*/\1/')
    echo "==> $name"
    xcrun simctl terminate "$udid" "$BUNDLE_ID" > /dev/null 2>&1 || true
    xcrun simctl uninstall "$udid" "$BUNDLE_ID" > /dev/null 2>&1 || true
    xcrun simctl install "$udid" "$APP_PATH"
    xcrun simctl launch "$udid" "$BUNDLE_ID" > /dev/null
    echo "    reinstalled and launched"
  done
fi

echo
echo "Done. Backend log: $LOG"
echo "For hot reload, attach a session per simulator (never two at once):"
echo "  flutter run -d <udid> --use-application-binary=$APP_PATH"
