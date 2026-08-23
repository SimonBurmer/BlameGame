#!/usr/bin/env bash
# Captures real screenshots of the app on a simulator, for the website.
#
# integration_test/marketing_screenshots_test.dart drives the UI and prints a
# "SHOT: <name>" marker whenever the app is sitting in a state worth
# photographing; this script watches for those markers and shoots with simctl.
# Doing the capture host-side keeps the pictures exactly what a person sees,
# and sidesteps the platform-specific screenshot APIs entirely.
set -euo pipefail

cd "$(git rev-parse --show-toplevel)"
OUT=${1:-build/app-screenshots}
mkdir -p "$OUT"

# --- backend --------------------------------------------------------------
BACKEND_PID=""
if curl -sf http://localhost:8000/health >/dev/null 2>&1; then
  echo "backend: already running"
else
  echo "backend: starting"
  ( cd backend && .venv/bin/python -m uvicorn app.main:app --port 8000 >/tmp/blame-backend.log 2>&1 ) &
  BACKEND_PID=$!
  for _ in $(seq 1 40); do
    curl -sf http://localhost:8000/health >/dev/null 2>&1 && break
    sleep 0.5
  done
  curl -sf http://localhost:8000/health >/dev/null 2>&1 || {
    echo "backend did not come up; see /tmp/blame-backend.log" >&2; exit 1; }
fi
cleanup() { [ -n "$BACKEND_PID" ] && kill "$BACKEND_PID" 2>/dev/null || true; }
trap cleanup EXIT

# --- simulator ------------------------------------------------------------
UDID=$(xcrun simctl list devices booted -j | python3 -c "
import json,sys
d=json.load(sys.stdin)['devices']
print(next((x['udid'] for v in d.values() for x in v if x['state']=='Booted'), ''))")
[ -n "$UDID" ] || { echo "no booted simulator" >&2; exit 1; }
echo "simulator: $UDID"

# --- drive, shooting on each marker ---------------------------------------
echo "driving…"
set +e
flutter drive \
  --driver=test_driver/integration_test.dart \
  --target=integration_test/marketing_screenshots_test.dart \
  -d "$UDID" 2>&1 | while IFS= read -r line; do
    case "$line" in
      *"SHOT: "*)
        name=$(printf '%s' "$line" | sed -E 's/.*SHOT: ([a-z]+).*/\1/')
        # The marker fires as the state lands; give the frame a moment to paint.
        sleep 2
        xcrun simctl io "$UDID" screenshot "$OUT/$name.png" >/dev/null 2>&1 \
          && echo "  shot $name"
        ;;
      *"Error"*|*"error:"*|*"FAILED"*) echo "  ! $line" ;;
    esac
  done
set -e

echo
echo "captured into $OUT:"
ls -1 "$OUT" 2>/dev/null || echo "  (nothing)"
