#!/usr/bin/env bash
# Turns the raw simulator captures into web-sized images for apps/website.
# Source: build/app-screenshots (see capture-app-screenshots.sh).
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"

SRC=${1:-build/app-screenshots}
OUT=apps/website/public/screenshots
mkdir -p "$OUT"

# Displayed at ~270 CSS px wide; 540 keeps them crisp on a 2x display without
# shipping a 1206px original for every one.
for name in lobby round guessed reveal results; do
  [ -f "$SRC/$name.png" ] || { echo "missing $SRC/$name.png" >&2; exit 1; }
  sips -s format jpeg -s formatOptions 78 -Z 540 "$SRC/$name.png" \
       --out "$OUT/$name.jpg" >/dev/null
done

echo "prepared:"
ls -lh "$OUT" | awk 'NR>1 {print "  " $9 "  " $5}'
