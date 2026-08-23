#!/usr/bin/env bash
# Turns the raw simulator captures into web-sized images for apps/website.
# Source: build/app-screenshots (see capture-app-screenshots.sh).
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"

SRC=${1:-build/app-screenshots}
OUT=apps/website/public/screenshots
mkdir -p "$OUT"

# The site shows a phone as large as ~420 CSS px wide, so 840 keeps it crisp on
# a 2x display without shipping the 1206px original for every one.
# `guessed` is captured too (the driver still stops there), but nothing on
# the site shows it, so it is not shipped.
for name in home lobby round reveal results; do
  [ -f "$SRC/$name.png" ] || { echo "missing $SRC/$name.png" >&2; exit 1; }
  sips -s format jpeg -s formatOptions 80 -Z 840 "$SRC/$name.png" \
       --out "$OUT/$name.jpg" >/dev/null
done

echo "prepared:"
ls -lh "$OUT" | awk 'NR>1 {print "  " $9 "  " $5}'
