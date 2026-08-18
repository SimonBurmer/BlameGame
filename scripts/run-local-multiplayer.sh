#!/usr/bin/env bash
# One-shot local dev setup: starts the backend, the Backlog.md board, and two
# iOS simulators running the app, so you can test multiplayer (create on one,
# join on the other) without a physical second device.
#
# Usage:
#   scripts/run-local-multiplayer.sh
#
# Requires: Xcode simulators, Flutter, CocoaPods (see README "First-time
# setup"), a backend/.venv with deps installed, and the `backlog` CLI.
set -euo pipefail

cd "$(dirname "$0")/.."

API_BASE="${API_BASE:-http://localhost:8000}"
BACKLOG_PORT="${BACKLOG_PORT:-6420}"
SIM_A_NAME="${SIM_A_NAME:-iPhone 17}"
SIM_B_NAME="${SIM_B_NAME:-iPhone 17 Pro}"

PIDS=()
cleanup() {
  echo
  echo "Shutting down..."
  for pid in "${PIDS[@]}"; do kill "$pid" 2>/dev/null || true; done
}
trap cleanup INT TERM EXIT

# --- backend -----------------------------------------------------------
if curl -sf "$API_BASE/health" > /dev/null 2>&1; then
  echo "Backend already running at $API_BASE"
else
  echo "Starting backend..."
  (cd backend && source .venv/bin/activate && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000) &
  PIDS+=("$!")
  for _ in $(seq 1 30); do
    curl -sf "$API_BASE/health" > /dev/null 2>&1 && break
    sleep 1
  done
  curl -sf "$API_BASE/health" > /dev/null 2>&1 || { echo "Backend failed to start" >&2; exit 1; }
  echo "Backend up at $API_BASE"
fi

# --- backlog board -------------------------------------------------------
echo "Starting Backlog.md board on port $BACKLOG_PORT..."
backlog browser --port "$BACKLOG_PORT" --no-open &
PIDS+=("$!")
sleep 1
open "http://127.0.0.1:$BACKLOG_PORT" || true

# --- simulators ----------------------------------------------------------
boot_by_name() {
  local name="$1"
  local udid
  udid=$(xcrun simctl list devices available | grep -F "$name (" | grep -v "Pro Max" | head -1 | sed -E 's/.*\(([-A-F0-9]+)\).*/\1/')
  if [ -z "$udid" ]; then
    echo "No simulator named '$name' found. Edit SIM_A_NAME/SIM_B_NAME or create one in Xcode." >&2
    exit 1
  fi
  xcrun simctl bootstatus "$udid" -b > /dev/null 2>&1 || xcrun simctl boot "$udid" > /dev/null 2>&1 || true
  echo "$udid"
}

UDID_A=$(boot_by_name "$SIM_A_NAME")
UDID_B=$(boot_by_name "$SIM_B_NAME")

echo "Player 1 -> $SIM_A_NAME ($UDID_A)"
echo "Player 2 -> $SIM_B_NAME ($UDID_B)"
echo "API_BASE=$API_BASE"
echo

open -a Simulator

flutter run -d "$UDID_A" --dart-define=API_BASE="$API_BASE" &
PIDS+=("$!")
sleep 3
flutter run -d "$UDID_B" --dart-define=API_BASE="$API_BASE" &
PIDS+=("$!")

wait
